from pathlib import Path


def test_research_skill_owns_facts_relationships_and_event_inventory():
    skill = Path("skills/pipelines/historical-story/research-director.md").read_text()
    for phrase in ("event inventory", "relationship map", "knowledge state", "certainty", "does not write the final narration"):
        assert phrase in skill


def test_story_design_skill_owns_material_map_and_scene_contracts():
    skill = Path("skills/pipelines/historical-story/story-design-director.md").read_text()
    for phrase in ("material_density_map", "scene_contracts", "event inventory", "不写最终旁白"):
        assert phrase in skill


def test_script_skill_consumes_architecture_instead_of_redesigning_it():
    skill = Path("skills/pipelines/historical-story/script-director.md").read_text()
    for phrase in ("material_density_map", "scene contract", "不要临时改变故事结构", "provider_text"):
        assert phrase in skill
