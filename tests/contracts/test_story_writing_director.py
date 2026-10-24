from pathlib import Path


def test_generic_story_skill_defines_causal_scene_contracts():
    skill = Path("skills/creative/story-writing-director.md").read_text()
    for phrase in (
        "desire",
        "opposition",
        "scene contract",
        "starting state",
        "immediate objective",
        "resistance",
        "reversal",
        "consequence",
        "knowledge state",
        "planted",
    ):
        assert phrase in skill


def test_historical_story_design_routes_through_generic_story_skill():
    skill = Path("skills/pipelines/historical-story/story-design-director.md").read_text()
    assert "skills/creative/story-writing-director.md" in skill
    assert "event_story" in skill


def test_script_director_routes_through_generic_story_skill():
    skill = Path("skills/pipelines/historical-story/script-director.md").read_text()
    assert "skills/creative/story-writing-director.md" in skill
    assert "scene contract" in skill


def test_generic_story_skill_includes_natural_chinese_revision_rules():
    skill = Path("skills/creative/story-writing-director.md").read_text()
    assert "observable behavior" in skill
    assert "formulaic contrast" in skill
    assert "不要为了字数" in skill
    assert "revise in context" in skill


def test_story_skill_requires_research_before_material_map_and_prose():
    skill = Path("skills/creative/story-writing-director.md").read_text()
    assert "research material inventory" in skill
    assert "material density map" in skill
    assert "Do not draft prose before" in skill
    assert "event inventory" in skill
