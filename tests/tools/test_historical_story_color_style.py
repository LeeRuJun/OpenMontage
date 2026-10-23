import json
from pathlib import Path

from tools.historical_story_shot_plan import main


def test_shot_plan_preserves_authored_visual_style_and_board_color_direction(tmp_path: Path):
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    (artifacts / "scene_plan.json").write_text(
        json.dumps(
            {
                "metadata": {
                    "period_label": "北宋熙宁年间",
                    "visual_style": {
                        "name": "冷暖宫城纪实",
                        "prompt_guidance": "blue-green dusk, saturated vermilion banners, warm oil-lamp pools, natural textile colors",
                    },
                },
                "scenes": [
                    {
                        "id": "s01",
                        "description": "熙宁二年，汴京政事堂，新法争议在灯火与暮色交界处展开",
                        "type": "reconstruction",
                        "color_direction": "cyan stone shadows against amber lamp light",
                        "required_core_assets": ["scene_ref:kaifeng-court"],
                        "start_seconds": 0,
                        "end_seconds": 20,
                    }
                ],
            },
            ensure_ascii=False,
        )
    )

    main(tmp_path)

    output = json.loads((artifacts / "shot_asset_plan.json").read_text())
    assert output["metadata"]["visual_style"] == {
        "name": "冷暖宫城纪实",
        "prompt_guidance": "blue-green dusk, saturated vermilion banners, warm oil-lamp pools, natural textile colors",
    }
    prompt = output["shots"][0]["prompt"]
    assert "blue-green dusk" in prompt
    assert "cyan stone shadows against amber lamp light" in prompt
    assert "北宋熙宁年间" in prompt
    assert "暖米白、木褐、灰瓦、低饱和靛青与少量赭红统一画面" not in prompt


def test_historical_color_direction_skill_is_parameterized():
    skill = Path("skills/creative/historical-color-direction.md").read_text()
    assert "按时段、天气、光源与材质" in skill
    assert "不使用固定外部视频" in skill
    assert "前景" in skill and "中景" in skill and "远景" in skill
    assert "人物属于环境" in skill
    assert "物品不能成为正式图片主体" in skill


def test_shot_asset_plan_skill_requires_the_shared_color_direction():
    skill = Path("skills/pipelines/historical-story/shot-asset-plan-director.md").read_text()
    assert "skills/creative/historical-color-direction.md" in skill
    assert "visual_style" in skill
    assert "color_direction" in skill
