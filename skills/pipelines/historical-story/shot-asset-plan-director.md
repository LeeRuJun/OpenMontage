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

## Gate

Reject a plan when the image could be moved to another board without changing meaning, when the prompt lacks a location/context, when a board has too few internal beats to sustain its duration, or when a final image is reused as another board's primary image. Generate one representative board sample, review it, then allow the `shot_assets` stage to batch-generate the approved board images.

Output `shot_asset_plan` and stop for human approval.
