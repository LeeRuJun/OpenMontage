from pathlib import Path


def test_script_director_is_self_contained():
    skill = Path("skills/pipelines/historical-story/script-director.md").read_text()
    # The script writer holds exactly one skill; no cross-layer feeding.
    assert "story-writing-director" not in skill
    assert "REQUIRED SUB-SKILL" not in skill
    assert "scene contract" in skill
    assert "research voice" in skill


def test_story_design_director_is_self_contained():
    skill = Path("skills/pipelines/historical-story/story-design-director.md").read_text()
    assert "story-writing-director" not in skill
    assert "REQUIRED SUB-SKILL" not in skill
    assert "event_story" in skill
    assert "material_density_map" in skill
    assert "scene_contracts" in skill


def test_script_and_review_are_separate_skills():
    writer = Path("skills/pipelines/historical-story/script-director.md").read_text()
    reviewer = Path("skills/pipelines/historical-story/script-review-director.md").read_text()
    # Writer and reviewer never merge into one skill.
    assert "independent reviewer" in reviewer
    assert "script-review-director" in writer
    # Both sides enforce the same research-voice blacklist.
    for term in ("异文", "证据边界", "各有边界"):
        assert term in reviewer
