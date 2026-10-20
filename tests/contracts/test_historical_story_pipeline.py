import json
from pathlib import Path

from lib.pipeline_loader import get_stage_order, load_pipeline_readonly
from schemas.artifacts import ARTIFACT_NAMES, load_schema


def test_historical_story_manifest_has_vertical_story_stages():
    manifest = load_pipeline_readonly("historical-story")
    assert get_stage_order(manifest) == [
        "intake", "research", "story_design", "proposal", "script",
        "narration_timing", "storyboard_blueprint", "character_bible", "scene_bible",
        "core_assets", "shot_assets", "edit", "compose", "publish",
    ]
    assert {mode["name"] for mode in manifest["production_modes"]} == {"pilot_2min", "full_longform"}
    assert all(stage.get("human_approval_default") for stage in manifest["stages"] if stage["name"] != "compose")


def test_historical_artifact_schemas_are_registered():
    for name in ("historical_evidence_ledger", "historical_character_bible", "historical_scene_bible", "narration_timing", "story_spine"):
        assert name in ARTIFACT_NAMES
        assert load_schema(name)["$id"].endswith(name)


def test_historical_schemas_are_valid_json():
    root = Path(__file__).parents[2] / "schemas" / "artifacts"
    for name in ("historical_evidence_ledger", "historical_character_bible", "historical_scene_bible", "narration_timing", "story_spine"):
        data = json.loads((root / f"{name}.schema.json").read_text())
        assert data["$id"].endswith(name)
