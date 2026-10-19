"""Video quality gates for pipeline deliveries.

Turn the failures that have actually shipped (black frames, missing
scenes, slideshow clips, out-of-target duration, missing audio/subtitles)
into hard, executable checks. A video that fails these gates must NOT be
presented as a deliverable — the compose/asset director sends it back to
assets instead.

Every gate returns a normalized result:
    {"name": str, "passed": bool, "value": float|int|str, "limit": float|int|str, "detail": str}

`run_all` returns {"passed": bool, "gates": [...], "summary": str}.

Checks are implemented with ffmpeg filters, so they run deterministically
and do not depend on the agent "remembering" to look at the video.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# ffmpeg helpers
# ---------------------------------------------------------------------------


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True)


def _run_text(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True)


def _ffprobe_duration(path: str) -> float:
    """Return media duration in seconds, or -1 on failure."""
    r = _run_text(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "csv=p=0",
            path,
        ]
    )
    try:
        return float(r.stdout.strip())
    except ValueError:
        return -1.0


def _has_stream(path: str, codec_type: str) -> bool:
    r = _run_text(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            codec_type,
            "-show_entries",
            "stream=codec_type",
            "-of",
            "csv=p=0",
            path,
        ]
    )
    return bool(r.stdout.strip())


# ---------------------------------------------------------------------------
# Individual gates
# ---------------------------------------------------------------------------


def gate_black_frame_ratio(
    video_path: str, max_black_ratio: float = 0.05, luma_threshold: int = 16
) -> dict[str, Any]:
    """Fraction of frames whose mean luma is below threshold (near-black).

    A deliberate fade-to-black is fine; a video that spends 50% of its
    runtime near-black (like the poem-video incident) is a composition bug.
    Uses raw grayscale frames: a near-black frame has mean luma < 16.
    """
    import numpy as np

    r = _run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-i",
            video_path,
            "-vf",
            "fps=2,scale=64:64,format=gray",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "gray",
            "-",
        ]
    )
    if not r.stdout:
        return {
            "name": "black_frame_ratio",
            "passed": False,
            "value": -1.0,
            "limit": max_black_ratio,
            "detail": "no frames produced",
        }
    buf = np.frombuffer(r.stdout, dtype=np.uint8).astype(float)
    n = int(len(buf) / (64 * 64))
    frames = buf[: n * 64 * 64].reshape(n, 64, 64)
    mean_luma = frames.mean(axis=(1, 2))
    black = int((mean_luma < luma_threshold).sum())
    ratio = black / n
    return {
        "name": "black_frame_ratio",
        "passed": ratio <= max_black_ratio,
        "value": round(ratio, 4),
        "limit": max_black_ratio,
        "detail": f"{black}/{n} frames near-black (mean luma<{luma_threshold}) ({ratio*100:.1f}%)",
    }


def gate_scene_count(
    manifest_scenes: list[Any], actual_clips: list[str]
) -> dict[str, Any]:
    """Every scene in the script/manifest must have a physical clip on disk."""
    expected = len(manifest_scenes or [])
    present = sum(1 for p in actual_clips if Path(p).is_file())
    return {
        "name": "scene_count",
        "passed": expected > 0 and present == expected,
        "value": present,
        "limit": expected,
        "detail": f"{present}/{expected} scene clips exist on disk",
    }


def gate_slideshow_motion(
    video_path: str, min_mean_diff: float = 1.5, sample_fps: int = 4
) -> dict[str, Any]:
    """Mean inter-frame luminance difference (0-255).

    Computed as the mean |frame[t+1] - frame[t]| across consecutive grayscale
    frames. Below ~1 the clip is a static image (slideshow); a real moving
    shot (Sora text-to-video push/pan) typically measures 3-6 at 4fps.
    """
    import numpy as np

    r = _run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-i",
            video_path,
            "-vf",
            f"fps={sample_fps},scale=90:160,format=gray",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "gray",
            "-",
        ]
    )
    # rawvideo of consecutive gray frames -> compare each frame to the next
    if not r.stdout:
        return {
            "name": "slideshow_motion",
            "passed": False,
            "value": -1.0,
            "limit": min_mean_diff,
            "detail": "no frames produced",
        }
    buf = np.frombuffer(r.stdout, dtype=np.uint8)
    n = int(len(buf) / (90 * 160))
    if n < 2:
        return {
            "name": "slideshow_motion",
            "passed": False,
            "value": -1.0,
            "limit": min_mean_diff,
            "detail": "too few frames",
        }
    frames = buf.reshape(n, 90, 160).astype(float)
    diff = float(np.abs(frames[1:] - frames[:-1]).mean())
    return {
        "name": "slideshow_motion",
        "passed": diff >= min_mean_diff,
        "value": round(diff, 3),
        "limit": min_mean_diff,
        "detail": f"mean inter-frame diff {diff:.2f} (0-255)",
    }


def gate_duration(
    video_path: str, target_seconds: float, tolerance: float = 0.10
) -> dict[str, Any]:
    dur = _ffprobe_duration(video_path)
    if dur < 0:
        return {
            "name": "duration",
            "passed": False,
            "value": -1.0,
            "limit": target_seconds,
            "detail": "cannot probe duration",
        }
    lo, hi = target_seconds * (1 - tolerance), target_seconds * (1 + tolerance)
    passed = lo <= dur <= hi
    return {
        "name": "duration",
        "passed": passed,
        "value": round(dur, 2),
        "limit": f"{lo:.1f}-{hi:.1f}",
        "detail": f"duration {dur:.2f}s, target {target_seconds:.1f}s",
    }


def gate_tone_contrast(
    video_path: str,
    max_dark_ratio: float = 0.55,
    min_bright_ratio: float = 0.03,
) -> dict[str, Any]:
    """Tone/contrast sanity: not a murky black blob.

    Uses a low-res grayscale histogram. 'dark' = luma < 32, 'bright' = luma > 160.
    Fails if the clip is overwhelmingly dark with almost no bright detail
    (the "ink wash but just black" failure mode).
    """
    import numpy as np

    r = _run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-i",
            video_path,
            "-vf",
            "fps=2,scale=64:64,format=gray",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "gray",
            "-",
        ]
    )
    if not r.stdout:
        return {
            "name": "tone_contrast",
            "passed": False,
            "value": -1.0,
            "limit": f"dark<{max_dark_ratio},bright>{min_bright_ratio}",
            "detail": "no frames produced",
        }
    buf = np.frombuffer(r.stdout, dtype=np.uint8).astype(float)
    n = int(len(buf) / (64 * 64))
    buf = buf[: n * 64 * 64]
    dark = float((buf < 32).mean())
    bright = float((buf > 160).mean())
    passed = dark <= max_dark_ratio and bright >= min_bright_ratio
    return {
        "name": "tone_contrast",
        "passed": passed,
        "value": round(dark, 3),
        "limit": f"dark<{max_dark_ratio},bright>{min_bright_ratio}",
        "detail": f"dark={dark*100:.1f}% bright={bright*100:.1f}%",
    }


def gate_has_audio(video_path: str) -> dict[str, Any]:
    has = _has_stream(video_path, "a")
    return {
        "name": "audio_present",
        "passed": has,
        "value": 1 if has else 0,
        "limit": 1,
        "detail": "AAC/mono audio stream present" if has else "NO audio stream",
    }


def gate_has_subtitles(subtitle_path: str) -> dict[str, Any]:
    p = Path(subtitle_path)
    exists = p.is_file() and p.stat().st_size > 0
    return {
        "name": "subtitles_present",
        "passed": exists,
        "value": 1 if exists else 0,
        "limit": 1,
        "detail": "subtitle file exists" if exists else "subtitle file missing",
    }


# ---------------------------------------------------------------------------
# Aggregate
# ---------------------------------------------------------------------------


def run_all(checks: list[dict[str, Any]]) -> dict[str, Any]:
    """Run a list of gates.

    Each check is a dict with a 'gate' key selecting the function, plus the
    kwargs for it:
        {"gate": "black_frame_ratio", "video_path": "...", "max_black_ratio": 0.05}

    Returns {passed, gates, summary}. `passed` is False if ANY gate fails.
    """
    GATES: dict[str, Any] = {
        "black_frame_ratio": gate_black_frame_ratio,
        "scene_count": gate_scene_count,
        "slideshow_motion": gate_slideshow_motion,
        "duration": gate_duration,
        "tone_contrast": gate_tone_contrast,
        "audio_present": gate_has_audio,
        "subtitles_present": gate_has_subtitles,
    }
    results = []
    for c in checks:
        fn = GATES.get(c.get("gate", ""))
        if fn is None:
            results.append(
                {
                    "name": c.get("gate", "?"),
                    "passed": False,
                    "value": None,
                    "limit": None,
                    "detail": f"unknown gate {c.get('gate')!r}",
                }
            )
            continue
        kwargs = {k: v for k, v in c.items() if k != "gate"}
        try:
            results.append(fn(**kwargs))
        except Exception as exc:  # noqa: BLE001 - a gate must never crash the run
            results.append(
                {
                    "name": c.get("gate", "?"),
                    "passed": False,
                    "value": None,
                    "limit": None,
                    "detail": f"gate raised: {exc}",
                }
            )
    passed = all(r["passed"] for r in results)
    failed = [r["name"] for r in results if not r["passed"]]
    summary = (
        "ALL GATES PASSED"
        if passed
        else f"FAILED GATES: {', '.join(failed)} — do not ship; send back to assets"
    )
    return {"passed": passed, "gates": results, "summary": summary}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser(description="Run OpenMontage video quality gates")
    parser.add_argument("--video", help="path to final video")
    parser.add_argument("--manifest-scenes", type=int, default=0, help="expected scene count")
    parser.add_argument("--clips", nargs="*", help="paths to scene clips")
    parser.add_argument("--target-duration", type=float, default=0, help="target duration in seconds")
    parser.add_argument("--subtitle", help="path to subtitle file (srt)")
    args = parser.parse_args()

    checks: list[dict[str, Any]] = []
    if args.video:
        checks += [
            {"gate": "black_frame_ratio", "video_path": args.video},
            {"gate": "slideshow_motion", "video_path": args.video},
            {"gate": "duration", "video_path": args.video, "target_seconds": args.target_duration},
            {"gate": "audio_present", "video_path": args.video},
        ]
        if args.target_duration <= 0:
            checks = [c for c in checks if c["gate"] != "duration"]
    if args.manifest_scenes > 0 or args.clips:
        checks.append(
            {
                "gate": "scene_count",
                "manifest_scenes": list(range(args.manifest_scenes)),
                "actual_clips": args.clips or [],
            }
        )
    if args.subtitle:
        checks.append({"gate": "subtitles_present", "subtitle_path": args.subtitle})

    result = run_all(checks)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["passed"] else 1)
