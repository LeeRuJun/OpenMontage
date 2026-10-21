# Historical Story Proposal Director

Lock the story angle before writing narration.

Present at least three angles. Each angle needs a hook, central conflict, point of view, visual grammar, why it works, and what it deliberately leaves out. Prefer a dramatic question over a chronological title.

Lock the selected angle, delivery strategy, story question, reveal, pilot/full mode, source versus reconstruction ratio, character treatment, runtime, composition mode, music, and budget.


## Runtime and composition decision

Before locking the proposal, **Present both** available composition runtimes for this historical story: **HyperFrames** (`hyperframes`) for the HTML/GSAP visual-board motion grammar, and **Remotion** when its React scene stack is the better fit. Also consider **FFmpeg** when the treatment is a video-only cut. State the tradeoff for each and wait for the user's choice; record the result in `decision_log` as `render_runtime_selection` with the full `options_considered` list. Carry the chosen `render_runtime` unchanged into `edit_decisions` and compose.

The proposal must also lock `composition_mode` separately from `render_runtime`; the visual-board plan is authored as unique final boards with internal microbeats, not as a larger count of repeated stills.
