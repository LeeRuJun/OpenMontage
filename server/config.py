"""Config loader — reads server/config.ini."""

from __future__ import annotations

import configparser
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent / "config.ini"

_config = configparser.ConfigParser()
_config.read(CONFIG_PATH, encoding="utf-8")


def get(section: str, key: str, fallback: str = "") -> str:
    return _config.get(section, key, fallback=fallback)


def smb_host() -> str: return get("SMB", "host")
def smb_share() -> str: return get("SMB", "share")
def smb_path() -> str: return get("SMB", "path")
def smb_user() -> str: return get("SMB", "username")
def smb_pass() -> str: return get("SMB", "password")

def llm_model() -> str: return get("LLM", "model")
def llm_api_key() -> str: return get("LLM", "api_key")
def llm_base_url() -> str: return get("LLM", "base_url")

def server_port() -> int: return int(get("Server", "port", fallback="8070"))
