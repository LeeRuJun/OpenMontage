"""Compile one timeline cut per authored final visual board."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def main(project: Path) -> None:
    project = Path(project).resolve()
    scene_plan = json.loads((project / "artifacts/scene_plan.json").read_text())
    manifest = json.loads((project / "artifacts/asset_manifest.json").read_text())
    boards = {asset["scene_id"]: asset for asset in manifest["assets"] if asset.get("subtype") == "final_board"}
    grouped: dict[str, list[dict[str, Any]]] = {}
    order: list[str] = []
    for scene in scene_plan.get("scenes", []):
        board_id = str(scene.get("visual_board_id") or scene["id"])
        if board_id not in grouped:
            grouped[board_id] = []
            order.append(board_id)
        grouped[board_id].append(scene)

    cuts = []
    for board_id in order:
        beats = grouped[board_id]
        if board_id not in boards:
            raise SystemExit(f"missing approved final board: {board_id}")
        start = min(float(beat["start_seconds"]) for beat in beats)
        end = max(float(beat["end_seconds"]) for beat in beats)
        motions = [str(beat.get("movement", "static")) for beat in beats]
        cuts.append({
            "id": f"cut-{board_id}",
            "source": boards[board_id]["id"],
            "in_seconds": round(start, 3),
            "out_seconds": round(end, 3),
            "layer": "primary",
            "transform": {"scale": 1.0, "position": "center", "animation": "board-microbeat-camera"},
            "transition_in": "dissolve",
            "transition_out": "dissolve",
            "transition_duration": 0.35,
            "reason": f"{beats[0].get('visual_claim', beats[0].get('shot_intent', 'claim-specific historical visual'))}; microbeats: {', '.join(motions)}",
        })

    edit = {
        "version": "1.0",
        "cuts": cuts,
        "audio": {
            "narration": {"src": "assets/audio/narration_full.mp3", "volume": 1.0},
            "music": {"asset_id": "leberch-history-documentary", "volume": 0.1, "ducking": {"enabled": True, "threshold_db": -18, "reduction_db": -10, "attack_ms": 200, "release_ms": 600}},
        },
        "subtitles": {"enabled": True, "style": "sentence", "source": "assets/audio/narration.zh-CN.srt", "font": "serif", "font_size": 34, "color": "#f0dfc5", "outline_color": "#17151a", "background": "#17151a99", "position": "bottom-center", "max_words_per_line": 18},
        "renderer_family": "documentary-montage",
        "render_runtime": "hyperframes",
        "composition_mode": "atelier",
        "metadata": {"pipeline": "historical-story", "unique_board_count": len(cuts), "microbeats_compiled_into_boards": True},
    }
    output = project / "artifacts/edit_decisions.json"
    output.write_text(json.dumps(edit, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"cuts": len(cuts), "runtime": "hyperframes", "composition_mode": "atelier"}, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", required=True)
    args = parser.parse_args()
    main(Path(args.project_dir))
