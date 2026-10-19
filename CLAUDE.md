# OpenMontage

**MANDATORY: Read [`AGENT_GUIDE.md`](AGENT_GUIDE.md) before responding to ANY user message.**

Do not act on the user's request until you have read AGENT_GUIDE.md.
It contains routing rules that determine your first action based on what the user asked.
Skipping it WILL cause you to take the wrong action.

There are no instructions in this file. All instructions are in AGENT_GUIDE.md.

## Image Context Handling

When inspecting reference images, avoid repeatedly sending original PNG/JPEG files into the model context. Use this workflow:

- Keep originals on disk; create local previews before visual inspection.
- Use a JPEG preview with the longest edge around 768px and quality around 65 for overall inspection.
- For fine details, create targeted 512–768px crops (for example: face/hair, upper body/arms/props, legs/shoes) instead of rereading the full image.
- For multiple references, create one low-resolution contact sheet first; inspect individual crops only when needed.
- Read at most one overview image or 2–3 related crops per visual-inspection round, and do not have multiple agents reread the same images.
- After inspection, write a compact textual visual reference so later SVG, animation, and preview work can reuse the description without rereading images.
- For rendered video checks, extract a small low-resolution contact sheet of keyframes instead of loading the full video or many full-resolution frames.

Example macOS preview conversion:

```bash
sips -Z 768 -s format jpeg -s formatOptions 65 \\
  input.png --out "$CLAUDE_JOB_DIR/tmp/preview.jpg"
```

This reduces Base64 image attachments in the conversation and helps prevent context-window errors.
