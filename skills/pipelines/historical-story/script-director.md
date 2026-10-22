# Historical Story Script Director

Write a story, not an encyclopedia entry.

Use: hook → subject/desire → pressure → escalation → midpoint/reversal → loss of options → climax choice → aftermath/theme.

## Opening contract — hook before detail

Every pilot and full episode starts with a short prologue before the first detailed historical explanation. The opening must:

1. **Hook** with a concrete danger, contradiction, or unanswered question.
2. **Promise** what this episode will explain and why the viewer should keep watching.
3. **Roadmap** two or three questions/turns the story will answer.
4. **Bridge** into the first act's place, person, or evidence board.

For full longform, target a 20–30 second opening prologue. Do not open by listing dates, names, institutions, or battlefield details before the viewer knows the episode's question. Record the contract in `script.opening`; the first section label should identify the prologue/hook, and its visual board should support the promise rather than jump straight into a detail card.

Every factual section includes `claim_refs`. Preserve the evidence ledger qualifier for probable, contested, and unknown material.

For the `historical-story` full-longform channel, `script.opening` is protected content, not optional flavor text. It must preserve this order:

1. Fixed brand welcome: `各位观众好，这里是读点东西。`
2. Episode identification: name the period, subject, and story being told.
3. Story overview: summarize the whole event before detailed exposition.
4. Hook: the concrete contradiction or unanswered question.
5. Promise and roadmap: what the episode will explain.
6. Detailed historical narration begins only after the above contract.

Any script revision that removes or reorders the fixed welcome, overview, hook, promise, or roadmap fails the script gate and invalidates narration timing and every downstream timing-dependent artifact.

## Script length is calculated from time

Use a measured Chinese narration density of approximately 4.0–4.8 characters/second. The script generator must calculate the range from the requested duration before writing:

- 120-second pilot: approximately 480–576 characters; allowed pilot contract 400–720.
- 22-minute full episode: approximately 5,280–6,336 characters.
- 23-minute full episode: approximately 5,520–6,624 characters.
- 24-minute full episode: approximately 5,760–6,912 characters.
- 25-minute full episode: approximately 6,000–7,200 characters.

The full contract allows 5,500–7,200 characters, but the measured narration timing is final. Never slow down, pad with silence, or stretch audio to hide an undersized script.

Pilot uses 3–4 meaningful turns. Full uses 8–10 acts. Use spoken language and leave visual work to the storyboard. Every section should end with a viewer question or deliberate landing silence. Output `script` and stop for human approval.
