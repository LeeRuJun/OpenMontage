from pathlib import Path


def test_script_director_requires_event_first_narration():
    skill = Path("skills/pipelines/historical-story/script-director.md").read_text()
    assert "built from events" in skill
    assert "event card with time, place, actors, action, resistance, consequence" in skill
    assert "One sentence, one job" in skill
    assert "Say it once" in skill


def test_script_director_separates_story_from_post_story_commentary():
    skill = Path("skills/pipelines/historical-story/script-director.md").read_text()
    assert "故事主体" in skill
    assert "独立点评" in skill
    assert "故事结局之后" in skill
    assert "不能穿插" in skill


def test_script_director_blocks_length_padding_and_route_recap():
    skill = Path("skills/pipelines/historical-story/script-director.md").read_text()
    assert "不能用路线复述填字数" in skill
    assert "一段只推进一个事件" in skill
    assert "字数不足只能补新证据事件" in skill
    assert "点评不能回放故事" in skill
    assert "审稿指令" in skill


def test_script_director_requires_research_and_material_map_before_drafting():
    skill = Path("skills/pipelines/historical-story/script-director.md").read_text()
    assert "research_brief" in skill
    assert "material_density_map" in skill
    assert "不要在素材地图完成前写正文" in skill
