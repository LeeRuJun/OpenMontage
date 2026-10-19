from pathlib import Path

from lib.pipeline_loader import (
    get_stage_order,
    get_stage_skill,
    load_pipeline,
    pipeline_supports_reference_input,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_book_comic_pipeline_classifies_before_research_and_assets_before_storyboard():
    manifest = load_pipeline("book-comic-explainer")
    order = get_stage_order(manifest)
    assert order.index("book_profile") < order.index("research")
    assert order.index("visual_asset_plan") < order.index("core_assets")
    assert order.index("core_assets") < order.index("storyboard")
    assert order.index("storyboard") < order.index("gap_assets")


def test_book_comic_pipeline_exposes_new_director_skills_and_reference_support():
    manifest = load_pipeline("book-comic-explainer")
    assert get_stage_skill(manifest, "book_profile") == "pipelines/book-comic-explainer/book-profile-director"
    assert get_stage_skill(manifest, "visual_asset_plan") == "pipelines/book-comic-explainer/visual-asset-plan-director"
    assert pipeline_supports_reference_input(manifest)


def test_character_and_scene_design_are_conditional_branches():
    manifest = load_pipeline("book-comic-explainer")
    order = get_stage_order(
        manifest,
        context={"requires_character_design": False, "requires_scene_design": False},
    )
    assert "character_design" not in order
    assert "scene_design" not in order

    enabled = get_stage_order(
        manifest,
        context={"requires_character_design": True, "requires_scene_design": True},
    )
    assert "character_design" in enabled
    assert "scene_design" in enabled
