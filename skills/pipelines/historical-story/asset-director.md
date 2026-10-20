# Historical Story Asset Director

Acquire and generate reusable, source-aware visual assets for a narrated historical story. This pipeline does not depend on generated video clips; designed stills, diagrams, maps, archival references, and final shot images carry the visual storytelling.

## core_assets stage

Create approved reusable groups: character references, location/scene plates, maps, diagrams, timelines, archival references, props, and music. Every group records provenance, historical treatment, rights, and continuity anchors.

Character references are never automatically final shots. Scene plates define where and how a subject can appear. For full longform, the asset unit is the **final visual board**: one unique contextual image per board, not one image per internal microbeat. Core maps, diagrams, and evidence graphics can be reused as deterministic overlays, while the board's primary image must remain unique and narratively specific.

## shot_assets stage

Read the approved `shot_asset_plan`. For each planned shot, combine the required character reference, scene reference, props/maps, narration beat, and composition into a final still image or editorial frame. The generated frame must fit the exact story context; do not place a generic portrait into a scene just because the person is mentioned.

Use the approved provider/model path only. Generate one representative shot first, inspect it for scene fidelity, then batch the remaining shot groups. Reuse a final shot only when the crop, overlay, or narrative function changes meaningfully and the reuse is recorded.

## Quality checklist

- Every final shot matches its narration beat and scene location.
- Characters are embedded in a relevant environment or evidence layout.
- Maps/diagrams carry exact labels through deterministic overlays, not AI-generated text.
- Generated reconstruction, archival, illustrative, and symbolic treatments are labeled.
- All files have prompt/model/provenance and `reused_by_scene_ids` metadata.

Output/update `asset_manifest`; stop for human review before edit.
