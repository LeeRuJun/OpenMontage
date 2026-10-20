import json
from pathlib import Path

from lib.pipeline_loader import get_stage_order, load_pipeline_readonly
from schemas.artifacts import ARTIFACT_NAMES, load_schema


def test_historical_story_manifest_has_vertical_story_stages():
    manifest = load_pipeline_readonly("historical-story")
    assert get_stage_order(manifest) == [
        "intake", "research", "story_design", "cover_plan", "proposal", "script",
        "narration_timing", "storyboard_blueprint", "character_bible", "scene_bible",
        "core_assets", "shot_asset_plan", "shot_assets", "edit", "compose", "publish",
    ]
    assert {mode["name"] for mode in manifest["production_modes"]} == {"pilot_2min", "full_longform"}
    full_mode = next(mode for mode in manifest["production_modes"] if mode["name"] == "full_longform")
    assert full_mode["visual_plan"] == {
        "final_visual_boards": {"min": 40, "max": 50, "recommended": 48},
        "boards_per_act": {"min": 5, "max": 7, "recommended": 6},
        "board_duration_seconds": {"min": 20, "max": 36, "preferred_max": 30},
        "microbeats_per_board": {"min": 3, "max": 5, "recommended": 4},
        "microbeat_duration_seconds": {"min": 4, "max": 8},
    }
    assert all(stage.get("human_approval_default") for stage in manifest["stages"] if stage["name"] != "compose")


def test_historical_artifact_schemas_are_registered():
    for name in ("historical_evidence_ledger", "historical_character_bible", "historical_scene_bible", "narration_timing", "story_spine", "cover_plan", "shot_asset_plan"):
        assert name in ARTIFACT_NAMES
        assert load_schema(name)["$id"].endswith(name)


def test_historical_schemas_are_valid_json():
    root = Path(__file__).parents[2] / "schemas" / "artifacts"
    for name in ("historical_evidence_ledger", "historical_character_bible", "historical_scene_bible", "narration_timing", "story_spine", "cover_plan", "shot_asset_plan"):
        data = json.loads((root / f"{name}.schema.json").read_text())
        assert data["$id"].endswith(name)


def test_script_schema_requires_opening_contract():
    schema = load_schema("script")
    assert "opening" in schema["required"]
    opening = schema["properties"]["opening"]
    assert opening["required"] == ["hook", "promise", "roadmap", "target_duration_seconds"]
    assert opening["properties"]["roadmap"]["maxItems"] == 3
