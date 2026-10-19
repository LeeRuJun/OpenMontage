"""Cover compositor — overlay Chinese text onto AI-generated base images.

A post-generation compositing step: takes a base image (typically from
``openai_image`` or another generation provider), applies a channel style
config, and outputs publication-ready covers at multiple aspect ratios.

Does NOT generate the base image — that stays with the existing image
generation tools. This tool is the deterministic text-overlay step.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import yaml

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    RetryPolicy,
    ToolResult,
    ToolRuntime,
    ToolStability,
    ToolStatus,
    ToolTier,
)

# ── Default channel style for seinen manga covers ──────────────────────
# Prefer loading from a channel.yaml file via load_channel_config().
# This inline default is a fallback for when no channel config is provided.
DEFAULT_CHANNEL_STYLE: dict[str, Any] = {
    "name": "seinen-manga-cover",
    "palette": {
        "text_primary": "#FFF8E7",
        "text_stroke": "#1A1A2E",
        "subtitle": "#C8C0B0",
        "channel_mark": "#787060",
        "overlay_gradient_start": (0, 0, 0, 0),
        "overlay_gradient_end": (0, 0, 0, 140),
    },
    "layouts": {
        "16x9": {
            "width": 1920,
            "height": 1080,
            "hook": {"x": 120, "y": 440, "max_width": 1360, "font_size": 96},
            "subtitle": {"x": 120, "y": 800, "font_size": 42},
            "channel_mark": {"x": 1660, "y": 1000, "anchor": "right", "font_size": 32},
        },
        "3x4": {
            "width": 1080,
            "height": 1440,
            "hook": {"x": 80, "y": 640, "max_width": 920, "font_size": 88},
            "subtitle": {"x": 80, "y": 1090, "font_size": 38},
            "channel_mark": {"x": 940, "y": 1360, "anchor": "right", "font_size": 30},
        },
    },
    "typography": {
        "font_paths": [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.otf",
            "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.otf",
        ],
        "hook_weight": "bold",
        "stroke_width": 6,
        "line_spacing": 1.18,
    },
}

# ── Channel config loader ──────────────────────────────────────────────

def load_channel_config(yaml_path: str | Path | None = None) -> dict[str, Any]:
    """Load channel style from a channel.yaml file.

    Args:
        yaml_path: Path to channel.yaml.  If None, looks for
            ``shared_assets/channel_seinen_manga/channel.yaml`` relative
            to the repo root.

    Returns:
        A channel style dict compatible with CoverCompositor.execute().
        Falls back to DEFAULT_CHANNEL_STYLE if the YAML is missing.
    """
    if yaml_path is None:
        # Default to the seinen manga channel
        yaml_path = Path(__file__).resolve().parent.parent.parent / "shared_assets" / "channel_seinen_manga" / "channel.yaml"

    cfg_path = Path(yaml_path)
    if not cfg_path.is_file():
        return dict(DEFAULT_CHANNEL_STYLE)

    raw = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    if not raw:
        return dict(DEFAULT_CHANNEL_STYLE)

    # Convert channel.yaml structure → internal cover compositor structure
    palette = raw.get("palette", {})
    typography = raw.get("typography", {})
    cover = raw.get("cover", {})

    # Parse overlay gradient tuples if they are lists
    grad_start = palette.get("overlay_gradient_start", [0, 0, 0, 0])
    grad_end = palette.get("overlay_gradient_end", [0, 0, 0, 140])
    if isinstance(grad_start, list):
        grad_start = tuple(grad_start)
    if isinstance(grad_end, list):
        grad_end = tuple(grad_end)

    layouts = {}
    layout_16x9 = cover.get("layout_16x9", {})
    if layout_16x9:
        layouts["16x9"] = layout_16x9

    layout_3x4 = cover.get("layout_3x4", {})
    if layout_3x4:
        layouts["3x4"] = layout_3x4

    return {
        "name": raw.get("name", "channel"),
        "palette": {
            "text_primary": palette.get("text_primary", "#FFF8E7"),
            "text_stroke": palette.get("text_stroke", "#1A1A2E"),
            "subtitle": palette.get("subtitle", "#C8C0B0"),
            "channel_mark": palette.get("channel_mark", "#787060"),
            "overlay_gradient_start": grad_start,
            "overlay_gradient_end": grad_end,
        },
        "layouts": layouts,
        "typography": {
            "font_paths": typography.get("font_paths", []),
            "hook_weight": typography.get("hook_weight", "bold"),
            "stroke_width": typography.get("stroke_width", 6),
            "line_spacing": typography.get("line_spacing", 1.18),
        },
        "_raw": raw,  # preserve original for prompt template, voice, etc.
    }


def get_cover_prompt_template(channel_config_path: str | Path | None = None) -> str:
    """Read the cover prompt template from a channel config.

    Args:
        channel_config_path: Path to channel.yaml.  Uses default if omitted.

    Returns:
        The prompt template string, or the built-in default.
    """
    if channel_config_path is None:
        channel_config_path = Path(__file__).resolve().parent.parent.parent / "shared_assets" / "channel_seinen_manga" / "channel.yaml"

    cfg_path = Path(channel_config_path)
    if cfg_path.is_file():
        raw = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
        if raw:
            cover = raw.get("cover", {})
            tmpl = cover.get("base_prompt_template")
            if tmpl:
                return tmpl.strip()

    return SEINEN_MANGA_PROMPT_TEMPLATE

# Built-in size presets — platform targets
SIZE_PRESETS: dict[str, tuple[int, int]] = {
    "bilibili": (1920, 1080),
    "douyin": (1080, 1440),
    "youtube": (1920, 1080),
    "xiaohongshu": (1080, 1440),
}


def _resolve_font(font_paths: list[str], size: int, weight: str = "bold") -> Any:
    """Try each font path; fall back to Pillow default."""
    from PIL import ImageFont

    for fp in font_paths:
        if Path(fp).exists():
            try:
                if weight == "bold":
                    return ImageFont.truetype(fp, size)
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
    # Ultimate fallback
    try:
        return ImageFont.truetype("PingFang.ttc", size)
    except Exception:
        return ImageFont.load_default()


def _draw_gradient_overlay(
    draw_ctx: Any, width: int, height: int, start_rgba: tuple, end_rgba: tuple
) -> Any:
    """Draw a vertical gradient overlay from top to bottom."""
    from PIL import Image

    grad = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    pix = grad.load()
    for y in range(height):
        t = y / max(height - 1, 1)
        r = int(start_rgba[0] + (end_rgba[0] - start_rgba[0]) * t)
        g = int(start_rgba[1] + (end_rgba[1] - start_rgba[1]) * t)
        b = int(start_rgba[2] + (end_rgba[2] - start_rgba[2]) * t)
        a = int(start_rgba[3] + (end_rgba[3] - start_rgba[3]) * t)
        for x in range(width):
            pix[x, y] = (r, g, b, a)
    return grad


def _draw_multiline_text(
    draw_ctx: Any,
    text: str,
    x: int,
    y: int,
    font: Any,
    fill: str,
    stroke_width: int,
    stroke_fill: str,
    line_spacing: float,
    max_width: int,
) -> int:
    """Draw text across multiple lines, returning the bottom y position."""
    lines = text.split("\n")
    line_height = int(font.size * line_spacing)
    for line in lines:
        draw_ctx.text(
            (x, y),
            line,
            fill=fill,
            stroke_width=stroke_width,
            stroke_fill=stroke_fill,
            font=font,
        )
        y += line_height
    return y


def _compose_one(
    bg_path: str | Path,
    hook_text: str,
    book_title: str,
    layout: dict[str, Any],
    palette: dict[str, str | tuple],
    typography: dict[str, Any],
    channel_mark_text: str | None = None,
) -> Any:
    """Composite one cover size. Returns a PIL Image."""
    from PIL import Image, ImageDraw

    bg = Image.open(bg_path).convert("RGBA")
    target_w = layout["width"]
    target_h = layout["height"]

    # Resize / crop background to fill target dimensions
    bg_ratio = bg.width / bg.height
    target_ratio = target_w / target_h
    if bg_ratio > target_ratio:
        new_h = target_h
        new_w = int(target_h * bg_ratio)
    else:
        new_w = target_w
        new_h = int(target_w / bg_ratio)
    bg = bg.resize((new_w, new_h), Image.Resampling.LANCZOS)
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    bg = bg.crop((left, top, left + target_w, top + target_h))

    im = bg.convert("RGBA")
    draw = ImageDraw.Draw(im)

    # Gradient overlay — bottom portion only (text legibility)
    grad_h = int(target_h * 0.55)
    grad = _draw_gradient_overlay(
        draw,
        target_w,
        grad_h,
        palette["overlay_gradient_start"],
        palette["overlay_gradient_end"],
    )
    im.alpha_composite(grad, (0, target_h - grad_h))

    # ── Hook text ──
    hk = layout["hook"]
    font_hook = _resolve_font(
        typography.get("font_paths", []), hk["font_size"], typography.get("hook_weight", "bold")
    )
    stroke_w = typography.get("stroke_width", 6)
    _draw_multiline_text(
        draw,
        hook_text,
        hk["x"],
        hk["y"],
        font_hook,
        palette["text_primary"],
        stroke_w,
        palette["text_stroke"],
        typography.get("line_spacing", 1.18),
        hk.get("max_width", 1360),
    )

    # ── Book title subtitle ──
    if book_title:
        sub = layout["subtitle"]
        font_sub = _resolve_font(typography.get("font_paths", []), sub["font_size"])
        draw.text(
            (sub["x"], sub["y"]),
            book_title,
            fill=palette["subtitle"],
            font=font_sub,
        )

    # ── Channel mark ──
    if channel_mark_text:
        cm = layout["channel_mark"]
        font_cm = _resolve_font(typography.get("font_paths", []), cm["font_size"])
        if cm.get("anchor") == "right":
            # Right-align the mark
            try:
                tw = draw.textlength(channel_mark_text, font=font_cm)
            except AttributeError:
                tw = font_cm.getlength(channel_mark_text)
            cm_x = cm["x"] - tw
        else:
            cm_x = cm["x"]
        draw.text((cm_x, cm["y"]), channel_mark_text, fill=palette["channel_mark"], font=font_cm)

    return im


class CoverCompositor(BaseTool):
    """Overlay styled Chinese text onto a base image to produce publication covers.

    This is a deterministic post-generation step.  Image generation (e.g.
    ``openai_image``) produces the base image; this tool applies the channel's
    visual style — typography, palette, gradient overlays — and outputs ready-
    to-publish covers at the requested aspect ratios.
    """

    name = "cover_compositor"
    version = "0.1.0"
    tier = ToolTier.ENHANCE
    capability = "graphics"
    provider = "openmontage"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.LOCAL

    dependencies = ["Pillow"]
    install_instructions = "pip install Pillow"
    agent_skills: list[str] = []

    capabilities = ["composite_cover", "text_overlay", "multi_size_output"]
    supports = {
        "multi_size": True,
        "custom_style": True,
        "channel_mark": True,
        "gradient_overlay": True,
    }
    best_for = [
        "self-media book commentary covers (Douyin / Bilibili / YouTube)",
        "consistent channel branding across episodes",
        "overlaying Chinese text onto AI-generated base images",
    ]
    not_good_for = [
        "generating base images (use openai_image / image_selector)",
        "English-only typography (use Canva or design tools)",
        "photo-realistic cover design",
    ]

    input_schema = {
        "type": "object",
        "required": ["base_image_path", "hook_text"],
        "properties": {
            "base_image_path": {
                "type": "string",
                "description": "Path to the AI-generated base image (RGBA/RGB PNG).",
            },
            "hook_text": {
                "type": "string",
                "description": "Main hook text, 6-12 Chinese characters. Use \\n for line breaks.",
            },
            "book_title": {
                "type": "string",
                "description": "Book title as subtitle, e.g. 《管道的故事》.",
            },
            "channel_mark": {
                "type": "string",
                "description": "Channel name watermark, e.g. 硬书解读.",
            },
            "sizes": {
                "type": "array",
                "items": {"type": "string", "enum": list(SIZE_PRESETS.keys())},
                "default": ["bilibili", "douyin"],
                "description": "Output size presets: bilibili=1920x1080, douyin=1080x1440, etc.",
            },
            "channel_style": {
                "type": "object",
                "description": (
                    "Optional channel style override.  Omit to use the built-in "
                    "seinen manga default."
                ),
            },
            "output_dir": {
                "type": "string",
                "description": "Directory for output cover files. Default: cwd.",
            },
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=2, ram_mb=512, vram_mb=0, disk_mb=100, network_required=False
    )
    retry_policy = RetryPolicy(max_retries=0, retryable_errors=[])
    idempotency_key_fields = ["base_image_path", "hook_text", "book_title", "sizes"]
    side_effects = ["writes cover images to output_dir"]
    user_visible_verification = ["Inspect cover images for text placement and legibility"]

    def get_status(self) -> ToolStatus:
        try:
            from PIL import Image, ImageDraw, ImageFont  # noqa: F401
        except ImportError:
            return ToolStatus.UNAVAILABLE
        return ToolStatus.AVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        base_path = inputs["base_image_path"]
        hook_text = inputs["hook_text"]
        book_title = inputs.get("book_title", "")
        channel_mark = inputs.get("channel_mark", "")
        sizes = inputs.get("sizes", ["bilibili", "douyin"])
        output_dir = Path(inputs.get("output_dir", "."))
        channel_style = inputs.get("channel_style") or DEFAULT_CHANNEL_STYLE

        if not Path(base_path).is_file():
            return ToolResult(
                success=False,
                error=f"base_image_path not found: {base_path}",
            )

        palette = channel_style["palette"]
        typography = channel_style["typography"]
        layouts = channel_style["layouts"]

        output_dir.mkdir(parents=True, exist_ok=True)
        results: list[dict[str, Any]] = []

        try:
            for size_key in sizes:
                if size_key not in SIZE_PRESETS:
                    results.append({"size": size_key, "success": False, "error": "unknown size preset"})
                    continue

                layout_key = "16x9" if SIZE_PRESETS[size_key] == (1920, 1080) else "3x4"
                layout = layouts.get(layout_key)
                if layout is None:
                    # Derive layout from nearest built-in
                    layout = layouts.get("16x9", {})

                im = _compose_one(
                    base_path,
                    hook_text,
                    book_title,
                    layout,
                    palette,
                    typography,
                    channel_mark_text=channel_mark or None,
                )

                out_path = output_dir / f"cover_{size_key}.png"
                im.convert("RGB").save(out_path, quality=95)
                results.append({
                    "size": size_key,
                    "dimensions": SIZE_PRESETS[size_key],
                    "success": True,
                    "output_path": str(out_path),
                })

            return ToolResult(
                success=True,
                data={
                    "covers": results,
                    "channel_style": channel_style["name"],
                    "base_image": base_path,
                },
            )

        except Exception as exc:
            return ToolResult(
                success=False,
                error=str(exc),
                data={"covers": results},
            )


# ── Prompt helper: build base-image prompt from topic description ──────

SEINEN_MANGA_PROMPT_TEMPLATE = (
    "日系青年漫画风格的封面插画，{topic_description}。"
    "粗线条动漫风，低饱和度配色，深色背景。"
    "画面留出左侧和顶部空间给标题文字。"
    "风格参考：贰瓶勉、林田球、沙村广明的青年漫画封面。"
    "画面中不要出现任何文字、字母、数字或标志。"
    "暗调高级感，气氛压抑但富有诗意，大面积阴影。"
)


def build_cover_prompt(topic_description: str) -> str:
    """Build a base-image prompt from a topic description.

    This is the cover-specific prompt template matching the seinen manga
    channel style.  Use the result with ``openai_image`` or
    ``image_selector`` to generate the base image before compositing.

    Args:
        topic_description: What the image should depict, in Chinese.
            e.g. "一架天平，左边是军事力量右边是外交规则，分裂的大陆"

    Returns:
        A full prompt string ready for ``openai_image.execute()``.
    """
    return SEINEN_MANGA_PROMPT_TEMPLATE.format(topic_description=topic_description)
