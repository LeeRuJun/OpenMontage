"""OpenMontage local API server.

Usage:
    uvicorn server.app:app --host 0.0.0.0 --port 8070
"""

from __future__ import annotations

import asyncio
import json

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from server.edit_api import router as edit_router
from server.smb_rough_cut_api import router as smb_rough_cut_router

app = FastAPI(title="OpenMontage API", docs_url="/docs", redoc_url=None)
app.include_router(edit_router)
app.include_router(smb_rough_cut_router)

# Allow 后羿 to call these APIs from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── SSE subscribers ──────────────────────────────────────────────────────────

_sse_queues: list[asyncio.Queue] = []


# ── API: Health ──────────────────────────────────────────────────────────────


@app.get("/api/health")
async def health() -> dict:
    return {"ok": True, "app": "openmontage"}


# ── API: Project State (Backlot-compatible) ───────────────────────────────────


@app.get("/api/project/{project_id}/state")
async def project_state(project_id: str):
    """Return full pipeline stage state for a project."""
    import asyncio as aio
    from backlot.state import PROJECTS_DIR, load_board_state, summarize_project

    project_dir = PROJECTS_DIR / project_id
    if not project_dir.is_dir():
        raise HTTPException(status_code=404, detail=f"Unknown project: {project_id}")

    def _load():
        try:
            return load_board_state(project_dir)
        except Exception:
            try:
                return summarize_project(project_dir)
            except Exception:
                return {"project_id": project_id, "error": "unreadable"}

    return await aio.to_thread(_load)


@app.get("/api/project/{project_id}/events")
async def project_events(project_id: str, request: Request) -> StreamingResponse:
    """Stream project-specific stage changes for Backlot-compatible clients."""
    async def stream():
        q: asyncio.Queue = asyncio.Queue(maxsize=64)
        _sse_queues.append(q)
        try:
            yield f"data: {json.dumps({'event': 'connected', 'project_id': project_id})}\n\n"
            while True:
                if await request.is_disconnected():
                    return
                try:
                    payload = await asyncio.wait_for(q.get(), timeout=15)
                except asyncio.TimeoutError:
                    yield "data: {\"event\": \"heartbeat\"}\n\n"
                    continue
                data = json.loads(payload)
                if data.get("project_id") == project_id:
                    yield f"data: {payload}\n\n"
        finally:
            _sse_queues.remove(q)

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
