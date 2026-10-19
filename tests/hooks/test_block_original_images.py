from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / ".claude/hooks/block-original-images.py"
PREVIEW = ROOT / ".claude/hooks/image_preview.py"


def run_hook(tool_input: dict, *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    payload = json.dumps({"tool_name": "Read", "tool_input": tool_input})
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=payload,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )


def denial(result: subprocess.CompletedProcess[str]) -> dict:
    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout.strip()
    return json.loads(result.stdout)


def test_non_image_and_missing_paths_are_ignored(tmp_path: Path) -> None:
    text_file = tmp_path / "notes.txt"
    text_file.write_text("notes")

    for path in (text_file, tmp_path / "missing.png"):
        result = run_hook({"file_path": str(path)})
        assert result.returncode == 0
        assert result.stdout == ""


def test_large_original_is_denied(tmp_path: Path) -> None:
    source = tmp_path / "reference.png"
    Image.new("RGB", (1200, 800), "white").save(source)

    result = run_hook({"file_path": str(source)})
    body = denial(result)
    output = body["hookSpecificOutput"]
    assert output["permissionDecision"] == "deny"
    assert "1200x800" in output["permissionDecisionReason"]
    assert "image_preview.py" in output["permissionDecisionReason"]


def test_small_unnamed_image_is_still_denied(tmp_path: Path) -> None:
    source = tmp_path / "reference.png"
    Image.new("RGB", (320, 240), "white").save(source)

    body = denial(run_hook({"path": str(source)}))
    assert body["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_named_small_preview_is_allowed(tmp_path: Path) -> None:
    preview = tmp_path / "reference-preview.jpg"
    Image.new("RGB", (768, 512), "white").save(preview)

    result = run_hook({"file_path": str(preview)})
    assert result.returncode == 0
    assert result.stdout == ""


def test_corrupt_image_is_denied(tmp_path: Path) -> None:
    corrupt = tmp_path / "broken-preview.png"
    corrupt.write_bytes(b"not an image")

    body = denial(run_hook({"file_path": str(corrupt)}))
    reason = body["hookSpecificOutput"]["permissionDecisionReason"]
    assert "Pillow could not verify" in reason


def test_pillow_preview_is_cached_and_does_not_modify_source(tmp_path: Path) -> None:
    source = tmp_path / "source.png"
    cache = tmp_path / "cache"
    Image.new("RGBA", (1200, 800), (255, 0, 0, 128)).save(source)
    source_before = source.read_bytes()

    first = subprocess.run(
        [sys.executable, str(PREVIEW), str(source), "--output-dir", str(cache)],
        text=True,
        capture_output=True,
        check=True,
    )
    second = subprocess.run(
        [sys.executable, str(PREVIEW), str(source), "--output-dir", str(cache)],
        text=True,
        capture_output=True,
        check=True,
    )

    assert first.stdout.strip() == second.stdout.strip()
    output = Path(first.stdout.strip())
    assert output.is_file()
    assert output != source
    assert source.read_bytes() == source_before
    with Image.open(output) as image:
        assert image.format == "JPEG"
        assert image.mode == "RGB"
        assert max(image.size) <= 768
