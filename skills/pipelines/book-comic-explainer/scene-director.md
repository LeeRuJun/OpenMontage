# Scene Design + Art Style Director — Book Comic Explainer Pipeline

## When to Use

You receive the `script` and `character_design`. Your job is to lock the visual world — art style and scene locations — before any image is generated. Characters are already designed. Now you define WHERE the story takes place and WHAT it looks like.

**Scene design and art style are locked together.** The mood of a room and the color of the sky are art direction decisions that affect every frame. Do them in one stage.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Prior artifact | `script` | All scene locations, era, mood, time of day |
| Prior artifact | `character_design` | Character visual style to match |
| Channel config | `shared_assets/channel_seinen_manga/channel.yaml` | Base palette, style references |
| Shared assets | `shared_assets/channel_seinen_manga/scenes/` | Existing scene backgrounds |
| Reference | `character_design.art_style` (if present) | May already have era/mood hints |

## Process

### Step 1: Lock the Art Style

Read `shared_assets/channel_seinen_manga/channel.yaml`. Read `script` for era, mood, locations. Read `character_design` to ensure visual consistency. Produce the definitive `art_style`:

```yaml
art_style:
  base: "日系青年漫画 — 粗线条勾线，低饱和度配色，大面积平涂阴影"
  references: ["贰瓶勉", "沙村广明"]

  episode:
    era: "1970s-2000s 中国"
    mood: "压抑但富有诗意"
    color_arc: "暖黄→冷蓝"             # ← Act 1 warm → Act 4 cold
    lighting: "永远侧光或底光。不用正面平光。"
    time_spans: ["1976年秦岭", "1980s县城", "1990s省城", "2000s"]

  constraints:
    - "画面中不要出现任何文字、字母、数字或标志。"
    - "不要出现：Q版、可爱风、大眼睛、日系萌系、少年漫、热血、科幻发光效果。"

  # Prepend to EVERY image prompt in all downstream stages:
  prompt_prefix: "日系青年漫画风格。粗线条勾线，低饱和度配色，大面积平涂阴影。{era}年代的中国。{mood}。{lighting}。风格参考：贰瓶勉、沙村广明。"
```

### Step 2: Inventory Script Locations

Walk every section of the script. Extract every unique location:

```
script → locations:
  灶房 (night, interior)
  秦岭山坡 (day, exterior)
  剧团练功房 (day, interior)
  县城街道 (day, exterior)
  后台化妆间 (night, interior)
  剧场舞台 (night, interior)
  ...
```

Group duplicates. Note time of day and season for each occurrence — the same location at different times may need different background images.

### Step 3: Match Against Shared Assets

Check `shared_assets/channel_seinen_manga/scenes/` for existing backgrounds. For each location:

```yaml
scenes:
  - id: "qinling_village"
    locations_used: ["秦岭山坡", "山间土路"]
    source: "generate"           # ← no match in shared_assets
    time: "day / exterior"
    prompt: |
      秦岭深处的山谷。晨雾缠山腰。山坡上土坯房夯土墙灰瓦。
      炊烟从一户人家升起。天上鹰在盘旋。初秋草已泛黄。苍凉广阔。
      1970年代的中国农村。没有现代建筑，没有电线杆。

  - id: "office"
    locations_used: ["工头办公室", "省剧团办公室"]
    source: "shared_assets"      # ← reuse
    path: "shared_assets/channel_seinen_manga/scenes/office/bg_day.png"

  - id: "rehearsal_room"
    locations_used: ["县剧团练功房", "省剧团排练厅"]
    source: "generate"
    time: "day / interior"
    prompt: |
      老式练功房。木地板磨得发亮。一整面墙的大镜子有划痕。
      墙边木质把杆。高窗透自然光投方形光斑在地板上。
      1980年代中国剧团。空气中有汗水松香味道。
```

### Step 4: Scene Prompt Construction Rules

Every new scene prompt MUST include:
1. Art style prefix + era + mood + lighting (from art_style)
2. The location description (specific, visual, atmospheric)
3. Time of day and season (affects lighting dramatically)
4. Era-appropriate details (architecture, objects, technology)
5. Style constraints ("不要出现任何文字..." etc.)

### Step 5: Self-Evaluate

Score the scene design (1-5):

| Criterion | Question |
|-----------|----------|
| **Coverage** | Does every script location have a scene assigned? |
| **Reuse first** | Did you check shared_assets before marking scenes as "generate"? |
| **Era accuracy** | Are objects, architecture, clothing cues era-appropriate? |
| **Mood consistency** | Do all scenes share the same emotional palette from art_style? |
| **Character compatibility** | Will the character designs work in these scenes? (scale, lighting, style) |
| **Prompt readiness** | Can every new scene prompt be passed directly to image_selector? |

If any dimension scores below 3, revise before submitting.

## Common Pitfalls

| Pitfall | Why it happens | How to fix |
|---------|---------------|------------|
| Forgetting time of day | Only describing the room, not the light | Every scene needs: time of day, light source, light quality |
| Era anachronisms | Not specifying the decade | "中国县城" ≠ 1970s. Specify era in every prompt. |
| Generating scenes that exist | Not checking shared_assets first | Always check `shared_assets/channel_seinen_manga/scenes/` first |
| Art style inconsistency | Forgetting to prepend prompt_prefix | The art_style.prompt_prefix goes on EVERY scene prompt. No exceptions. |

## When You Don't Know How

If you're uncertain about a location's visual reference:
- Use `web_search` to find images of real locations from that era
- Read the book's descriptions of places — authors embed visual details
- Check art style references (贰瓶勉, 沙村广明) for how they handle similar settings
- Log in decision log: `category="scene_reference_research"`

## Gate Reminder (Binding)

This stage gates on human approval (`human_approval_default: true`). After review passes:
checkpoint with `status="awaiting_human"`, present the art style + scene list (with
reuse/generate decisions and prompts), and **END YOUR TURN**. Do not start the next
stage in the same response. Approval is per-gate — an earlier "go ahead" does not
cover this gate.
