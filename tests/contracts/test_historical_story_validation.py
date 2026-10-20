from lib.historical_story_validation import (
    validate_asset_reuse,
    validate_claim_coverage,
    validate_scene_rhythm,
    validate_timing,
)


def test_pilot_timing_contract_accepts_two_minute_sample():
    assert validate_timing("pilot_2min", duration_seconds=120, character_count=520, act_count=3) == []


def test_full_timing_contract_rejects_short_sample():
    errors = validate_timing("full_longform", duration_seconds=120, character_count=520, act_count=3)
    assert len(errors) == 3


def test_scene_rhythm_requires_reason_for_long_hold():
    scenes = [{"id": "s1", "start_seconds": 0, "end_seconds": 10}]
    errors = validate_scene_rhythm("pilot_2min", scenes)
    assert any("micro_shot_count" in e for e in errors)
    scenes[0]["hold_reason"] = "emotional_hold"
    errors = validate_scene_rhythm("pilot_2min", scenes)
    assert any("micro_shot_count" in e for e in errors)


def test_claims_need_known_ledger_refs():
    script = {"sections": [{"id": "s1", "source_ref": "source", "claim_refs": ["c-missing"]}]}
    ledger = {"claims": [{"id": "c1"}]}
    errors = validate_claim_coverage(script, ledger)
    assert "unknown claims" in errors[0]


def test_generated_assets_need_reuse_or_exception():
    errors = validate_asset_reuse([{"id": "hero", "origin_type": "generated", "reused_by_scene_ids": ["s1"]}])
    assert errors
