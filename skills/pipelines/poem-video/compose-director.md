# Compose Director — Poem Video Pipeline

## Purpose

Stitch all assets together: video clips, narration, music, subtitles,
title card, closing card → one polished vertical MP4.

## Workflow

### 1. Load Artifacts

Read `edit_decisions` and `asset_manifest`. All source files must exist.
Verify every path in asset_manifest before starting.

### 2. Pre-compose Checks

```bash
# Verify all media files are valid
for f in $(python3 -c "import json; d=json.load(open('projects/<id>/artifacts/asset_manifest.json')); [print(a['path']) for a in d['assets']['video_clips']]"); do
  ffprobe -v error -show_entries format=duration "$f" || echo "BROKEN: $f"
done
```

### 2b. HARD QUALITY GATES (non-negotiable, run before composing)

Run `lib/qa_lib.run_all()` on the final video. **If any gate fails, DO NOT
ship.** Send back to the assets stage with the failing gate names. A video
with black frames, a missing scene, no audio, or no subtitles is NOT a
deliverable.

```bash
python3 -m lib.qa_lib \
  --video projects/<id>/renders/final.mp4 \
  --manifest-scenes <scene_count from script> \
  --clips projects/<id>/assets/video/scene_01.mp4 ... \
  --target-duration <total_duration from edit_decisions> \
  --subtitle projects/<id>/assets/subtitles.srt
```

Minimum gates, in order of importance:

| Gate | Fails when | Why |
|---|---|---|
| `scene_count` | a script scene has no clip on disk | Missing scenes ship as a broken film |
| `black_frame_ratio` | >5% of frames are near-black | 52% black video shipped before |
| `audio_present` | no audio stream | Narration is the poem |
| `subtitles_present` | subtitle file missing/empty | Poem text must be on screen |
| `duration` | outside ±10% of target | Script promised Ns, shipped N/4 |
| `tone_contrast` | murky / all-dark / no bright detail | "Ink wash" ≠ black blob |
| `slideshow_motion` | mean frame diff < 1.2 | Stills with pan/zoom are not video |

**How to use in Python:**

```python
import sys; sys.path.insert(0, ".")
from lib import qa_lib
result = qa_lib.run_all([...])
assert result["passed"], result["summary"]   # blocks compose on failure
```

If the video fails gates, append a `decision_log` entry noting the send-back,
fix the assets (regenerate dark/missing/static clips), and re-run gates.

### 3. Compose via video_compose

Call `video_compose.execute()` with the edit_decisions artifact:

```
Action: video_compose
Params:
  edit_decisions: <path to edit_decisions artifact>
  output_path: projects/<project-id>/renders/final.mp4
  render_runtime: remotion (or hyperframes, or ffmpeg)
```

The `video_compose` tool reads `edit_decisions.render_runtime` and routes to
the correct engine automatically:

| Runtime | What happens |
|---|---|
| `remotion` | React-based composition: Ken Burns, spring animations, subtitle burn, particle effects |
| `hyperframes` | HTML/CSS/GSAP: kinetic typography, layered parallax, registry blocks |
| `ffmpeg` | Simple concat + audio mix + subtitle burn (fallback) |

### 4. Audio Processing

Narration is the primary audio track. Music sits under it:

- Narration: normalize to -6 dB LUFS
- Music: duck to -22 dB LUFS, sidechain duck to -30 dB during active narration
- Fade music in over 2s at start, fade out over 3s at end

If `video_compose` doesn't handle audio mixing internally, pre-mix with
`audio_mixer` before compose, then pass the mixed track as the audio source.

### 5. Subtitle Burn

Burn subtitles into the video:
- Font: 楷体 or a Chinese serif that renders well at small sizes
- Character-by-character or line-by-line reveal
- White text, 2px dark shadow or outline for readability
- Safe zone: don't place text where it overlaps the visual focal point

### 6. Verify

```bash
ffprobe -v error -show_entries format=duration,size \
  -show_entries stream=codec_type,width,height \
  projects/<project-id>/renders/final.mp4
```

Expected:
- Resolution: 1080×1920 (vertical) or 1920×1080 (horizontal)
- Duration: within ±10% of target
- Video codec: H.264
- Audio codec: AAC, present and audible

### Output

A `render_report` artifact with:
- Output file path and size
- Duration, resolution, codec info
- Render runtime used
- Any warnings or issues noted

## Post-compose

After successful render:
1. Move final video to `projects/<project-id>/renders/final.mp4`
2. Write `render_report` artifact
3. If the Backlot board is open, it auto-refreshes from the checkpoint

## Review Checklist

- [ ] `qa_lib.run_all()` passes on the final video — NO failing gates
- [ ] Scene count == script scene count (no missing scenes)
- [ ] Black frame ratio < 5%
- [ ] Output MP4 exists and passes ffprobe validation
- [ ] Resolution matches target (1080×1920 or user choice)
- [ ] Narration is clear and synchronized with visuals
- [ ] Music is present but ducked under narration
- [ ] Subtitles are readable and correctly timed
- [ ] Title card and closing card are present
- [ ] No black frames or audio gaps
- [ ] Schema-valid render_report artifact
