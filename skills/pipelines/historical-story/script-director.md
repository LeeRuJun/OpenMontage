# Historical Story Script Director

**REQUIRED REVIEW:** Before narration generation, run the independent `pipelines/historical-story/script-review-director` review and require `READY`.

This skill is self-contained. Do not load any other writing, research, or architecture skill while drafting prose.

You are writing for a listener with earphones, not for a reviewer with a checklist. Every sentence must earn its place by advancing time, place, action, or consequence.

## Core writing rules

- **One sentence, one job.** A sentence either advances the event, shows a person acting, or delivers a consequence. Test: delete it — if the story loses nothing, delete it for real.
- **Say it once.** The same idea may appear exactly once in the entire script. Restating it in different words is repetition, not emphasis.
- **No self-description.** The narration never describes its own method, sources, boundaries, or structure. That information lives in the evidence ledger, never in spoken text.
- **No bracket instructions.** Anything like "（温和、克制……）" is a direction to the voice actor, not narration. Put it in `delivery_cues`, never in `text`.

## Anti-pattern: research voice vs. story voice

The most common failure is writing like a research summary instead of a story:

**WRONG (research voice — never do this):**
> 事实记录、政治解释和后世记忆属于不同层次。事实记录提供时间、地点、人物行动与结果；政治解释说明弹劾者怎样理解文字。证据边界保留。异文仍按来源保留。记忆与案卷分开。各有边界。事实与解释分开。

**RIGHT (story voice):**
> 同一句诗，苏轼写下它的时候是一个意思，御史读出来变成了另一个意思，后人记住的又是第三个意思。这场案子最可怕的地方就在这里：文字本身没有变，变的是读它的人手里的权力。

**WRONG:**
> 事件顺序由年谱与地方志共同提供。押送从湖州开始，终点是京城。案件从捕人行动进入押送程序。

**RIGHT:**
> 七月二十八日，苏轼在湖州被捕。押送的队伍向北走了一个多月，八月十八日，他走进的是御史台的监狱。

**WRONG:**
> 多份材料较稳定记载苏轼免于死刑并被贬黄州；供状措辞、牵连范围仍有异文。稳定结果与差异细节各自保留。

**RIGHT:**
> 苏轼没有死。那年年底，他活着走出了御史台，但去的不是家，是黄州。监狱里那几个月他到底被问了什么，留下来的记录说法不一，但结局没有争议：他保住了命，丢掉了官位。

## How to handle uncertainty

When sources disagree, do not describe the evidence management. Weave the uncertainty into the story naturally:

- "关于那晚的细节，留下的记载并不一致。"
- "有材料说他做了什么，也有材料说没有。"
- "具体人数，现在已难以确认。"

Never: "异文按来源保留""证据边界""certainty为probable""claim_refs" — these are internal bookkeeping.

## Commentary writing (the final 1–3 minutes)

**SUB-SKILL for the post-story commentary only:** Read `skills/creative/historical-commentary-craft.md`. It holds the five-scale evaluation framework (个人/国家/时代/文化/历史走向), the three-move commentary skeleton (钉死与飘着 → 翻转 → 落在人与物), the closing-line test, the self-check prompt, and the anti-patterns distilled from 易中天/王立群/罗振宇/当年明月. Do not load it while drafting the story body — it governs only the closing evaluation.

The commentary is what you would tell a friend after the movie, not a research conclusion. One stance, 1–2 scales, one quotable line grown from narrated facts, opening on a concrete thing and closing the opening loop. Write it as natural spoken opinion: one idea, one paragraph, said once.

## What fills length (and what never does)

When the script is short, add verified events: a person arriving, a document sent, a wall repaired, a prisoner moved, a sentence passed. Never add:
- Restatements of themes or routes
- Abstract analysis of institutions or processes
- "This shows that..." commentary in the story body
- Research metadata or source descriptions

## Scene contract before prose

For every section, record starting state, immediate objective, resistance, attempt, reversal or discovery, consequence, and the question that forces the next section. The event card supplies the historical fields; the scene contract supplies the causal fields. A section cannot be lengthened with commentary when one of these fields is empty.

## Event-first writing

Every narration section must be built from events. Fill an event card with time, place, actors, action, resistance, consequence, and claim_refs before writing prose. Every factual section includes `claim_refs`. `metadata.section_event_refs` records the event IDs used by each section.

## Prose contract

- 用叙事动词：到达、下令、起兵、围攻、撤退、渡河、打开城门、接管、处置、改年号。
- 让地点推动剧情：命令从哪里发出，军队沿什么道路移动，哪座城/哪条河改变了选择。
- 不虚构对白、心理独白、未被证实的战术细节或确定的争议结论。
- 不把后世评价写成当时人物已经知道的动机。
- 台词里不能出现 montage、蒙太奇或任何制作术语。

## Failure-proofing rules

- **不能用路线复述填字数。** Mention a place or route only when a person arrives, leaves, receives an order, crosses a barrier, or causes a new consequence there.
- **一段只推进一个事件。** A section may contain setup and immediate consequence, but it must not repeat the same event in three explanatory forms.
- Do not let "案件", "案卷", "朝廷", "局势", or "情况" perform an action that belongs to a named or explicitly bounded actor.
- Evidence limits must become listener-facing factual language (for example, "不同记载说法不一"), never an instruction to the writer about what they must not invent.
- Do not end a section with a second summary of the same route, case, or conclusion. End on the next pressure, action, or changed situation.
- **字数不足只能补新证据事件。** Add a verified actor, decision, place, document, confrontation, consequence, or post-story insight; never add repeated explanation, editorial padding, or production language.
- **点评不能回放故事。** The post-story section may interpret a choice, cost, uncertainty, or memory; it must not retell the whole event chain.
- Provider text must be regenerated from the final reviewed text after every revision; never leave an older payload beside a newer section body.
- Any **审稿指令** or production note in spoken text is a blocking defect, even if the surrounding history is accurate.

## Story body and post-story commentary

For later episodes, the full script has two clearly labeled phases:

### 故事主体

The story body runs from the opening event through the concrete resolution. It contains time, place, actors, actions, resistance, reversals, and consequences. Keep analysis subordinate to the event chain.

### 故事结局之后的独立点评

After the story has reached its ending, add a final **独立点评** section of no more than 3 minutes. Mark it explicitly in the script metadata and section label. It may discuss which choice changed the direction of the story, what alternatives were available at that moment, what each side gained and lost, which consequences lasted beyond the ending, and which facts are certain and which remain contested.

The commentary begins only after the story resolution. **不能穿插** commentary into the event sequence, and it must not replace missing events. The transition should make the phase change audible.

For a 22–27 minute episode, target at least 90% for the story body and no more than 10% for the post-story commentary. The commentary is a separate narrative function, not filler used to reach the character target.

## Required inputs before prose

The script writer consumes the approved `material_density_map` and `scene_contracts`; **不要临时改变故事结构** while drafting. Every final section must preserve its event refs and clean `provider_text`.

Read `research_brief`, `historical_evidence_ledger`, `story_spine.metadata.event_story`, and the approved `material_density_map` before drafting. **不要在素材地图完成前写正文。** If the event inventory is short, return to research; do not fill the target with commentary or repeated background.

## Opening contract — hook before detail

Full and pilot episodes都先有 20–30 秒开场，但开场也必须包含事件或具体危险：固定品牌开场、说清时代人物冲突、提出具体问题、预告路线、立刻进入第一个时间地点人物行动。

## Length contract

For full longform, target 5,940–7,290 Chinese characters and 1,320–1,620 measured narration seconds (22–27 minutes). If the draft is short, research and add verified events; never pad with repeated analysis, audience instruction, or production terminology.

**Overshoot-then-trim strategy (binding):**

1. **Research fat before writing long.** The ledger must hold roughly 1.5× the claims you expect to narrate — specific poems with lines, named actors, dated actions, consequences. A thin ledger cannot be stretched into a dense script; it can only be padded into research voice.
2. **Write past the target, then cut.** Draft to about 110–120% of the character target with only verified material. Character estimates run 15–25% optimistic — the v3→v6 lesson: estimated 5000, delivered 3369. Do not aim at the number; aim above it.
3. **Cut the weakest material, never the strongest.** Trimming order: background that repeats what the event chain already shows → commentary that re-explains a narrated fact → a second example where one suffices → scene-setting that adds no new action. Never cut: the specific poem line, the named person, the dated action, the consequence that forces the next event.
4. **Density plan before drafting.** Mark each section 细写 (case core: quote the poem, name the person, walk the action), 粗写 (background: one sentence, move on), or 拓展 (newly researched material worth a beat of its own). The plan decides where characters go — not the character target.
5. **Measure after every pass.** Run the deterministic gates after each rewrite; adjust by measured numbers, not by feel.

Output `script` and stop for review before narration generation.
