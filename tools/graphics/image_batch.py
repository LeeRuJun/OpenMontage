"""Concurrent orchestration for independent image generation requests.

The batch runner is deliberately separate from :class:`ImageSelector`: selector
routing and ``execute`` semantics remain synchronous and unchanged.  This
module adds bounded concurrency, resumability, and per-request accounting on
top of that existing tool contract.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import time
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

from tools.base_tool import ToolResult
from tools.graphics.image_selector import ImageSelector


_RETRYABLE_MARKERS = ("timeout", "timed out", "rate_limit", "rate limit", "429")


def _request_key(request: Mapping[str, Any], index: int) -> str:
    """Return a stable key for a request's content and position."""
    payload = {"index": index, "request": request}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _output_path(request: Mapping[str, Any]) -> Path | None:
    value = request.get("output_path")
    if not value or not isinstance(value, (str, Path)):
        return None
    return Path(value).expanduser()


def _is_valid_output(path: Path | None) -> bool:
    """A resumable output must be a regular, non-empty file."""
    if path is None:
        return False
    try:
        return path.is_file() and path.stat().st_size > 0
    except OSError:
        return False


def _retryable(error: BaseException | str | None) -> bool:
    text = str(error or "").lower()
    # HTTP 5xx responses are commonly reported as ``500``, ``HTTP 503``, etc.
    if any(marker in text for marker in _RETRYABLE_MARKERS):
        return True
    return any(f"5{code}" in text for code in range(0, 10)) or "5xx" in text


def _selected_metadata(data: Mapping[str, Any]) -> dict[str, Any]:
    """Keep provider-selection details without copying arbitrary payloads."""
    keys = (
        "selected_tool", "selected_provider", "selection_reason", "provider_score",
        "alternatives_considered", "selected_tool_agent_skills",
        "selected_tool_usage_location", "selected_tool_best_for",
    )
    return {key: data[key] for key in keys if key in data}


class ImageBatchRunner:
    """Run independent requests through a synchronous ``ImageSelector``.

    ``selector`` is injectable so callers and tests can provide an already
    configured selector (or a fake with the same ``execute`` method).
    """

    def __init__(self, selector: ImageSelector | None = None) -> None:
        self.selector = selector or ImageSelector()

    def run(
        self,
        requests: Iterable[Mapping[str, Any]],
        *,
        max_workers: int = 3,
        max_retries: int = 2,
        backoff_seconds: float = 1.0,
        fail_fast: bool = False,
        sleep: Callable[[float], None] = time.sleep,
    ) -> dict[str, Any]:
        """Generate all requests and return ordered, structured results.

        Validation errors (including duplicate output paths) are raised before
        any work starts. Provider/API errors are captured in item results and
        do not raise, allowing a partial batch to complete.
        """
        items = [dict(request) for request in requests]
        if max_workers < 1:
            raise ValueError("max_workers must be at least 1")
        if max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if backoff_seconds < 0:
            raise ValueError("backoff_seconds must be non-negative")

        self._validate_requests(items)
        results: list[dict[str, Any] | None] = [None] * len(items)
        if not items:
            return self._aggregate(results)

        with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="image-batch") as pool:
            futures: dict[Future[dict[str, Any]], int] = {
                pool.submit(
                    self._run_one,
                    index,
                    request,
                    max_retries,
                    backoff_seconds,
                    sleep,
                ): index
                for index, request in enumerate(items)
            }
            stop_submitting = False
            for future in as_completed(futures):
                index = futures[future]
                try:
                    results[index] = future.result()
                except Exception as exc:  # defensive: item failures never escape the batch API
                    results[index] = self._failed_result(index, items[index], 1, str(exc))
                if fail_fast and results[index]["status"] == "failed":
                    stop_submitting = True
                    for pending, pending_index in futures.items():
                        if pending is not future and pending.cancel():
                            results[pending_index] = self._cancelled_result(
                                pending_index, items[pending_index]
                            )
            # Futures that raced cancellation are still guaranteed a result.
            for index, result in enumerate(results):
                if result is None:
                    results[index] = self._cancelled_result(index, items[index]) if stop_submitting else self._failed_result(
                        index, items[index], 1, "Batch worker did not return a result"
                    )

        return self._aggregate(results)

    async def run_async(self, requests: Iterable[Mapping[str, Any]], **kwargs: Any) -> dict[str, Any]:
        """Async facade that keeps provider execution off the event loop."""
        return await asyncio.to_thread(self.run, requests, **kwargs)

    def _validate_requests(self, requests: list[dict[str, Any]]) -> None:
        seen: dict[str, int] = {}
        for index, request in enumerate(requests):
            if not isinstance(request, dict):
                raise ValueError(f"request {index} must be a mapping")
            path = _output_path(request)
            if path is None:
                continue
            key = str(path.absolute())
            if key in seen:
                raise ValueError(
                    f"duplicate output_path {path!s} in requests {seen[key]} and {index}"
                )
            seen[key] = index

    def _run_one(
        self,
        index: int,
        request: dict[str, Any],
        max_retries: int,
        backoff_seconds: float,
        sleep: Callable[[float], None],
    ) -> dict[str, Any]:
        key = _request_key(request, index)
        path = _output_path(request)
        if _is_valid_output(path):
            return {
                "index": index,
                "task_id": key,
                "status": "skipped",
                "attempts": 0,
                "error": None,
                "cost": 0.0,
                "artifacts": [str(path)],
                "selected_metadata": {},
            }

        inputs = dict(request)
        inputs.setdefault("external_task_id", key)
        attempts = 0
        last_error: str | None = None
        while attempts <= max_retries:
            attempts += 1
            try:
                result = self.selector.execute(inputs)
            except Exception as exc:  # selectors should return ToolResult, but be defensive
                result = ToolResult(success=False, error=str(exc))
            if result.success:
                data = result.data or {}
                return {
                    "index": index,
                    "task_id": key,
                    "status": "succeeded",
                    "attempts": attempts,
                    "error": None,
                    "cost": float(result.cost_usd or 0.0),
                    "artifacts": list(result.artifacts or data.get("outputs", [])),
                    "selected_metadata": _selected_metadata(data),
                }
            last_error = result.error or "Image generation failed"
            if attempts > max_retries or not _retryable(last_error):
                break
            sleep(backoff_seconds * (2 ** (attempts - 1)))

        return self._failed_result(index, request, attempts, last_error or "Image generation failed", key=key)

    @staticmethod
    def _failed_result(
        index: int, request: Mapping[str, Any], attempts: int, error: str, *, key: str | None = None
    ) -> dict[str, Any]:
        return {
            "index": index,
            "task_id": key or _request_key(request, index),
            "status": "failed",
            "attempts": attempts,
            "error": error,
            "cost": 0.0,
            "artifacts": [],
            "selected_metadata": {},
        }

    @staticmethod
    def _cancelled_result(index: int, request: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "index": index,
            "task_id": _request_key(request, index),
            "status": "cancelled",
            "attempts": 0,
            "error": "Cancelled after another request failed (fail_fast=True)",
            "cost": 0.0,
            "artifacts": [],
            "selected_metadata": {},
        }

    @staticmethod
    def _aggregate(results: list[dict[str, Any] | None]) -> dict[str, Any]:
        ordered = [result for result in results if result is not None]
        return {
            "results": ordered,
            "totals": {
                "requested": len(results),
                "succeeded": sum(item["status"] == "succeeded" for item in ordered),
                "failed": sum(item["status"] == "failed" for item in ordered),
                "skipped": sum(item["status"] == "skipped" for item in ordered),
                "cancelled": sum(item["status"] == "cancelled" for item in ordered),
                "attempts": sum(item["attempts"] for item in ordered),
                "cost": round(sum(item["cost"] for item in ordered), 10),
            },
        }


def generate_images(
    requests: Iterable[Mapping[str, Any]],
    *,
    selector: ImageSelector | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Convenience wrapper around :class:`ImageBatchRunner`."""
    return ImageBatchRunner(selector).run(requests, **kwargs)


async def generate_images_async(
    requests: Iterable[Mapping[str, Any]],
    *,
    selector: ImageSelector | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Async convenience wrapper around :class:`ImageBatchRunner`."""
    return await ImageBatchRunner(selector).run_async(requests, **kwargs)


__all__ = ["ImageBatchRunner", "generate_images", "generate_images_async"]
