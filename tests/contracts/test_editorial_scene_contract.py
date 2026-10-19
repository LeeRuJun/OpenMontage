import pytest

from schemas.artifacts import validate_artifact
from tests.contracts.test_knowledge_book_artifacts import (
    valid_asset_plan,
    valid_book_profile,
    valid_delivery_strategy,
)


def editorial_asset_manifest():
    return {
        "version": "1.0",
        "assets": [
            {
                "id": "asset-tax-flow",
                "type": "diagram",
                "path": "assets/editorial/tax-flow.svg",
                "source_tool": "editorial_svg",
                "scene_id": "section-03",
                "visual_role": "explain_mechanism",
                "book_sections": ["section-03", "section-06"],
                "generation_mode": "code",
                "reusable": True,
                "status": "approved",
            }
        ],
    }


def test_book_profile_strategy_asset_plan_and_manifest_form_a_valid_chain():
    validate_artifact("book_profile", valid_book_profile())
    validate_artifact("delivery_strategy", valid_delivery_strategy())
    validate_artifact("visual_asset_plan", valid_asset_plan())
    validate_artifact("asset_manifest", editorial_asset_manifest())


def test_asset_manifest_rejects_unknown_lifecycle_status():
    manifest = editorial_asset_manifest()
    manifest["assets"][0]["status"] = "published"
    with pytest.raises(Exception):
        validate_artifact("asset_manifest", manifest)


def test_reusable_asset_records_all_sections_that_use_it():
    asset = editorial_asset_manifest()["assets"][0]
    assert asset["reusable"] is True
    assert asset["book_sections"] == ["section-03", "section-06"]
