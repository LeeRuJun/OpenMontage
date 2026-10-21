# Cover Plan Director

Design the account-aware cover and first frame before story production assets.

## Master brand

Use the existing `brand_assets` paths when provided. The account logo/IP is not optional decoration: the cover and first-frame plan must state where the master mark, series label, and episode title appear. Never invent a replacement logo when existing assets are supplied.


## Series cover DNA

Keep these account-level invariants across different historical stories:

- **Palette:** warm rice-paper base, charcoal/ink structure, muted indigo, one vermilion conflict accent.
- **Brand:** use the supplied master mark; keep it small and stable in the upper-left safe zone. Never let the mark cover the title.
- **Title hierarchy:** a two-line mobile-readable hook, large and high-contrast; one short content subtitle beneath it; series/brand label remains the smallest line.
- **Layout:** reserve the left upper/middle region for text with at least 120px landscape margin; use the right side for the story-specific historical metaphor.
- **Story variation:** change the map, route, object, seal, document, or architectural metaphor for each episode, but do not change the title hierarchy, brand placement, palette family, or safe-zone logic.
- **Text treatment:** AI generates the clean visual base only; all title, subtitle, and brand text is added deterministically in the composition layer. Never rely on AI-rendered Chinese typography.
- **Cover identity:** the cover is a dedicated asset, not a video frame or a random still from the timeline.

## First frame

Design the first 0–3 seconds as a promise: immediate visual conflict, route/object/character context, then the hook text. It must be distinct from the static cover while sharing the same brand and visual metaphor.

Output `cover_plan`, show it at the proposal gate, and require approval before cover/first-frame asset generation.
