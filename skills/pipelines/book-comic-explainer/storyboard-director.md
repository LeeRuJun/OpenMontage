# Storyboard Director — Book Comic Explainer Pipeline

## When to Use

You receive `character_design`, `asset_manifest`, and `script`. Your job is to generate the storyboard frames — assembling the art style, character appearances, scene backgrounds, and frame specs into image prompts, then generating them.

**You execute. You do not redesign.** The script's frame descriptions already specify character, action, scene, shot, and composition. The character_design already provides appearance anchors and the art style prefix. Your job is assembly and generation — not reinterpretation.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Prior artifact | `character_design` | Art style prompt_prefix, character appearances, scene list |
| Prior artifact | `asset_manifest` | Scene background paths, narration audio paths |
| Prior artifact | `script` | Frame specs per section (character, action, scene, shot, composition) |
| Tools | `image_selector` or `openai_image` | Frame generation |
| Batch tool | `tools/graphics/image_batch.py` | Concurrent generation (use this — not sequential) |

## The Prompt Template

Every storyboard frame prompt follows this exact template. Copy the art style prefix and character appearances verbatim from character_design:

```
{art_style.prompt_prefix}
{scene background description}

画面中的角色：{character.appearance 全文 — copy-paste, do not rewrite}。
{character action from script frame spec}。

{composition from script frame spec}。

画面中不要出现任何文字、字母、数字或标志。
不要出现：Q版、可爱风、大眼睛、日系萌系、少年漫、热血、科幻发光效果。
```

**Critical rule:** The character appearance block is pasted VERBATIM from character_design. Do not paraphrase. Do not reword. The anchoring depends on identical words every time.

## Process

### Step 1: Inventory the Frames

Walk every script section. For each frame, verify you have:
- Character appearance (from character_design) ✓
- Scene background (from asset_manifest — either generated or shared_asset path) ✓
- Art style prefix (from character_design) ✓
- Action + shot + composition (from script frame spec) ✓

If anything is missing, stop and flag it. Do not improvise.

### Step 2: Build Frame Prompts

For each frame, assemble the full prompt from the template. Write it out in full — no abbreviations, no placeholder references. The prompt IS the contract with the image generator.

### Step 3: Shot Type Rotation Check

Verify no 3+ consecutive frames use the same shot type:

| Shot | When to use | Visual cue |
|------|-------------|------------|
| `wide` / `extreme_wide` | Establishing location, isolation, scale | "环境占画面大部分" |
| `mid_shot` | Character acting, dialogue, everyday moments | "角色在画面中央，半身" |
| `close_up` | Emotion, reaction, realization | "面部特写，强调表情" |
| `over_shoulder` | Confrontation, debate, watching | "从角色A身后看过去" |
| `high_angle` | Vulnerability, defeat, smallness | "从上方俯视，角色渺小" |
| `low_angle` | Power, threat, determination | "从下方仰视，角色显得高大" |

Rotate. Repetition kills visual rhythm.

### Step 4: Generate Frames — Batch Concurrent

Use `ImageBatchRunner` from `tools/graphics/image_batch.py`. Do NOT generate sequentially.

```python
from tools.graphics.image_batch import ImageBatchRunner

requests = [
    {
        "prompt": full_prompt_for_frame_01,
        "size": "1920x1088",
        "quality": "high",
        "preferred_provider": "openai",
        "output_path": "projects/<project>/assets/storyboard/s01_f01.png",
    },
    # ... all frames
]

runner = ImageBatchRunner()
result = runner.run(requests, max_workers=4, max_retries=2)
```

**Before batch:** Generate ONE sample frame. Show the user. Confirm the style. Then batch the rest with `max_workers=4`.

**Resolution:** 1920×1088 (divisible by 16 for OpenAI). Output as PNG.

### Step 5: Review Consistency

After all frames generated, review for:
- Same character looks like the same person across frames
- Seinen manga style is consistent
- No AI-generated text in any image
- Shot types properly rotate

Regenerate any frame that breaks consistency.

### Step 6: Self-Evaluate

Score the storyboard (1-5):

| Criterion | Question |
|-----------|----------|
| **Script fidelity** | Does every frame match its script spec (character, action, scene, composition)? |
| **Character consistency** | Does the same character look like the same person across all frames? |
| **Style consistency** | Is seinen manga style maintained in every frame? |
| **Shot variety** | Do shot types rotate — no 3+ consecutive identical types? |
| **Composition quality** | Is every frame well-composed, not just "character standing center"? |
| **No AI text** | Are all frames free of AI-generated text/hallucinated characters? |

If any dimension scores below 3, fix before submitting.

## Common Pitfalls

| Pitfall | Why it happens | How to fix |
|---------|---------------|-------------|
| Paraphrasing appearance | Trying to "improve" or vary the character description | Paste verbatim from character_design. Every time. |
| Generating sequentially | Using a for-loop with openai_image | Use ImageBatchRunner with max_workers=4 |
| Skipping the sample | Eager to batch all frames at once | Generate one. Show it. THEN batch. |
| Same shot type repeatedly | Not checking rotation | Audit shot types before generating. Rotate explicitly. |
| Wrong provider routing | image_selector routes to local_diffusion | Set preferred_provider="openai" in every request |
| Forgetting constraints | Prompt template incomplete | Always include "不要出现任何文字" and "不要出现Q版" blocks |

## When You Don't Know How

If a frame prompt produces poor results:
- Read the character appearance again — is it specific enough for the generator?
- Check if the composition instruction conflicts with the scene (e.g. "over_shoulder" in "extreme_wide landscape")
- Try regenerating with the same prompt (GPT Image 2 is stochastic — same prompt, different result)
- If 3 attempts fail: adjust the composition, not the character appearance
- Log failed attempts: `category="storyboard_prompt_debug"`

## Gate Reminder (Binding)

This stage gates on human approval (`human_approval_default: true`). After review passes:
checkpoint with `status="awaiting_human"`, present all frames as a visual sequence
(the Backlot board's filmstrip), and **END YOUR TURN**. Do not start the next stage
in the same response. Approval is per-gate — an earlier "go ahead" does not cover this gate.

## Generic Knowledge-Book Mode

When `asset_manifest` and `visual_asset_plan` are present, storyboard is an asset
assembly artifact. Do not generate a new image for every frame. For each narration
section, select approved asset ids, define the scene primitive (`image_card`,
`map_scene`, `diagram_scene`, `timeline_scene`, `data_reveal`, or `quote_card`),
set in/out timing, and record any missing visual as a gap request.

The storyboard must preserve the 1920x1080 canvas and put important text and data
inside the editorial safe region. Use `talking_head_overlay` only when the plan
contains an approved talking-head asset. Character appearance prompts and the
seinen-manga constraints apply only when `requires_character_design` is true.
