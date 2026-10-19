#!/usr/bin/env python3
"""Create cached, low-resolution image previews for vision inspection."""

from __future__ import annotations

import argparse
import hashlib
import os
import tempfile
from pathlib import Path

from PIL import Image, ImageOps

DEFAULT_MAX_EDGE = 768
DEFAULT_QUALITY = 68
CACHE_VERSION = "preview-v1"


def default_cache_dir() -> Path:
    """Return a session-local cache when available, otherwise a user cache."""
    job_dir = os.environ.get("CLAUDE_JOB_DIR")
    if job_dir:
        return Path(job_dir) / "tmp" / "image-previews"
    return Path.home() / ".cache" / "openmontage" / "image-previews"


def _cache_key(source: Path, max_edge: int, quality: int) -> str:
    stat = source.stat()
    payload = "|".join(
        (
            CACHE_VERSION,
            str(source),
            str(stat.st_size),
            str(stat.st_mtime_ns),
            str(max_edge),
            str(quality),
        )
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]


def create_preview(
    source: str | Path,
    *,
    cache_dir: str | Path | None = None,
    max_edge: int = DEFAULT_MAX_EDGE,
    quality: int = DEFAULT_QUALITY,
) -> Path:
    """Create or reuse an RGB JPEG preview and return its path.

    The source is never modified. The cache key includes source metadata and
    rendering parameters, so edits to the source produce a new preview.
    """
    source_path = Path(source).expanduser().resolve()
    if not source_path.is_file():
        raise FileNotFoundError(source_path)
    if max_edge < 1:
        raise ValueError("max_edge must be positive")
    if not 1 <= quality <= 95:
        raise ValueError("quality must be between 1 and 95")

    target_dir = Path(cache_dir).expanduser() if cache_dir else default_cache_dir()
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{_cache_key(source_path, max_edge, quality)}-preview.jpg"
    if target.is_file() and target.stat().st_size > 0:
        return target

    # Image.open reads metadata lazily; the resize/save operation below is the
    # only point at which pixels are decoded, and they never enter Claude's log.
    with Image.open(source_path) as image:
        image = ImageOps.exif_transpose(image)
        image.thumbnail((max_edge, max_edge), Image.Resampling.LANCZOS)
        if image.mode in ("RGBA", "LA") or "transparency" in image.info:
            background = Image.new("RGB", image.size, "white")
            alpha = image.convert("RGBA")
            background.paste(alpha, mask=alpha.getchannel("A"))
            image = background
        else:
            image = image.convert("RGB")

        fd, temporary_name = tempfile.mkstemp(
            prefix=f".{target.name}.", suffix=".tmp", dir=target_dir
        )
        os.close(fd)
        temporary = Path(temporary_name)
        try:
            image.save(temporary, format="JPEG", quality=quality, optimize=True)
            os.replace(temporary, target)
        finally:
            temporary.unlink(missing_ok=True)

    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--max-edge", type=int, default=DEFAULT_MAX_EDGE)
    parser.add_argument("--quality", type=int, default=DEFAULT_QUALITY)
    args = parser.parse_args()
    print(
        create_preview(
            args.source,
            cache_dir=args.output_dir,
            max_edge=args.max_edge,
            quality=args.quality,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
