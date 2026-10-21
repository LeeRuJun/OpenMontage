# Historical Narration Timing Director

Make measured narration the timeline source of truth.

Generate or ingest approved narration, align the transcript, and record section, act, and word timestamps in `narration_timing`.

Pilot must measure 90–150 seconds; full must measure 1,320–1,500 seconds. If timing misses the mode contract, return to script. Do not silently time-stretch, pad with silence, or cut narration to fit pictures.

After approval, changing script text or voice invalidates narration timing and all downstream timing artifacts.
