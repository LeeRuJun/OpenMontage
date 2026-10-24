from pathlib import Path


def test_integrated_story_skill_owns_research_architecture_and_prose():
    skill = Path("skills/creative/story-writing-director.md").read_text()
    for phrase in (
        "research material inventory",
        "material density map",
        "approved story architecture",
        "Do not redesign the plot while drafting prose",
        "scene contract",
        "provider_text",
    ):
        assert phrase in skill


def test_historical_story_design_routes_to_the_integrated_skill():
    skill = Path("skills/pipelines/historical-story/story-design-director.md").read_text()
    assert "skills/creative/story-writing-director.md" in skill
    assert "material_density_map" in skill
