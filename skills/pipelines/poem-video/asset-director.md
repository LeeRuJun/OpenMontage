# Asset Director — Poem Video Pipeline

## Purpose

Generate all production assets: video clips from text-to-video, narration
audio from TTS, and background music.

## Workflow

### 1. Read the Script

Load the `script` artifact. You have a list of scenes, each with a visual
prompt and estimated duration.

### 2. Generate Video Clips — TEXT-TO-VIDEO FIRST (video_selector)

**MANDATORY: Use text-to-video, not image-to-video.** This pipeline's promise
is *motion*: scenes must be generated as animated clips directly from the
visual prompt. Do NOT:

- Pre-generate still images and feed them as a first frame (that produces a
  Ken Burns slideshow, not a poetry video)
- Ship a composition made of still frames with pan/zoom

**How to ensure text-to-video:**

- Call `video_selector` with `operation: "text_to_video"` explicitly. Most
  providers default to text-to-video, but set it anyway so a fallback cannot
  silently route you into image-to-video.
- Confirm the resolved provider supports text-to-video before prompting. If
  the only available provider is image-only, STOP and surface a blocker — do
  not quietly fall back to stills.
- **Prompt style must be TIME-SEGMENTED:** "0-2s: ... 2-4s: ..." — slice 1
  establishes the shot, slice 2 advances with a micro-event. A single flowing
  paragraph produces a still, empty scene. See the script-director's
  "TIME-SEGMENTED and RICH" rules.

```
Action: video_selector
Params:
  prompt: "<visual_prompt from script + explicit motion clause>"
  operation: "text_to_video"     # MANDATORY — never image_to_video
  duration: <duration_estimate from script>
  aspect_ratio: "9:16"
  style_preset: <art_style from brief>
Output saved to: projects/<project-id>/assets/video/<scene_id>.mp4
```

**Per-clip motion gate (non-negotiable):** every generated clip MUST pass
`qa_lib.gate_slideshow_motion` (mean frame difference ≥ 1.2). Run it on the
clip before accepting it. A clip that fails is a still image wearing a video
wrapper — regenerate, do not keep it.

**Critical rules:**
- Read the Layer 3 skill for the selected video provider before crafting prompts
- All clips MUST be same resolution and aspect ratio
- **Tone/contrast gate per clip:** run `qa_lib.gate_tone_contrast` on each
  clip. Failing it (murky, all-dark, no bright detail) means the visual
  prompt is too dark/abstract — tighten the prompt toward visible subject,
  moonlight/highlights, and white space before regenerating.
- Review each generated clip: does it match the visual prompt? does it match the art style?
- If a clip is off-style or wrong content, regenerate it
- Batch clips only after the first 2-3 samples are approved
- **Generate ALL scenes before moving on.** A missing scene (script has N,
  disk has < N) is a blocker — do not leave assets stage with an incomplete
  scene set.

### 3. Generate Narration (tts_selector)

The narration is the poem itself, read in classical Chinese.

```
Action: tts_selector
Params:
  text: "<full poem text>"
  voice: <voice from decision_log>
  speed: <speed from decision_log>
Output saved to: projects/<project-id>/assets/audio/narration.mp3
```

**Rules:**
- Generate a sample first (first 2 lines only) and get user approval
- Add natural pauses: 1-2s between lines, 2-3s between couplets
- If the TTS can't handle pauses natively, insert silence in post with ffmpeg

### 4. Generate or Select Music (music_gen)

Music must match the poem's mood per `creative/poem-video.md`.

```
Action: music_gen
Params:
  mood: <mood from decision_log>
  duration: <total video duration + 5s padding>
  instruments: <instruments from decision_log>
Output saved to: projects/<project-id>/assets/music/bgm.mp3
```

**Alternative:** If the user has tracks in `music_library/`, present those as
options before calling the API.

### 5. Produce Asset Manifest

```json
{
  "version": "1.0",
  "project_id": "<project-id>",
  "assets": {
    "video_clips": [
      {"scene_id": "scene_01", "path": "projects/<id>/assets/video/scene_01.mp4", "duration": 10.5, "provider": "kling"},
      ...
    ],
    "narration": {"path": "projects/<id>/assets/audio/narration.mp3", "duration": 42.0, "provider": "minimax"},
    "music": {"path": "projects/<id>/assets/music/bgm.mp3", "duration": 47.0, "provider": "music_gen"}
  }
}
```

## Review Checklist

- [ ] Every scene has a generated video clip (scene count == script count)
- [ ] Clips were generated via **text-to-video**, not image-to-video / stills
- [ ] All clips share the same resolution and aspect ratio
- [ ] Visual style is coherent across all clips (same art style)
- [ ] Every clip passes `qa_lib.gate_slideshow_motion` (has real motion)
- [ ] Every clip passes `qa_lib.gate_tone_contrast` (not a murky black blob)
- [ ] Narration audio covers the full poem, clear and well-paced
- [ ] Background music file exists and matches the poem's mood
- [ ] All files exist on disk and pass ffprobe validation
- [ ] Asset manifest is schema-valid
