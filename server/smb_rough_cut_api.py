"""
SMB Rough Cut API — OpenMontage 粗剪接口

Routes (all under /api):
  POST /api/smb-rough-cut/tasks                    按日期范围异步触发粗剪
  GET  /api/smb-rough-cut/tasks/{task_id}          查询任务状态
  GET  /api/smb-rough-cut/assets?date=YYYY-MM-DD   枚举某日期已上传的 SMB 产物
  GET  /api/smb-rough-cut/assets/{date}/videos/{file_name}  下载产物（支持 Range）
"""

from __future__ import annotations

import re
import threading
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse

from server import smb_rough_cut

router = APIRouter(prefix="/api/smb-rough-cut", tags=["smb-rough-cut"])

MAX_DATE_RANGE_DAYS = 31

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _parse_date(value: str) -> date:
    if not _DATE_RE.match(value):
        raise HTTPException(status_code=400, detail=f"非法日期: {value}")
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"非法日期: {value}")


# ── POST /api/smb-rough-cut/tasks ────────────────────────────────────────────


@router.post("/tasks")
async def create_tasks(request: Request) -> dict:
    """按日期范围触发粗剪。支持 {date} 单日或 {start_date,end_date} 范围。

    异步：入队后立即返回 task_id，后台线程逐个日期执行。
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    if body.get("date"):
        start = end = _parse_date(str(body["date"]))
    else:
        start = _parse_date(str(body.get("start_date", "")))
        end = _parse_date(str(body.get("end_date", "")))
        if end < start:
            raise HTTPException(status_code=400, detail="end_date 不能早于 start_date")

    if (end - start).days + 1 > MAX_DATE_RANGE_DAYS:
        raise HTTPException(status_code=400, detail=f"日期范围不能超过 {MAX_DATE_RANGE_DAYS} 天")

    days = [start + timedelta(days=i) for i in range((end - start).days + 1)]

    # Idempotency: if any date is already running, return that task (409-ish).
    for day in days:
        existing_id = smb_rough_cut._active_dates.get(day.isoformat())
        if existing_id and smb_rough_cut.get_task(existing_id):
            existing = smb_rough_cut.get_task(existing_id)
            if existing.get("status") in ("queued", "running"):
                raise HTTPException(
                    status_code=409,
                    detail=f"该日期粗剪任务正在运行: {existing_id}",
                )

    task_id = f"rc_{start.isoformat()}_{end.isoformat()}_{len(days)}d"
    task_ids: list[str] = []

    def _worker(day: date) -> None:
        smb_rough_cut.run_rough_cut_for_date(day)

    for day in days:
        # Guard against races within this request's loop.
        existing_id = smb_rough_cut._active_dates.get(day.isoformat())
        if existing_id and smb_rough_cut.get_task(existing_id):
            t = smb_rough_cut.get_task(existing_id)
            if t.get("status") in ("queued", "running"):
                task_ids.append(existing_id)
                continue
        tid = f"rc_{day.isoformat()}_{len(smb_rough_cut._tasks) + 1:04d}"
        smb_rough_cut._new_task(tid, day)
        smb_rough_cut._active_dates[day.isoformat()] = tid
        task_ids.append(tid)
        threading.Thread(target=_worker, args=(day,), daemon=True).start()

    return {
        "task_id": task_ids[0] if task_ids else task_id,
        "dates": [d.isoformat() for d in days],
        "task_ids": task_ids,
        "status": "queued",
        "message": f"已入队 {len(task_ids)} 个日期的粗剪任务",
    }


# ── GET /api/smb-rough-cut/tasks/{task_id} ────────────────────────────────────


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str) -> dict:
    task = smb_rough_cut.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")
    return task


# ── GET /api/smb-rough-cut/assets?date= ───────────────────────────────────────


@router.get("/assets")
async def list_date_assets(date: str) -> dict:
    """枚举某日期已上传到 SMB 广告素材库的产物。"""
    day = _parse_date(date)
    remote_dir = f"直播素材/{day:%Y-%m}"
    try:
        from server.smb_browser import list_files
        result = list_files(remote_dir)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"SMB 枚举失败: {exc}")

    prefix = f"{day.strftime('%d')}_"
    files = [
        f for f in result.get("files", [])
        if f.get("name", "").startswith(prefix)
    ]
    return {"date": day.isoformat(), "remote_dir": remote_dir, "assets": files}


# ── GET /api/smb-rough-cut/assets/{date}/videos/{file_name} ──────────────────


@router.get("/assets/{date}/videos/{file_name}")
async def download_asset_video(date: str, file_name: str) -> FileResponse:
    """下载某日期的产物视频（支持 HTTP Range）。"""
    day = _parse_date(date)
    safe_name = Path(file_name).name
    remote_path = f"直播素材/{day:%Y-%m}/{safe_name}"
    try:
        from server.smb_browser import get_local_path
        local = get_local_path(remote_path)
    except Exception:
        local = None
    if not local:
        raise HTTPException(status_code=404, detail=f"产物不存在: {remote_path}")
    return FileResponse(local, media_type="video/mp4", filename=safe_name)
