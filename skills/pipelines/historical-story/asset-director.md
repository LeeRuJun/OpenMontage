# Historical Story Asset Director

Acquire and generate reusable, source-aware visual assets for a narrated historical story. This pipeline does not depend on generated video clips; designed stills, diagrams, maps, archival references, and final shot images carry the visual storytelling.

## core_assets stage

Create approved reusable groups: character references, location/scene plates, maps, diagrams, timelines, archival references, props, and music. Every group records provenance, historical treatment, rights, and continuity anchors.

Character references are never automatically final shots. Scene plates define where and how a subject can appear. For full longform, the asset unit is the **final visual board**: one unique contextual image per board, not one image per internal microbeat. Core maps, diagrams, and evidence graphics can be reused as deterministic overlays, while the board's primary image must remain unique and narratively specific.

## shot_assets stage

Read the approved `shot_asset_plan`. For each planned shot, combine the required character reference, scene reference, props/maps, narration beat, and composition into a final still image or editorial frame. The generated frame must fit the exact story context; do not place a generic portrait into a scene just because the person is mentioned.

For high-quality boards, the asset director consumes `prompt_spec` rather than a bare narration paragraph: preserve the claim, embed the subject in the location, show the evidence layer, honor the historical boundary, and leave the dynamic layers for edit/compose. A visually impressive image that loses the causal claim is a failed asset even when its style is attractive.

## Fixed image provider policy

When a new image must be generated, use the manifest `provider_policy.image_generation`: `openai_image` / OpenAI `gpt-image-2`. Do not re-rank to another provider or silently fall back; if the fixed provider is unavailable, stop with a blocker. Existing approved local assets may still be reused as references or deterministic board layers when the asset plan explicitly permits it.


Music selection is catalog-only for this pipeline:

- Read `assets/bgm/music_catalog.json` as the single source of truth.
- The AI may select among catalog tracks by `story_act`, `narrative_role`, `mood`, `tension`, `energy`, `duration_fit`, and `voice_compatibility`.
- Copy the selected user-uploaded file into the project `assets/bgm/` directory when needed and record its catalog `id`, source path, selection reason, volume, ducking, and license status in `asset_manifest`/`edit_decisions`.
- Do not call music generation, music search, or an unlisted fallback for historical-story. If no catalog track fits, stop with a blocker and ask for a user-uploaded BGM; do not synthesize a replacement.


- Every final shot matches its narration beat and scene location.
- Characters are embedded in a relevant environment or evidence layout.
- Maps/diagrams carry exact labels through deterministic overlays, not AI-generated text.
- Generated reconstruction, archival, illustrative, and symbolic treatments are labeled.
- All files have prompt/model/provenance and `reused_by_scene_ids` metadata.

Output/update `asset_manifest`; stop for human review before edit.
