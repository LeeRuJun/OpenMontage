"""Offline tests for the concurrent image batch runner."""

from __future__ import annotations

import threading
import time
from pathlib import Path

import pytest

from tools.base_tool import BaseTool, ToolResult, ToolStatus
from tools.graphics.image_batch import ImageBatchRunner
from tools.graphics.image_selector import ImageSelector


class FakeSelector:
    def __init__(self, handler):
        self.handler = handler
        self.calls = []
        self.lock = threading.Lock()

    def execute(self, inputs):
        with self.lock:
            self.calls.append(dict(inputs))
        return self.handler(inputs)


def test_bounded_concurrency_and_input_order(tmp_path):
    active = 0
    peak = 0
    lock = threading.Lock()

    def execute(inputs):
        nonlocal active, peak
        with lock:
            active += 1
            peak = max(peak, active)
        time.sleep(0.02 * (5 - int(inputs["prompt"])))
        path = Path(inputs["output_path"])
        path.write_bytes(inputs["prompt"].encode())
        with lock:
            active -= 1
        return ToolResult(success=True, artifacts=[str(path)], data={"selected_provider": "fake"})

    selector = FakeSelector(execute)
    requests = [
        {"prompt": str(i), "output_path": str(tmp_path / f"{i}.png")}
        for i in range(5)
    ]
    result = ImageBatchRunner(selector).run(requests, max_workers=2)

    assert peak == 2
    assert [item["index"] for item in result["results"]] == list(range(5))
    assert [item["status"] for item in result["results"]] == ["succeeded"] * 5
    assert result["totals"] == {
        "requested": 5, "succeeded": 5, "failed": 0, "skipped": 0,
        "cancelled": 0, "attempts": 5, "cost": 0.0,
    }


def test_retryable_timeout_uses_exponential_backoff(monkeypatch, tmp_path):
    attempts = 0
    delays = []

    def execute(inputs):
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            return ToolResult(success=False, error="timeout from provider")
        path = Path(inputs["output_path"])
        path.write_bytes(b"ok")
        return ToolResult(success=True, artifacts=[str(path)], cost_usd=0.25, data={"selected_tool": "fake"})

    selector = FakeSelector(execute)
    result = ImageBatchRunner(selector).run(
        [{"prompt": "retry", "output_path": str(tmp_path / "retry.png")}],
        max_retries=2,
        backoff_seconds=0.01,
        sleep=delays.append,
    )

    assert attempts == 3
    assert delays == [0.01, 0.02]
    assert result["results"][0]["attempts"] == 3
    assert result["results"][0]["cost"] == 0.25
    assert result["totals"]["cost"] == 0.25


def test_skip_existing_nonempty_output_without_call(tmp_path):
    output = tmp_path / "already.png"
    output.write_bytes(b"existing")
    selector = FakeSelector(lambda inputs: pytest.fail("existing output must be skipped"))

    result = ImageBatchRunner(selector).run(
        [{"prompt": "not called", "output_path": str(output)}]
    )

    item = result["results"][0]
    assert item["status"] == "skipped"
    assert item["attempts"] == 0
    assert item["artifacts"] == [str(output)]
    assert result["totals"]["skipped"] == 1


def test_duplicate_output_paths_rejected_before_execution(tmp_path):
    selector = FakeSelector(lambda inputs: pytest.fail("duplicate validation must happen first"))
    requests = [
        {"prompt": "one", "output_path": str(tmp_path / "same.png")},
        {"prompt": "two", "output_path": str(tmp_path / "same.png")},
    ]

    with pytest.raises(ValueError, match="duplicate output_path"):
        ImageBatchRunner(selector).run(requests)
    assert selector.calls == []


def test_partial_failure_is_returned_and_does_not_raise(tmp_path):
    def execute(inputs):
        if inputs["prompt"] == "bad":
            return ToolResult(success=False, error="invalid prompt")
        output = Path(inputs["output_path"])
        output.write_bytes(b"good")
        return ToolResult(success=True, artifacts=[str(output)], data={})

    result = ImageBatchRunner(FakeSelector(execute)).run([
        {"prompt": "good", "output_path": str(tmp_path / "good.png")},
        {"prompt": "bad", "output_path": str(tmp_path / "bad.png")},
    ])

    assert [item["status"] for item in result["results"]] == ["succeeded", "failed"]
    assert result["results"][1]["error"] == "invalid prompt"
    assert result["totals"]["succeeded"] == 1
    assert result["totals"]["failed"] == 1


def test_selector_allowlist_keeps_input_fidelity_and_workflow_json_separate(monkeypatch):
    class Provider(BaseTool):
        name = "fake"
        provider = "fake"
        capability = "image_generation"
        input_schema = {"properties": {"prompt": {}, "input_fidelity": {}, "workflow_json": {}}}
        supports = {"custom_workflow": True}
        best_for = []

        def get_status(self):
            return ToolStatus.AVAILABLE

        def execute(self, inputs):
            self.inputs = inputs
            return ToolResult(success=True, data={})

    provider = Provider()
    monkeypatch.setattr(ImageSelector, "_providers", lambda self: [provider])
    result = ImageSelector().execute({
        "prompt": "x", "preferred_provider": "fake",
        "input_fidelity": "high", "workflow_json": "{}", "output_node": "1",
    })

    assert result.success
    assert provider.inputs["input_fidelity"] == "high"
    assert provider.inputs["workflow_json"] == "{}"
    assert "input_fidelityworkflow_json" not in provider.inputs
