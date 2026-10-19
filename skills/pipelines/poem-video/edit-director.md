# Edit Director — Poem Video Pipeline

## Purpose

Arrange all video clips to the narration timeline, plan transitions,
and define subtitle placement.

## Workflow

### 1. Load Artifacts

Read `script` and `asset_manifest`. Know:
- The scene order (from script)
- Each clip's path and duration (from asset_manifest)
- Narration audio and its duration

### 2. Narrate IS the Timeline

The narration audio drives everything. The narration.mp3 is the master
timeline — video clips must align to it, not the other way around.

**Alignment strategy:**
- Play narration audio in full
- Map each scene's clip to appear when the corresponding poetic line is spoken
- Add 1-2 second padding at start (title card)
- Add 2-3 second padding at end (closing card with hold)

### 3. Define the Edit Sequence

```json
{
  "version": "1.0",
  "render_runtime": "remotion",
  "total_duration": 48.0,
  "segments": [
    {
      "id": "title_card",
      "type": "title_card",
      "source": null,
      "in_seconds": 0.0,
      "out_seconds": 4.0,
      "overlay": {
        "text": "静夜思 — 李白 (唐)",
        "style": "calligraphy_center"
      },
      "transition": "dissolve_1s"
    },
    {
      "id": "scene_01",
      "type": "scene",
      "source": "projects/<id>/assets/video/scene_01.mp4",
      "in_seconds": 0.0,
      "out_seconds": 10.5,
      "subtitle": "床前明月光",
      "camera_motion": {"type": "zoom_in", "intensity": 0.05},
      "transition": "dissolve_1s"
    },
    ...
    {
      "id": "closing_card",
      "type": "closing_card",
      "source": null,
      "in_seconds": 0.0,
      "out_seconds": 5.0,
      "overlay": {
        "text": "静夜思",
        "style": "calligraphy_center_fade"
      },
      "transition": "none"
    }
  ],
  "audio": {
    "narration": "projects/<id>/assets/audio/narration.mp3",
    "music": "projects/<id>/assets/music/bgm.mp3",
    "music_level_db": -22,
    "narration_level_db": -6
  }
}
```

### 4. Camera Motion Per Scene

If the edit is destined for a Remotion or HyperFrames render:
- Assign a simple Ken Burns-style motion to each clip
- `zoom_in`, `zoom_out`, `pan_left`, `pan_right`, or `static`
- Motion should be subtle — poetry video, not action movie
- Intensity: 0.03–0.08 (3-8% scale change over duration)

### 5. Subtitle Plan

- Subtitles appear character-by-character or line-by-line
- Position: bottom-center for vertical video (safe zone: y from 1400-1800)
- Style: white text with slight shadow, 楷体 or serif font
- Timing: subtitle appears 0.3s before the corresponding narration line

### Output

An `edit_decisions` artifact following the schema in
`schemas/artifacts/edit_decisions.schema.json`.

## Review Checklist

- [ ] Full duration covered, no gaps between segments
- [ ] Narration timing drives segment placement
- [ ] Camera motion assigned to every scene clip
- [ ] Transitions specified between all segments
- [ ] Subtitle timing mapped to narration
- [ ] render_runtime locked (default: remotion)
- [ ] Schema-valid edit_decisions artifact
