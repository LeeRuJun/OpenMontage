# Historical Story Compose Director

Render the approved edit with the proposal-locked `render_runtime` and canvas. Route by the locked `render_runtime` value; when it is `hyperframes`, use the HyperFrames HTML/GSAP runtime and never silently fall back to Remotion or FFmpeg.

For longform visual boards, HyperFrames executes the motion authored in `edit_decisions` before encoding: each unique board image is animated through its internal microbeats, overlays, labels, and audio timing. Do not render a repeated still montage and do not add a vague global effect after the video is assembled.

Validate output duration against the narration lock, caption/provenance safe areas, audio intelligibility, reconstruction labels, unique primary-board image coverage, and source treatment. Use the selected HyperFrames or other locked runtime; never silently substitute a different runtime.

Produce `render_report` and `final_review`. Compose cannot repair an unapproved story, character bible, timing artifact, or board asset plan.
