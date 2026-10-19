import pytest

from schemas.artifacts import validate_artifact


def valid_book_profile():
    return {
        "version": "1.0",
        "primary_type": "history",
        "secondary_types": ["politics", "economics"],
        "narrative_mode": "explanatory",
        "visual_grammar": "historical_diagram",
        "confidence": 0.91,
        "evidence": ["The book explains institutional change through fiscal systems."],
    }


def valid_delivery_strategy():
    return {
        "version": "1.0",
        "core_promise": "Explain the book's central mechanism.",
        "audience_problem": "The audience knows the conclusion but not the mechanism.",
        "narrative_mode": "reframing_explainer",
        "hook": "The familiar explanation is incomplete.",
        "question_left_with_viewer": "What mechanism actually caused the change?",
        "progression": ["challenge the common view", "show evidence", "reframe the conclusion"],
        "explanation_style": {
            "abstraction_level": "popular",
            "summary_ratio": 0.2,
            "interpretation_ratio": 0.5,
            "example_ratio": 0.3,
        },
        "pacing": {
            "hook_seconds": 30,
            "concept_change_every_seconds": 45,
            "visual_change_every_seconds": 8,
        },
        "ending": {"type": "reframe", "takeaway": "The system matters."},
    }


def valid_asset_plan():
    return {
        "version": "1.0",
        "visual_grammar": "historical_diagram",
        "canvas": {"width": 1920, "height": 1080, "aspect_ratio": "16:9"},
        "assets": [
            {
                "id": "asset-map",
                "type": "map",
                "role": "Establish spatial relationships",
                "used_by": ["section-2"],
                "generation_mode": "svg",
                "status": "planned",
                "reusable": True,
            }
        ],
    }


def test_knowledge_book_artifacts_validate():
    validate_artifact("book_profile", valid_book_profile())
    validate_artifact("delivery_strategy", valid_delivery_strategy())
    validate_artifact("visual_asset_plan", valid_asset_plan())


def test_book_profile_rejects_unknown_primary_type():
    profile = valid_book_profile()
    profile["primary_type"] = "made_up_type"
    with pytest.raises(Exception):
        validate_artifact("book_profile", profile)


def test_delivery_strategy_rejects_ratios_that_do_not_sum_to_one():
    strategy = valid_delivery_strategy()
    strategy["explanation_style"]["example_ratio"] = 0.4
    with pytest.raises(Exception):
        validate_artifact("delivery_strategy", strategy)


def test_asset_plan_rejects_asset_without_identity():
    plan = valid_asset_plan()
    del plan["assets"][0]["id"]
    with pytest.raises(Exception):
        validate_artifact("visual_asset_plan", plan)


def test_asset_plan_rejects_non_landscape_canvas():
    plan = valid_asset_plan()
    plan["canvas"] = {"width": 1080, "height": 1920, "aspect_ratio": "9:16"}
    with pytest.raises(Exception):
        validate_artifact("visual_asset_plan", plan)
