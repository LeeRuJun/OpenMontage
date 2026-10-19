"""
SMB Livestream Rough Cut — core pipeline (no FastAPI dependency).

Scans the mounted SMB source dirs (源视频 + SRT), builds a timestamped
transcript, runs LLM clip selection, cuts clips with ffmpeg (stream copy),
uploads them to the SMB 广告素材库, and writes asset rows directly into the
fs-houyi `livestream_material_asset` table.

This is a faithful port of fs-houyi's SMB rough-cut pipeline, adapted to run
inside OpenMontage with mounted read-only source shares (/mnt/nas-fandenglive,
/mnt/nas-audio) and the configured 广告素材库 write share.

Path rule (critical): source inputs live under the *Data* share root
(樊老师直播素材文件, audio/live) — NOT under 广告素材库. So reads go through the
mounts; only uploads go through server.smb_browser (relative to 广告素材库).
"""

from __future__ import annotations

import json
import logging
import os
import re
import shutil
import subprocess
import time
import uuid
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Optional

from server.config import (
    smb_host, smb_share, smb_path, smb_user, smb_pass,
)
from server import llm_gateway

logger = logging.getLogger("openmontage.smb_rough_cut")

# ── module paths ──────────────────────────────────────────────────────────────

_OPENMONTAGE_ROOT = Path(__file__).resolve().parent.parent
SKILL_PATH = _OPENMONTAGE_ROOT / "skills" / "creative" / "livestream-clipper.md"
PROJECTS_DIR = _OPENMONTAGE_ROOT / "projects" / "rough-cuts"

# Mounted source roots (server-side, read-only). Overridable via env for dev.
SOURCE_VIDEO_ROOT = Path(os.environ.get("SMB_SOURCE_VIDEO_ROOT", "/mnt/nas-fandenglive"))
SOURCE_AUDIO_ROOT = Path(os.environ.get("SMB_SOURCE_AUDIO_ROOT", "/mnt/nas-audio"))
SMB_LIVE_DIR = "live"

# Output write root (relative to smb_browser's 广告素材库 base).
OUTPUT_SMB_BASE = "直播素材"

# ── SRT parsing (ported from fs-houyi smb_livestream_service) ─────────────────

_SRT_TS_RE = re.compile(
    r"^(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})[,.](\d{3})$"
)


def _ts_to_sec(hours: str, mins: str, secs: str) -> float:
    return int(hours) * 3600 + int(mins) * 60 + int(secs)


def parse_srt_to_transcript(srt_path: str | Path) -> tuple[str, float]:
    """Parse an SRT file into a timestamped transcript.

    Returns (transcript, duration_sec): one line per subtitle as
    "HH:MM:SS.mmm  text". Duration = end timestamp of the last subtitle.
    """
    content = Path(srt_path).read_text(encoding="utf-8", errors="replace")
    lines: list[str] = []
    duration = 0.0

    for block in content.strip().split("\n\n"):
        block = block.strip()
        if not block:
            continue
        parts = block.split("\n")
        if len(parts) < 3:
            continue

        ts_match = _SRT_TS_RE.match(parts[1].strip())
        if not ts_match:
            continue

        start_sec = _ts_to_sec(ts_match.group(1), ts_match.group(2), ts_match.group(3))
        end_sec = _ts_to_sec(ts_match.group(5), ts_match.group(6), ts_match.group(7))
        text = " ".join(parts[2:]).strip()
        if not text:
            continue

        hours = int(start_sec) // 3600
        minutes = (int(start_sec) % 3600) // 60
        seconds = int(start_sec) % 60
        millis = int((start_sec - int(start_sec)) * 1000)

        timestamp = f"{hours:02d}:{minutes:02d}:{seconds:02d}.{millis:03d}"
        lines.append(f"{timestamp}  {text}")

        if end_sec > duration:
            duration = end_sec

    return "\n".join(lines), duration


# ── timestamp / clip helpers (ported from fs-houyi livestream_rough_cut_service) ─

TIME_RE = re.compile(r"^(?:(\d+):)?(\d{1,2}):(\d{2})$")
_SEARCH_TS_RE = re.compile(r"(?:^|\s)(\d{2}):(\d{2}):(\d{2})(?:\s|$|\.)")


class RoughCutNoCandidatesError(RuntimeError):
    """Raised when the LLM returns no usable rough-cut candidates."""


def parse_timestamp(value: str) -> float:
    match = TIME_RE.match(str(value).strip())
    if not match:
        raise ValueError(f"invalid timestamp: {value}")
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2))
    seconds = int(match.group(3))
    if minutes >= 60 or seconds >= 60:
        raise ValueError(f"invalid timestamp: {value}")
    return hours * 3600 + minutes * 60 + seconds


def _find_ts_sec(text: str) -> float | None:
    match = _SEARCH_TS_RE.search(text)
    if not match:
        return None
    return int(match.group(1)) * 3600 + int(match.group(2)) * 60 + int(match.group(3))


def _slice_transcript(raw: str, start_sec: float, end_sec: float) -> str:
    lines: list[str] = []
    for line in raw.splitlines():
        line = line.rstrip("\r")
        if not line:
            continue
        sec = _find_ts_sec(line)
        if sec is None:
            if lines and start_sec <= end_sec:
                lines.append(line)
            continue
        if start_sec <= sec <= end_sec:
            lines.append(line)
    return "\n".join(lines)


def _json_from_llm(raw: str | None) -> list[dict[str, Any]]:
    if not raw:
        return []
    text = raw.strip()
    if text.startswith("```"):
        parts = text.split("\n", 1)
        if len(parts) != 2:
            raise ValueError("LLM result contains an incomplete Markdown fence")
        text = parts[1].rsplit("```", 1)[0].strip()
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"LLM result is not valid JSON: {exc.msg}") from exc
    if isinstance(parsed, dict):
        parsed = parsed.get("clips") or parsed.get("candidates") or []
    if not isinstance(parsed, list):
        raise ValueError("LLM result must be a JSON array")
    return [item for item in parsed if isinstance(item, dict)]


def select_candidates(transcript: str) -> list[dict[str, Any]]:
    if not SKILL_PATH.exists():
        raise RuntimeError(f"livestream-clipper skill not found: {SKILL_PATH}")
    skill = SKILL_PATH.read_text(encoding="utf-8")
    raw = llm_gateway._chat(skill, transcript, max_tokens=4096)
    if raw is None:
        raise RuntimeError("LLM gateway call failed (timeout or empty response)")
    return _json_from_llm(raw)


def normalize_candidates(candidates: list[dict[str, Any]], video_duration: float) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for candidate in candidates:
        try:
            start = parse_timestamp(candidate["start"])
            end = parse_timestamp(candidate["end"])
            theme = str(candidate.get("theme") or "").strip()
            if not theme or end <= start or start < 0 or end > video_duration or end - start < 20 or end - start > 300:
                continue
            normalized.append({**candidate, "start_sec": start, "end_sec": end, "duration_sec": end - start, "theme": theme})
        except (KeyError, TypeError, ValueError):
            logger.warning("Ignoring malformed rough-cut candidate: %r", candidate)
    normalized.sort(key=lambda item: (item["start_sec"], -item["duration_sec"]))
    result: list[dict[str, Any]] = []
    for candidate in normalized:
        if any(candidate["start_sec"] < other["end_sec"] and candidate["end_sec"] > other["start_sec"] for other in result):
            continue
        result.append(candidate)
    return result


def video_duration(path: str | Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        check=True, capture_output=True, text=True,
    )
    return float(result.stdout.strip())


def cut_candidate(source_path: str, output_path: str, start: float, duration: float) -> None:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", str(start),
         "-i", source_path, "-t", str(duration),
         "-map", "0:v:0", "-map", "0:a:0?", "-c", "copy",
         "-avoid_negative_ts", "make_zero", output_path],
        check=True,
    )


def uploaded_video_relative_path(live_date: date, file_name: str) -> str:
    """2026-01-08_01.mp4 → 直播素材/2026-01/08_01.mp4"""
    path = Path(file_name)
    name = path.stem.replace(live_date.isoformat(), live_date.strftime("%d")) + path.suffix
    return f"{OUTPUT_SMB_BASE}/{live_date:%Y-%m}/{name}"


# ── source discovery (mounted dirs + fs-houyi video index) ────────────────────

_VIDEO_YEAR_DIRS = ("{year}年周四直播素材", "{year}年居家直播素材")

# fs-houyi's hand-maintained date→video index (relative to the video root).
# Higher priority than filename scanning. Checked in OpenMontage's own config/
# first (synced from fs-houyi back/app/config/), then the fs-houyi repo copy.
_OPENMONTAGE_ROOT = Path(__file__).resolve().parent.parent
_VIDEO_INDEX_CANDIDATES = [
    _OPENMONTAGE_ROOT / "config" / "smb_livestream_video_index.json",
    Path(__file__).resolve().parents[2] / "back" / "app" / "config" / "smb_livestream_video_index.json",
]


def _load_video_index() -> dict:
    for p in _VIDEO_INDEX_CANDIDATES:
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                logger.warning("Failed to load video index: %s", p, exc_info=True)
    return {}


def _indexed_source_for_date(target_date: date) -> tuple[Optional[Path], Optional[str]]:
    """Resolve the video path from the fs-houyi index, if present.

    Returns (local_path_under_video_root, remote_video_path) or (None, None).
    video_path in the index is relative to the 樊老师直播素材文件 root; asr_path
    (if any) is relative to the Data share root and validated separately.
    """
    index = _load_video_index()
    root = str(index.get("root") or "").strip("/\\")
    entry = (index.get("index") or {}).get(target_date.isoformat())
    if not entry:
        return None, None
    video_path = ""
    asr_path = ""
    if isinstance(entry, str):
        video_path = entry
    elif isinstance(entry, dict):
        video_path = str(entry.get("video_path") or entry.get("path") or "")
        asr_path = str(entry.get("asr_path") or "")
    video_path = video_path.strip("/\\")
    if not video_path:
        return None, None

    # Build the full remote path (root/video_path) and map onto the mount.
    remote = f"{root}/{video_path}" if root else video_path
    # Prefer mounted path: SOURCE_VIDEO_ROOT maps to the 樊老师直播素材文件 share root.
    mounted = SOURCE_VIDEO_ROOT / video_path
    if mounted.is_file():
        return mounted, remote
    return None, None


def _date_tokens(d: date) -> list[str]:
    """Filename tokens for a date, most specific first."""
    return [
        d.isoformat(),                              # 2026-01-08
        d.strftime("%Y%m%d"),                       # 20260108
        f"{d.month:02d}月{d.day:02d}日",            # 01月08日
        f"{d.month}月{d.day}日",                    # 1月8日
    ]


def find_source_video(target_date: date) -> tuple[Optional[Path], Optional[str]]:
    """Find a source video for the date.

    Priority: fs-houyi video index → filename scan of mounted dirs.
    Returns (local_path, source_video_name).
    """
    # 1. index
    indexed, remote_path = _indexed_source_for_date(target_date)
    if indexed:
        logger.info("Source video for %s from index: %s", target_date, remote_path)
        return indexed, indexed.name

    # 2. filename scan
    if not SOURCE_VIDEO_ROOT.is_dir():
        logger.warning("Source video root not mounted: %s", SOURCE_VIDEO_ROOT)
        return None, None

    tokens = _date_tokens(target_date)
    candidates: list[tuple[int, Path]] = []

    for year_dir in _VIDEO_YEAR_DIRS:
        sub = SOURCE_VIDEO_ROOT / year_dir.format(year=target_date.year)
        if not sub.is_dir():
            continue
        for f in sub.iterdir():
            if not f.is_file() or f.suffix.lower() not in (".mp4", ".mov", ".mkv"):
                continue
            if any(tok in f.name for tok in tokens):
                candidates.append((f.stat().st_size, f))

    if not candidates:
        logger.info("No source video matched for %s under %s", target_date, SOURCE_VIDEO_ROOT)
        return None, None

    candidates.sort(key=lambda item: item[0], reverse=True)
    big = [c for c in candidates if c[0] >= 50 * 1024 * 1024]
    picked = (big or candidates)[0][1]
    logger.info("Source video for %s: %s (%d bytes)", target_date, picked, picked.stat().st_size)
    return picked, picked.name


def _indexed_asr_for_date(target_date: date) -> Optional[Path]:
    """Resolve the ASR/SRT path from the fs-houyi index, if present.

    asr_path is relative to the Data share root (e.g. audio/live/2024-01-04_01.srt),
    mapped onto the mounted audio root.
    """
    index = _load_video_index()
    entry = (index.get("index") or {}).get(target_date.isoformat())
    if not isinstance(entry, dict):
        return None
    asr_path = str(entry.get("asr_path") or "").strip("/\\")
    if not asr_path:
        return None
    # asr_path like "audio/live/2026-01-08_01.srt" → SOURCE_AUDIO_ROOT is the Data root mount.
    mounted = SOURCE_AUDIO_ROOT / asr_path
    if mounted.is_file():
        return mounted
    return None


def find_srt_paths(target_date: date) -> list[Path]:
    """Find all SRT files for the date.

    Priority: fs-houyi index asr_path → scan of mounted audio/live dir.
    """
    # 1. index
    indexed = _indexed_asr_for_date(target_date)
    if indexed:
        return [indexed]

    # 2. scan
    live_dir = SOURCE_AUDIO_ROOT / SMB_LIVE_DIR
    if not live_dir.is_dir():
        logger.warning("Audio live dir not mounted: %s", live_dir)
        return []
    prefix = f"{target_date.isoformat()}_"
    srt_files: list[tuple[int, Path]] = []
    for f in live_dir.iterdir():
        if f.suffix.lower() != ".srt" or not f.name.startswith(prefix):
            continue
        rest = f.name[len(prefix):]
        m = re.match(r"(\d+)\.", rest)
        if not m:
            continue
        srt_files.append((int(m.group(1)), f))
    srt_files.sort()
    return [p for _, p in srt_files]


def build_transcript(srt_paths: list[Path]) -> tuple[str, float]:
    """Parse each SRT and merge into one timestamped transcript."""
    transcripts: list[str] = []
    duration = 0.0
    for srt in srt_paths:
        text, dur = parse_srt_to_transcript(srt)
        if text:
            transcripts.append(text)
        if dur > duration:
            duration = dur
    return "\n\n".join(transcripts), duration


# ── rough cut run ─────────────────────────────────────────────────────────────

def run_rough_cut(
    live_date: date,
    source_video_path: str,
    source_video_name: str,
    transcript: str,
    output_root: str,
) -> list[dict[str, Any]]:
    """LLM select candidates → ffmpeg cut each → write .txt transcripts.

    Mirrors fs-houyi run_rough_cut; returns asset rows (without DB fields).
    """
    raw_candidates = select_candidates(transcript)
    duration = video_duration(source_video_path)
    candidates = normalize_candidates(raw_candidates, duration)
    logger.info(
        "Rough-cut candidate selection: date=%s source=%s raw=%d normalized=%d duration=%.2f",
        live_date, source_video_name, len(raw_candidates), len(candidates), duration,
    )
    if not candidates:
        raise RoughCutNoCandidatesError(
            f"LLM 未返回可用切片候选（原始候选 {len(raw_candidates)} 个，过滤后 0 个，视频时长 {duration:.0f} 秒）"
        )

    output_dir = Path(output_root)
    output: list[dict[str, Any]] = []
    for index, candidate in enumerate(candidates, 1):
        file_name = f"{live_date.isoformat()}_{index:02d}.mp4"
        file_path = output_dir / file_name
        cut_candidate(source_video_path, str(file_path), candidate["start_sec"], candidate["duration_sec"])
        clip_transcript = _slice_transcript(transcript, candidate["start_sec"], candidate["end_sec"])
        text_path = file_path.with_suffix(".txt")
        text_tmp = text_path.with_suffix(text_path.suffix + ".tmp")
        text_tmp.write_text(clip_transcript, encoding="utf-8")
        os.replace(text_tmp, text_path)
        output.append({
            "live_date": live_date,
            "source_video_name": source_video_name,
            "source_video_path": str(source_video_path),
            "file_name": file_name,
            "file_path": str(file_path),
            "theme": candidate["theme"],
            "transcript": clip_transcript,
            "search_text": " ".join(str(value or "") for value in (candidate.get("theme"), candidate.get("category"), candidate.get("reason"), clip_transcript)),
            "category": candidate.get("category"),
            "score": candidate.get("score"),
            "reason": candidate.get("reason"),
            "duration_sec": candidate["duration_sec"],
            "file_size": file_path.stat().st_size,
            "status": "ready",
        })
    return output


def upload_assets(live_date: date, assets: list[dict[str, Any]]) -> tuple[int, list[dict[str, Any]]]:
    """Upload each local clip to SMB 广告素材库/直播素材/{Y-m}/{day}.mp4.

    Returns (uploaded_count, uploaded_asset_rows). Failed uploads are left in
    place (local dir retained for retry) and omitted from the returned rows.
    """
    from server.smb_browser import upload_local_file

    uploaded_rows: list[dict[str, Any]] = []
    uploaded = 0
    for asset in assets:
        local_path = asset["file_path"]
        remote_path = uploaded_video_relative_path(live_date, asset["file_name"])
        ok = upload_local_file(local_path, remote_path)
        if not ok:
            logger.warning("SMB upload failed, keeping local: %s -> %s", local_path, remote_path)
            continue
        uploaded += 1
        uploaded_rows.append({
            **asset,
            "status": "uploaded",
            "smb_path": remote_path,
        })
    return uploaded, uploaded_rows


# ── in-memory task state (mirrors ai_clipper._tasks) ──────────────────────────

_tasks: dict[str, dict[str, Any]] = {}
_active_dates: dict[str, str] = {}  # date iso → task_id (idempotency guard)


def get_task(task_id: str) -> Optional[dict[str, Any]]:
    return _tasks.get(task_id)


def _new_task(task_id: str, day: date) -> dict[str, Any]:
    task = {
        "id": task_id,
        "date": day.isoformat(),
        "status": "queued",
        "progress": 0,
        "message": "任务已入队",
        "error": None,
        "assets": [],
        "created_at": time.time(),
        "started_at": None,
        "finished_at": None,
    }
    _tasks[task_id] = task
    return task


def _update_task(task_id: str, **kw: Any) -> None:
    if task_id in _tasks:
        _tasks[task_id].update(kw)


# ── main pipeline ─────────────────────────────────────────────────────────────

def run_rough_cut_for_date(day: date) -> dict[str, Any]:
    """Full pipeline for one date. Returns the final task state dict.

    Steps: find video → find SRTs → build transcript → LLM select → cut →
    upload → write DB. Any failure is captured into the task state (status
    failed/skipped) rather than raised.
    """
    task_id = _active_dates.get(day.isoformat())
    if not task_id:
        task_id = f"rc_{day.isoformat()}_{uuid.uuid4().hex[:8]}"
        _active_dates[day.isoformat()] = task_id
    task = _tasks.get(task_id) or _new_task(task_id, day)
    task.update(status="running", started_at=time.time(), progress=5,
                message="正在扫描素材源…", error=None)
    try:
        # 1. source video
        task.update(progress=10, message="定位源视频…")
        video_path, video_name = find_source_video(day)
        if not video_path:
            task.update(status="skipped", progress=100, finished_at=time.time(),
                        message="未匹配到该日期的源视频")
            return task

        # 2. SRT → transcript
        task.update(progress=20, message="解析 SRT 字幕…")
        srt_paths = find_srt_paths(day)
        if not srt_paths:
            task.update(status="skipped", progress=100, finished_at=time.time(),
                        message="audio/live 中无该日期 SRT 字幕")
            return task
        transcript, _duration = build_transcript(srt_paths)
        if not transcript.strip():
            task.update(status="failed", progress=100, finished_at=time.time(),
                        message="SRT 内容为空", error="SRT 内容为空")
            return task

        # 3. LLM select + cut
        task.update(progress=35, message="LLM 选点 + 切片中…")
        date_dir = PROJECTS_DIR / day.isoformat()
        output_root = str(date_dir / "rough")
        rows = run_rough_cut(day, str(video_path), video_name, transcript, output_root)
        if not rows:
            task.update(status="failed", progress=100, finished_at=time.time(),
                        message="LLM 未生成任何切片", error="LLM 未生成任何切片")
            return task

        # 4. upload
        task.update(progress=80, message=f"上传 {len(rows)} 个切片到广告素材库…")
        uploaded, uploaded_rows = upload_assets(day, rows)
        if not uploaded_rows:
            task.update(status="failed", progress=100, finished_at=time.time(),
                        message="切片上传失败", error="切片上传失败（保留本地）")
            return task

        # 5. persist to fs-houyi DB
        task.update(progress=92, message="写入资产记录…")
        try:
            persist_assets(day, uploaded_rows)
        except Exception as exc:
            logger.exception("DB persist failed for %s", day)
            task.update(status="failed", progress=100, finished_at=time.time(),
                        message=f"资产记录写入失败: {exc}", error=str(exc))
            return task

        # 6. cleanup local workdir
        if date_dir.exists():
            shutil.rmtree(str(date_dir), ignore_errors=True)

        task.update(status="done", progress=100, finished_at=time.time(),
                    message=f"完成：生成 {len(uploaded_rows)} 个切片，上传 {uploaded} 个",
                    assets=uploaded_rows)
        return task

    except RoughCutNoCandidatesError as exc:
        logger.warning("Rough cut no candidates for %s: %s", day, exc)
        task.update(status="failed", progress=100, finished_at=time.time(),
                    message=str(exc), error=str(exc))
        return task
    except Exception as exc:
        logger.exception("Rough cut pipeline failed for %s", day)
        task.update(status="failed", progress=100, finished_at=time.time(),
                    message=f"粗剪失败: {exc}", error=str(exc))
        return task


# ── fs-houyi DB persistence ───────────────────────────────────────────────────

DB_ENABLED = os.environ.get("OPENMONTAGE_DB_ENABLED", "1") in ("1", "true", "yes")


def _db_url() -> str:
    """Build fs-houyi MySQL URL from env, falling back to config-ini if present."""
    url = os.environ.get("FS_HOUYI_DB_URL")
    if url:
        return url
    from urllib.parse import quote_plus
    host = os.environ.get("FS_HOUYI_DB_HOST", "rm-bp16xk8stl0473obz.mysql.rds.aliyuncs.com")
    port = os.environ.get("FS_HOUYI_DB_PORT", "3306")
    user = os.environ.get("FS_HOUYI_DB_USER", "fddsh_p_13_YHX3lw")
    pw = os.environ.get("FS_HOUYI_DB_PASSWORD", "")
    name = os.environ.get("FS_HOUYI_DB_NAME", "fs-houyi_prod")
    return f"mysql+pymysql://{quote_plus(user)}:{quote_plus(pw)}@{host}:{port}/{name}?charset=utf8mb4"


def _db_engine():
    from sqlalchemy import create_engine
    return create_engine(_db_url(), pool_pre_ping=True, pool_recycle=300)


def persist_assets(day: date, rows: list[dict[str, Any]]) -> int:
    """Insert asset rows into fs-houyi livestream_material_asset table."""
    if not DB_ENABLED:
        logger.info("DB persistence disabled (OPENMONTAGE_DB_ENABLED=0); skipped %d rows", len(rows))
        return 0
    from sqlalchemy import text
    engine = _db_engine()
    inserted = 0
    with engine.begin() as conn:
        for row in rows:
            conn.execute(
                text(
                    """INSERT INTO livestream_material_asset
                       (live_date, source, source_video_name, source_video_path,
                        file_name, file_path, theme, transcript, search_text,
                        category, score, reason, duration_sec, file_size,
                        status, flagged, is_deleted, created_at, updated_at)
                       VALUES
                       (:live_date, :source, :source_video_name, :source_video_path,
                        :file_name, :file_path, :theme, :transcript, :search_text,
                        :category, :score, :reason, :duration_sec, :file_size,
                        :status, 0, 0, NOW(), NOW())"""
                ),
                {
                    "live_date": day,
                    "source": "smb",
                    "source_video_name": row.get("source_video_name") or "",
                    "source_video_path": row.get("source_video_path") or "",
                    "file_name": row.get("file_name") or "",
                    "file_path": row.get("file_path") or "",
                    "theme": row.get("theme") or "",
                    "transcript": row.get("transcript") or "",
                    "search_text": row.get("search_text") or "",
                    "category": row.get("category"),
                    "score": row.get("score"),
                    "reason": row.get("reason"),
                    "duration_sec": row.get("duration_sec"),
                    "file_size": row.get("file_size"),
                    "status": "uploaded",
                },
            )
            inserted += 1
    logger.info("Persisted %d asset rows for %s", inserted, day)
    return inserted
