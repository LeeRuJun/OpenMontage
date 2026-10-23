"""Generate project-authored historical-story cover variants."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

from tools.graphics.openai_image import OpenAIImage

FONT_CANDIDATES = [
    "/System/Library/AssetsV2/com_apple_MobileAsset_Font8/86ba2c91f017a3749571a82f2c6d890ac7ffb2fb.asset/AssetData/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
]


def _font(size: int):
    for candidate in FONT_CANDIDATES:
        if Path(candidate).is_file():
            return ImageFont.truetype(candidate, size, index=0)
    return ImageFont.load_default()


def _background_prompt(plan: dict, variant: dict) -> str:
    return (
        "Cinematic documentary cover background for a fact-grounded historical story. "
        f"Story subject: {plan['story_title']}. "
        f"Visual metaphor: {variant['visual_metaphor']}. "
        f"Composition: {variant['composition']}. "
        f"Text safe zone: {variant['text_safe_zone']}. "
        f"Color and lighting direction: {variant.get('color_direction', 'natural period-appropriate light with clear material color separation')}. "
        "Use a single coherent historical environment with foreground, midground and background, "
        "people embedded in the place when the plan calls for them, authored material colors, "
        "period-appropriate light, vivid but controlled color separation, and no generated text. "
        "No letters, digits, logos, watermarks, modern objects, collage, split-screen, contact sheet, "
        "floating portrait, or isolated object-only still life."
    )


def _draw_overlay(image: Image.Image, plan: dict, variant: dict) -> Image.Image:
    image = image.convert("RGBA")
    width, height = image.size
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    portrait = variant["canvas"] == "portrait_9_16"
    safe_width = int(width * (0.92 if portrait else 0.52))
    for x in range(safe_width):
        alpha = int(78 * (1 - x / max(1, safe_width - 1)))
        draw.line((x, 0, x, height), fill=(18, 17, 21, alpha))
    margin = int(width * (0.075 if not portrait else 0.08))
    brand_size = 28 if not portrait else 34
    title_size = 74 if not portrait else 68
    subtitle_size = 34 if not portrait else 38
    accent_y = int(height * (0.27 if not portrait else 0.28))
    draw.rectangle((margin, accent_y, margin + 70, accent_y + 6), fill=(184, 92, 56, 255))
    draw.text((margin, int(height * 0.11)), "读点东西 · 历史故事", font=_font(brand_size), fill=(196, 91, 61, 255))
    title = plan["hook_text"] or plan["story_title"]
    draw.multiline_text((margin, int(height * 0.34)), title, font=_font(title_size), fill=(244, 229, 201, 255), spacing=12, stroke_width=2, stroke_fill=(18, 17, 21, 220))
    subtitle = plan.get("subtitle", "")
    draw.multiline_text((margin, int(height * 0.58)), subtitle, font=_font(subtitle_size), fill=(244, 229, 201, 255), spacing=8, stroke_width=1, stroke_fill=(18, 17, 21, 220))
    return Image.alpha_composite(image, overlay).convert("RGB")


def main(project: Path) -> None:
    load_dotenv("/Users/fanshu01/rep/github/OpenMontage/.env")
    plan = json.loads((project / "artifacts/cover_plan.json").read_text(encoding="utf-8"))
    output_dir = project / "assets/images/cover"
    output_dir.mkdir(parents=True, exist_ok=True)
    variants = []
    size_by_canvas = {"landscape_16_9": ("1536x864", "16x9"), "portrait_9_16": ("1024x1536", "portrait")}
    for variant in plan["cover_variants"]:
        size, slug = size_by_canvas[variant["canvas"]]
        background = output_dir / f"{slug}-background.png"
        final = output_dir / f"{slug}.png"
        if not background.is_file():
            result = OpenAIImage().execute({
                "model": "gpt-image-2", "prompt": _background_prompt(plan, variant), "size": size,
                "quality": "high", "output_format": "png", "n": 1, "output_path": str(background),
            })
            if not result.success:
                raise SystemExit(result.error or f"cover background generation failed: {slug}")
        image = Image.open(background)
        _draw_overlay(image, plan, variant).save(final, quality=95)
        variants.append({"id": variant["id"], "canvas": variant["canvas"], "path": str(final.relative_to(project)), "background_path": str(background.relative_to(project)), "provider": "openai", "model": "gpt-image-2", "text_overlay": "deterministic Pillow overlay", "status": "approved"})
    artifact = {"version": "1.0", "story_title": plan["story_title"], "variants": variants, "cover_plan_ref": "artifacts/cover_plan.json"}
    (project / "artifacts/cover_asset.json").write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"variants": len(variants), "provider": "openai", "model": "gpt-image-2"}, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", required=True)
    args = parser.parse_args()
    main(Path(args.project_dir).resolve())
