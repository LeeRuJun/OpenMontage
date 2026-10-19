"""
Editor API — 剪映式手动编辑器后端

Pure API. 素材浏览由后羿负责，后羿把文件路径直接放在 edit_decisions 的 cuts[].source 中传给后端。

Routes (all under /api):
  POST   /api/edit-sessions                 创建编辑会话
  GET    /api/edit-sessions/{id}            加载会话 (edit_decisions)
  PUT    /api/edit-sessions/{id}            保存会话
  DELETE /api/edit-sessions/{id}            删除会话

  POST   /api/edit-sessions/{id}/render     提交渲染
  GET    /api/edit-sessions/{id}/render-status  查询渲染进度
  GET    /api/edit-sessions/{id}/download   下载成品
"""

from __future__ import annotations

import json
import os
import shutil
import threading
import time
import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from server.media_editing import trim_segment, concat_segments, add_overlay_text
from server.smb_browser import get_local_path

router = APIRouter(prefix="/api", tags=["editor"])

PROJECTS_DIR = Path(__file__).resolve().parent.parent / "projects"
_render_tasks: dict[str, dict[str, Any]] = {}


# ── helpers ──────────────────────────────────────────────────────────────────

def _session_dir(session_id: str) -> Path:
    return PROJECTS_DIR / session_id


def _load_session(session_id: str) -> dict:
    sd = _session_dir(session_id)
    dec_path = sd / "edit_decisions.json"
    if not dec_path.exists():
        raise HTTPException(status_code=404, detail="会话不存在")
    return json.loads(dec_path.read_text(encoding="utf-8"))


def _save_session(session_id: str, data: dict) -> None:
    sd = _session_dir(session_id)
    sd.mkdir(parents=True, exist_ok=True)
    dec_path = sd / "edit_decisions.json"
    dec_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    proj_path = sd / "project.json"
    if not proj_path.exists():
        proj_path.write_text(json.dumps({
            "id": session_id,
            "title": data.get("metadata", {}).get("title", session_id[:8]),
            "pipeline_type": "manual-editor",
            "created_at": time.time(),
        }, ensure_ascii=False, indent=2), encoding="utf-8")


# ── Edit Sessions ────────────────────────────────────────────────────────────

@router.post("/edit-sessions")
def create_session(body: dict):
    """创建新的编辑会话。

    Request: { "title": "项目名称" }
    """
    session_id = uuid.uuid4().hex[:12]
    title = body.get("title", "未命名项目")
    data = {
        "version": "1.0",
        "cuts": [],
        "overlays": [],
        "audio": {},
        "render_runtime": "ffmpeg",
        "metadata": {"title": title, "session_id": session_id},
    }
    _save_session(session_id, data)
    return {"session_id": session_id, "title": title}


@router.get("/edit-sessions/{session_id}")
def load_session(session_id: str):
    """加载编辑会话的 edit_decisions。"""
    return _load_session(session_id)


@router.put("/edit-sessions/{session_id}")
def save_session(session_id: str, body: dict):
    """保存编辑会话。前端传入完整的 edit_decisions JSON。

    cuts[].source 应为后羿解析后的本地文件路径。
    """
    sd = _session_dir(session_id)
    if not (sd / "edit_decisions.json").exists():
        raise HTTPException(status_code=404, detail="会话不存在")
    body.setdefault("version", "1.0")
    if "render_runtime" not in body:
        body["render_runtime"] = "ffmpeg"
    _save_session(session_id, body)
    return {"ok": True, "session_id": session_id}


@router.delete("/edit-sessions/{session_id}")
def delete_session(session_id: str):
    """删除编辑会话及所有中间文件。"""
    sd = _session_dir(session_id)
    if not sd.is_dir():
        raise HTTPException(status_code=404, detail="会话不存在")
    shutil.rmtree(sd)
    return {"ok": True, "deleted": session_id}


# ── Render ───────────────────────────────────────────────────────────────────

def _do_render(session_id: str) -> None:
    task = _render_tasks.get(session_id)
    if not task:
        return
    try:
        task["status"] = "running"
        task["progress"] = 5
        task["message"] = "加载编辑决策..."

        data = _load_session(session_id)
        cuts = data.get("cuts", [])
        if not cuts:
            raise RuntimeError("时间轴上没有片段")

        output_dir = _session_dir(session_id) / "render_output"
        output_dir.mkdir(parents=True, exist_ok=True)
        final_path = str(_session_dir(session_id) / "final.mp4")

        meta = data.get("metadata", {})
        tw = meta.get("output_width", 1080)
        th = meta.get("output_height", 1920)

        total = len(cuts)
        clips: list[str] = []

        for i, cut in enumerate(cuts):
            src_path = cut.get("source", "")
            in_sec = cut.get("in_seconds", 0)
            out_sec = cut.get("out_seconds", 0)
            duration = out_sec - in_sec

            if duration <= 0:
                continue
            if not src_path:
                continue
            if not os.path.exists(src_path):
                task["message"] = f"下载素材 {i+1}/{total}..."
                src_path = get_local_path(src_path) or ""
            if not src_path or not os.path.exists(src_path):
                continue

            clip_path = str(output_dir / f"clip_{i:04d}.mp4")
            task["progress"] = 10 + int((i / total) * 50)
            task["message"] = f"裁剪 {i+1}/{total}..."
            trim_segment(
                src_path, clip_path,
                start=in_sec, duration=duration,
                target_width=tw, target_height=th,
            )
            clips.append(clip_path)

        if not clips:
            raise RuntimeError("没有有效片段可渲染")

        task["progress"] = 65
        task["message"] = "拼接片段..."

        if len(clips) == 1:
            shutil.copy(clips[0], final_path)
        else:
            concat_segments(clips, final_path)

        # Overlays
        overlays = data.get("overlays", [])
        if overlays:
            task["progress"] = 80
            task["message"] = "添加叠加层..."
            current = final_path
            for i, ov in enumerate(overlays):
                out = str(output_dir / f"overlay_{i:04d}.mp4")
                add_overlay_text(
                    current, out,
                    text=ov.get("text", ov.get("subtitle", "")),
                    position=ov.get("position", "top"),
                    font_size=ov.get("font_size", 48),
                )
                current = out
            if current != final_path:
                shutil.move(current, final_path)

        task["progress"] = 100
        task["status"] = "done"
        task["message"] = "渲染完成"
        task["output_file"] = final_path
    except Exception as e:
        task["status"] = "failed"
        task["error"] = str(e)
        task["message"] = f"渲染失败: {e}"


@router.post("/edit-sessions/{session_id}/render")
def start_render(session_id: str, body: dict | None = None):
    """提交渲染任务。异步执行，通过 render-status 轮询进度。

    Request (可选):
        { "output_width": 1080, "output_height": 1920 }
    """
    sd = _session_dir(session_id)
    if not (sd / "edit_decisions.json").exists():
        raise HTTPException(status_code=404, detail="会话不存在")

    data = _load_session(session_id)
    if not data.get("cuts"):
        raise HTTPException(status_code=400, detail="时间轴上没有片段，无法渲染")

    if body:
        if "output_width" in body:
            data.setdefault("metadata", {})["output_width"] = body["output_width"]
        if "output_height" in body:
            data.setdefault("metadata", {})["output_height"] = body["output_height"]
        _save_session(session_id, data)

    _render_tasks[session_id] = {
        "status": "queued",
        "progress": 0,
        "message": "排队中...",
        "output_file": None,
        "error": None,
    }

    t = threading.Thread(target=_do_render, args=(session_id,), daemon=True)
    t.start()

    return {"session_id": session_id, "status": "queued"}


@router.get("/edit-sessions/{session_id}/render-status")
def render_status(session_id: str):
    """查询渲染进度。"""
    task = _render_tasks.get(session_id)
    if not task:
        return {"status": "unknown", "message": "没有渲染任务"}
    return task


@router.get("/edit-sessions/{session_id}/download")
def download_render(session_id: str):
    """下载渲染完成的最终视频。"""
    task = _render_tasks.get(session_id)
    if task and task.get("output_file"):
        path = task["output_file"]
        if os.path.exists(path):
            return FileResponse(path, media_type="video/mp4",
                                filename=f"edit_{session_id}.mp4")

    candidate = str(_session_dir(session_id) / "final.mp4")
    if os.path.exists(candidate):
        return FileResponse(candidate, media_type="video/mp4",
                            filename=f"edit_{session_id}.mp4")

    raise HTTPException(status_code=404, detail="成品不存在，请先渲染")
