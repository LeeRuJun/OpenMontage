from pathlib import Path


def test_script_review_skill_has_independent_ai_review_rubric():
    skill = Path("skills/pipelines/historical-story/script-review-director.md").read_text()
    for phrase in (
        "independent reviewer",
        "causal chain",
        "repeated explanation",
        "character agency",
        "evidence boundary",
        "post-story commentary",
        "READY",
        "BLOCKED",
    ):
        assert phrase in skill
