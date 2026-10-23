from pathlib import Path


def test_script_director_requires_event_first_narration():
    skill = Path("skills/pipelines/historical-story/script-director.md").read_text()
    assert "时间、地点、人物、行动、后果" in skill
    assert "每个段落先写事件" in skill
    assert "分析不能替代事件" in skill
    assert "不要对观众解释" in skill
    assert "每个事件之后再写后果" in skill
