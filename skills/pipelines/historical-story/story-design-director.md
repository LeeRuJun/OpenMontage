# Historical Story Design Director

**REQUIRED SUB-SKILL:** Read `skills/creative/story-writing-director.md` before designing the story spine. This Skill contains the research, architecture, drafting, and review phases; complete the architecture phase before prose.

Decide how the history will be told before writing narration or designing images. Use the generic causal story blueprint, then add the historical evidence boundary.

## Research → material map → spine

After the evidence ledger and before the story spine, create `metadata.material_density_map`. Each entry contains `section_id`, `event_refs`, `material_role` (`core_event`, `support`, `bridge`, or `commentary`), `target_seconds`, `required_facts`, `allowed_summary`, and `forbidden_repetition`. The map decides what deserves detail and what is deliberately brief; the script writer must not make this decision while padding prose.

## Story spine contract

Lock:

- central story question;
- narrative subject and point of view;
- subject’s immediate desire or pressure;
- opposing institutional/person/group pressure;
- stakes and what changes if the subject fails;
- event chain with time, place, actors, action, consequence, and claim refs;
- flexible arc functions: orientation, pressure, inciting incident, development, reversal, recovery, escalation, consequence, ending;
- fact boundary: established, probable, contested, unknown;
- knowledge state: what each actor knew at each event;
- planted elements and later payoffs.

`event_story` is required in `story_spine.metadata`. It contains the stable event records and the flexible arc mapping. Arc labels are functions, not fixed five-act slots: they may repeat, combine, or interleave.

## Event-first rule

A chronological list is not a story spine. For every event, write:

```text
id | time | place | actors | action | consequence | claim_refs
```

The next event must be made more likely, necessary, or impossible by the consequence of the previous event. Do not use an analysis claim as a reversal, climax, or ending. If a proposed turning point contains no actor action and no changed situation, send it back for redesign.

## Gate

Produce `story_spine` after research and stop for review. Script, character bible, scene bible, and asset generation must wait for this approval.

## Structure handoff boundary

This stage consumes the research event inventory and creates `material_density_map` and `scene_contracts` inside the approved story architecture. It decides which events are core, support, bridge, or commentary; assigns target time; records required facts and forbidden repetition; and maps objective, resistance, action, reversal, consequence and next pressure. **不写最终旁白**，也不在正文阶段临时发明结构。
