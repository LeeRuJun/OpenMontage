# Book Profile Director — Knowledge Book Explainer

## Purpose

Classify the book before research chooses the angle. This stage must produce `book_profile` and must not write the final script or generate assets.

## Classification

Choose one `primary_type`: `history`, `politics`, `business_economics`, `psychology_self_help`, `science_technology`, `biography`, `literature`, `philosophy_social`, `mixed`, or `unknown`. Add zero or more `secondary_types`.

Choose a `narrative_mode`: `explanatory`, `story_driven`, `practical`, `debate`, or `case_study`.

Choose `visual_grammar`:

- history/politics/economics → `historical_diagram`
- business/economics → `business_system`
- psychology/self-help → `behavior_diagram`
- science/technology → `technical_explainer`
- biography → `biographical_timeline`
- literature → `narrative_illustration`
- philosophy/social science → `concept_map`
- mixed or confidence below 0.7 → `editorial_explainer`

## Output

Write `book_profile` with `primary_type`, `secondary_types`, `narrative_mode`, `visual_grammar`, `confidence` from 0 to 1, and evidence strings grounded in the supplied book/research material.

If classification is uncertain, use `unknown` or `mixed`, set `visual_grammar` to `editorial_explainer`, and record the uncertainty. Never silently invent a precise category.

## Review

Check that the visual grammar can explain the book's actual argument, not merely decorate it. The next stage uses this artifact to select research questions and candidate assets.
