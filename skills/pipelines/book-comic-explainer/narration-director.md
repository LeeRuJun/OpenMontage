# Narration Director — Book Comic Explainer

## When to Use

Script is approved. Your job: record the narration. Voice IS the timeline. Everything downstream follows the voice.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Prior artifact | `script` | Narration text + delivery cues per section |
| Channel config | `shared_assets/channel_seinen_manga/channel.yaml` | Voice profile |
| Tools | `tts_selector` | TTS generation |

## Process

### Step 1: Read the Script Voice Plan

Extract every section's text and delivery cues. The delivery cues are your recording instructions: pace, tone, pauses, emphasis.

### Step 2: Sample First

Generate 10-15 seconds from a representative section. Use the channel voice profile. Let user approve before batch.

### Step 3: Batch Record

Record every section. Use exact delivery cues from script. Record exact duration per section. These durations ARE the timeline.

### Step 4: Output

Write narration audio to `projects/<project>/assets/audio/<section_id>.mp3`. Record durations in narration_audio artifact.

## Gate Reminder

This stage gates on human approval. Voice sample MUST be approved before batch.
