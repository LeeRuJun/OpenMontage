"""Executable gates for the historical-story pipeline."""
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
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HistoricalStoryGateError(f"invalid JSON in {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise HistoricalStoryGateError(f"{label} must be a JSON object")
    return value

def validate_asset_contract(project_dir: Path, assets: dict[str, Any] | None = None) -> dict[str, Any]:
    """Validate core assets, shot plan, and unique final board coverage."""
    manifest = assets or _load_json(project_dir / "artifacts/asset_manifest.json", "asset_manifest")
    try:
        validate_artifact("asset_manifest", manifest)
    except Exception as exc:
        raise HistoricalStoryGateError(f"asset_manifest schema failure: {exc}") from exc
    core = manifest.get("core_assets") or {}
    characters, scenes, boards = core.get("characters") or [], core.get("scenes") or [], manifest.get("board_assets") or []
    if not characters: raise HistoricalStoryGateError("asset_manifest core_assets.characters is empty")
    if not scenes: raise HistoricalStoryGateError("asset_manifest core_assets.scenes is empty")
    if not 40 <= len(boards) <= 50:
        raise HistoricalStoryGateError(f"asset_manifest has {len(boards)} board assets; full_longform requires 40-50")
    ids, paths = [x.get("visual_board_id") for x in boards], [x.get("path") for x in boards]
    if any(not x for x in ids + paths): raise HistoricalStoryGateError("every board asset needs visual_board_id and path")
    if len(ids) != len(set(ids)): raise HistoricalStoryGateError("visual_board_id values must be unique")
    if len(paths) != len(set(paths)): raise HistoricalStoryGateError("final board primary images must be unique")
    for item in boards:
        bid = item["visual_board_id"]
        if item.get("unique_primary_image") is not True: raise HistoricalStoryGateError(f"{bid} is not marked unique_primary_image")
        if item.get("source_refs") is None: raise HistoricalStoryGateError(f"{bid} has no source_refs")
        if item.get("provenance") is None: raise HistoricalStoryGateError(f"{bid} has no provenance")
        if not (project_dir / item["path"]).is_file(): raise HistoricalStoryGateError(f"board asset missing on disk: {project_dir / item['path']}")
    shot_plan = _load_json(project_dir / "artifacts/shot_asset_plan.json", "shot_asset_plan")
    try: validate_artifact("shot_asset_plan", shot_plan)
    except Exception as exc: raise HistoricalStoryGateError(f"shot_asset_plan schema failure: {exc}") from exc
    planned = shot_plan.get("boards") or shot_plan.get("shots") or []
    if len(planned) != len(boards): raise HistoricalStoryGateError(f"shot_asset_plan has {len(planned)} entries but asset_manifest has {len(boards)}")
    return {"characters": len(characters), "scenes": len(scenes), "boards": len(boards)}

def enforce_historical_stage_gate(project_dir: Path, stage: str, artifacts: dict[str, Any]) -> None:
    """Fail closed at edit/compose/publish for historical-story runs."""
    if stage not in {"edit", "compose", "publish"}: return
    manifest = artifacts.get("asset_manifest")
    validate_asset_contract(project_dir, manifest if isinstance(manifest, dict) else None)
    if stage in {"compose", "publish"} and not (project_dir / "artifacts/edit_decisions.json").is_file() and "edit_decisions" not in artifacts:
        raise HistoricalStoryGateError("compose requires completed edit_decisions")
    if stage == "publish" and not (project_dir / "artifacts/render_report.json").is_file() and "render_report" not in artifacts:
        raise HistoricalStoryGateError("publish requires completed render_report")
