"""Compile authored historical-story boards into provider-ready shot contracts."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any


DEFAULT_COMPOSITION = (
    "wide environmental documentary composition with a readable foreground, "
    "midground, and background; one continuous camera view"
)
DEFAULT_DYNAMIC_LAYERS = [
    "foreground-to-background depth read",
    "slow emphasis on the claim-bearing area",
    "caption-safe negative space for deterministic overlays",
]
VALID_VISUAL_FUNCTIONS = {
    "establish_context",
    "introduce_subject",
    "explain_mechanism",
    "show_event",
    "show_consequence",
    "emotional_landing",
    "evidence_insert",
    "transition",
}


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    return value if isinstance(value, dict) else None


def _first_dict(*values: Any) -> dict[str, Any] | None:
    for value in values:
        if isinstance(value, dict) and value:
            return copy.deepcopy(value)
    return None


def _artifact(project: Path, name: str) -> dict[str, Any] | None:
    return _read_json(project / "artifacts" / name) or _read_json(project / name)


def _resolve_visual_style(scene_plan: dict[str, Any], project: Path) -> dict[str, Any]:
    metadata = scene_plan.get("metadata") or {}
    settings = _artifact(project, "production_settings.json") or {}
    proposal = _artifact(project, "proposal_packet.json") or {}
    production_plan = proposal.get("production_plan") or {}

    style = _first_dict(
        metadata.get("visual_style"),
        settings.get("visual_style"),
        production_plan.get("visual_style"),
    )
    if style:
        return style

    art_direction = production_plan.get("art_direction")
    palette_discipline = production_plan.get("palette_discipline")
    guidance_parts = [
        value for value in (art_direction, palette_discipline)
        if isinstance(value, str) and value.strip()
    ]
    if guidance_parts:
        return {
            "name": "approved-project-art-direction",
            "prompt_guidance": " ".join(guidance_parts),
        }

    # An absent style is valid at this compiler boundary; the stage gate can
    # require a project-authored style before paid generation begins.
    return {}


def _resolve_period_label(scene_plan: dict[str, Any], project: Path) -> str:
    metadata = scene_plan.get("metadata") or {}
    proposal = _artifact(project, "proposal_packet.json") or {}
    production_plan = proposal.get("production_plan") or {}
    return str(
        metadata.get("period_label")
        or production_plan.get("period_label")
        or "historical period specified by the approved evidence"
    )


def _resolve_board(scene: dict[str, Any]) -> dict[str, Any]:
    board = scene.get("visual_board") or scene.get("board")
    return board if isinstance(board, dict) else scene


def _resolve_references(scene: dict[str, Any], board: dict[str, Any]) -> list[str]:
    candidates = (
        board.get("required_core_assets"),
        scene.get("required_core_assets"),
        board.get("reference_asset_ids"),
        scene.get("reference_asset_ids"),
    )
    for value in candidates:
        if isinstance(value, list) and value:
            refs = [str(item) for item in value if str(item).strip()]
            if refs:
                return refs

    explicit_ids = []
    for key in ("environment_reference_id", "scene_reference_id", "character_reference_id"):
        value = board.get(key) or scene.get(key)
        if value:
            explicit_ids.append(str(value))
    if explicit_ids:
        return explicit_ids

    raise ValueError(
        f"scene {scene.get('id', '<unknown>')} has no explicit required_core_assets "
        "or environment reference; refusing to invent project-specific references"
    )


def _resolve_scene_anchors(project: Path, scene: dict[str, Any], board: dict[str, Any]) -> list[str]:
    bible = _artifact(project, "historical_scene_bible.json") or {}
    anchors = bible.get("approved_visual_anchors")
    if isinstance(anchors, dict):
        values = anchors.get(scene.get("id")) or anchors.get(board.get("visual_board_id"))
        if isinstance(values, list):
            return [str(value) for value in values]
    if isinstance(anchors, list):
        return [str(value) for value in anchors]
    return []


def _resolve_dynamic_layers(scene: dict[str, Any], board: dict[str, Any]) -> list[str]:
    value = board.get("dynamic_layers") or scene.get("dynamic_layers")
    if isinstance(value, list) and value:
        return [str(item) for item in value[:5]]
    microbeats = board.get("microbeats") or scene.get("microbeats")
    if isinstance(microbeats, list) and microbeats:
        labels = []
        for item in microbeats[:5]:
            if isinstance(item, dict):
                labels.append(str(item.get("description") or item.get("id") or "microbeat"))
            else:
                labels.append(str(item))
        return labels
    return list(DEFAULT_DYNAMIC_LAYERS)


def _resolve_style_text(style: dict[str, Any]) -> str:
    values = [
        style.get("prompt_guidance"),
        style.get("description"),
        style.get("palette_discipline"),
    ]
    return " ".join(str(value).strip() for value in values if isinstance(value, str) and value.strip())


def _resolve_visual_function(scene: dict[str, Any], board: dict[str, Any]) -> str:
    value = board.get("visual_function") or scene.get("visual_function") or "show_event"
    return value if value in VALID_VISUAL_FUNCTIONS else "show_event"


def _build_prompt(
    *,
    period: str,
    claim: str,
    subject_action: str,
    location_context: str,
    evidence_layer: str,
    historical_boundary: str,
    composition: str,
    lighting: str,
    style_text: str,
    color_direction: str,
    dynamic_layers: list[str],
    microbeat_states: list[dict[str, Any]],
) -> str:
    style_clause = style_text or "follow the approved project art direction without adding an unapproved palette"
    color_clause = color_direction or "use the board-authored light and color direction"
    layers = "; ".join(dynamic_layers)
    return (
        f"Historical period: {period}. "
        f"Narrative claim: {claim}. "
        f"Subject/action: {subject_action}. "
        f"Location and spatial relationship: {location_context}. "
        f"Evidence layer: {evidence_layer}. "
        f"Historical boundary: {historical_boundary}. "
        f"Composition and camera: {composition}. "
        f"Lighting and color: {lighting}; {color_clause}. "
        f"Approved visual style: {style_clause}. "
        f"Microbeat visual states: {'; '.join(str(state.get('description', '')) for state in microbeat_states)}. "
        f"Dynamic layers reserved for edit: {layers}. "
        "Use references for continuity only; integrate people and evidence into the environment. "
        "Create one single coherent shot with one continuous camera view. "
        "Do not collage or show source images, do not use split-screen or contact-sheet layouts. "
        "Keep the lower third and the authored caption-safe area clear for deterministic overlays. "
        "No readable text or digits, no logos, no modern objects, no unsupported insignia, "
        "and no generic floating portrait."
    )


def _compile_shot(scene: dict[str, Any], project: Path, visual_style: dict[str, Any], period_label: str, index: int) -> dict[str, Any]:
    board = _resolve_board(scene)
    claim = str(board.get("visual_claim") or scene.get("visual_claim") or scene.get("description") or "")
    if not claim.strip():
        raise ValueError(f"scene {scene.get('id', '<unknown>')} has no visual claim")

    refs = _resolve_references(scene, board)
    anchors = _resolve_scene_anchors(project, scene, board)
    refs = list(dict.fromkeys(refs + anchors))
    period = str(board.get("period_label") or scene.get("period_label") or period_label)
    location_context = str(
        board.get("location_context")
        or scene.get("location_context")
        or scene.get("location")
        or "the specific historical location defined by the approved scene bible"
    )
    subject_action = str(
        board.get("subject_action")
        or scene.get("subject_action")
        or scene.get("information_role")
        or claim
    )
    evidence_layer = str(
        board.get("evidence_layer")
        or scene.get("evidence_layer")
        or "diegetic evidence layer tied to the narrative claim"
    )
    historical_boundary = str(
        board.get("historical_boundary")
        or scene.get("historical_boundary")
        or "illustrative reconstruction; do not invent dialogue, text, insignia, or unsupported action"
    )
    composition = str(
        board.get("composition")
        or scene.get("composition")
        or scene.get("framing")
        or DEFAULT_COMPOSITION
    )
    lighting = str(
        board.get("lighting")
        or scene.get("lighting")
        or (scene.get("shot_language") or {}).get("lighting_key")
        or "board-authored historical light"
    )
    color_direction = str(board.get("color_direction") or scene.get("color_direction") or "")
    dynamic_layers = _resolve_dynamic_layers(scene, board)
    microbeat_states = board.get("microbeat_visual_states") or board.get("microbeats") or []
    microbeat_states = [state if isinstance(state, dict) else {"id": str(state), "description": str(state)} for state in microbeat_states]
    prompt = _build_prompt(
        period=period,
        claim=claim,
        subject_action=subject_action,
        location_context=location_context,
        evidence_layer=evidence_layer,
        historical_boundary=historical_boundary,
        composition=composition,
        lighting=lighting,
        style_text=_resolve_style_text(visual_style),
        color_direction=color_direction,
        dynamic_layers=dynamic_layers,
        microbeat_states=microbeat_states,
    )
    scene_id = str(scene["id"])
    board_id = str(board.get("visual_board_id") or scene.get("visual_board_id") or scene_id)
    start = float(scene.get("start_seconds", 0))
    end = float(scene.get("end_seconds", start + 20))
    microbeats = board.get("microbeat_ids") or scene.get("microbeat_ids")
    if not isinstance(microbeats, list) or not microbeats:
        microbeats = [f"{board_id}-m{n}" for n in range(1, 4)]

    return {
        "shot_id": f"shot-{index:02d}",
        "scene_id": scene_id,
        "visual_board_id": board_id,
        "board_duration_seconds": max(20, end - start),
        "microbeat_ids": [str(item) for item in microbeats],
        "internal_motion_plan": dynamic_layers,
        "prompt_spec": {
            "script_section_id": str(scene.get("script_section_id") or scene_id),
            "visual_claim": claim,
            "subject_action": subject_action,
            "location_context": f"{period}; {location_context}",
            "evidence_layer": evidence_layer,
            "historical_boundary": historical_boundary,
            "dynamic_layers": dynamic_layers,
            "microbeat_visual_states": microbeat_states,
            "caption_safe_area": str(board.get("caption_safe_area") or "lower third and board-authored safe region"),
            "positive_prompt": prompt,
            "constraints": [
                "single coherent shot",
                "one continuous camera view",
                "use references for continuity only",
                "do not collage or show source images",
                "no readable text or digits",
                "no modern objects or unsupported insignia",
            ],
        },
        "narration_beat": claim,
        "visual_function": _resolve_visual_function(scene, board),
        "generation_mode": str(board.get("generation_mode") or scene.get("generation_mode") or "composite_references"),
        "required_core_assets": refs,
        "prompt": prompt,
        "camera": composition,
        "composition": composition,
        "prompt_constraints": [
            "single coherent shot",
            "one continuous camera view",
            "use references for continuity only",
            "do not collage or show source images",
            "no readable text or digits",
            "no modern objects",
        ],
        "reuse_policy": "primary image unique to this board; explicit references are continuity anchors only",
        "reused_by_shots": [],
        "status": "approved",
    }


def main(project: Path) -> None:
    project = Path(project).resolve()
    scene_plan = _artifact(project, "scene_plan.json")
    if not scene_plan:
        raise FileNotFoundError(f"missing scene_plan.json under {project / 'artifacts'}")
    visual_style = _resolve_visual_style(scene_plan, project)
    period_label = _resolve_period_label(scene_plan, project)
    scenes = scene_plan.get("scenes") or []
    board_groups: dict[str, list[dict[str, Any]]] = {}
    board_order: list[str] = []
    for scene in scenes:
        board_id = str(scene.get("visual_board_id") or scene.get("id"))
        if board_id not in board_groups:
            board_groups[board_id] = []
            board_order.append(board_id)
        board_groups[board_id].append(scene)
    board_scenes = []
    for board_id in board_order:
        beats = board_groups[board_id]
        board = copy.deepcopy(beats[0])
        board["start_seconds"] = min(float(beat.get("start_seconds", 0)) for beat in beats)
        board["end_seconds"] = max(float(beat.get("end_seconds", 0)) for beat in beats)
        board["microbeat_ids"] = [str(beat.get("id")) for beat in beats]
        board["microbeats"] = [
            {"id": str(beat.get("id")), "description": str(beat.get("description", ""))}
            for beat in beats
        ]
        board["microbeat_visual_states"] = [
            {
                "id": str(beat.get("id")),
                "description": str(beat.get("description", "")),
                "movement": str(beat.get("movement", "static")),
                "framing": str(beat.get("framing", "wide")),
                "information_role": str(beat.get("information_role", "")),
            }
            for beat in beats
        ]
        board["description"] = " ".join(str(beat.get("description", "")) for beat in beats)
        board_scenes.append(board)
    shots = [_compile_shot(scene, project, visual_style, period_label, index) for index, scene in enumerate(board_scenes, 1)]
    mode = (scene_plan.get("metadata") or {}).get("mode") or "full_longform"
    output = {
        "version": "1.0",
        "mode": mode,
        "shots": shots,
        "metadata": {
            "board_count": len(shots),
            "provider": "openai:gpt-image-2",
            "unique_primary_image_required": True,
            "prompt_stage": "shot-prompt-director",
            "coherent_single_shot_required": True,
            "period_label": period_label,
            "visual_style": visual_style,
            "prompt_diversity_contract": "v2",
        },
    }
    output_path = project / "artifacts" / "shot_asset_plan.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"shots": len(shots), "stage": "shot_prompt_director"}, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", required=True)
    args = parser.parse_args()
    main(Path(args.project_dir))
