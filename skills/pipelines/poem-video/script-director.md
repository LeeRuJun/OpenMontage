# Script Director — Poem Video Pipeline

## Purpose

Break the poem into a sequence of visual scenes. The poem IS the script.

## Workflow

### 1. Load the Brief + Reference Style

Load the `brief` artifact. Know the poem, the locked art style, voice,
and music direction.

**If the brief's decision_log contains a `reference_style`** (from the idea
stage's reference analysis), that IS the visual contract for every scene.
Read it and apply it uniformly:
- Reuse the reference's palette and art style in every visual_prompt
- Reuse the reference's character/living elements (the same figure, the
  same window/moon, the same density) so the poem reads as one continuous
  moment in the same world
- Match the reference's motion style (real video motion → text-to-video;
  push/pan → same camera feel)

### 2. Split the Poem into Scenes

Each line or couplet becomes one scene. A 4-line 绝句 → 4 scenes + title card + closing card = 6 segments.
A 8-line 律诗 → 8 scenes + title + closing = 10 segments.

### 3. Write Scene Descriptions

For each scene, provide:

```yaml
- scene_id: scene_01
  poetic_line: "床前明月光"
  visual_prompt: >
    Chinese ink wash painting style, moonlight streaming through
    a latticed window onto a wooden floor, a simple bed visible
    in the corner, cool blue-white light on dark wood, quiet and
    contemplative atmosphere, slow gentle zoom in
  duration_estimate: 10
  camera_hint: slow zoom in toward the moonlight on the floor
  subtitle_text: "床前明月光"
```

### Rules for Visual Prompts — TIME-SEGMENTED and RICH

**A scene must be TIME-SEGMENTED, not a static paragraph.** Sora/video models
treat a single flowing description as a still scene — that is why sparse or
single-paragraph prompts come back empty. Write the prompt as labeled time
slices, each with its own task:

```
0-2s: <establish the shot> — who is in the frame, where, what state
      (asleep / standing / head bowed), key objects, lighting, camera LOCKED
2-4s: <push the action> — one clear micro-event: the figure wakes and looks
      up, wind lifts the curtain, a leaf falls, candle flame flickers; camera
      slow push-in / pan / tilt toward the action
```

Every scene prompt MUST contain at least two slices (establish + act), and
each slice must be FULL (3-5 concrete elements), not a single object.

1. **Start with the ART STYLE — and if a reference exists, its EXACT style.**
   Open the scene prompt with a faithful description of the reference's 美术风格:
   not just "ink wash" but the actual look — 浓淡笔触 / 细线勾勒 / 青绿设色 /
   留白比例 / 纸张质感 / 色调. Record this once as the style block and reuse
   it verbatim at the start of every scene prompt so the style cannot drift.
2. **Time-slice the prompt** — "0-2s: ... 2-4s: ..." (or the clip duration).
   Slice 1 establishes, slice 2 (and 3) advances. Never a single flowing
   paragraph.
3. **Character** — who is in the frame? Specify costume (汉服/素袍), hair
   style, posture, AND what they are DOING in each slice (asleep → waking →
   looking up). A poem scene without a person reading as an empty room.
4. **Environment** — where is it? Architecture (亭台/书房/窗前/庭院), or
   landscape (远山/江面/竹林/云海). Give 2-3 concrete objects per slice.
5. **Secondary elements** — what fills the air and edges? 月亮/灯笼/烛火/
   飞鸟/落叶/雾气/雪/水波. These make the frame feel alive.
6. **Light and color** — where is the light coming from? 月光/烛光/晨光,
   and the palette (宣纸暖 / 月夜冷蓝), with deliberate 留白 (white space).
7. **One clear micro-event per action slice** — "the scholar lifts his head",
   "mist drifts across the moon", "wind stirs the curtain". Motion and event
   are mandatory; a slice with no verb is rejected.

**Target density:** 3-5 concrete visual elements per slice. A prompt that
fits on one short line is too thin — expand it.

**Maintain coherence:** same palette, same era feel, same style across ALL
scenes — reuse the character (same 素袍 scholar) and the same window/moon so
the four scenes read as one continuous moment.

### 4. Plan Transitions

Between scenes, default to:
- **dissolve** (1-1.5s) for contemplative/gentle poems
- **fade to black then fade in** for poems with distinct emotional shifts
- **hard cut** only for fast-paced/modern poems

### 5. Plan Subtitles

- Each scene shows the corresponding poetic line
- Title card: poem title + author + dynasty
- Closing card: repeat title, optional channel watermark

### Output

A `script` artifact with:
- `title`: poem title
- `author`: poet name + dynasty
- `scenes[]`: ordered list of scenes with visual prompts
- `transitions[]`: transition type between each scene
- `total_duration_estimate`: sum of scene durations

## Review Checklist

- [ ] Every poetic line has a scene
- [ ] Visual prompts are concrete and generation-ready
- [ ] Art style is consistent across all scene prompts
- [ ] Camera hints specified for each scene
- [ ] Transitions planned between scenes
- [ ] Duration estimates are realistic (8-12s per line)
