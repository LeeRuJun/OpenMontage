from lib.historical_story_validation import validate_script_prose


def test_script_prose_gate_rejects_production_instructions_in_story_body():
    script = {
        "sections": [
            {"id": "s1", "text": "镜头沿着城墙推进，画面出现第三个微分镜。"},
        ]
    }
    errors = validate_script_prose(script)
    assert errors
    assert "s1" in errors[0]


def test_script_prose_gate_allows_fixed_welcome_and_post_story_commentary():
    script = {
        "sections": [
            {"id": "prologue", "text": "各位观众好，这里是读点东西。"},
            {"id": "commentary-1", "text": "故事结局之后，我们回头点评这个选择造成的后果。"},
        ]
    }
    assert validate_script_prose(script) == []


def test_checkpoint_validation_rejects_script_meta_language():
    from lib.checkpoint import CheckpointValidationError, _validate_artifacts_for_stage

    script = {
        "version": "1.0",
        "title": "测试",
        "total_duration_seconds": 120,
        "opening": {"brand_name": "读点东西", "column_name": "历史故事", "hook": "问题", "promise": "承诺", "roadmap": ["一", "二"], "target_duration_seconds": {"min": 20, "max": 30}},
        "sections": [{"id": "s1", "text": "镜头沿着城墙推进。", "start_seconds": 0, "end_seconds": 10}],
    }
    try:
        _validate_artifacts_for_stage("script", "completed", {"script": script})
    except CheckpointValidationError as exc:
        assert "prose" in str(exc)
    else:
        raise AssertionError("checkpoint validation accepted production meta-language")


def test_commentary_contract_requires_post_story_duration():
    from lib.historical_story_validation import validate_commentary_contract

    script = {
        "metadata": {"commentary_start_section_id": "commentary-1"},
        "sections": [
            {"id": "story", "text": "故事事件。" * 500},
            {"id": "commentary-1", "text": "点评。" * 250},
        ],
    }
    assert validate_commentary_contract(script) == []


def test_commentary_contract_rejects_short_or_interleaved_commentary():
    from lib.historical_story_validation import validate_commentary_contract

    script = {
        "metadata": {"commentary_start_section_id": "commentary-1"},
        "sections": [
            {"id": "story", "text": "故事事件。" * 500},
            {"id": "commentary-1", "text": "点评。" * 100},
            {"id": "story-after", "text": "后续故事。" * 100},
        ],
    }
    errors = validate_commentary_contract(script)
    assert errors
    assert any("commentary" in error for error in errors)
