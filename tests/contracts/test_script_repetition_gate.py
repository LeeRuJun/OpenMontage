from lib.historical_story_validation import validate_script_repetition


def test_script_repetition_gate_rejects_repeated_explanation_paragraphs():
    script = {
        "sections": [
            {"id": "s1", "text": "湖州的州衙、驿路和御史台把案件连起来。\n湖州的州衙、驿路和御史台把案件推向京城。"},
            {"id": "s2", "text": "湖州的州衙、驿路和御史台成为案件路线。"},
        ]
    }
    errors = validate_script_repetition(script)
    assert errors
    assert "s1" in errors[0] or "s2" in errors[0]


def test_script_repetition_gate_allows_distinct_event_paragraphs():
    script = {
        "sections": [
            {"id": "s1", "text": "七月二十八日，苏轼在湖州被捕。"},
            {"id": "s2", "text": "八月十八日，苏轼被送入御史台狱。"},
        ]
    }
    assert validate_script_repetition(script) == []
