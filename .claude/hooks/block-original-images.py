#!/usr/bin/env python3
"""Block direct Read calls for original raster images.

Only explicitly named, low-resolution derivatives are allowed through Read. This
keeps large reference images out of the model context instead of relying on a
prompt-only instruction.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # pragma: no cover - exercised through the subprocess test
    Image = None  # type: ignore[assignment]

RASTER_EXTENSIONS = {
    ".avif",
    ".bmp",
    ".gif",
    ".jpeg",
    ".jpg",
    ".png",
    ".tif",
    ".tiff",
    ".webp",
}
PREVIEW_MARKERS = (
    "contact",
    "crop",
    "overview",
    "preview",
    "thumb",
    "thumbnail",
)
MAX_PREVIEW_EDGE = 768


def emit_denial(path: Path, reason: str) -> None:
    payload = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }
    print(json.dumps(payload, ensure_ascii=False))


def image_dimensions(path: Path) -> tuple[int, int] | None:
    """Read image metadata with Pillow without emitting image bytes."""
    if Image is None:
        return None
    try:
        with Image.open(path) as image:
            return image.size
    except (OSError, ValueError):
        return None


def is_named_preview(path: Path) -> bool:
    stem = path.stem.lower()
    return any(marker in stem for marker in PREVIEW_MARKERS)


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        # A malformed hook event should not make unrelated Read calls unusable.
        return 0

    tool_input = event.get("tool_input") or {}
    raw_path = tool_input.get("file_path") or tool_input.get("path")
    if not isinstance(raw_path, str):
        return 0

    path = Path(os.path.expanduser(raw_path))
    if not path.is_absolute():
        path = Path.cwd() / path
    path = path.resolve()

    if path.suffix.lower() not in RASTER_EXTENSIONS:
        return 0

    # Let Read produce its normal missing-file error. There is no image to send.
    if not path.exists() or not path.is_file():
        return 0

    dimensions = image_dimensions(path)
    if dimensions is None:
        emit_denial(
            path,
            "Blocked direct raster-image Read: Pillow could not verify this image. "
            "Create a low-resolution JPEG preview first (longest edge <= 768px) "
            "with a filename containing preview, overview, contact, or crop.",
        )
        return 0

    width, height = dimensions
    longest_edge = max(width, height)
    if longest_edge > MAX_PREVIEW_EDGE or not is_named_preview(path):
        emit_denial(
            path,
            f"Blocked direct original-image Read for {path.name} ({width}x{height}). "
            "Read only a derived image with longest edge <= 768px and a filename "
            "containing preview, overview, contact, or crop. Keep the original on disk. "
            "Generate one with the project Pillow helper: "
            "python3 .claude/hooks/image_preview.py original.png.",
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
