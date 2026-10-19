"""
SMB Video Asset Browser — pysmb-based, no mount needed.

Reads video files from the SMB share configured in server/config.ini.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any, Optional

from smb.SMBConnection import SMBConnection
from smb.base import SharedDevice

from server.config import smb_host, smb_share, smb_path, smb_user, smb_pass

VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv", ".wmv", ".m4v"}
CACHE_DIR = Path(tempfile.gettempdir()) / "openmontage_smb_cache"


def _connect() -> SMBConnection:
    """Create an authenticated SMB connection."""
    conn = SMBConnection(
        username=smb_user(),
        password=smb_pass(),
        my_name="openmontage",
        remote_name=smb_host(),
        domain="",
        use_ntlm_v2=True,
        is_direct_tcp=True,
    )
    ok = conn.connect(smb_host(), port=445, timeout=15)
    if not ok:
        raise ConnectionError(f"SMB auth to {smb_host()} failed — check credentials")
    return conn


def _full_remote(directory: str = "") -> str:
    """Build a path inside the SMB share without duplicating share/base prefixes."""
    base = smb_path().strip("/")
    remote = (directory or "").replace("\\", "/").strip("/")

    share = smb_share().strip("/")
    if share and (remote == share or remote.startswith(f"{share}/")):
        remote = remote[len(share):].strip("/")

    if not remote:
        return base
    if base and (remote == base or remote.startswith(f"{base}/")):
        return remote
    return f"{base}/{remote}".strip("/")


def list_files(directory: str = "") -> dict[str, Any]:
    """List video files and directories in the SMB share.

    Returns: { "files": [...], "directories": [...], "path": "..." }
    """
    try:
        conn = _connect()
    except Exception as e:
        return {"error": f"连接 SMB 失败: {e}", "files": [], "directories": [], "path": directory}

    try:
        remote = _full_remote(directory)
        files = []
        dirs = []

        for item in conn.listPath(smb_share(), remote):
            name = item.filename
            if name in (".", ".."):
                continue
            if item.isDirectory:
                dirs.append({"name": name})
            else:
                ext = os.path.splitext(name)[1].lower()
                if ext in VIDEO_EXTS:
                    files.append({
                        "name": name,
                        "size": item.file_size,
                        "size_mb": round(item.file_size / (1024 * 1024), 1) if item.file_size > 0 else 0,
                        "remote_path": f"{directory}/{name}".lstrip("/") if directory else name,
                        "created": item.last_attr_change_time if hasattr(item, 'last_attr_change_time') else None,
                    })

        files.sort(key=lambda f: f.get("created") or 0, reverse=True)
        return {"files": files, "directories": sorted(dirs, key=lambda d: d["name"]), "path": directory}
    except Exception as e:
        return {"error": str(e), "files": [], "directories": [], "path": directory}
    finally:
        try:
            conn.close()
        except Exception:
            pass


def search_files(query: str, directory: str = "") -> dict[str, Any]:
    """Search video files matching a query."""
    result = list_files(directory)
    if result.get("files"):
        q = query.lower()
        result["files"] = [f for f in result["files"] if q in f["name"].lower()]
        result["query"] = query
    return result


def get_local_path(remote_path: str) -> Optional[str]:
    """Download a remote file to local cache, return the local path."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    filename = Path(remote_path).name
    local = CACHE_DIR / filename

    if local.exists() and local.stat().st_size > 0:
        return str(local)

    try:
        conn = _connect()
    except Exception:
        return None

    try:
        full = _full_remote(remote_path)
        with open(local, "wb") as f:
            conn.retrieveFile(smb_share(), full, f)
        return str(local) if local.exists() else None
    except Exception:
        return None
    finally:
        try:
            conn.close()
        except Exception:
            pass


def _ensure_remote_dirs(conn: SMBConnection, remote_dir: str) -> None:
    """Create remote directories under the configured SMB base path."""
    parts = [p for p in remote_dir.strip("/").split("/") if p]
    current = smb_path().strip("/")
    for part in parts:
        current = f"{current}/{part}".strip("/")
        try:
            conn.createDirectory(smb_share(), current)
        except Exception:
            # Directory may already exist; pysmb does not expose a stable
            # cross-platform errno here, so treat failures as idempotent.
            pass


def upload_local_file(local_path: str, remote_path: str) -> Optional[str]:
    """Upload a local file to the configured SMB share.

    remote_path is relative to the configured SMB base path. Returns that
    relative path on success, or None on failure.
    """
    if not local_path or not os.path.exists(local_path):
        return None

    try:
        conn = _connect()
    except Exception:
        return None

    try:
        remote_path = remote_path.strip("/")
        remote_dir = os.path.dirname(remote_path)
        if remote_dir:
            _ensure_remote_dirs(conn, remote_dir)
        full = _full_remote(remote_path)
        with open(local_path, "rb") as f:
            conn.storeFile(smb_share(), full, f)
        return remote_path
    except Exception:
        return None
    finally:
        try:
            conn.close()
        except Exception:
            pass
