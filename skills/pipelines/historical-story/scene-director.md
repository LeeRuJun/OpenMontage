# Historical Storyboard Blueprint Director

Design the storyboard before designing or generating character and scene assets. This is a narrated historical explainer, not a character-animation workflow.

## What this stage does

Translate locked narration into acts, sequence beats, and micro-shot requirements. This stage does not generate final images. Every micro-shot must state the visual idea, evidence or claim being explained, relevant historical subject/location, required map/diagram/scene/character asset group, camera framing, duration, caption or label, and editorial purpose.

Do not require detailed character acting, choreography, dialogue blocking, gaze paths, or pose-by-pose animation. Characters are visual anchors inside contextual scenes; maps, timelines, diagrams, archival references, objects, and location plates carry most of the explanation.

## Rhythm

Pilot: 3–4 acts and 14–28 micro-shots. Full: 8–10 acts, 20–40 second sequence beats, 180–240 micro-shots. Normal shot duration is 4–8 seconds. An 8–12 second hold requires `hold_reason: emotional_hold` or `diagram_hold`.

## Asset requests

Use `character_asset_requests` for identity references, `scene_asset_requests` for locations, and `editorial_asset_requests` for maps, diagrams, timelines, evidence cards, props, and archival material. A final shot request combines the approved references with the narration claim and editorial composition; it does not ask a character to perform detailed animation.

Output `scene_plan` and stop for human approval. Only after approval may character/scene bibles and core assets be designed.
