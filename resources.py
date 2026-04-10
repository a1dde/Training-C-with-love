"""Paths for dev vs PyInstaller frozen bundle."""

from __future__ import annotations

import sys
from pathlib import Path


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False)) and getattr(sys, "_MEIPASS", None) is not None


def bundle_dir() -> Path:
    """Directory with bundled resources (memes, assets) — _MEIPASS when frozen."""
    if is_frozen():
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            return Path(meipass)
    return Path(__file__).resolve().parent


def user_data_dir() -> Path:
    """Where user-writable files live: next to exe when frozen, else project root."""
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def resource_path(*parts: str) -> Path:
    return bundle_dir().joinpath(*parts)
