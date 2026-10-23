import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

import pytest

from scripts.pipeline_gate import GateError, read_artifact


def test_gate_rejects_full_longform_narration_below_duration_contract(tmp_path):
    project = tmp_path / "project"
    artifacts = project / "artifacts"
    artifacts.mkdir(parents=True)
    script_text = "script text"
    (artifacts / "script.md").write_text(script_text)
    timing = {
        "version": "1.0",
        "mode": "full_longform",
        "script_revision": hashlib.sha256(script_text.encode()).hexdigest()[:16],
        "narration_asset_id": "narration-full-minimax",
        "narration_path": "assets/audio/narration_full.mp3",
        "measured_duration_seconds": 1200,
        "character_count": 5800,
        "word_timestamps": [],
        "sections": [{"id": "s1", "start_seconds": 0, "end_seconds": 1200}],
        "acts": [{"id": "s1", "title": "section", "start_seconds": 0, "end_seconds": 1200}],
        "alignment_confidence": 0.9,
        "timing_locked_at": datetime.now(timezone.utc).isoformat(),
    }
    (artifacts / "narration_timing.json").write_text(json.dumps(timing))

    with pytest.raises(GateError, match="duration"):
        read_artifact(project, "narration_timing")


def test_status_marks_stale_produced_narration_as_invalid(tmp_path):
    from scripts.pipeline_gate import statuses

    project = tmp_path / "project"
    artifacts = project / "artifacts"
    artifacts.mkdir(parents=True)
    script = {
        "version": "1.0",
        "title": "测试",
        "total_duration_seconds": 1200,
        "opening": {
            "brand_name": "读点东西",
            "column_name": "历史故事",
            "hook": "问题",
            "promise": "承诺",
            "roadmap": ["一", "二"],
            "target_duration_seconds": {"min": 20, "max": 30},
        },
        "sections": [{"id": "s1", "text": "各位观众好，这里是读点东西。", "start_seconds": 0, "end_seconds": 10}],
    }
    script_path = artifacts / "script.json"
    script_path.write_text(json.dumps(script, ensure_ascii=False))
    script_text = "current script"
    (artifacts / "script.md").write_text(script_text)
    timing = {
        "version": "1.0",
        "mode": "full_longform",
        "script_revision": "stale-revision",
        "narration_asset_id": "narration",
        "narration_path": "assets/audio/narration_full.mp3",
        "measured_duration_seconds": 1355,
        "character_count": 6000,
        "word_timestamps": [],
        "sections": [{"id": "s1", "start_seconds": 0, "end_seconds": 1355}],
        "acts": [{"id": "s1", "title": "section", "start_seconds": 0, "end_seconds": 1355}],
        "alignment_confidence": 0.9,
        "timing_locked_at": datetime.now(timezone.utc).isoformat(),
    }
    (artifacts / "narration_timing.json").write_text(json.dumps(timing))

    item = next(item for item in statuses(Path("."), project, "historical-story") if item["name"] == "narration_timing")
    assert item["status"] == "blocked_invalid_input"
