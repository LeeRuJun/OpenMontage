"""Doubao Seedance video generation via a LiteLLM/Ark-style gateway.

Calls the custom gateway's `/v3/contents/generations/tasks` endpoint
(Volcengine Ark video-task API exposed through an OpenAI-compatible LiteLLM
proxy). Supports text-to-video and image-to-video through a Bearer API key.

API flow: POST /v3/contents/generations/tasks -> returns task id ->
poll GET /v3/contents/generations/tasks/{id} until status=succeeded ->
download content.video_url.

Config:
  DOUBAO_VIDEO_API_KEY   Bearer token for the gateway (e.g. aigate.dushu365.com)
  DOUBAO_VIDEO_BASE_URL  gateway base URL, default https://aigate.dushu365.com
  DOUBAO_VIDEO_MODEL     default model, e.g. doubao-seedance-2-0

The gateway's video path is NOT the OpenAI /v1/videos route — the gateway
routes Seedance to /v3/contents/generations/tasks. We match that.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import requests

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


_DEFAULT_BASE_URL = "https://aigate.dushu365.com"
_DEFAULT_MODEL = "doubao-seedance-2-0"
_VALID_DURATIONS = (5, 10)          # seconds; Seedance supports 5s and 10s
_VALID_RATIOS = ("16:9", "9:16", "1:1", "4:3", "3:4", "21:9")


class DoubaoVideo(BaseTool):
    name = "doubao_video"
    version = "0.1.0"
    tier = ToolTier.GENERATE
    capability = "video_generation"
    provider = "doubao"
    stability = ToolStability.EXPERIMENTAL
    execution_mode = ExecutionMode.ASYNC
    determinism = Determinism.STOCHASTIC
    runtime = ToolRuntime.API

    dependencies = ["env:DOUBAO_VIDEO_API_KEY"]
    install_instructions = (
        "Set DOUBAO_VIDEO_API_KEY to a gateway Bearer token that can access "
        "doubao-seedance video models (e.g. aigate.dushu365.com). Optionally "
        "set DOUBAO_VIDEO_BASE_URL and DOUBAO_VIDEO_MODEL."
    )
    agent_skills = ["ai-video-gen"]

    capabilities = ["text_to_video", "image_to_video"]
    supports = {
        "text_to_video": True,
        "image_to_video": True,
        "native_audio": True,          # Seedance generates audio in the same pass
        "seed": True,
    }
    best_for = [
        "Doubao Seedance text-to-video via a custom Ark-style gateway",
        "native audio in the same video pass (Seedance generates ambience)",
        "5s/10s short-form vertical or horizontal clips",
    ]
    not_good_for = ["offline generation", "users without a gateway Bearer token"]
    fallback_tools = ["sora_video", "jimeng_video", "minimax_video"]

    input_schema = {
        "type": "object",
        "required": ["prompt"],
        "properties": {
            "prompt": {
                "type": "string",
                "maxLength": 2000,
                "description": "Video description. Supports Chinese and the "
                               "time-sliced '0-2s: ... 2-4s: ...' format.",
            },
            "operation": {
                "type": "string",
                "enum": ["text_to_video", "image_to_video"],
                "default": "text_to_video",
            },
            "image_url": {
                "type": "string",
                "description": "First-frame image URL for image-to-video.",
            },
            "duration": {
                "type": "integer",
                "enum": [5, 10],
                "default": 5,
                "description": "Clip length in seconds (Seedance supports 5 and 10).",
            },
            "aspect_ratio": {
                "type": "string",
                "enum": list(_VALID_RATIOS),
                "default": "9:16",
                "description": "Aspect ratio; drives resolution.",
            },
            "seed": {
                "type": "integer",
                "default": -1,
                "description": "Random seed. -1 for random.",
            },
            "output_path": {"type": "string"},
            "poll_interval_seconds": {
                "type": "number",
                "minimum": 2,
                "default": 5.0,
            },
            "timeout_seconds": {
                "type": "integer",
                "minimum": 60,
                "default": 600,
            },
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=1, ram_mb=512, vram_mb=0, disk_mb=500, network_required=True
    )
    retry_policy = RetryPolicy(
        max_retries=2,
        backoff_seconds=2.0,
        retryable_errors=["rate_limit", "timeout"],
    )
    idempotency_key_fields = [
        "prompt",
        "operation",
        "image_url",
        "duration",
        "aspect_ratio",
        "seed",
    ]
    side_effects = [
        "writes video file to output_path",
        "calls gateway /v3/contents/generations/tasks (submit + poll + download)",
    ]
    user_visible_verification = [
        "Watch generated clip for motion coherence and prompt adherence",
    ]

    # -- config ------------------------------------------------------------

    def _api_key(self) -> str | None:
        val = os.environ.get("DOUBAO_VIDEO_API_KEY", "")
        if val and not val.strip().startswith("#"):
            return val.strip()
        return None

    def _base_url(self) -> str:
        return os.environ.get("DOUBAO_VIDEO_BASE_URL", _DEFAULT_BASE_URL).rstrip("/")

    def _model(self) -> str:
        return os.environ.get("DOUBAO_VIDEO_MODEL", _DEFAULT_MODEL).strip()

    def get_status(self) -> ToolStatus:
        return ToolStatus.AVAILABLE if self._api_key() else ToolStatus.UNAVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        duration = int(inputs.get("duration", 5))
        return round(0.06 * duration, 2)

    def estimate_runtime(self, inputs: dict[str, Any]) -> float:
        return 120.0 + int(inputs.get("duration", 5)) * 12.0

    # -- execute -----------------------------------------------------------

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        api_key = self._api_key()
        if not api_key:
            return ToolResult(
                success=False,
                error="DOUBAO_VIDEO_API_KEY not set. " + self.install_instructions,
            )

        operation = inputs.get("operation", "text_to_video")
        if operation == "image_to_video" and not inputs.get("image_url"):
            return ToolResult(
                success=False,
                error="image_to_video requires image_url (public URL).",
            )

        start = time.time()
        try:
            result = self._generate(inputs, api_key=api_key)
        except Exception as exc:  # noqa: BLE001 - surface any gateway failure
            return ToolResult(
                success=False,
                error=f"Doubao video generation failed: {self._safe_error(exc)}",
            )
        result.duration_seconds = round(time.time() - start, 2)
        return result

    def _generate(self, inputs: dict[str, Any], *, api_key: str) -> ToolResult:
        base = self._base_url()
        model = self._model()
        task_id = self._submit_task(inputs, api_key=api_key, base=base, model=model)
        result_json = self._poll_task(
            task_id, api_key=api_key, base=base,
            poll_interval=float(inputs.get("poll_interval_seconds", 5.0)),
            timeout_seconds=int(inputs.get("timeout_seconds", 600)),
        )

        video_url = (result_json.get("content") or {}).get("video_url")
        if not video_url:
            raise RuntimeError(f"Doubao task done but no video_url: {result_json}")

        download = requests.get(video_url, timeout=180)
        download.raise_for_status()

        output_path = Path(inputs.get("output_path", "doubao_video.mp4"))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(download.content)

        from tools.video._shared import probe_output
        probed = probe_output(output_path)

        return ToolResult(
            success=True,
            data={
                "provider": "doubao",
                "route": "ark_gateway_tasks",
                "model": model,
                "resolved_model": result_json.get("model", model),
                "prompt": inputs["prompt"],
                "operation": inputs.get("operation", "text_to_video"),
                "task_id": task_id,
                "duration": result_json.get("duration", inputs.get("duration", 5)),
                "ratio": result_json.get("ratio"),
                "resolution": result_json.get("resolution"),
                "fps": result_json.get("framespersecond"),
                "seed": result_json.get("seed"),
                "generate_audio": result_json.get("generate_audio"),
                "video_url": video_url,
                "output": str(output_path),
                "format": "mp4",
                **probed,
            },
            artifacts=[str(output_path)],
            cost_usd=self.estimate_cost(inputs),
            model=model,
        )

    # -- API helpers -------------------------------------------------------

    def _submit_task(
        self, inputs: dict[str, Any], *, api_key: str, base: str, model: str
    ) -> str:
        prompt = str(inputs["prompt"]).strip()
        operation = inputs.get("operation", "text_to_video")
        duration = int(inputs.get("duration", 5))
        if duration not in _VALID_DURATIONS:
            duration = 5 if duration < 8 else 10

        content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
        if operation == "image_to_video" and inputs.get("image_url"):
            content.append(
                {"type": "image_url", "image_url": {"url": inputs["image_url"]}}
            )

        payload: dict[str, Any] = {
            "model": model,
            "content": content,
            "duration": duration,
        }
        ratio = inputs.get("aspect_ratio", "9:16")
        if ratio in _VALID_RATIOS:
            payload["size"] = self._ratio_to_size(ratio)
        seed = int(inputs.get("seed", -1))
        if seed > 0:
            payload["seed"] = seed

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        url = f"{base}/v3/contents/generations/tasks"
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        data = self._json_or_raise(resp)
        task_id = data.get("id")
        if not task_id:
            raise RuntimeError(f"Doubao submit returned no task id: {data}")
        return task_id

    def _poll_task(
        self, task_id: str, *, api_key: str, base: str,
        poll_interval: float, timeout_seconds: int,
    ) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {api_key}"}
        url = f"{base}/v3/contents/generations/tasks/{task_id}"
        deadline = time.time() + timeout_seconds
        while time.time() < deadline:
            time.sleep(poll_interval)
            resp = requests.get(url, headers=headers, timeout=30)
            data = self._json_or_raise(resp)
            status = data.get("status", "")
            if status == "succeeded":
                return data
            if status == "failed":
                raise RuntimeError(
                    f"Doubao task {task_id} failed: {json.dumps(data, ensure_ascii=False)}"
                )
            if status in ("not_found", "expired"):
                raise RuntimeError(f"Doubao task invalid: status={status}")
        raise TimeoutError(f"Doubao task {task_id} did not finish within {timeout_seconds}s")

    @staticmethod
    def _ratio_to_size(ratio: str) -> str:
        return {
            "16:9": "1280x720",
            "9:16": "720x1280",
            "1:1": "1024x1024",
            "4:3": "1152x864",
            "3:4": "864x1152",
            "21:9": "1280x548",
        }.get(ratio, "1280x720")

    @staticmethod
    def _safe_error(exc: Exception) -> str:
        msg = str(exc)
        for var in ("DOUBAO_VIDEO_API_KEY",):
            val = os.environ.get(var, "")
            if val:
                msg = msg.replace(val, "[redacted]")
        return msg

    @staticmethod
    def _json_or_raise(response: Any) -> dict[str, Any]:
        try:
            data = response.json()
        except ValueError as exc:
            raise RuntimeError(
                f"Non-JSON response from Doubao gateway: HTTP {response.status_code}"
            ) from exc
        if isinstance(data, dict) and data.get("error"):
            raise RuntimeError(
                f"Doubao gateway error: {json.dumps(data['error'], ensure_ascii=False)}"
            )
        return data
