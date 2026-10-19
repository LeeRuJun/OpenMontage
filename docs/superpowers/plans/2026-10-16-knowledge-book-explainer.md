# Knowledge Book Explainer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade `book-comic-explainer` into a generic 16:9 knowledge-book pipeline that classifies the book, chooses how to explain it, generates reusable visual assets before storyboard, and renders a first 《安史之乱》 editorial-diagram episode.

**Architecture:** Preserve the existing research → proposal → script → narration → edit → compose contracts, but insert `book_profile`, `visual_asset_plan`, `core_assets`, and `gap_assets` stages. The storyboard becomes an asset-assembly/timing artifact rather than a per-frame image-generation request. Remotion’s `Explainer` remains the render entry point and gains editorial 2D scene primitives for maps, diagrams, timelines, data, quotes, image cards, and optional talking-head overlay.

**Tech Stack:** Python/YAML/JSON Schema for pipeline orchestration and artifacts; existing checkpoint/registry system; React + TypeScript + Remotion 4 for deterministic composition; FFmpeg/ffprobe for media QA.

**Spec:** `docs/superpowers/specs/2026-10-16-knowledge-book-explainer-design.md`

## Global Constraints

- Default output is 1920×1080, 16:9, optimized for YouTube long-form.
- The pipeline must classify book type before selecting visual grammar.
- The pipeline must decide how to explain the book before writing the final script.
- Narration remains the timeline spine.
- Core reusable assets are generated and reviewed before storyboard.
- Storyboard assembles approved assets and records missing assets; it does not blindly generate one image per frame.
- Pure AI video generation is not the default visual treatment.
- Character and scene design are conditional for novel/biography/case-scene content.
- Generation calls require registry preflight, provider/model announcement, cost estimate, and the manifest’s human-approval gates.
- All production outputs write under `projects/<project-id>/`.

## Review Focus

- Low-confidence or mixed book classification must not silently select the wrong visual grammar; test fallback to `editorial_explainer`.
- A delivery strategy must preserve the selected angle and keep summary/interpretation/example ratios valid; test rejection of inconsistent strategies.
- Asset reuse must work across multiple sections without duplicate generation; test `used_by` indexing and approved-status filtering.
- Editorial scenes must render deterministically at frame 0, midpoint, and final frame; test map/diagram/timeline/data scenes without network assets.
- Narration duration must remain the composition duration and no cut may leave a timing gap; test the 《安史之乱》 edit timeline with ffprobe.

---

### Task 1: Add Book Profile, Delivery Strategy, and Visual Asset Plan Contracts

**Files:**
- Create: `schemas/artifacts/book_profile.schema.json`
- Create: `schemas/artifacts/delivery_strategy.schema.json`
- Create: `schemas/artifacts/visual_asset_plan.schema.json`
- Modify: `schemas/artifacts/__init__.py` only if schema discovery is not filename-automatic
- Test: `tests/contracts/test_knowledge_book_artifacts.py`
- Modify: `tests/contracts/test_phase0_contracts.py` sample artifact registry

**Interfaces:**
- `book_profile`: primary/secondary types, narrative mode, visual grammar, confidence, evidence.
- `delivery_strategy`: core promise, audience problem, narrative mode, hook, progression, pacing, ratios, ending.
- `visual_asset_plan`: canvas, visual grammar, reusable asset records, generation mode, section usage, status.
- Each artifact uses `version: "1.0"` and rejects unknown required enum values.

- [ ] **Step 1: Write failing schema tests** for one valid sample and invalid cases: unknown `primary_type`, ratios not summing to 1, asset with no `id/type/status`, and non-16:9 canvas.
- [ ] **Step 2: Run** `pytest tests/contracts/test_knowledge_book_artifacts.py -v` and confirm failures because the schemas do not exist.
- [ ] **Step 3: Implement the three JSON Schemas** with explicit enums, required fields, numeric bounds, `additionalProperties: false`, and reusable asset records.
- [ ] **Step 4: Add minimal valid samples** to `sample_artifact()` and ensure `validate_artifact()` discovers all three schemas.
- [ ] **Step 5: Run** `pytest tests/contracts/test_knowledge_book_artifacts.py tests/contracts/test_phase0_contracts.py -v` and confirm PASS.
- [ ] **Step 6: Commit** `feat: add knowledge book artifact contracts`.

### Task 2: Insert Classification, Strategy, and Asset-First Pipeline Stages

**Files:**
- Modify: `pipeline_defs/book-comic-explainer.yaml`
- Create: `skills/pipelines/book-comic-explainer/book-profile-director.md`
- Create: `skills/pipelines/book-comic-explainer/visual-asset-plan-director.md`
- Modify: `skills/pipelines/book-comic-explainer/proposal-director.md`
- Modify: `skills/pipelines/book-comic-explainer/storyboard-director.md`
- Modify: `skills/pipelines/book-comic-explainer/asset-director.md`
- Test: `tests/contracts/test_knowledge_book_pipeline.py`

**Interfaces:**
- New stage `book_profile` produces `book_profile` before `research`.
- `research` consumes `book_profile`.
- `proposal` produces `proposal_packet`, `delivery_strategy`, and `decision_log`.
- New stage `visual_asset_plan` consumes `book_profile`, `delivery_strategy`, `script`, and `narration_audio`; produces `visual_asset_plan`.
- New gated stage `core_assets` consumes `visual_asset_plan`; produces the initial approved `asset_manifest`.
- `storyboard` consumes `asset_manifest` and produces asset references plus missing-asset requests.
- New `gap_assets` stage resolves only missing storyboard assets and revises `asset_manifest`.
- `character_design` and `scene_design` become conditional branches driven by `requires_character_design` and `requires_scene_design` context flags.

- [ ] **Step 1: Add failing manifest contract tests** for stage order, required inputs, produced artifacts, approval defaults, and conditional character/scene branches.
- [ ] **Step 2: Run** `pytest tests/contracts/test_knowledge_book_pipeline.py -v` and confirm failure.
- [ ] **Step 3: Update the manifest** while preserving the pipeline name and existing checkpoint conventions.
- [ ] **Step 4: Write the book-profile director** with the taxonomy and confidence/fallback rules from the spec.
- [ ] **Step 5: Update proposal/storyboard/asset directors** so delivery strategy is approved before script and storyboard consumes approved reusable assets.
- [ ] **Step 6: Add visual asset planning and gap-asset instructions** including `planned/generated/approved/rejected/needs_refinement` lifecycle states.
- [ ] **Step 7: Run** `pytest tests/contracts/test_knowledge_book_pipeline.py tests/contracts/test_pipeline_catalog.py -v` and confirm PASS.
- [ ] **Step 8: Commit** `feat: make book explainer asset-first`.

### Task 3: Add Editorial Remotion Scene Primitives

**Files:**
- Create: `remotion-composer/src/components/editorial/EditorialCanvas.tsx`
- Create: `remotion-composer/src/components/editorial/ImageCardScene.tsx`
- Create: `remotion-composer/src/components/editorial/MapScene.tsx`
- Create: `remotion-composer/src/components/editorial/DiagramScene.tsx`
- Create: `remotion-composer/src/components/editorial/TimelineScene.tsx`
- Create: `remotion-composer/src/components/editorial/DataRevealScene.tsx`
- Create: `remotion-composer/src/components/editorial/QuoteCardScene.tsx`
- Create: `remotion-composer/src/components/editorial/TalkingHeadOverlay.tsx`
- Create: `remotion-composer/src/components/editorial/index.ts`
- Modify: `remotion-composer/src/Explainer.tsx`
- Modify: `remotion-composer/src/components/index.ts`
- Test: `remotion-composer/` TypeScript compile and deterministic render smoke

**Interfaces:**
- Every primitive accepts `durationInFrames`, `theme`, and deterministic props only.
- `MapScene` accepts `backgroundSrc`, `nodes`, `paths`, `highlightColor`.
- `DiagramScene` accepts `nodes`, `edges`, `revealOrder`, `accentColor`.
- `TimelineScene` accepts `events`, `activeIndex`, `lineColor`.
- `DataRevealScene` accepts `label`, `value`, `unit`, `from`, `accentColor`.
- `TalkingHeadOverlay` accepts `src`, `size`, `right`, `bottom`, `opacity`, `borderColor`.
- `SceneRenderer` maps cut types `image_card`, `map_scene`, `diagram_scene`, `timeline_scene`, `data_reveal`, and `quote_card` to these components.

- [ ] **Step 1: Add TypeScript prop/type definitions** and a compile-only fixture for each primitive.
- [ ] **Step 2: Run** `cd remotion-composer && npx tsc --noEmit` and confirm failures for missing components/mappings.
- [ ] **Step 3: Implement the primitives** with `useCurrentFrame`, `interpolate`, `spring`, SVG paths, and no random/time/network calls.
- [ ] **Step 4: Extend `Cut` and `SceneRenderer`** without changing existing cut behavior.
- [ ] **Step 5: Add a deterministic fixture** containing one image card, map, diagram, timeline, data reveal, quote, and optional talking-head overlay.
- [ ] **Step 6: Run** `cd remotion-composer && npx tsc --noEmit` and render the fixture with the existing Remotion CLI; inspect frame 0, midpoint, and final frame.
- [ ] **Step 7: Commit** `feat: add editorial book explainer scenes`.

### Task 4: Add Workflow Contract and Renderer Tests

**Files:**
- Modify: `tests/contracts/test_phase0_contracts.py`
- Modify: `tests/contracts/test_phase1_contracts.py`
- Create: `tests/contracts/test_editorial_scene_contract.py`
- Create: `tests/qa/test_knowledge_book_smoke.py`
- Modify: `remotion-composer/src/Explainer.tsx` only if compile tests expose type gaps

**Interfaces:**
- Contract tests validate a complete book profile → strategy → asset plan → storyboard → edit decision chain.
- Smoke test uses local generated SVG/data fixtures and never calls a paid provider.
- QA test checks `1920x1080`, audio presence, duration equality within ±0.5 seconds, and no uncovered timeline intervals.

- [ ] **Step 1: Write failing contract tests** for the full artifact chain and conditional branch flags.
- [ ] **Step 2: Run** `pytest tests/contracts/test_editorial_scene_contract.py tests/qa/test_knowledge_book_smoke.py -v` and confirm failures.
- [ ] **Step 3: Implement fixture builders** that use exact schema-valid dictionaries and local SVG/PNG assets.
- [ ] **Step 4: Run** the contract tests and the existing phase 0/1 suites.
- [ ] **Step 5: Run** the Remotion typecheck and deterministic fixture render.
- [ ] **Step 6: Commit** `test: cover editorial book workflow contracts`.

### Task 5: Build the 《安史之乱》 Episode Brief and Asset Pack

**Files:**
- Create: `projects/anshi-lushan-book/project.json`
- Create: `projects/anshi-lushan-book/artifacts/book_profile.json`
- Create: `projects/anshi-lushan-book/artifacts/research_brief.json`
- Create: `projects/anshi-lushan-book/artifacts/proposal_packet.json`
- Create: `projects/anshi-lushan-book/artifacts/delivery_strategy.json`
- Create: `projects/anshi-lushan-book/artifacts/script.json`
- Create: `projects/anshi-lushan-book/artifacts/visual_asset_plan.json`
- Create: `projects/anshi-lushan-book/assets/editorial/` local SVG/PNG assets
- Create: `projects/anshi-lushan-book/assets/narration/` generated narration only after approved provider decision

**Interfaces:**
- The episode uses `primary_type: history`, secondary `politics/economics`, `visual_grammar: historical_diagram`, and `narrative_mode: reframing_explainer`.
- The reference video is style/pacing evidence, not a source for copying its frames or narration.
- Core assets include paper canvas, Tang-era map, fiscal-flow diagram, timeline, money/grain objects, actor/force cards, data cards, quote cards, and optional talking-head overlay.

- [ ] **Step 1: Run registry preflight** using `provider_menu_summary()` and report available TTS/image/music/composition tools, including Remotion and HyperFrames status.
- [ ] **Step 2: Present the content angle, runtime, composition mode, asset plan, cost, and music plan; stop at the manifest’s approval gate before paid generation.**
- [ ] **Step 3: Research and write the book profile, research brief, delivery strategy, and script with claims/sources recorded.**
- [ ] **Step 4: Generate one representative editorial asset sample** and review style, legibility, historical treatment, and 16:9 composition.
- [ ] **Step 5: After approval, generate the reusable core asset pack** with explicit `output_path` values under the project workspace.
- [ ] **Step 6: Review every asset and revise rejected assets before storyboard.
- [ ] **Step 7: Commit only code/artifacts intended for source control; keep rendered media under the project’s ignored workspace paths.

### Task 6: Assemble, Render, and QA the First Episode

**Files:**
- Create: `projects/anshi-lushan-book/artifacts/storyboard_spec.json`
- Create: `projects/anshi-lushan-book/artifacts/asset_manifest.json`
- Create: `projects/anshi-lushan-book/artifacts/edit_decisions.json`
- Create: `projects/anshi-lushan-book/artifacts/render_report.json`
- Create: `projects/anshi-lushan-book/renders/final.mp4`
- Create: `projects/anshi-lushan-book/renders/contact-sheet.jpg`

**Interfaces:**
- Storyboard references approved asset IDs, not ad hoc absolute paths.
- Edit decisions cover the full narration duration with no gaps and use editorial cut types.
- Render report records resolution, fps, duration, codec, audio codec, runtime, and asset provenance.

- [ ] **Step 1: Build storyboard timing from narration durations** and assign one or more approved assets to every section.
- [ ] **Step 2: Run `gap_assets` only for missing visuals** and update the manifest with provenance.
- [ ] **Step 3: Render the 16:9 Remotion composition** with captions, narration, music ducking, editorial canvas, diagrams, maps, and optional avatar overlay.
- [ ] **Step 4: Run ffprobe QA** for `1920x1080`, audio/video tracks, duration, and frame rate.
- [ ] **Step 5: Extract a low-resolution contact sheet and visually inspect hook, section transitions, diagram readability, caption placement, and ending.
- [ ] **Step 6: Write the schema-valid render report and final checkpoint.**
- [ ] **Step 7: Commit the workflow/code changes separately from the generated project artifacts.**

### Task 7: Whole-Branch Verification and Review

**Files:**
- Modify: any failing test or schema file identified by the preceding tasks
- Test: all affected Python contract suites and `remotion-composer` typecheck/render smoke

- [ ] **Step 1: Run** `pytest tests/contracts/test_knowledge_book_artifacts.py tests/contracts/test_knowledge_book_pipeline.py tests/contracts/test_editorial_scene_contract.py tests/qa/test_knowledge_book_smoke.py -v`.
- [ ] **Step 2: Run** `pytest tests/contracts/test_phase0_contracts.py tests/contracts/test_phase1_contracts.py tests/contracts/test_pipeline_catalog.py -v`.
- [ ] **Step 3: Run** `cd remotion-composer && npx tsc --noEmit`.
- [ ] **Step 4: Run** the deterministic Remotion fixture render and inspect its contact sheet.
- [ ] **Step 5: Run GitNexus change-impact analysis and a final code review before claiming completion.
- [ ] **Step 6: Report any blocked provider, failed gate, skipped generation, or test failure explicitly; do not silently substitute a provider or runtime.
