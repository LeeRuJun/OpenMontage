"""OpenAI GPT Image generation and editing (gpt-image-2)."""

from __future__ import annotations

import base64
import os
import re
import time
from contextlib import ExitStack
from pathlib import Path
from typing import Any

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


_SIZE_RE = re.compile(r"^(?P<width>\d+)x(?P<height>\d+)$", re.IGNORECASE)


class OpenAIImage(BaseTool):
    name = "openai_image"
    version = "0.2.0"
    tier = ToolTier.GENERATE
    capability = "image_generation"
    provider = "openai"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.STOCHASTIC
    runtime = ToolRuntime.API

    dependencies = []  # checked dynamically
    install_instructions = (
        "Set OPENAI_API_KEY to your OpenAI API key.\n"
        "  pip install openai"
    )
    agent_skills = ["flux-best-practices"]  # general image gen knowledge

    capabilities = [
        "generate_image",
        "edit_image",
        "generate_illustration",
        "text_to_image",
        "reference_image",
        "multiple_reference_images",
        "mask",
        "custom_size",
    ]
    supports = {
        "complex_instructions": True,
        "text_in_image": True,
        "multiple_outputs": True,
        "image_edit": True,
        "reference_image": True,
        "multiple_reference_images": True,
        "mask": True,
        "custom_size": True,
        "background": True,
        "moderation": True,
        "output_compression": True,
    }
    best_for = [
        "complex multi-element compositions",
        "images with text/labels",
        "following detailed instructions accurately",
        "editing or compositing one or more reference images",
    ]
    not_good_for = ["offline generation", "budget-constrained projects at high quality"]

    input_schema = {
        "type": "object",
        "required": ["prompt"],
        "properties": {
            "prompt": {"type": "string"},
            "model": {
                "type": "string",
                "default": "gpt-image-2",
                "description": "OpenAI image model. Defaults to gpt-image-2.",
            },
            "generation_mode": {
                "type": "string",
                "enum": ["generate", "edit"],
                "default": "generate",
            },
            "size": {
                "type": "string",
                "default": "1024x1024",
                "description": (
                    "auto or WIDTHxHEIGHT. GPT Image 2 accepts custom dimensions "
                    "subject to the API's geometry and pixel limits."
                ),
            },
            "quality": {
                "type": "string",
                "enum": ["low", "medium", "high", "auto"],
                "default": "high",
            },
            "output_format": {
                "type": "string",
                "enum": ["png", "jpeg", "webp"],
                "default": "png",
            },
            "output_compression": {
                "type": "integer",
                "description": "JPEG/WebP compression percentage, when supported by the API.",
            },
            "background": {
                "type": "string",
                "enum": ["auto", "opaque"],
                "default": "auto",
            },
            "moderation": {
                "type": "string",
                "enum": ["auto", "low"],
                "default": "auto",
            },
            "input_fidelity": {"type": "string"},
            "image_path": {"type": "string"},
            "image_paths": {"type": "array", "items": {"type": "string"}},
            "image_url": {"type": "string"},
            "image_urls": {"type": "array", "items": {"type": "string"}},
            "mask_path": {"type": "string"},
            "mask_url": {"type": "string"},
            "n": {
                "type": "integer",
                "minimum": 1,
                "description": "Number of outputs. The API determines the model-specific maximum.",
            },
            "output_path": {"type": "string"},
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=1, ram_mb=512, vram_mb=0, disk_mb=100, network_required=True
    )
    retry_policy = RetryPolicy(max_retries=2, retryable_errors=["rate_limit", "timeout"])
    idempotency_key_fields = ["prompt", "size", "quality", "model", "generation_mode", "n"]
    side_effects = ["writes image file to output_path", "calls OpenAI API"]
    user_visible_verification = ["Inspect generated image for relevance and quality"]

    @staticmethod
    def _output_paths(output_path: str | None, count: int, extension: str) -> list[Path]:
        """Derive one output path per generated image."""
        ext = extension if extension.startswith(".") else f".{extension}"
        if not output_path:
            return [Path(f"generated_image_{idx + 1}{ext}") for idx in range(count)]

        path = Path(output_path)
        suffix = path.suffix or ext
        if count == 1:
            return [path if path.suffix else path.with_suffix(suffix)]

        base = path.with_suffix("") if path.suffix else path
        return [base.parent / f"{base.name}_{idx + 1}{suffix}" for idx in range(count)]

    def get_status(self) -> ToolStatus:
        if os.environ.get("OPENAI_API_KEY"):
            return ToolStatus.AVAILABLE
        return ToolStatus.UNAVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        # Provider pricing changes; keep this as a conservative estimate until
        # the cost registry has dimension-aware GPT Image 2 pricing.
        quality = inputs.get("quality", "high")
        n = int(inputs.get("n", 1) or 1)
        cost_map = {"low": 0.006, "medium": 0.053, "high": 0.211, "auto": 0.053}
        return cost_map.get(quality, 0.053) * n

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        if not os.environ.get("OPENAI_API_KEY"):
            return ToolResult(
                success=False,
                error="OPENAI_API_KEY not set. " + self.install_instructions,
            )

        start = time.time()
        try:
            normalized = self._normalize_inputs(inputs)
            from openai import OpenAI

            client = OpenAI()
            payload = self._build_payload(normalized)
            with ExitStack() as stack:
                image_inputs = self._open_image_inputs(normalized, stack)
                mask = self._open_mask(normalized, stack)
                if image_inputs:
                    payload["image"] = image_inputs[0] if len(image_inputs) == 1 else image_inputs
                if mask is not None:
                    payload["mask"] = mask

                if image_inputs or normalized["generation_mode"] == "edit":
                    if not image_inputs:
                        return ToolResult(success=False, error="generation_mode='edit' requires an input image")
                    response = client.images.edit(**payload)
                else:
                    response = client.images.generate(**payload)

            items = response.data or []
            if not items:
                return ToolResult(success=False, error="OpenAI returned no image outputs")

            output_format = normalized["output_format"]
            output_paths = self._output_paths(inputs.get("output_path"), len(items), output_format)
            outputs: list[str] = []
            for item, out_path in zip(items, output_paths):
                b64_json = getattr(item, "b64_json", None)
                if not b64_json:
                    return ToolResult(success=False, error="OpenAI image response item had no b64_json output")
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_bytes(base64.b64decode(b64_json))
                outputs.append(str(out_path))

        except (TypeError, ValueError, FileNotFoundError) as exc:
            return ToolResult(success=False, error=f"Invalid OpenAI image input: {exc}")
        except Exception as exc:
            return ToolResult(success=False, error=f"OpenAI image generation failed: {exc}")

        return ToolResult(
            success=True,
            data={
                "provider": "openai",
                "model": normalized["model"],
                "prompt": normalized["prompt"],
                "generation_mode": normalized["generation_mode"],
                "output": outputs[0],
                "outputs": outputs,
                "images_generated": len(outputs),
            },
            artifacts=outputs,
            cost_usd=self.estimate_cost(normalized),
            duration_seconds=round(time.time() - start, 2),
            model=normalized["model"],
        )

    @classmethod
    def _normalize_inputs(cls, inputs: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(inputs)
        normalized["prompt"] = str(inputs["prompt"])
        normalized["model"] = str(inputs.get("model", "gpt-image-2"))
        normalized["generation_mode"] = inputs.get("generation_mode")
        if normalized["generation_mode"] not in {None, "generate", "edit"}:
            raise ValueError("generation_mode must be 'generate' or 'edit'")

        normalized["size"] = str(inputs.get("size", "1024x1024"))
        normalized["output_format"] = str(inputs.get("output_format", "png"))
        cls._validate_size(normalized["size"])
        normalized["n"] = int(inputs.get("n", 1) or 1)
        if normalized["n"] < 1:
            raise ValueError("n must be at least 1")

        paths = list(inputs.get("image_paths") or [])
        if inputs.get("image_path"):
            paths.insert(0, str(inputs["image_path"]))
        urls = list(inputs.get("image_urls") or [])
        if inputs.get("image_url"):
            urls.insert(0, str(inputs["image_url"]))
        normalized["image_paths"] = paths
        normalized["image_urls"] = urls
        if normalized["generation_mode"] == "generate" and (paths or urls):
            raise ValueError("generation_mode='generate' cannot be combined with input images")
        if normalized["generation_mode"] is None:
            normalized["generation_mode"] = "edit" if (paths or urls) else "generate"
        if inputs.get("mask_path") and not (paths or urls):
            raise ValueError("mask requires an input image")
        if inputs.get("output_compression") is not None:
            compression = int(inputs["output_compression"])
            if not 0 <= compression <= 100:
                raise ValueError("output_compression must be between 0 and 100")
        if inputs.get("partial_images") is not None:
            raise ValueError("partial_images requires a streaming image implementation and is not supported by this wrapper")
        return normalized

    @staticmethod
    def _validate_size(size: str) -> None:
        if size == "auto":
            return
        match = _SIZE_RE.fullmatch(size)
        if not match:
            raise ValueError("size must be 'auto' or WIDTHxHEIGHT")
        width, height = int(match.group("width")), int(match.group("height"))
        if width <= 0 or height <= 0 or width % 16 or height % 16:
            raise ValueError("custom image dimensions must be positive multiples of 16")
        ratio = max(width / height, height / width)
        if ratio > 3:
            raise ValueError("custom image aspect ratio cannot exceed 3:1")
        if max(width, height) > 3840:
            raise ValueError("custom image dimensions cannot exceed 3840 pixels on one edge")
        pixels = width * height
        if pixels < 655_360 or pixels > 8_294_400:
            raise ValueError("custom image dimensions exceed GPT Image 2 pixel limits")

    @staticmethod
    def _build_payload(inputs: dict[str, Any]) -> dict[str, Any]:
        payload = {
            "model": inputs["model"],
            "prompt": inputs["prompt"],
            "size": inputs["size"],
            "quality": inputs.get("quality", "high"),
            "output_format": inputs.get("output_format", "png"),
            "n": inputs["n"],
        }
        for key in ("background", "moderation", "output_compression", "input_fidelity"):
            if inputs.get(key) is not None:
                payload[key] = inputs[key]
        return payload

    @staticmethod
    def _open_image_inputs(inputs: dict[str, Any], stack: ExitStack) -> list[Any]:
        values: list[Any] = []
        for path in inputs["image_paths"]:
            file_path = Path(path)
            if not file_path.exists():
                raise FileNotFoundError(f"input image not found: {file_path}")
            values.append(stack.enter_context(file_path.open("rb")))
        values.extend(inputs["image_urls"])
        return values

    @staticmethod
    def _open_mask(inputs: dict[str, Any], stack: ExitStack) -> Any | None:
        if inputs.get("mask_path"):
            path = Path(str(inputs["mask_path"]))
            if not path.exists():
                raise FileNotFoundError(f"mask image not found: {path}")
            return stack.enter_context(path.open("rb"))
        return inputs.get("mask_url")
