"""Deterministic cross-artifact gates for the historical-story pipeline."""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any


@dataclass(frozen=True)
class VisualBoardContract:
    min_boards: int
    max_boards: int
    recommended_boards: int
    min_boards_per_act: int
    max_boards_per_act: int
    recommended_boards_per_act: int
    min_duration_seconds: float
    max_duration_seconds: float
    preferred_max_duration_seconds: float
    min_microbeats: int
    max_microbeats: int
    recommended_microbeats: int
    min_microbeat_seconds: float
    max_microbeat_seconds: float


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
    visual_boards: VisualBoardContract


CONTRACTS = {
    "pilot_2min": StoryContract(
        "pilot_2min", 90, 150, 400, 720, 3, 4, 14, 28,
        VisualBoardContract(6, 12, 8, 2, 4, 3, 8, 24, 18, 2, 4, 3, 3, 8),
    ),
    "full_longform": StoryContract(
        "full_longform", 1500, 1920, 6750, 8640, 8, 10, 200, 320,
        VisualBoardContract(50, 64, 56, 5, 8, 7, 20, 36, 30, 3, 5, 4, 4, 8),
    ),
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


def validate_visual_boards(mode: str, scenes: list[dict[str, Any]]) -> list[str]:
    """Validate final-image boards without forcing one image per microbeat."""
    contract = contract_for(mode)
    board_contract = contract.visual_boards
    board_ids = {scene.get("visual_board_id") for scene in scenes}
    if None in board_ids or len(board_ids) == 0:
        return ["visual_board_id is required for the board/microbeat relationship"]

    errors: list[str] = []
    boards: dict[str, list[dict[str, Any]]] = {}
    for scene in scenes:
        board_id = scene.get("visual_board_id")
        boards.setdefault(board_id, []).append(scene)

    board_count = len(boards)
    if not board_contract.min_boards <= board_count <= board_contract.max_boards:
        errors.append(
            f"visual_board_count {board_count} outside "
            f"{board_contract.min_boards}-{board_contract.max_boards}"
        )

    boards_by_act: dict[str, set[str]] = {}
    for board_id, beats in boards.items():
        beats.sort(key=lambda item: float(item["start_seconds"]))
        beat_count = len(beats)
        if not board_contract.min_microbeats <= beat_count <= board_contract.max_microbeats:
            errors.append(
                f"visual board {board_id} has {beat_count} microbeats; "
                f"expected {board_contract.min_microbeats}-{board_contract.max_microbeats}"
            )
        board_start = float(beats[0]["start_seconds"])
        board_end = max(float(beat["end_seconds"]) for beat in beats)
        board_duration = board_end - board_start
        if not board_contract.min_duration_seconds <= board_duration <= board_contract.max_duration_seconds:
            errors.append(
                f"visual board {board_id} duration {board_duration:.2f}s violates "
                f"{board_contract.min_duration_seconds}-{board_contract.max_duration_seconds}s"
            )
        if board_duration > board_contract.preferred_max_duration_seconds and not any(
            beat.get("hold_reason") in {"emotional_hold", "diagram_hold"} for beat in beats
        ):
            errors.append(
                f"visual board {board_id} duration {board_duration:.2f}s exceeds preferred "
                f"{board_contract.preferred_max_duration_seconds}s without hold_reason"
            )
        act_id = beats[0].get("script_section_id", "unknown")
        boards_by_act.setdefault(act_id, set()).add(board_id)

    for act_id, act_boards in boards_by_act.items():
        if not board_contract.min_boards_per_act <= len(act_boards) <= board_contract.max_boards_per_act:
            errors.append(
                f"act {act_id} has {len(act_boards)} visual boards; expected "
                f"{board_contract.min_boards_per_act}-{board_contract.max_boards_per_act}"
            )
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
    if any("visual_board_id" in scene for scene in scenes):
        errors.extend(validate_visual_boards(mode, scenes))
    errors.extend(validate_claim_coverage(script, ledger))
    errors.extend(validate_asset_reuse(assets))
    if errors:
        raise ValueError("historical-story validation failed: " + "; ".join(errors))


_SCRIPT_PROSE_META_PATTERNS = (
    "镜头", "画面", "微分镜", "分镜", "提示词", "prompt", "board",
    "storyboard", "microbeat", "montage", "蒙太奇", "制作说明",
    "caption-safe", "starting state", "dynamic layer", "visual board",
)

def validate_script_prose(script: dict[str, Any]) -> list[str]:
    """Reject production instructions leaking into narrated prose."""
    errors: list[str] = []
    for section in script.get("sections", []):
        section_id = str(section.get("id", ""))
        text = str(section.get("text", ""))
        scan_text = text.replace("各位观众好，这里是读点东西。", "")
        for pattern in _SCRIPT_PROSE_META_PATTERNS:
            if pattern.lower() in scan_text.lower():
                errors.append(f"section {section_id} contains production/meta term {pattern!r}")
    return errors


def _script_ngrams(value: str, size: int = 2) -> set[str]:
    compact = re.sub(r"\s+", "", value)
    return {compact[index:index + size] for index in range(max(0, len(compact) - size + 1))}


def validate_script_repetition(script: dict[str, Any], max_similarity: float = 0.60) -> list[str]:
    """Reject repeated explanatory paragraphs while allowing recurring event names."""
    paragraphs: list[tuple[str, str]] = []
    for section in script.get("sections", []):
        section_id = str(section.get("id", ""))
        for paragraph in str(section.get("text", "")).split("\n"):
            paragraph = paragraph.strip()
            if len(paragraph) >= 18:
                paragraphs.append((section_id, paragraph))
    errors: list[str] = []
    for index, (left_id, left) in enumerate(paragraphs):
        left_grams = _script_ngrams(left)
        for right_id, right in paragraphs[index + 1:]:
            right_grams = _script_ngrams(right)
            if not left_grams or not right_grams:
                continue
            similarity = len(left_grams & right_grams) / len(left_grams | right_grams)
            if similarity >= max_similarity:
                errors.append(f"sections {left_id} and {right_id} contain near-duplicate prose (jaccard={similarity:.3f})")
    return errors


def validate_commentary_contract(script: dict[str, Any], min_chars: int = 360, max_chars: int = 810) -> list[str]:
    """Require an explicit, final 3-5 minute post-story commentary section."""
    sections = script.get("sections", [])
    start_id = (script.get("metadata") or {}).get("commentary_start_section_id")
    if not start_id:
        return ["commentary_start_section_id is required"]
    ids = [str(section.get("id", "")) for section in sections]
    if start_id not in ids:
        return [f"commentary start section {start_id!r} is missing"]
    start_index = ids.index(start_id)
    commentary = sections[start_index:]
    if not commentary or any(not section_id.startswith("commentary") for section_id in ids[start_index:]):
        return ["commentary sections must be contiguous and final"]
    count = sum(len(re.sub(r"\s+", "", str(section.get("text", "")))) for section in commentary)
    if count < min_chars or count > max_chars:
        return [f"commentary character count {count} outside {min_chars}-{max_chars}"]
    return []
