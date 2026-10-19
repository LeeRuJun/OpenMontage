# Edit Director — Book Comic Explainer Pipeline

## When to Use

You receive `storyboard_frames`, `asset_manifest`, and `script`. Your job is to produce `edit_decisions` — the timeline that defines how key frames connect into continuous motion with narration.

**The storyboard frames are KEY FRAMES — they are not every frame.** The edit stage designs how to move between them. A 45-second script section may have 2-4 key frames. The space between them is filled by camera motion (push-in, pan, crossfade), not by generating more images.

## The Key Frame Principle

```
一段戏 45秒 × 3张关键帧 = 观众感受是连续的

关键帧1 (0-18s):   远景 → slow push-in → 建立空间
     ↓ crossfade
关键帧2 (18-35s):  特写 → hold → 让观众看清细节
     ↓ crossfade  
关键帧3 (35-45s):  过肩 → slow push-in → 揭示第三个人在场
```

The viewer doesn't see the cuts. They see a story unfolding.
The key frames are the anchor points. The motion is the connective tissue.
The narration is the thread that pulls them forward.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Schema | `schemas/artifacts/edit_decisions.schema.json` | Artifact validation |
| Prior artifact | `storyboard_frames` | Key frame image paths |
| Prior artifact | `asset_manifest` | Narration audio paths and durations |
| Prior artifact | `script` | Section durations, dramatic functions, frame specs |

## Process

### Step 1: Load Narration and Group by Script Section

Read narration durations from `asset_manifest`. Organize storyboard frames by their parent script section. Each section in the script already defines which frames belong to it.

```
Script Section s03 "灶门口" (45s target):
  Key frames: s03_f01, s03_f02
  Narration: n03 (6.2s)
  Dramatic function: build_world
```

### Step 2: Design the Section Rhythm

For each script section, decide how its key frames play:

```
RULES PER SECTION:

Single key frame:
  → camera motion over the full duration
  → push-in for emotional weight, pan for establishing, hold for dialogue

Multiple key frames (2-4):
  → Key frames 1→2→3→... connected by crossfade (0.5-1.0s)
  → Each key frame gets a portion of the section duration
  → Distribution: opening frame gets 30-40%, middle frames split evenly, closing frame gets 25-35%
  → Narration starts 0.3-0.5s after the first key frame appears

Section without narration:
  → 3-6 seconds of visual alone
  → Used for: breathing room, establishing shots, emotional weight after heavy moments
```

### Step 3: Assign Camera Motion Per Key Frame

| Dramatic function | Default motion | Intensity |
|-------------------|---------------|-----------|
| `hook` | hold (3s) then slow push-in | subtle — let the image hit first |
| `build_world` | slow pan or push-in | gentle — let the viewer absorb |
| `raise_stakes` | push-in, accelerating | building — match rising tension |
| `reveal_character` | hold → micro-push on key detail | precise — focus the eye |
| `escalate` | faster push-in or crossfade chain | urgent — shorter holds between frames |
| `peak` | hold. just hold. | none — the image does the work |
| `land` | slow pull-back or fade to black | releasing — let the viewer go |

**No 3+ consecutive sections of the same motion pattern.** Vary the rhythm.

### Step 4: Build the Edit Decision Timeline

Each entry maps one key frame to its time on screen:

```json
{
  "section_id": "s03",
  "section_label": "灶门口",
  "dramatic_function": "build_world",
  "narration_id": "n03",
  "narration_duration": 6.2,
  "section_duration": 18.0,

  "keyframes": [
    {
      "frame": "s03_f01.png",
      "duration": 10.0,
      "animation": "push-in",
      "zoom_range": [1.0, 1.03],
      "narration_starts_at": 0.5,
      "transition_out": "crossfade",
      "transition_duration": 0.8
    },
    {
      "frame": "s03_f02.png", 
      "duration": 8.0,
      "animation": "hold",
      "transition_out": "fade_to_black",
      "transition_duration": 1.0
    }
  ],

  "vignette": true,
  "notes": "灶门口的光线变化 — 从暗到亮，火着了"
}
```

**Key rules:**
- `narration_starts_at` is relative to keyframe start — always >= 0.3s
- Keyframe `duration` >= (narration_duration assigned to it) + 1.0s breathing room
- Total section duration must be within ±15% of script target

### Step 5: Validate the Timeline

- [ ] Total video duration matches target within ±10%
- [ ] Every narration clip is assigned to exactly one keyframe
- [ ] No narration starts before its keyframe appears
- [ ] Every narration clip has >= 0.3s padding before it starts
- [ ] Motion patterns vary — no 3+ consecutive same type at section level
- [ ] Opening section has at least 3s of silent visual before first words (for hook sections)
- [ ] Closing section ends with >= 2s of silence
- [ ] All frame paths resolve to existing files
- [ ] All narration paths resolve to existing files

### Step 6: Self-Evaluate

Score the edit (1-5):

| Criterion | Question |
|-----------|----------|
| **Rhythm** | Does the motion pattern vary across sections — not monotonous? |
| **Sync** | Is every narration clip precisely placed relative to its keyframe? |
| **Breathing room** | Are there silent pauses after heavy moments? |
| **Key frame flow** | If you flip through just the key frames, can you feel the story arc? |
| **Duration accuracy** | Total within ±10% of target? |

If any dimension scores below 3, revise before submitting.

### Step 7: Output

Write `edit_decisions` artifact. Validate against schema. Compose reads this and plays it exactly — no improvisation, no reinterpretation.

## Common Pitfalls

| Pitfall | Why it happens | How to fix |
|---------|---------------|------------|
| Every section same motion | Not checking variety | Audit motion types across sections. Force rotation. |
| Narration starts before frame | Not accounting for visual buildup | Always `narration_starts_at` >= 0.3 |
| No silence after heavy moments | Racing to the next section | After `peak` sections: hold 2-3s minimum |
| Key frames treated as slideshow | Fixed durations, no motion design | Design the camera movement per frame, not just the duration |
| Too many key frames per section | Generating every possible angle | 2-4 key frames max per section. Motion fills the rest. |

## Gate Reminder

This stage does NOT gate on human approval (`human_approval_default: false`). But review must pass before compose.
