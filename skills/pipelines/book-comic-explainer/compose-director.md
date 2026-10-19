# Compose Director — Book Comic Explainer Pipeline

## When to Use

You receive `storyboard_frames`, `asset_manifest`, and `script`. Your job is to assemble the final video: sequence the storyboard frames, add camera motion (Ken Burns / push-in / pan), layer narration and music, and render the output. Also generate the cover images.

## Runtime

Default: **Remotion**. The storyboard frames are still images — Remotion adds camera motion, transitions, and audio sync. FFmpeg is the fallback for simple crossfade + audio.

Read `skills/meta/animation-runtime-selector.md` before deciding.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Prior artifacts | `storyboard_frames`, `asset_manifest`, `script` | What to compose |
| Channel config | `shared_assets/channel_seinen_manga/channel.yaml` | Cover style, channel mark |
| Tools | `video_compose`, `cover_compositor` | Rendering + cover |

## Process

### Step 1: Build the Edit Decisions

Map storyboard frames to a timeline:

```json
{
  "cuts": [
    {
      "id": "cut_01",
      "script_section": "s1",
      "type": "anime_scene",
      "images": ["assets/storyboard/s1_01.png"],
      "animation": "push-in",
      "in_seconds": 0,
      "out_seconds": 8,
      "vignette": true
    },
    {
      "id": "cut_02",
      "script_section": "s2",
      "type": "anime_scene",
      "images": ["assets/storyboard/s2_01.png"],
      "animation": "pan-right",
      "in_seconds": 8,
      "out_seconds": 18
    }
  ]
}
```

**Animation per shot type:**
| Shot type | Animation |
|-----------|-----------|
| 中景 (mid shot) | subtle push-in (1.02 → 1.06) |
| 近景 (close-up) | hold or micro push |
| 远景 (wide) | slow pan (left→right or right→left) |
| 过肩 (over-shoulder) | slight rack focus feel (blur → sharp) |
| 对话场景 | alternate push on the speaking character |

**Transitions:**
- Default: crossfade (0.5s)
- Dramatic moment: hard cut
- Scene change: fade to black (0.3s)

### Step 2: Audio

Layer narration audio from `asset_manifest` synced to the timeline.

Music: if available in `asset_manifest`, add as background track, ducked to 8-12% during narration.

### Step 3: Subtitles

Word-level captions synced to narration. Use the Remotion `CaptionOverlay` component.

Style: white text with dark background pill, channel palette from `channel.yaml`.

### Step 4: Compose via Remotion

Create a Remotion composition referencing the storyboard frames and audio. Use the `anime_scene` cut type for frame-based scenes with camera motion.

### Step 5: Generate Cover Images

Use `cover_compositor` to create final cover images at bilibili (16:9) and douyin (3:4) sizes.

```python
from tools.graphics.cover_compositor import CoverCompositor, load_channel_config

channel = load_channel_config()
CoverCompositor().execute({
    'base_image_path': 'projects/<project>/assets/cover_base.png',
    'hook_text': script['hook_text'],        # from script metadata
    'book_title': script['book_title'],       # from script metadata
    'channel_mark': channel['name'],
    'sizes': ['bilibili', 'douyin'],
    'channel_style': channel,
    'output_dir': 'projects/<project>/assets/cover',
})
```

### Step 6: Render

Call `video_compose.execute()` with the edit decisions and asset manifest. Output to `projects/<project>/renders/final.mp4`.

### Step 7: Verify

Check the output:
- Duration within ±5% of target
- Audio clear, narration audible over music
- Camera motion smooth, no jitter
- Cover images generated at both sizes

## Output

1. `render_report` — schema-valid, with output paths and encoding info
2. `projects/<project>/renders/final.mp4` — the deliverable
3. `projects/<project>/assets/cover/cover_bilibili.png` — B站封面
4. `projects/<project>/assets/cover/cover_douyin.png` — 抖音封面
