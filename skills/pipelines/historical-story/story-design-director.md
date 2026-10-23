# Historical Story Design Director

**REQUIRED SUB-SKILL:** Read `skills/creative/story-writing-director.md` before designing the story spine.

Decide how the history will be told before writing narration or designing images. Use the generic causal story blueprint, then add the historical evidence boundary.

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
