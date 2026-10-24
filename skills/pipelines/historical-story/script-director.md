# Historical Story Script Director

**REQUIRED SUB-SKILL:** Read `skills/creative/story-writing-director.md` before drafting.

**REQUIRED REVIEW:** Before narration generation, run the independent `pipelines/historical-story/script-review-director` review and require `READY`.

Write a historical story, not an encyclopedia entry and not a narrated essay.

## Required inputs before prose

Read `research_brief`, `historical_evidence_ledger`, `story_spine.metadata.event_story`, and the approved `material_density_map` before drafting. **不要在素材地图完成前写正文。** If the event inventory is short, return to research; do not fill the target with commentary or repeated background.

## Governing rule

**Every narration section must be built from events.** Before writing prose, fill an event card with:

- **时间**：具体年份、月份、季节或“某日之后”；
- **地点**：城、府、河、道路、宫门、营地或其他可视空间；
- **人物**：谁在场、谁发令、谁执行、谁承受后果；
- **行动**：人物实际做了什么，命令如何抵达，军队/官员/城市如何回应；
- **后果**：这次行动立刻改变了什么，下一件事为什么被迫发生。

**事件顺序：时间、地点、人物、行动、后果。**

**每个段落先写事件；每个事件之后再写后果。** 分析不能替代事件。如果一句话不能回答“谁在何处做了什么”，它不能占据故事主体。分析、评价和历史解释只能附着在已经讲清楚的事件之后，不能替代事件。

## Scene contract before prose

For every section, record starting state, immediate objective, resistance, attempt, reversal or discovery, consequence, and the question that forces the next section. The event card supplies the historical fields; the scene contract supplies the causal fields. A section cannot be lengthened with commentary when one of these fields is empty.

## Prose contract

- 用叙事动词：到达、下令、起兵、围攻、撤退、渡河、打开城门、接管、处置、改年号。
- 让地点推动剧情：命令从哪里发出，军队沿什么道路移动，哪座城/哪条河改变了选择。
- 让人物选择推动下一段：前一段的后果必须成为下一段的压力、机会或新目标。
- 不要对观众解释“这说明什么”“观众应该理解什么”“这不是……而是……”；把判断改写成下一件具体发生的事。
- 不用连续的“制度分析、财政分析、信任分析、正统分析”撑时长；每次分析最多一句，并且必须紧跟在已叙述的事件之后。
- 不虚构对白、心理独白、未被证实的战术细节或确定的争议结论。
- 不把后世评价写成当时人物已经知道的动机；使用“史家常将其解释为……”时，必须有 claim_ref 和限定词。

## Story movement

长篇可以使用 orientation、pressure、inciting_incident、development、reversal、recovery、escalation、consequence、ending 等叙事功能。它们可以重复、交错或合并，但每个功能都必须由具体事件承载：

```text
事件卡：1399年，北平，朱棣与燕军，起兵并控制城门
行动后果：朝廷必须调兵北上；北平从藩王驻地变成战争基地
下一事件：朝廷军抵达北平周边，战争进入城防与道路争夺
```

不要先写抽象主题再寻找例子。先按事件链排列，再决定哪里停顿、转折、升级和收束。

## Opening contract — hook before detail

Full and pilot episodes都先有 20–30 秒开场，但开场也必须包含事件或具体危险：

1. 固定品牌开场：`各位观众好，这里是读点东西。`
2. 说清时代、人物和正在发生的冲突；
3. 提出一个具体问题；
4. 预告将沿哪些地点/事件继续；
5. 立刻进入第一个时间、地点和人物行动。

不要用一串日期、人名、制度名开头，也不要用抽象金句代替事件。

## Evidence and structure

Every factual section includes `claim_refs`. `metadata.section_event_refs` records the event IDs used by each section. Preserve the evidence ledger qualifier for probable, contested, and unknown material.

Use spoken Chinese. Each section should normally contain 2–4 linked event beats, and end with either the immediate consequence that starts the next section or a short landing pause. Do not add commentary merely to meet the character target; add the next verified event, location, actor, action, or consequence instead.

For full longform, target 6,750–8,640 Chinese characters and 1,500–1,920 measured narration seconds (25–32 minutes). If the draft is short, research and add verified events; never pad with repeated analysis, audience instruction, or production terminology.

Output `script` and stop for review before narration generation.

## Story body and post-story commentary

For later episodes, the full script has two clearly labeled phases:

### 故事主体

The story body runs from the opening event through the concrete resolution. It contains time, place, actors, actions, resistance, reversals, and consequences. Keep analysis subordinate to the event chain.

### 故事结局之后的独立点评

After the story has reached its ending, add a final **独立点评** section of no more than 3 minutes. Mark it explicitly in the script metadata and section label. It may discuss:

- which choice changed the direction of the story;
- what alternatives were available at that moment;
- what each side gained and lost;
- which consequences lasted beyond the ending;
- which facts are certain and which remain contested.

The commentary begins only after the story resolution. **不能穿插** commentary into the event sequence, and it must not replace missing events. The transition should make the phase change audible: `故事讲到这里，事件的结局已经明确。接下来，我们回头看……`

For a 25–32 minute episode, target at least 90% for the story body and no more than 10% for the post-story commentary. The commentary is a separate narrative function, not filler used to reach the character target.

## Failure-proofing rules

The following are hard writing rules, not optional review suggestions:

- **不能用路线复述填字数。** Mention a place or route only when a person arrives, leaves, receives an order, crosses a barrier, or causes a new consequence there.
- **一段只推进一个事件。** A section may contain setup and immediate consequence, but it must not repeat the same event in three explanatory forms.
- Do not let “案件”, “案卷”, “朝廷”, “局势”, or “情况” perform an action that belongs to a named or explicitly bounded actor.
- Evidence limits must become listener-facing factual language (for example, “不同记载说法不一”), never an instruction to the writer about what they must not invent. Move audit notes into the evidence ledger.
- Do not end a section with a second summary of the same route, case, or conclusion. End on the next pressure, action, or changed situation.
- **字数不足只能补新证据事件。** Add a verified actor, decision, place, document, confrontation, consequence, or post-story insight; never add repeated explanation, editorial padding, or production language.
- **点评不能回放故事。** The post-story section may interpret a choice, cost, uncertainty, or memory; it must not retell the whole event chain.
- Provider text must be regenerated from the final reviewed text after every revision; never leave an older payload beside a newer section body.
- Any **审稿指令** or production note in spoken text is a blocking defect, even if the surrounding history is accurate.
