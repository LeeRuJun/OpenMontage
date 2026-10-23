# Shot Asset Plan Director

This stage maps **final visual boards** to unique final images. It does not create one image for every storyboard microbeat.

## Board contract

- Pilot: 6–12 final visual boards, usually 2–4 microbeats per board.
- Full longform: 40–50 final visual boards, recommended 48, normally 5–7 boards per act.
- Each full-longform board normally lasts 20–30 seconds; 30–36 seconds requires an explicit diagram/evidence/emotional `hold_reason`.
- Each board contains 3–5 internal microbeats, each normally 4–8 seconds.
- Every board gets one unique final image. Reuse of a final image as another board's primary image is rejected; deterministic maps, diagrams, and overlays may be reused only as supporting layers.

## Inputs

Read the approved story spine, script, locked narration timing, storyboard blueprint, historical character bible, historical scene bible, and approved core asset manifest.

## For every final visual board

Write one `shot_asset_plan` entry containing:

- `visual_board_id`, act/scene ID, board duration, and the contained microbeat IDs
- the narration claim and visual function served by the whole board
- the exact character, scene, prop, map, diagram, or archival asset IDs required as references/overlays
- generation mode: composite references, diagram overlay, provided asset, or archive reference
- a full prompt describing the subject in the scene, the action/context, spatial relationship, camera/composition, lighting, and safe text area
- the internal dynamic features: camera path, layer reveals, route drawing, evidence emphasis, caption/label timing
- reuse policy, provenance, and the fact that the final primary image is unique to this board

A character reference alone is never a final shot. A final board must show the historical subject in a relevant place, context, or evidence layout that answers the narration beat. A board can carry several narration beats only when its internal visual state changes meaningfully; otherwise split it.

## Script → visual board → prompt

Do not copy the narration into an image prompt. Translate each approved script section through these fields:

1. **Narrative claim** — what the viewer must understand from this board, not the whole paragraph.
2. **Subject + action** — who/what is acting or changing; keep people embedded in context.
3. **Location + spatial relationship** — where the action happens and what sits near/far from what.
4. **Evidence layer** — map, route, seal, ledger, timeline, object, or diagram that makes the claim legible.
5. **Historical boundary** — documented fact, illustrative reconstruction, contested detail, or symbolic aftermath; state what must not be invented.
6. **Composition** — camera/framing, light, palette, hierarchy, and a clean caption-safe region.
7. **Dynamic layers** — 3–5 things edit/compose may reveal or move during the 20–30 second board: route draw, crop, parallax, evidence reveal, label, or emphasis.
8. **Constraints** — no AI text, modern objects, unsupported insignia, generic floating portrait, or cinematic action that changes the factual meaning.

Store this translation in `prompt_spec` as well as the provider-ready `prompt`. The prompt is a production contract: a reviewer should be able to trace it back to the script section and evidence ledger without guessing.


Reject a plan when the image could be moved to another board without changing meaning, when the prompt lacks a location/context, when a board has too few internal beats to sustain its duration, or when a final image is reused as another board's primary image. Generate one representative board sample, review it, then allow the `shot_assets` stage to batch-generate the approved board images.

Output `shot_asset_plan` and stop for human approval.

## Shared art direction

**Before authoring prompts, read `skills/creative/historical-color-direction.md`.** Treat `visual_style` as approved project input and `color_direction` as board-level input. Pass both through without replacing them with a fixed dynasty palette, global low-saturation filter, or external-video look.

Every board must be either a person embedded in a meaningful environment or an environment-led composition. Use foreground, midground, and background to create a 20-second reading path. An isolated portrait or object-only image is not a final board. References are continuity anchors, never source-image frames or collage material.
