# Visual Asset Plan Director — Knowledge Book Explainer

## Purpose

Create `visual_asset_plan` after script and narration. Plan reusable visual assets before storyboard assembly; do not generate one image per storyboard frame.

## Inputs

Read `book_profile`, `delivery_strategy`, `script`, and exact narration section durations. Keep the 16:9 canvas at 1920×1080.

## Asset Grammar

Select assets that explain the chosen delivery strategy:

- `reframing_explainer`: contrast cards, causal diagrams, evidence visuals, quote cards
- `one_big_idea`: one anchor diagram plus three supporting data/example cards
- `problem_solution`: pain-point scene, mechanism diagram, step cards, risk card
- `case_study`: subject portrait, timeline, event cards, before/after data
- `concept_ladder`: concrete object, analogy, layered abstraction, summary model
- `character_arc`: portraits, relationship graph, scene illustrations, timeline
- `debate_compare`: opposing cards, evidence columns, synthesis diagram
- `practical_playbook`: principle cards, process diagram, example scene, checklist

## Required Asset Records

Each planned asset needs a stable id, type, visual role, referenced sections, generation mode, reusable flag, and lifecycle status. Prefer `svg` or `code` for maps, diagrams, timelines, and data cards; use image generation or stock only where a raster/illustration is the right medium.

Use lifecycle states exactly as defined by `visual_asset_plan.schema.json`: `planned`, `generated`, `approved`, `rejected`, `needs_refinement`.

## Reuse Rules

- One map, diagram, object, or portrait may serve multiple sections.
- Record all section ids in `used_by` before generation.
- Do not create a second asset when an approved reusable asset can support the visual claim.
- Add `talking_head` only when the brief explicitly wants the optional lower-right presenter overlay.

## Gate

Present the asset plan and one representative sample asset for approval before batch generation. The storyboard stage may reference only approved assets; unresolved needs become explicit gap requests.
