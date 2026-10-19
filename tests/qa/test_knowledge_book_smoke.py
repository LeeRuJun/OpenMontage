import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "remotion-composer" / "public" / "editorial-fixture" / "props.json"


def test_editorial_fixture_covers_a_contiguous_16_9_timeline():
    props = json.loads(FIXTURE.read_text())
    cuts = sorted(props["cuts"], key=lambda cut: cut["in_seconds"])
    assert cuts
    assert {cut["type"] for cut in cuts} >= {
        "image_card",
        "map_scene",
        "diagram_scene",
        "timeline_scene",
        "data_reveal",
        "quote_card",
    }
    assert cuts[0]["in_seconds"] == 0
    for previous, current in zip(cuts, cuts[1:]):
        assert previous["out_seconds"] == current["in_seconds"]
    assert cuts[-1]["out_seconds"] == 24


def test_editorial_fixture_uses_no_paid_generation_provider():
    props = json.loads(FIXTURE.read_text())
    assert all("provider" not in cut for cut in props["cuts"])
