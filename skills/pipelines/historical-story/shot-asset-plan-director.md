# Shot Asset Plan Director

This stage is mandatory for narrated historical storytelling because the video is built from designed stills, diagrams, and scene plates rather than generated video clips.

## Inputs

Read the approved story spine, script, locked narration timing, storyboard blueprint, historical character bible, historical scene bible, and approved core asset manifest.

## For every shot

Write one `shot_asset_plan` entry containing:

- the narration beat and claim being visualized
- the scene/shot ID and visual function
- the exact character, scene, prop, map, diagram, or archival asset IDs required
- generation mode: composite references, diagram overlay, provided asset, or archive reference
- a full prompt describing the subject in the scene, the action/context, spatial relationship, camera/composition, lighting, and safe text area
- prompt constraints: era fidelity, no AI text, no modern objects, reconstruction label when needed
- reuse policy and every shot that reuses the resulting image

A character reference alone is never a final shot. A final shot must show the historical subject in a relevant place, context, or evidence layout that answers the narration beat.

## Gate

Reject a plan when the image could be moved to another scene without changing meaning, when the prompt lacks a location/context, or when a generated asset is repeated without a new visual function. Generate one representative scene sample, review it, then allow the `shot_assets` stage to batch-generate the approved shot images.

Output `shot_asset_plan` and stop for human approval.
