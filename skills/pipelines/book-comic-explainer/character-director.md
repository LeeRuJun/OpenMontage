# Character Design Director — Book Comic Explainer Pipeline

## When to Use

You receive the `script` and `research_brief`. Your job is to design the characters — and only the characters. Scene design and art style are handled by the next stage (`scene_design`).

**Every character needs an anchored appearance description** that gets pasted verbatim into every image prompt downstream. If the appearance changes, the character won't look like the same person across frames. The appearance block IS the character contract.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Schema | `schemas/artifacts/character_design.schema.json` | Artifact validation |
| Prior artifact | `script` | Characters referenced, their actions, age spans |
| Prior artifact | `research_brief` | Character traits, book context |
| Channel config | `shared_assets/channel_seinen_manga/channel.yaml` | Base style references |

## Process

### Step 1: Inventory Characters from the Script

Walk every section of the script. Collect every character that appears. For each, note:
- Name, role, type (protagonist / antagonist / supporting / explainer)
- Age span(s) — characters may appear at different ages across the story
- Personality — defines how they stand, move, and hold their face
- Relationship to other characters

### Step 2: Design Each Character — Anchored Appearance

For each character, write the appearance description. This is the single source of truth that every storyboard prompt will copy verbatim:

```yaml
characters:
  - id: "zhaodi"
    name: "招弟 / 易青娥 / 忆秦娥"
    type: "protagonist"
    age_spans: ["11岁", "20-35岁", "50-60岁"]

    appearance_young: |
      11岁的瘦小女孩。头发乱蓬蓬，扎两根细麻花辫，发梢干枯分叉。
      脸上有泥，嘴唇干裂。眼睛很大但眼神是空的 — 不是天真，是没见过世界的茫然。
      穿洗得发白的碎花布衫，袖子短了半截露出细瘦手腕。赤脚。脚上有旧泥。
      山里孩子，骨骼细小结实。

    appearance_young_adult: |
      20多岁的年轻女性。身材瘦，窄肩，腰背笔直 — 练功练进了骨头里。
      长发盘成髻，用木簪固定。脸型瘦长，颧骨略高。皮肤因长期化妆略显粗糙。
      眼睛锐利专注，但眼底有疲惫。穿素色练功服。手指细长有力，指尖有茧。
      脚踝隐约有旧伤疤。

    appearance_middle: |
      60岁左右的女性。花白短发，梳得一丝不苟。瘦，窄肩，腰背仍然直。
      眼角有深刻皱纹像刀刻。嘴唇紧抿。眼神平视前方 — 平静但有力，像看透了一切。
      穿素色中式对襟上衣。手上有老茧。

    personality: "沉默、能忍、什么都不会说但什么都在看"
    silhouette: "窄肩，腰背永远笔直 — 任何年龄，从背后一眼认出"

  - id: "hu_sanyuan"
    name: "胡三元"
    type: "supporting"
    role: "舅舅 — 打鼓的，把她带出山的人"

    appearance: |
      粗壮中年男性，40岁左右。短发硬得像刷子，鬓角灰白。
      方脸，皮肤黝黑粗糙，眉头总是皱着。
      胳膊粗壮，指节粗大，虎口有老茧 — 打鼓的手。
      穿褪色蓝色工装外套，肩膀处磨得发白。
      背上背一面用旧布裹着的鼓。
      表情凶狠，但眼睛里藏着愧疚。

    personality: "暴烈、固执、一辈子都在补偿那个下午"
    silhouette: "粗壮，背鼓，永远微驼"
```

**Appearance rules:**
- Be specific enough to draw from: "蓝色工装衬衫，领口有汗渍" not "普通衣服"
- Be stable: describe things that don't change between frames (bone structure, scars, build)
- Define the silhouette: one feature that makes the character recognizable at any angle
- Be style-safe: work in seinen manga line art — no photorealistic details
- For characters at multiple ages: write a separate appearance block per age span
- For idea/nonfiction books: create 2-3 explainer characters. Their appearance should telegraph their worldview.

### Step 3: Validate Character Distinctness

Before submitting, check:
- Every character referenced in the script has an appearance block
- Appearance descriptions are copy-paste ready (no placeholders like "普通长相")
- No two characters look too similar (different body types, face shapes, silhouettes)
- Every character has one distinctive feature that identifies them in any frame
- Multi-age characters have appearance blocks for each age span used in the script

### Step 4: Self-Evaluate

Score the character design (1-5):

| Criterion | Question |
|-----------|----------|
| **Specificity** | Could an artist draw each character from the description alone? |
| **Stability** | Are the anchored traits (bone structure, build, scars) stable across frames? |
| **Distinctness** | If all characters were silhouettes, could you tell them apart? |
| **Copy-paste ready** | Can every appearance block be pasted verbatim into a prompt? |
| **Style compatibility** | Do all characters work in seinen manga (not anime, not photorealistic)? |
| **Script coverage** | Does every character in the script have a design? |

If any dimension scores below 3, revise before submitting.

## Common Pitfalls

| Pitfall | Why it happens | How to fix |
|---------|---------------|------------|
| Vague appearance | Writing "普通中国女性" | Describe specific hair, face shape, clothing, one distinctive feature |
| Style mismatch | Character works for anime but not seinen manga | Check references. No big eyes, no cute, no sparkly hair. |
| Same-face syndrome | All characters have similar builds and faces | Force different body types, face shapes, ages, postures |
| Copy-paste not ready | Appearance has placeholders or options ("短发或长发") | Finalize. One answer per trait. |
| Missing age span | Character appears at 11 and 35 but only one appearance | Check script for all ages. One block per age span. |

## When You Don't Know How

If you're uncertain about a character's visual reference:
- Use `web_search` to find descriptions or adaptations of the book's characters
- Read the book's own descriptions — authors include specific physical details
- Check the art style references (贰瓶勉, 沙村广明) for character design language
- Log in decision log: `category="character_reference_research"`

## Gate Reminder (Binding)

This stage gates on human approval (`human_approval_default: true`). After review passes:
checkpoint with `status="awaiting_human"`, present the character designs (all characters
with appearance blocks), and **END YOUR TURN**. Do not start the next stage in the same
response. Approval is per-gate — an earlier "go ahead" does not cover this gate.
