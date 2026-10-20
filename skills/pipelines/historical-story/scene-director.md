# Historical Storyboard Blueprint Director

Design the storyboard before designing or generating character and scene assets.

## What this stage does

Translate locked narration into acts, sequence beats, and micro-shot requirements. This stage does not generate final images. Every micro-shot must state who appears, what they do, where they are, what props/relations matter, camera language, duration, and the exact asset groups it needs.

## Rhythm

Pilot: 3–4 acts and 14–28 micro-shots. Full: 8–10 acts, 20–40 second sequence beats, 180–240 micro-shots. Normal shot duration is 4–8 seconds. An 8–12 second hold requires `hold_reason: emotional_hold` or `diagram_hold`.

## Asset requests

Use `character_asset_requests` for continuity references and `scene_asset_requests` for locations. A final shot request combines those references with action, props, relationship, camera, and visual intent. One shot is not automatically one new image.

Output `scene_plan` and stop for human approval. Only after approval may character/scene bibles and core assets be designed.
