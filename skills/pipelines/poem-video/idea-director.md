# Idea Director — Poem Video Pipeline

## Purpose

Understand the poem, propose visual directions, and lock creative decisions
before any assets are generated.

## Workflow

### 1. Receive the Poem

The user provides a poem. It may be:
- A complete classical poem (Tang/宋/其他)
- A single line or couplet
- A modern Chinese poem
- A poem with a specific visual request ("水墨风格", "像王家卫那样", etc.)

### 2. Research the Poem

Understand:
- **Author and dynasty** — context shapes the visual language
- **Imagery** — what does the poet describe visually? (mountains, rivers, moon, flowers, wine, rain, etc.)
- **Emotional arc** — joyful, melancholy, longing, awe, tranquility?
- **Structure** — how many lines/couplets? Where are the emotional peaks?
- **Famous allusions** — any historical or literary references that should be visually hinted at?

### 2b. LEARN THE REFERENCE VIDEO (mandatory when one exists)

**If a reference video was provided** — a local file in `reference_videos/`, a
URL, or "make it like this" — you MUST analyze it BEFORE proposing any
visual direction. This is the `video-reference-analyst` protocol
(`skills/meta/video-reference-analyst.md`). It is NOT optional, and it is
NOT satisfied by "glancing at it." Run the analysis:

```python
video_analyzer.execute({
    "source": "<reference path or url>",
    "analysis_depth": "standard",
    "max_keyframes": 20
})
```

From the resulting VideoAnalysisBrief, lift the fields that matter for a
poetry video and record them in the `decision_log` as `reference_style`:

- **Style**: ink wash / gongbi / blue-green / anime — from what the reference
  actually shows, not from a menu
- **Color palette**: the actual dominant colors extracted from keyframes
- **Structure**: how the reference paces scenes (X scenes over Y seconds,
  title card length, transitions)
- **Motion type**: `motion_clip` (真视频) vs `animated_still` (静帧+推拉) vs
  `static_image`. This DECIDES whether you plan around text-to-video or
  image+Ken Burns. If the reference uses real video, text-to-video is the
  only acceptable path.
- **Character/living elements**: does it have people, animals, weather,
  particles? Copy the *density* of the reference (a full frame with a
  person + environment + atmosphere), not its literal content.
- **Camera**: how shots move (slow push / pan / tilt / static)

**Rules:**
- The reference's STYLE flows into the script prompts verbatim (shared
  character, shared palette, same visual language across all scenes).
- Do NOT copy the reference's content literally — absorb its style and
  density, apply it to THIS poem's imagery.
- If no reference video exists, skip this step and note "no reference"
  in the decision_log.

**Where the reference file lives:** the user drops reference videos into
`reference_videos/`. Check that folder at the start of every run.

### 3. Present Visual Directions

Offer 2-3 visual directions, each with:
1. **Art style** (水墨 / 工笔 / 青绿山水 / 素描线稿 / 动漫国风)
2. **Color palette** — dominant colors and mood
3. **Voice direction** — 朗诵 style, pace
4. **Music direction** — instruments and emotional register
5. **Target duration** — based on poem length (1 line ≈ 8-12 seconds, 4-line poem ≈ 30-50 seconds)

### 4. Lock Decisions

Record in `decision_log`:
- `art_style`: the chosen visual style
- `voice_selection`: TTS provider and voice
- `music_direction`: mood and instruments
- `target_duration`: estimated video length
- `aspect_ratio`: 9:16 vertical (default) or 16:9 horizontal

### 5. Produce Brief

Output a `brief` artifact containing the poem, its analysis, and all locked
creative decisions. This becomes the contract for the script stage.

## Review Checklist

- [ ] Poem correctly interpreted (author, dynasty, imagery, emotion)
- [ ] At least 2 visual directions presented
- [ ] **If a reference video exists: it was analyzed (video-reference-analyst protocol) and its 美术风格/调色/结构/运动 extracted into `decision_log.reference_style`**
- [ ] Art style locked and appropriate for the poem's era and mood
- [ ] **Art style matches the reference's actual look when a reference exists**
- [ ] Voice direction chosen (specific voice + speed)
- [ ] Music mood selected
- [ ] Target duration is realistic
