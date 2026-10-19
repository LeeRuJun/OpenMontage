# Asset Director — Book Comic Explainer Pipeline

## When to Use

You receive `character_design`, `scene_list`, `art_style`, and `storyboard_spec`. Narration is already recorded. Your job: generate character art and scene backgrounds. No voice work — that was done in the narration stage.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Schema | `schemas/artifacts/asset_manifest.schema.json` | Artifact validation |
| Prior artifacts | `character_design`, `scene_list`, `art_style`, `storyboard_spec` | What to generate |
| Channel config | `shared_assets/channel_seinen_manga/channel.yaml` | Style, palette |
| Tools | `image_selector`, `music_gen` | Generation |
| Cover tool | `tools/graphics/cover_compositor.py` | Cover compositing |

## Style Specification (READ FIRST)

Load `shared_assets/channel_seinen_manga/channel.yaml`. All generated images must follow:

```
Style: seinen manga (日系青年漫画)
Line: 粗线条勾线
Color: 低饱和度配色，平涂阴影
Mood: 暗调高级感，气氛压抑但富有诗意
Reference: 贰瓶勉、沙村广明、林田球
Constraint: 画面中不要出现任何文字、字母、数字或标志
```

## Process

### Step 1: Generate Scene Backgrounds

For each scene in `scene_list`:

- **source: "shared_assets"** → skip, file already exists
- **source: "generate"** → use `image_selector` with the scene's prompt + style anchors

```python
# Prompt construction
prompt = f"{scene['prompt']}\n{STYLE_ANCHORS}"
# STYLE_ANCHORS = "日系青年漫画风格。粗线条勾线，低饱和度配色，平涂阴影。暗调高级感。画面中不要出现任何文字、字母、数字或标志。"
```

Save to: `projects/<project>/assets/scenes/<scene_id>.png`

### Step 2: Generate Character Art

For each character in `character_design`:

Generate a **character reference sheet** (not a scene frame — just the character):

```
Prompt: {STYLE_ANCHORS}
角色设计参考图。
{character.appearance 全文}。
{character.personality}。
全身站立姿势，纯浅灰背景，角色居中。
风格参考：沙村广明的角色设计。
画面中不要出现任何文字、字母或数字。
```

Save to: `projects/<project>/assets/characters/<character_id>_ref.png`

**Sample first.** Generate one character, show the user. Confirm style before generating the rest.

### Step 3: Generate Narration Audio

Use `tts_selector`. Read the channel voice profile from `channel.yaml`:

```yaml
voice:
  provider: minimax
  model: speech-2.8-hd
  voice_id: "Chinese (Mandarin)_Reliable_Executive"
  speed: 0.92
```

For each script section:
1. Extract text + delivery_cues
2. Generate audio via `tts_selector`
3. Verify duration matches section timing (±15%)

Save to: `projects/<project>/assets/audio/narration_<section_id>.mp3`

**Sample first.** Generate 10-15 seconds, let user approve voice, then batch.

### Step 4: Music (if available)

Check `music_gen` or `music_library/`. Generate or select a background track that fits the book's tone.

For idea/nonfiction books: subtle, atmospheric, not distracting.
For story/novel books: can carry more emotional weight.

### Step 5: Generate Cover Base Image

Use `build_cover_prompt()` from `cover_compositor.py`. The topic should be the book's central visual metaphor from research.

Then use `cover_compositor` to overlay hook text + book title:

```python
from tools.graphics.cover_compositor import CoverCompositor, build_cover_prompt, load_channel_config

channel = load_channel_config()
prompt = build_cover_prompt("一架天平，左边是规则右边是权力，天平倾斜")

# Generate base image with openai_image
# Then composite:
CoverCompositor().execute({
    'base_image_path': 'projects/<project>/assets/cover_base.png',
    'hook_text': '强者相信权力\n弱者相信规则',
    'book_title': '《文明的冲突》',
    'channel_mark': channel['name'],
    'sizes': ['bilibili', 'douyin'],
    'channel_style': channel,
    'output_dir': 'projects/<project>/assets/cover',
})
```

### Step 6: Assemble Asset Manifest

Build the `asset_manifest` with all generated files, paths, and metadata.

## Quality Checklist

- [ ] All generated images follow seinen manga style
- [ ] Character reference sheets are clear and usable
- [ ] Character appearance is consistent (same anchored description used)
- [ ] Narration audio covers all script sections
- [ ] Voice matches channel profile
- [ ] Cover images generated at both sizes
- [ ] All files exist on disk
- [ ] No AI-generated text in any image

## Gate Reminder

This stage gates on human approval. Present samples first, then batch generate. Show all assets before checkpointing.

## Generic Knowledge-Book Mode

When the stage receives `visual_asset_plan`, ignore the legacy assumption that all
assets are character art and scene backgrounds. Generate the reusable asset pack
specified by the plan: style kit, illustrations, maps, diagrams, timelines,
object visuals, data cards, quote cards, portraits, and optional talking head.

Generate one representative sample first. After approval, batch the remaining
assets with explicit `output_path` values under `projects/<project>/assets/`.
Record each file's source tool, prompt/model metadata, visual role, section ids,
reusable flag, and lifecycle status in `asset_manifest`.

When this stage runs as `gap_assets`, generate only unresolved storyboard gap
requests. Never replace an approved asset without a new decision-log entry.
