"""Historical-story asset generation driven entirely by project-authored plans."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from tools.graphics.image_batch import ImageBatchRunner


def _load(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _run_requests(requests: list[dict[str, Any]]) -> dict[str, Any]:
    result = ImageBatchRunner().run(requests, max_workers=3, max_retries=2)
    failed = [item for item in result.get("results", []) if item.get("status") == "failed"]
    if failed:
        raise SystemExit(f"image generation failed: {failed}")
    return result


def _asset_record(item: dict[str, Any], path: Path, *, prompt: str, group_id: str, treatment: str) -> dict[str, Any]:
    return {
        "id": str(item["id"]),
        "type": item.get("type", "image"),
        "path": str(path),
        "source_tool": "image_selector",
        "scene_id": str(item.get("scene_id") or f"core-{item['id']}"),
        "prompt": prompt,
        "model": "gpt-image-2",
        "provider": "openai",
        "generation_mode": "image",
        "status": "approved",
        "origin_type": "generated",
        "historical_treatment": treatment,
        "asset_group_id": group_id,
        "reused_by_scene_ids": item.get("reused_by_scene_ids", []),
        "rights_note": "project_generated",
    }


def core(project: Path) -> None:
    load_dotenv("/Users/fanshu01/rep/github/OpenMontage/.env")
    plan = _load(project / "artifacts/core_asset_plan.json")
    items = plan.get("assets") or []
    if not items:
        raise SystemExit("core_asset_plan has no assets")

    requests = []
    missing_items = []
    for item in items:
        output_path = project / str(item["path"])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if output_path.is_file() and output_path.stat().st_size > 0:
            continue
        missing_items.append(item)
        requests.append({
            "prompt": str(item["prompt"]),
            "preferred_provider": "openai",
            "allowed_providers": ["openai"],
            "model": "gpt-image-2",
            "size": "1280x720",
            "quality": "medium",
            "output_format": "png",
            "n": 1,
            "output_path": str(output_path),
            "task_context": {"pipeline": "historical-story", "stage": "core_assets", "asset_group_id": item["asset_group_id"]},
        })
    result = _run_requests(requests) if requests else {"totals": {"cost": 0}}
    assets = []
    for item in items:
        path = project / str(item["path"])
        if not path.is_file():
            raise SystemExit(f"core asset missing after generation: {path}")
        assets.append(_asset_record(item, path.relative_to(project), prompt=str(item["prompt"]), group_id=str(item["asset_group_id"]), treatment=str(item.get("historical_treatment", "dramatic_reconstruction"))))
    manifest = {
        "version": "1.0",
        "assets": assets,
        "total_cost_usd": result.get("totals", {}).get("cost", 0),
        "metadata": {"pipeline": "historical-story", "stage": "core_assets", "provider_policy": "openai:gpt-image-2", "core_asset_plan": "artifacts/core_asset_plan.json"},
    }
    (project / "artifacts/asset_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"core_assets": len(assets), "cost": result.get("totals", {}).get("cost", 0)}, ensure_ascii=False))


def shot_assets(project: Path, only: set[str] | None = None, sample: bool = False) -> None:
    load_dotenv("/Users/fanshu01/rep/github/OpenMontage/.env")
    manifest_path = project / "artifacts/asset_manifest.json"
    plan = _load(project / "artifacts/shot_asset_plan.json")
    manifest = _load(manifest_path)
    refs_by_id = {str(item.get("id")): project / str(item["path"]) for item in manifest.get("assets", [])}
    selected = [shot for shot in plan.get("shots", []) if only is None or (shot.get("visual_board_id") or shot["shot_id"]).lower() in only]
    if not selected:
        raise SystemExit("no shot boards selected")
    out_dir = project / ("assets/images/boards/sample" if sample else "assets/images/boards")
    out_dir.mkdir(parents=True, exist_ok=True)
    requests = []
    for shot in selected:
        board_id = str(shot.get("visual_board_id") or shot["shot_id"])
        output_path = out_dir / f"{board_id.lower()}.png"
        sample_path = project / "assets/images/boards/sample" / f"{board_id.lower()}.png"
        if not output_path.is_file() and sample_path.is_file() and not sample:
            output_path.write_bytes(sample_path.read_bytes())
        if output_path.is_file() and output_path.stat().st_size > 0:
            continue
        ref_ids = [str(value) for value in shot.get("required_core_assets", [])]
        if not ref_ids:
            raise SystemExit(f"{board_id} has no required_core_assets")
        missing = [ref_id for ref_id in ref_ids if ref_id not in refs_by_id]
        if missing:
            raise SystemExit(f"{board_id} references unknown core assets: {missing}")
        prompt = str(shot.get("prompt") or "")
        if not prompt:
            raise SystemExit(f"{board_id} has no compiled prompt")
        requests.append({
            "prompt": prompt,
            "generation_mode": "edit",
            "image_paths": [str(refs_by_id[ref_id]) for ref_id in ref_ids],
            "preferred_provider": "openai",
            "allowed_providers": ["openai"],
            "model": "gpt-image-2",
            "size": "1280x720",
            "quality": "medium",
            "output_format": "png",
            "n": 1,
            "output_path": str(output_path),
            "task_context": {"pipeline": "historical-story", "stage": "shot_assets", "visual_board_id": board_id},
        })
    result = _run_requests(requests) if requests else {"totals": {"cost": 0}}
    if sample:
        sample_manifest = {"version": "1.0", "stage": "shot_assets_sample", "boards": [{"id": str(shot.get("visual_board_id") or shot["shot_id"]), "path": str((out_dir / f"{(shot.get('visual_board_id') or shot['shot_id']).lower()}.png").relative_to(project)), "provider": "openai", "model": "gpt-image-2"} for shot in selected]}
        (project / "artifacts/shot_asset_sample_manifest.json").write_text(json.dumps(sample_manifest, ensure_ascii=False, indent=2) + "\n")
        print(json.dumps({"shot_assets_sample": len(selected), "cost": result.get("totals", {}).get("cost", 0)}, ensure_ascii=False))
        return
    core_assets = [item for item in manifest.get("assets", []) if item.get("subtype") != "final_board"]
    for shot in plan.get("shots", []):
        board_id = str(shot.get("visual_board_id") or shot["shot_id"])
        path = out_dir / f"{board_id.lower()}.png"
        if not path.is_file():
            raise SystemExit(f"final board missing after generation: {path}")
        core_assets.append({
            "id": board_id, "type": "image", "path": str(path.relative_to(project)), "source_tool": "image_selector", "scene_id": board_id,
            "model": "gpt-image-2", "provider": "openai", "prompt": shot["prompt"], "generation_mode": "image", "status": "approved", "origin_type": "generated",
            "historical_treatment": "dramatic_reconstruction", "asset_group_id": "final_board", "subtype": "final_board", "reused_by_scene_ids": [board_id], "rights_note": "project_generated",
        })
    manifest["assets"] = core_assets
    manifest["total_cost_usd"] = round(float(manifest.get("total_cost_usd", 0)) + float(result.get("totals", {}).get("cost", 0)), 6)
    manifest.setdefault("metadata", {}).update({"stage": "shot_assets", "unique_final_boards": len(plan.get("shots", []))})
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"shot_assets": len(plan.get("shots", [])), "cost": result.get("totals", {}).get("cost", 0)}, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=["core_assets", "shot_assets"])
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--boards", default="")
    parser.add_argument("--sample", action="store_true")
    args = parser.parse_args()
    selected = {value.strip().lower() for value in args.boards.split(",") if value.strip()} or None
    if args.stage == "core_assets":
        core(Path(args.project_dir).resolve())
    else:
        shot_assets(Path(args.project_dir).resolve(), only=selected, sample=args.sample)
