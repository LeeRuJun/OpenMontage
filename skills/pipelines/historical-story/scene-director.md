# Historical Story Scene Director

Translate locked narration into acts, sequence beats, and micro-shots.

Pilot: 3–4 acts and 14–28 micro-shots. Full: 8–10 acts, 20–40 second sequence beats, 180–240 micro-shots. Normal shot duration is 4–8 seconds. An 8–12 second hold requires `hold_reason: emotional_hold` or `diagram_hold`.

Use map, character, evidence, diagram, scene, and aftermath shot language in rotation. One shot is not automatically one new image: a reusable asset may support crop, push, route draw, label reveal, and contextual reuse. Attach `asset_group_id`, `shot_intent`, `narrative_role`, and `timing_ref` to every micro-shot.

Output `scene_plan` from measured timestamps and stop for human approval.
