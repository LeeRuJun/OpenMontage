# Poem Video — Chinese Poetry Short Video Guide

Use this Layer 2 skill when OpenMontage produces a short-form poetry video,
especially for the 国风+古诗词 AI video format popular on Douyin, Xiaohongshu,
and WeChat Channels.

This is not a literature lecture. The goal is to turn a classical Chinese poem
into a visually stunning, emotionally resonant short video that the viewer
wants to watch — and share.

## When to Use

Use when the user asks for:

- 诗词视频 / 古诗视频 / 唐诗宋词视频
- 国风视频 / 古风短视频
- "把这首诗做成视频"
- A Chinese poem turned into a visual experience

## Core Promise

> 让一首诗看得见，听得懂，感受到。

Don't analyze the poem academically. Visualize it faithfully, respect its
emotional core, and let the viewer feel what the poet felt.

## Content Architecture

For poetry videos, structure is determined by the poem itself:

1. **Title card** — Poem title + author + dynasty, styled as 国风 calligraphy
2. **Scene per couplet / line** — Each line or couplet becomes one visual scene
3. **Closing card** — Repeat title, add channel/watermark if needed

The poem IS the script. Each line dictates what the viewer sees.

## Art Styles

Present these options at the idea stage. The user picks one.

### 水墨 (Ink Wash)
- Black ink on rice paper texture
- Misty mountains, flowing water, bamboo, lone figures
- Subtle gradients, negative space is deliberate
- Best for: Tang poetry, landscape poems, contemplative works

### 工笔 (Gongbi — Fine Brush)
- Detailed line work, flat rich colors
- Flowers, birds, court ladies, palace scenes
- Clean, precise, decorative
- Best for: Song dynasty 词, romantic poems, nature imagery

### 青绿山水 (Blue-Green Landscape)
- Mineral blue and green palette
- Mountains, rivers, cloud layers
- Bright, vibrant, almost jewel-like
- Best for: Grand landscape poems, Li Bai, Wang Wei

### 素描线稿 (Sketch / Line Art)
- Minimalist ink lines, parchment background
- Suggestive rather than detailed
- Black/white or sepia tone
- Best for: Philosophical poems, 道家/禅意 content

### 动漫国风 (Anime Guofeng)
- Modern anime style with Chinese costume and architecture
- Dynamic compositions, saturated colors
- Character-driven scenes
- Best for: Narrative poems, 长恨歌-style storytelling

## Voice Direction

Poetry narration needs to honor the meter and rhythm of the original.

### 朗诵 (Recitation) — Default
```yaml
provider: minimax
voice_id: Chinese (Mandarin)_Gentle_Senior
speed: 0.85
# Slow, deliberate, with natural pauses between lines
```

### 吟诵 (Chanting) — For Tang poetry
```yaml
speed: 0.75
# Slower, more drawn-out syllables
```

### 清亮 (Clear and Bright) — For 词/Song dynasty
```yaml
voice_id: Chinese (Mandarin)_Clear_Bright
speed: 0.90
```

### Modern Narration — For modern translations
```yaml
voice_id: Chinese (Mandarin)_Reliable_Executive
speed: 0.92
# Natural speaking pace for白话解读
```

Rules:
- Always generate a sample first (first 2 lines only)
- Batch only after user approves the voice
- Add 1-2 second silence between lines for breathing room
- The pause between couplets should be longer than pauses within couplets

## Text-to-Video Prompting

Each scene's visual prompt should be concrete and generation-ready.

### Prompt Formula

```
[Art style], [Subject and composition], [Color palette and mood],
[Camera movement], [Lighting], [Atmosphere]
```

### Examples

```
Chinese ink wash painting style, a solitary fisherman in a small boat
on a misty lake at dawn, distant mountains fading into fog, black ink
on cream paper texture, subtle ripples on water, quiet and contemplative,
slow upward camera tilt

Chinese blue-green landscape style, towering green mountains rising
from clouds, waterfall cascading between peaks, golden morning light
breaking through mist, pine trees clinging to cliffs, majestic and
awe-inspiring, slow horizontal pan
```

### Rules

- Keep the art style consistent across ALL scenes — don't switch styles mid-poem
- Include camera movement hints: "slow pan right", "gentle zoom in", etc.
- Avoid complex multi-subject compositions that confuse video models
- One visual idea per prompt — don't cram multiple concepts together

## Music Selection

Music must match the poem's mood, not fight it.

| Poem Mood | Music Style | Instruments |
|---|---|---|
| 壮阔 (majestic) | Slow orchestral, building | 古筝 + strings + drums |
| 婉约 (delicate) | Soft ambient, minimal | 琵琶 or 古琴 solo |
| 思乡 (nostalgic) | Melancholic, gentle | 笛子 + ambient pad |
| 豪放 (bold) | Rhythmic, driving | 古筝 + percussion |
| 禅意 (zen) | Very sparse, ambient | Single instrument + reverb |

Rule: music volume should sit at -18 to -22 dB LUFS, duck to -30 dB under narration.

## Subtitle Styling

### On-screen poem text (primary)
- Large, calligraphic style (use a 楷体 or 行楷 font)
- Appears character by character or line by line, synced to narration
- Position: center or upper-third of frame
- Color: white or gold on dark backgrounds, black on light backgrounds

### Modern translation (secondary, optional)
- Smaller, sans-serif font
- Position: bottom quarter, above the music credit if any
- Appears after the classical line has been read

### Title card text
- Poem title: large, 楷体, centered
- Author + dynasty: smaller, below title
- Decorative frame or ink-brush border encouraged

## Quality Checklist

Before presenting the video as ready:

- [ ] Title card shows poem name and author correctly
- [ ] Each scene visually matches its poetic line
- [ ] Art style is consistent from first scene to last
- [ ] Narration pace respects the poem's meter
- [ ] Music matches the emotional arc and ducks during narration
- [ ] Subtitles are readable and styled for vertical video
- [ ] Closing card leaves a lasting impression
- [ ] Output is 1080×1920 vertical (or user's chosen format)
- [ ] Complete poem is narrated — no missing lines

## Common Failures

- Art style switching between scenes (水墨 in scene 1, 动漫 in scene 3)
- Narration too fast — poetry needs breathing room
- Music overpowering the narration
- Scene descriptions that are too abstract for video models
- Subtitles that cover the visual focal point
- Title card missing poem title or author
- Using modern anime style for a meditative Tang poem (or vice versa)
