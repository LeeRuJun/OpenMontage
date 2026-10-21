"""Executable stage gates for the historical-story pipeline."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from schemas.artifacts import validate_artifact

class HistoricalStoryGateError(ValueError):
    """A historical-story stage cannot advance."""

def _load_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise HistoricalStoryGateError(f"missing {label}: {path}")
    try: value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc: raise HistoricalStoryGateError(f"invalid JSON in {label}: {exc}") from exc
    if not isinstance(value, dict): raise HistoricalStoryGateError(f"{label} must be a JSON object")
    return value

def _manifest(project_dir: Path, assets: dict[str, Any] | None) -> dict[str, Any]:
    value = assets if isinstance(assets, dict) else _load_json(project_dir / "artifacts/asset_manifest.json", "asset_manifest")
    try: validate_artifact("asset_manifest", value)
    except Exception as exc: raise HistoricalStoryGateError(f"asset_manifest schema failure: {exc}") from exc
    return value

def validate_core_assets(project_dir: Path, assets: dict[str, Any] | None = None) -> dict[str, int]:
    manifest = _manifest(project_dir, assets)
    items = manifest.get("assets") or []
    characters = [x for x in items if x.get("asset_group_id") == "character_reference"]
    scenes = [x for x in items if x.get("asset_group_id") in {"scene_plate", "map", "diagram"}]
    if not characters: raise HistoricalStoryGateError("core_assets has no character_reference assets")
    if not scenes: raise HistoricalStoryGateError("core_assets has no scene_plate/map/diagram assets")
    for item in characters + scenes:
        if not item.get("path") or not (project_dir / item["path"]).is_file(): raise HistoricalStoryGateError(f"core asset missing on disk: {item.get('path')}")
        if not item.get("provider") or not item.get("model") or not item.get("historical_treatment"): raise HistoricalStoryGateError(f"core asset lacks provider/model/historical_treatment: {item.get('id')}")
    return {"characters": len(characters), "scenes": len(scenes)}

def validate_shot_plan(project_dir: Path) -> int:
    shot_plan = _load_json(project_dir / "artifacts/shot_asset_plan.json", "shot_asset_plan")
    try: validate_artifact("shot_asset_plan", shot_plan)
    except Exception as exc: raise HistoricalStoryGateError(f"shot_asset_plan schema failure: {exc}") from exc
    shots = shot_plan.get("shots") or []
    if shot_plan.get("mode") != "full_longform": raise HistoricalStoryGateError("shot_asset_plan mode must be full_longform")
    if not 40 <= len(shots) <= 50: raise HistoricalStoryGateError(f"shot_asset_plan has {len(shots)} shots; full_longform requires 40-50")
    ids = [x.get("visual_board_id") or x.get("shot_id") for x in shots]
    if any(not x for x in ids) or len(ids) != len(set(ids)): raise HistoricalStoryGateError("shot_asset_plan board IDs must be unique")
    for shot in shots:
        if not shot.get("required_core_assets"): raise HistoricalStoryGateError(f"{shot.get('shot_id')} has no required_core_assets")
        if not shot.get("prompt_spec"): raise HistoricalStoryGateError(f"{shot.get('shot_id')} has no prompt_spec")
    return len(shots)

def validate_final_boards(project_dir: Path, assets: dict[str, Any] | None = None) -> dict[str, int]:
    counts = validate_core_assets(project_dir, assets)
    planned = validate_shot_plan(project_dir)
    boards = [x for x in _manifest(project_dir, assets).get("assets", []) if x.get("subtype") == "final_board"]
    if len(boards) != planned: raise HistoricalStoryGateError(f"asset_manifest has {len(boards)} final boards but shot_asset_plan has {planned}")
    ids, paths = [x.get("scene_id") for x in boards], [x.get("path") for x in boards]
    if any(not x for x in ids + paths) or len(ids) != len(set(ids)): raise HistoricalStoryGateError("final board scene_id values must be unique")
    if len(paths) != len(set(paths)): raise HistoricalStoryGateError("final board primary images must be unique")
    for item in boards:
        bid = item["scene_id"]
        if item.get("status") != "approved": raise HistoricalStoryGateError(f"{bid} is not approved")
        if item.get("provider") != "openai" or item.get("model") != "gpt-image-2": raise HistoricalStoryGateError(f"{bid} violates fixed OpenAI gpt-image-2 policy")
        if not item.get("prompt") or not item.get("historical_treatment"): raise HistoricalStoryGateError(f"{bid} lacks prompt or historical_treatment")
        if not (project_dir / item["path"]).is_file(): raise HistoricalStoryGateError(f"board asset missing on disk: {project_dir / item['path']}")
    return {**counts, "boards": len(boards)}

def enforce_historical_stage_gate(project_dir: Path, stage: str, artifacts: dict[str, Any]) -> None:
    """Fail closed at each historical-story asset/edit/compose boundary."""
    manifest = artifacts.get("asset_manifest") if isinstance(artifacts.get("asset_manifest"), dict) else None
    if stage == "core_assets": validate_core_assets(project_dir, manifest)
    elif stage == "shot_asset_plan": validate_core_assets(project_dir, manifest); validate_shot_plan(project_dir)
    elif stage in {"shot_assets", "edit", "compose", "publish"}: validate_final_boards(project_dir, manifest)
    else: return
    if stage in {"compose", "publish"} and not (project_dir / "artifacts/edit_decisions.json").is_file() and "edit_decisions" not in artifacts: raise HistoricalStoryGateError("compose requires completed edit_decisions")
    if stage == "publish" and not (project_dir / "artifacts/render_report.json").is_file() and "render_report" not in artifacts: raise HistoricalStoryGateError("publish requires completed render_report")
