# Proposal Director — Book Comic Explainer Pipeline

## When to Use

You sit between research and script. You receive a `research_brief` with book content, characters, and at least 3 angles. Your job is to present the angles, production plan, and cost estimate—and get explicit user approval before any creative work begins.

**This is THE approval gate.** Nothing downstream runs until the user locks the angle.

## The Golden Rule

> The angle IS the creative. A bad angle properly executed is still a bad video. A great angle with mediocre execution is still worth watching.

The proposal stage exists to lock the angle. Everything else flows from it.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Prior artifact | `research_brief` | Book content, characters, angles |
| Channel config | `shared_assets/channel_seinen_manga/channel.yaml` | Voice profile, visual style |
| Pipeline manifest | `pipeline_defs/book-comic-explainer.yaml` | Stage definitions, budget |

## Process

### Step 1: Absorb the Research

Read the `research_brief` thoroughly. Key fields:
- `book_classification` — story / idea / hybrid
- `core_content` — characters and scenes, or frameworks and metaphors
- `angles_discovered` — the raw material

### Step 2: Polish and Present the Angles

Take the 3+ angles from research and sharpen each into a clear pitch:

```yaml
angle_a:
  title: "当主角不是享荣光，是扛罪"
  hook: "你们看到的，是她的光。你们看不到的，是她扛的罪。"
  type: "character_lens"
  why_it_works: "书的核心矛盾在忆秦娥身上——她一辈子在台上当主角，但她从来没选过"
  visual_approach: "从最痛苦的瞬间倒叙，每一帧都是重量"

angle_b:
  title: "她叫招弟"
  hook: "一个不该有名字的人，最后所有人都记住了她的名字"
  type: "identity_lens"
  why_it_works: "名字是身份，从招弟到忆秦娥，她从未拥有过自己的名字"
  visual_approach: "名字的变迁作为视觉线索贯穿"

angle_c:
  title: "台下没有观众"
  hook: "戏剧让观众只看到前台。但真正的主角在台下"
  type: "behind_the_scenes"
  why_it_works: "对比台上光芒和台下代价"
  visual_approach: "从后台看前台——所有的光芒背后都是血"
```

### Step 3: Recommend, Don't Dictate

Present all angles with:
- One-sentence hook that would stop a scroller
- Visual approach (what the viewer SEES)
- Why this angle over the others

Mark your recommendation. Explain why. Then **wait for user choice.**

### Step 4: Build the Production Plan

After angle is chosen, produce a plan:

```yaml
production_plan:
  duration_target: "3-4 minutes (Act 1 of 4)"
  total_duration: "12-18 minutes (4 acts)"
  frames_per_act: "25-35"
  total_frames: "100-140"
  narration_style: "single narrator, mature female voice"
  scene_count: "5-7 (3-4 reused from shared_assets, 2-4 new)"
  cover_sizes: ["bilibili", "douyin"]
  
cost_estimate:
  frames: "$18-28 (GPT Image 2 high quality)"
  narration: "$1-3 (MiniMax TTS)"
  total: "$20-32"
```

### Step 5: Record the Angle Decision

Write `decision_log`:
```json
{
  "category": "angle_selection",
  "subject": "Book comic angle",
  "selected": "当主角不是享荣光，是扛罪",
  "options_considered": ["angle_a", "angle_b", "angle_c"],
  "reason": "最锋利，书的核心矛盾在角儿不是选的是扛的"
}
```

### Step 6: Assemble Proposal Packet

Output `proposal_packet` and `decision_log`. Validate against schema.

## Gate Reminder (Binding)

This stage gates on human approval. Write checkpoint as `awaiting_human`, present the angles + production plan + cost, and **END YOUR TURN**. Do not write script until angle is approved.

## Quality Checklist

- [ ] At least 3 polished angles presented
- [ ] Each angle has: title, hook, visual approach, why it works
- [ ] Recommended angle marked with rationale
- [ ] Production plan reflects actual tool availability
- [ ] Cost estimate is itemized and honest
- [ ] Angle decision recorded in decision_log
- [ ] User explicitly chose the angle

## Generic Knowledge-Book Mode

When `book_profile` is present, proposal must also produce `delivery_strategy`.
The strategy decides how the book is explained, not just which chapter is summarized.
Choose one: `reframing_explainer`, `one_big_idea`, `problem_solution`, `case_study`,
`concept_ladder`, `character_arc`, `debate_compare`, or `practical_playbook`.

Record the core promise, audience problem, hook, viewer question, progression,
summary/interpretation/example ratios, pacing, and ending takeaway. Ratios must sum
to 1.0. Present the angle and delivery strategy together at the approval gate.
