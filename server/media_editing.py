"""Shared FFmpeg helpers for the manual video editor."""

from __future__ import annotations

import json
import os
import subprocess
from fractions import Fraction
from pathlib import Path


def _ff(args: list[str], desc: str = "") -> subprocess.CompletedProcess:
    cmd = ["ffmpeg", "-y", "-loglevel", "error"] + args
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed ({desc}): {result.stderr.strip()}")
    return result


def ffprobe_info(path: str) -> dict:
    """Get video metadata: duration, resolution, codec."""
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=width,height,codec_name,r_frame_rate",
            "-of",
            "json",
            path,
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    info = json.loads(result.stdout)
    fmt = info.get("format", {})
    streams = info.get("streams", [])
    video_stream = next((s for s in streams if s.get("codec_type") == "video"), {})
    audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), {})

    return {
        "path": path,
        "duration": float(fmt.get("duration", 0)),
        "width": video_stream.get("width"),
        "height": video_stream.get("height"),
        "video_codec": video_stream.get("codec_name"),
        "has_audio": audio_stream is not None,
        "fps": float(Fraction(video_stream.get("r_frame_rate", "0/1"))) if video_stream.get("r_frame_rate") else None,
    }


def trim_segment(
    source: str,
    output: str,
    start: float,
    duration: float,
    fade_in: float = 0,
    fade_out: float = 0,
    target_width: int = 1080,
    target_height: int = 1920,
) -> dict:
    """Trim a video segment with optional fades and resize to target dimensions."""
    vf_parts = [
        f"scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,"
        f"pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2"
    ]
    af_parts = []

    if fade_in > 0:
        vf_parts.append(f"fade=t=in:st=0:d={fade_in}")
        af_parts.append(f"afade=t=in:st=0:d={fade_in}")
    if fade_out > 0:
        fs = max(0, duration - fade_out)
        vf_parts.append(f"fade=t=out:st={fs}:d={fade_out}")
        af_parts.append(f"afade=t=out:st={fs}:d={fade_out}")

    args = ["-ss", str(start), "-i", source, "-t", str(duration), "-vf", ",".join(vf_parts)]
    if af_parts:
        args += ["-af", ",".join(af_parts)]
    args += [
        "-c:v",
        "libx264",
        "-preset",
        "ultrafast",
        "-crf",
        "23",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        output,
    ]
    _ff(args, f"trim {source}")
    return {"output": output, "start": start, "duration": duration}


def concat_segments(segments: list[str], output: str) -> dict:
    """Concatenate video segments in order."""
    concat_file = output + ".concat.txt"
    with open(concat_file, "w") as handle:
        for segment in segments:
            handle.write(f"file '{Path(segment).resolve()}'\n")
    _ff(["-f", "concat", "-safe", "0", "-i", concat_file, "-c", "copy", output], "concat")
    os.remove(concat_file)
    return {"output": output, "count": len(segments)}


def add_overlay_text(
    input_video: str,
    output: str,
    text: str,
    position: str = "top",
    font_size: int = 48,
    text_color: str = "white",
    bg_color: str = "black@0.5",
) -> dict:
    """Add a text overlay banner using Pillow + ffmpeg."""
    from PIL import Image, ImageDraw, ImageFont

    font = None
    for font_path in [
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]:
        if os.path.exists(font_path):
            try:
                font = ImageFont.truetype(font_path, font_size)
                break
            except Exception:
                pass
    if font is None:
        font = ImageFont.load_default()

    def parse_color(color: str):
        if color == "white":
            return (255, 255, 255, 255)
        if color == "black":
            return (0, 0, 0, 255)
        if "@" in color:
            base, alpha = color.split("@")
            rgb = parse_color(base)
            return (rgb[0], rgb[1], rgb[2], int(float(alpha) * 255))
        return (255, 255, 255, 255)

    background = parse_color(bg_color)
    foreground = parse_color(text_color)
    info = ffprobe_info(input_video)
    width, height = info["width"] or 1080, info["height"] or 1920

    dummy = Image.new("RGBA", (1, 1))
    draw = ImageDraw.Draw(dummy)
    bounds = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = bounds[2] - bounds[0], bounds[3] - bounds[1]
    padding = 20
    banner_width = min(width, text_width + padding * 2 + 40)
    banner_height = text_height + padding * 2

    banner = Image.new("RGBA", (banner_width, banner_height), background)
    ImageDraw.Draw(banner).text(
        ((banner_width - text_width) // 2, padding),
        text,
        font=font,
        fill=foreground,
    )

    png_path = output + ".overlay.png"
    banner.save(png_path)
    y_map = {"top": 30, "bottom": height - banner_height - 30, "center": (height - banner_height) // 2}
    y = y_map.get(position, 30)

    _ff(
        [
            "-i",
            input_video,
            "-i",
            png_path,
            "-filter_complex",
            f"[0][1]overlay=(W-w)/2:{y}",
            "-c:v",
            "libx264",
            "-preset",
            "ultrafast",
            "-crf",
            "23",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            output,
        ],
        "overlay",
    )
    os.remove(png_path)
    return {"output": output, "text": text, "position": position}
