from lib.historical_story_gate import validate_prompt_diversity


def _shot(board_id, claim, location, state):
    return {
        "visual_board_id": board_id,
        "prompt_spec": {
            "visual_claim": claim,
            "subject_action": "人物在场景中采取改变局面的行动",
            "location_context": location,
            "evidence_layer": "路线和地点关系",
            "color_direction": "冷蓝环境光与暖色局部光源",
            "microbeat_visual_states": [{"id": f"{board_id}-m1", "description": state}],
        },
    }


def test_prompt_diversity_rejects_near_duplicate_board_contracts():
    errors = validate_prompt_diversity({"shots": [
        _shot("b01", "军队抵达城门", "北平城门", "城门和道路出现军队"),
        _shot("b02", "军队抵达城门", "北平城门", "城门和道路出现军队"),
    ]})
    assert errors
    assert "b01" in errors[0] and "b02" in errors[0]


def test_prompt_diversity_accepts_different_claim_location_and_state():
    errors = validate_prompt_diversity({"shots": [
        _shot("b01", "军队抵达城门", "北平城门", "城门和道路出现军队"),
        _shot("b02", "朝廷军在河岸溃退", "白沟河堤岸", "河水、堤岸和撤退路线改变战场方向"),
    ]})
    assert errors == []
