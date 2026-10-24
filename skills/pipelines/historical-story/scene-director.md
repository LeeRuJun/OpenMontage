# Historical Storyboard Blueprint Director

Design the storyboard before designing or generating character and scene assets. This is a narrated historical explainer, not a character-animation workflow.

## What this stage does

Translate locked narration into acts, sequence beats, and micro-shot requirements. This stage does not generate final images. Every micro-shot must state the visual idea, evidence or claim being explained, relevant historical subject/location, required map/diagram/scene/character asset group, camera framing, duration, caption or label, and editorial purpose.

Do not require detailed character acting, choreography, dialogue blocking, gaze paths, or pose-by-pose animation. Characters are visual anchors inside contextual scenes; maps, timelines, diagrams, archival references, objects, and location plates carry most of the explanation.

## Rhythm and visual-board math

The storyboard has two nested levels:

1. **Final visual board** — one unique final image/scene composition that may stay on screen while its internal layers move.
2. **Microbeat** — a 4–8 second narration/animation beat inside that board. A microbeat changes the crop, camera move, route, evidence layer, caption, or emotional emphasis; it does **not** request another image.

Pilot: 3–4 acts, 6–12 final visual boards, and 2–4 microbeats per board. A board usually holds 8–24 seconds.

Full longform: 8–10 acts, **40–50 final visual boards** (recommended 48; normally 5–7 boards per act), and 3–5 microbeats per board. A board normally holds 20–30 seconds; 30–36 seconds is allowed only for a diagram, evidence board, or emotional landing with an explicit `hold_reason`.

The 22–25 minute full contract therefore favors a rich board over a large image count. Each board must carry a clear location, subject, relationship, or evidence layout and must receive a unique final image. Core maps/diagrams may appear as deterministic overlays, but never substitute for the board's contextual image. Do not make one generated image per microbeat and do not stretch a static frame without internal motion or information change.

The scene plan must identify `visual_board_id`, `microbeat_index`, and the board's internal beat purpose. The shot-asset plan has one final-image entry per `visual_board_id`; the edit stage turns its microbeats into camera, overlay, label, and audio timing.

## Asset requests

Use `character_asset_requests` for identity references, `scene_asset_requests` for locations, and `editorial_asset_requests` for maps, diagrams, timelines, evidence cards, props, and archival material. A final shot request combines the approved references with the narration claim and editorial composition; it does not ask a character to perform detailed animation.

Output `scene_plan` and stop for human approval. Only after approval may character/scene bibles and core assets be designed.


## Board content diversity

A consistent art direction does not mean repeated content. Within one act, adjacent final boards must change at least one story-bearing dimension: arrival/setting, actor position, concrete action, resistance, evidence or route, consequence, or the next destination. Reusing the same palette, lens family, architecture and character continuity is allowed; reusing the same claim, spatial arrangement and microbeat descriptions is not.

Before approving a scene plan, run the shot-plan prompt-diversity check. It compares board-specific claim, action, evidence and microbeat text while ignoring shared style guidance. Near-duplicate content returns the plan to storyboard revision before image generation.
