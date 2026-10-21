# Historical Narration Timing Director

Make measured narration the timeline source of truth.

Generate or ingest approved narration, align the transcript, and record section, act, and word timestamps in `narration_timing`.

Pilot must measure 90–150 seconds; full must measure 1,320–1,500 seconds. If timing misses the mode contract, return to script. Do not silently time-stretch, pad with silence, or cut narration to fit pictures.


## Fixed provider policy

Historical-story uses the manifest `provider_policy.tts` without provider re-ranking: call `minimax_tts` with MiniMax `speech-2.8-hd` and the approved voice settings. Do not substitute Doubao, ElevenLabs, Google, OpenAI, or a local fallback when MiniMax is unavailable; surface a blocker and preserve the timing artifact history. Any change of provider or voice is a new decision-log entry and invalidates downstream timing-dependent artifacts.
