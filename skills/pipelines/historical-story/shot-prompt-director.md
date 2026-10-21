# Historical Story Shot Prompt Director

Translate each approved visual board into a production-grade image prompt contract.

## Non-negotiable input

Read the approved `script`, `historical_evidence_ledger`, `scene_plan`, `historical_character_bible`, `historical_scene_bible`, and `asset_manifest` before writing prompts. Do not generate an image from a board title or a copied narration paragraph alone.

## Required `prompt_spec` fields for every board

- `script_section_id`: the exact narration section or claim source
- `visual_claim`: the one thing the viewer must understand from this board
- `subject_action`: who/what acts or changes, embedded in context
- `location_context`: the fixed historical scene and spatial relationship
- `evidence_layer`: map, seal, ledger, route, timeline, object, or diagram that makes the claim legible
- `historical_boundary`: established fact, probable interpretation, contested claim, or illustrative reconstruction
- `dynamic_layers`: 3–5 layers that edit/compose may reveal, draw, crop, or emphasize
- `caption_safe_area`: explicit area reserved for deterministic labels/subtitles
- `constraints`: no AI-readable text, unsupported insignia, modern objects, generic floating portraits, or action that changes factual meaning

## Prompt construction

The provider prompt must combine the structured fields in this order:

1. Narrative claim
2. Subject/action
3. Location and spatial relationship
4. Evidence layer
5. Historical boundary
6. Composition, camera, lighting, palette, and caption-safe area
7. Dynamic layers reserved for edit
8. Negative constraints

Every board must use a board-specific composition. Vary visual grammar deliberately across maps, diagrams, evidence tables, environmental reconstructions, symbolic still lifes, timelines, diptychs, and closing landscapes. A prompt is rejected when its image could be moved to another board without changing meaning.

## Coherent-shot rule

The final board is one coherent cinematic shot, not a collage of the supplied assets. Reference assets are continuity anchors only: integrate the character into the scene with one camera, one spatial relationship, one lighting world, and one focal action. Never show reference-image frames, side-by-side panels, contact sheets, pasted portraits, asset grids, or a collection of objects arranged as a mood board. Maps, ledgers, seals, and archival material must appear as one diegetic evidence layer or be added later as deterministic overlays.

Every provider prompt must explicitly include: `single coherent shot`, `one continuous camera view`, `use references for continuity only`, `do not collage or show source images`, and `no readable text or digits`.

## Prompt specificity standard

A passing prompt names concrete subject matter and camera intent, not just mood adjectives. Use the generated-asset standard:

- **Evidence still life:** lacquered desk, unsealed memorial, jade seal, bamboo slips, bronze oil lamp, night light, material detail, clean caption-safe region.
- **Environment plate:** canals, rice fields, low city walls, boats, mist, distant hills, time of day, wide documentary framing.
- **Map/evidence plate:** layered parchment, river systems, border marks, route space, overhead editorial composition, no generated labels.

If a prompt could describe any historical period or any board after replacing its title, reject it and add the missing object, location, spatial relationship, camera, and claim-specific evidence.


Final board generation uses only the manifest `provider_policy.image_generation` provider: OpenAI `gpt-image-2`. The shot-assets stage must pass approved character and scene references to the provider and record the prompt, model, references, historical treatment, and output path in `asset_manifest`.

## Gate

Do not mark `shot_asset_plan` complete unless every board has all required `prompt_spec` fields, at least one approved core reference, 3–5 internal microbeats, and a unique board ID. Do not enter `shot_assets` when any prompt is generic, missing a location, or missing an evidence layer.
