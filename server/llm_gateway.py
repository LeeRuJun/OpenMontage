"""
LLM Gateway — OpenAI-compatible chat completions against the company AIGATE.

Faithful port of fs-houyi `back/app/services/llm_service.py::_chat`
(requests-based, no openai SDK). Config comes from server/config.ini [LLM].
"""

from __future__ import annotations

import logging
import os

import requests

from server.config import llm_base_url, llm_api_key, llm_model

logger = logging.getLogger("openmontage.llm_gateway")

DEFAULT_TIMEOUT_SECONDS = 300
DEFAULT_MAX_TOKENS = 4096


def _chat(system: str, user: str, max_tokens: int = DEFAULT_MAX_TOKENS) -> str | None:
    """Single-turn chat completion. Returns assistant text, or None on failure.

    Mirrors fs-houyi llm_service._chat semantics:
    - missing API key → None
    - network/timeout/empty response → None (caller decides failure handling)
    """
    api_key = llm_api_key()
    base_url = llm_base_url()
    model = llm_model()
    if not api_key:
        logger.warning("LLM gateway: no api_key configured")
        return None

    timeout = float(os.environ.get("LLM_TIMEOUT_SECONDS", DEFAULT_TIMEOUT_SECONDS))
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.1,
        "max_tokens": max_tokens,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    url = base_url.rstrip("/") + "/chat/completions"

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        return content.strip() if content else None
    except Exception:
        logger.exception("LLM gateway call failed: %s", url)
        return None
