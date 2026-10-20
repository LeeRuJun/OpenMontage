"""MiniMax text-to-speech provider tool."""

from __future__ import annotations

import binascii
import json
import os
import time
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


class MiniMaxTTS(BaseTool):
    name = "minimax_tts"
    version = "0.1.0"
    tier = ToolTier.VOICE
    capability = "tts"
    provider = "minimax"
    stability = ToolStability.EXPERIMENTAL
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.STOCHASTIC
    runtime = ToolRuntime.API

    dependencies = []
    install_instructions = (
        "Set MINIMAX_TTS_API_KEY to your MiniMax TTS API key and "
        "MINIMAX_GROUP_ID to your MiniMax group id. Optional defaults: "
        "MINIMAX_TTS_MODEL, MINIMAX_TTS_VOICE_ID, MINIMAX_TTS_EMOTION, "
        "MINIMAX_TTS_API_URL."
    )
    fallback = "openai_tts"
    fallback_tools = ["doubao_tts", "elevenlabs_tts", "openai_tts", "piper_tts"]
    agent_skills = ["text-to-speech"]

    capabilities = [
        "text_to_speech",
        "voice_selection",
        "mandarin_narration",
    ]
    supports = {
        "voice_cloning": False,
        "multilingual": True,
        "offline": False,
        "native_audio": True,
        "pause_markers": True,
    }
    best_for = [
        "natural Mandarin book narration",
        "Chinese explainer voiceovers",
        "mature narrator voices with MiniMax Speech models",
    ]
    not_good_for = [
        "fully offline production",
        "word-level timestamp generation",
    ]

    DEFAULT_API_URL = "https://api-uw.minimax.io/v1/t2a_v2"
    DEFAULT_MODEL = "speech-2.8-hd"
    DEFAULT_VOICE_ID = "Chinese (Mandarin)_Gentle_Senior"

    input_schema = {
        "type": "object",
        "required": ["text"],
        "properties": {
            "text": {"type": "string", "description": "Text to convert to speech"},
            "voice_id": {
                "type": "string",
                "description": "MiniMax voice_id. Defaults to MINIMAX_TTS_VOICE_ID or a mature Mandarin narrator.",
            },
            "model": {
                "type": "string",
                "default": DEFAULT_MODEL,
                "description": "MiniMax speech model, e.g. speech-2.8-hd, speech-02-hd, speech-02-turbo.",
            },
            "model_id": {
                "type": "string",
                "description": "Alias for model; accepted for selector pass-through compatibility.",
            },
            "speed": {
                "type": "number",
                "default": 0.92,
                "minimum": 0.5,
                "maximum": 2.0,
            },
            "vol": {
                "type": "number",
                "default": 1,
                "minimum": 0,
                "maximum": 10,
            },
            "pitch": {
                "type": "number",
                "default": 0,
                "minimum": -12,
                "maximum": 12,
            },
            "emotion": {
                "type": "string",
                "description": "Optional MiniMax emotion, e.g. calm, happy, sad, surprised. Defaults to MINIMAX_TTS_EMOTION when set.",
            },
            "format": {
                "type": "string",
                "default": "mp3",
                "enum": ["mp3", "wav", "pcm"],
            },
            "sample_rate": {
                "type": "integer",
                "default": 32000,
                "enum": [16000, 24000, 32000, 44100],
            },
            "bitrate": {
                "type": "integer",
                "default": 128000,
            },
            "channel": {
                "type": "integer",
                "default": 1,
                "enum": [1, 2],
            },
            "language_boost": {
                "type": "string",
                "default": "Chinese",
            },
            "output_path": {"type": "string"},
            "metadata_path": {
                "type": "string",
                "description": "Where to save a sanitized response summary. Defaults next to output_path.",
            },
            "api_url": {
                "type": "string",
                "description": "Override MiniMax T2A endpoint. Defaults to MINIMAX_TTS_API_URL or api-uw endpoint.",
            },
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=1, ram_mb=256, vram_mb=0, disk_mb=50, network_required=True
    )
    retry_policy = RetryPolicy(max_retries=2, retryable_errors=["timeout", "rate_limit"])
    idempotency_key_fields = ["text", "voice_id", "model", "model_id", "speed", "pitch"]
    side_effects = [
        "writes audio file to output_path",
        "writes sanitized MiniMax response metadata next to output_path",
        "calls MiniMax T2A API",
    ]
    user_visible_verification = ["Listen to generated audio for Mandarin naturalness and narrator fit"]
    quality_score = 0.9
    latency_p50_seconds = 6.0

    def get_status(self) -> ToolStatus:
        if self._api_key() and self._group_id():
            return ToolStatus.AVAILABLE
        return ToolStatus.UNAVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        # MiniMax pricing varies by model/account. Keep a conservative placeholder;
        # provider usage metadata is recorded when available.
        return round(len(inputs.get("text", "")) * 0.000015, 4)

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        api_key = self._api_key()
        group_id = self._group_id()
        if not api_key:
            return ToolResult(success=False, error="No MiniMax TTS API key. Set MINIMAX_TTS_API_KEY.")
        if not group_id:
            return ToolResult(success=False, error="No MiniMax group id. Set MINIMAX_GROUP_ID.")

        start = time.time()
        try:
            result = self._generate(inputs, api_key=api_key, group_id=group_id)
        except Exception as exc:
            return ToolResult(success=False, error=f"MiniMax TTS failed: {self._safe_error(exc)}")

        result.duration_seconds = round(time.time() - start, 2)
        if not result.cost_usd:
            result.cost_usd = self.estimate_cost(inputs)
        return result

    def _generate(self, inputs: dict[str, Any], *, api_key: str, group_id: str) -> ToolResult:
        import requests

        fmt = inputs.get("format", "mp3")
        output_path = Path(inputs.get("output_path", f"minimax_tts.{fmt}"))
        metadata_path = Path(inputs.get("metadata_path") or output_path.with_suffix(output_path.suffix + ".json"))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        metadata_path.parent.mkdir(parents=True, exist_ok=True)

        model = inputs.get("model") or inputs.get("model_id") or os.environ.get("MINIMAX_TTS_MODEL") or self.DEFAULT_MODEL
        voice_id = inputs.get("voice_id") or os.environ.get("MINIMAX_TTS_VOICE_ID") or self.DEFAULT_VOICE_ID
        speed = self._float_input(inputs, "speed", "MINIMAX_TTS_SPEED", 0.92)
        vol = self._numeric_input(inputs, "vol", "MINIMAX_TTS_VOL", 1)
        pitch = self._numeric_input(inputs, "pitch", "MINIMAX_TTS_PITCH", 0)
        emotion = inputs.get("emotion")
        if emotion is None:
            emotion = os.environ.get("MINIMAX_TTS_EMOTION")
        api_url = inputs.get("api_url") or os.environ.get("MINIMAX_TTS_API_URL") or self.DEFAULT_API_URL

        voice_setting = {
            "voice_id": voice_id,
            "speed": speed,
            "vol": vol,
            "pitch": pitch,
        }
        if emotion is not None:
            voice_setting["emotion"] = emotion

        payload = {
            "model": model,
            "text": inputs["text"],
            "stream": False,
            "language_boost": inputs.get("language_boost", "Chinese"),
            "output_format": "hex",
            "voice_setting": voice_setting,
            "audio_setting": {
                "sample_rate": inputs.get("sample_rate", 32000),
                "bitrate": inputs.get("bitrate", 128000),
                "format": fmt,
                "channel": inputs.get("channel", 1),
            },
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        response = requests.post(
            api_url,
            params={"GroupId": group_id},
            headers=headers,
            json=payload,
            timeout=(10, 120),
        )
        data = self._json_or_raise(response)
        self._raise_for_minimax_error(response.status_code, data)

        audio_hex = data.get("data", {}).get("audio")
        if not audio_hex:
            raise RuntimeError("MiniMax TTS response did not include data.audio")
        output_path.write_bytes(binascii.unhexlify(audio_hex))

        extra = data.get("extra_info") or {}
        summary = {
            "provider": self.provider,
            "model": model,
            "voice_id": voice_id,
            "trace_id": data.get("trace_id"),
            "base_resp": data.get("base_resp"),
            "extra_info": extra,
            "data_status": data.get("data", {}).get("status"),
        }
        metadata_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        audio_duration = self._audio_duration(output_path)
        cost = self._cost_from_usage(extra) or self.estimate_cost(inputs)
        return ToolResult(
            success=True,
            data={
                **summary,
                "format": fmt,
                "sample_rate": inputs.get("sample_rate", 32000),
                "speed": speed,
                "vol": vol,
                "pitch": pitch,
                "text_length": len(inputs.get("text", "")),
                "usage_characters": extra.get("usage_characters"),
                "audio_duration_seconds": round(audio_duration, 2) if audio_duration else None,
                "output": str(output_path),
                "metadata_path": str(metadata_path),
            },
            artifacts=[str(output_path), str(metadata_path)],
            cost_usd=cost,
            model=model,
        )

    @staticmethod
    def _api_key() -> str | None:
        return os.environ.get("MINIMAX_TTS_API_KEY") or os.environ.get("MINIMAX_API_KEY")

    @staticmethod
    def _group_id() -> str | None:
        return os.environ.get("MINIMAX_GROUP_ID") or os.environ.get("MINIMAX_GROUPID")

    @staticmethod
    def _float_input(inputs: dict[str, Any], key: str, env_key: str, default: float) -> float:
        if key in inputs and inputs[key] is not None:
            return float(inputs[key])
        if os.environ.get(env_key):
            return float(os.environ[env_key])
        return float(default)

    @staticmethod
    def _numeric_input(inputs: dict[str, Any], key: str, env_key: str, default: float) -> int | float:
        if key in inputs and inputs[key] is not None:
            value = float(inputs[key])
        elif os.environ.get(env_key):
            value = float(os.environ[env_key])
        else:
            value = float(default)
        return int(value) if value.is_integer() else value

    @staticmethod
    def _json_or_raise(response: Any) -> dict[str, Any]:
        try:
            return response.json()
        except ValueError as exc:
            raise RuntimeError(f"Non-JSON response from MiniMax API: HTTP {response.status_code}") from exc

    @staticmethod
    def _raise_for_minimax_error(http_status: int, payload: dict[str, Any]) -> None:
        base = payload.get("base_resp") or {}
        status_code = base.get("status_code")
        if http_status < 400 and status_code == 0:
            return
        message = base.get("status_msg") or payload.get("message") or "unknown error"
        raise RuntimeError(f"HTTP {http_status}, status_code {status_code}: {message}")

    @staticmethod
    def _safe_error(exc: Exception) -> str:
        text = str(exc)
        for key in (os.environ.get("MINIMAX_TTS_API_KEY"), os.environ.get("MINIMAX_API_KEY")):
            if key:
                text = text.replace(key, "[redacted]")
        return text

    @staticmethod
    def _audio_duration(path: Path) -> float | None:
        try:
            from tools.analysis.audio_probe import probe_duration

            return probe_duration(path)
        except Exception:
            return None

    @staticmethod
    def _cost_from_usage(extra_info: Any) -> float | None:
        if not isinstance(extra_info, dict):
            return None
        usage = extra_info.get("usage_characters")
        if not isinstance(usage, (int, float)):
            return None
        return round(float(usage) * 0.000015, 4)
