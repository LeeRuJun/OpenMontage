# Historical Story Executive Producer

Coordinate the `historical-story` pipeline without turning it into a book-summary flow.

## Modes

- `pilot_2min`: 90–150 seconds, 6–12 visual boards, 2–4 microbeats per board.
- `full_longform`: 22–25 minutes, 40–50 visual boards, 3–5 microbeats per board, 20–30 second preferred board holds.

## Non-negotiable order

intake → research/evidence ledger → proposal → character bible → script → narration timing → scene plan → assets → edit → compose → publish.

A later stage cannot silently repair a failed earlier contract. If evidence, script, narration, or timing changes, invalidate downstream timing-dependent artifacts.

## Approval policy

This pipeline defaults to `approval_policy: autonomous`. Every stage still writes its checkpoint and runs self-review. The coordinator auto-advances when the artifact is schema-valid and no critical review finding remains; it does not write `awaiting_human` or stop for routine creative approval. A critical contract failure still blocks the run and is reported with the exact artifact and fix needed. Set the manifest policy to `guided` for a human-reviewed run.

## Quality gates

In autonomous mode, the coordinator checks story mode, fact coverage, character continuity, narration duration, visual-board count, microbeat rhythm, unique board-image coverage, prompt traceability, and asset provenance before marking a stage completed. Suggestions are recorded and carried forward; critical findings block.

## Output

Pass a compact cross-artifact report to the next director: current mode, approved story question, evidence coverage, timing lock, character bible revision, and unresolved risks.
