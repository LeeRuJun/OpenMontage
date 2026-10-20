"""Deterministic cross-artifact gates for the historical-story pipeline."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class StoryContract:
    mode: str
    min_duration: float
    max_duration: float
    min_chars: int
    max_chars: int
    min_acts: int
    max_acts: int
    min_shots: int
    max_shots: int


CONTRACTS = {
    "pilot_2min": StoryContract("pilot_2min", 90, 150, 400, 720, 3, 4, 14, 28),
    "full_longform": StoryContract("full_longform", 1320, 1500, 5500, 7200, 8, 10, 180, 240),
}

CHINESE_NARRATION_CPS = (4.0, 4.8)


def recommended_character_range(duration_seconds: float) -> tuple[int, int]:
    """Return the spoken-character range for a measured duration."""
    low, high = CHINESE_NARRATION_CPS
    return round(duration_seconds * low), round(duration_seconds * high)


def contract_for(mode: str) -> StoryContract:
    try:
        return CONTRACTS[mode]
    except KeyError as exc:
        raise ValueError(f"Unknown historical-story mode: {mode!r}") from exc


def validate_timing(mode: str, *, duration_seconds: float, character_count: int, act_count: int) -> list[str]:
    contract = contract_for(mode)
    errors: list[str] = []
    if not contract.min_duration <= duration_seconds <= contract.max_duration:
        errors.append(f"duration {duration_seconds} outside {contract.min_duration}-{contract.max_duration}s")
    if not contract.min_chars <= character_count <= contract.max_chars:
        errors.append(f"character_count {character_count} outside {contract.min_chars}-{contract.max_chars}")
    if duration_seconds > 0:
        cps = character_count / duration_seconds
        min_cps, max_cps = CHINESE_NARRATION_CPS
        if not min_cps <= cps <= max_cps:
            recommended = recommended_character_range(duration_seconds)
            errors.append(
                f"character_density {cps:.2f} chars/s outside {min_cps}-{max_cps}; "
                f"recommended range for {duration_seconds:.1f}s is {recommended[0]}-{recommended[1]} chars"
            )
    if not contract.min_acts <= act_count <= contract.max_acts:
        errors.append(f"act_count {act_count} outside {contract.min_acts}-{contract.max_acts}")
    return errors


def validate_scene_rhythm(mode: str, scenes: list[dict[str, Any]]) -> list[str]:
    contract = contract_for(mode)
    errors: list[str] = []
    if not contract.min_shots <= len(scenes) <= contract.max_shots:
        errors.append(f"micro_shot_count {len(scenes)} outside {contract.min_shots}-{contract.max_shots}")
    for scene in scenes:
        duration = float(scene["end_seconds"]) - float(scene["start_seconds"])
        hold_reason = scene.get("hold_reason")
        if duration < 4 or duration > 8:
            if not (8 <= duration <= 12 and hold_reason in {"emotional_hold", "diagram_hold"}):
                errors.append(f"scene {scene.get('id')} duration {duration:.2f}s violates rhythm contract")
    return errors


def validate_claim_coverage(script: dict[str, Any], ledger: dict[str, Any]) -> list[str]:
    claim_ids = {claim["id"] for claim in ledger.get("claims", [])}
    errors: list[str] = []
    for section in script.get("sections", []):
        refs = section.get("claim_refs", [])
        if section.get("source_ref") and not refs:
            errors.append(f"section {section.get('id')} has a factual source but no claim_refs")
        missing = [ref for ref in refs if ref not in claim_ids]
        if missing:
            errors.append(f"section {section.get('id')} references unknown claims: {missing}")
    return errors


def validate_asset_reuse(assets: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    for asset in assets:
        if asset.get("origin_type") == "generated":
            reused = asset.get("reused_by_scene_ids", [])
            if len(set(reused)) < 2 and not asset.get("hero_exception_approved", False):
                errors.append(f"generated asset {asset.get('id')} is not reused or approved as a hero exception")
    return errors


def validate_story(mode: str, *, timing: dict[str, Any], scenes: list[dict[str, Any]], script: dict[str, Any], ledger: dict[str, Any], assets: list[dict[str, Any]]) -> None:
    errors = []
    errors.extend(validate_timing(mode, duration_seconds=timing["measured_duration_seconds"], character_count=timing["character_count"], act_count=len(timing.get("acts", []))))
    errors.extend(validate_scene_rhythm(mode, scenes))
    errors.extend(validate_claim_coverage(script, ledger))
    errors.extend(validate_asset_reuse(assets))
    if errors:
        raise ValueError("historical-story validation failed: " + "; ".join(errors))
