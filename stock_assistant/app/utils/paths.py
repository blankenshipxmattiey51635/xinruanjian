"""Filesystem helpers for the desktop application."""
from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    """Return the root folder that contains this project."""
    return Path(__file__).resolve().parents[2]


def ensure_runtime_dirs(root: Path | None = None) -> dict[str, Path]:
    """Create and return standard runtime directories."""
    base = root or project_root()
    dirs = {
        "data": base / "data",
        "config": base / "config",
        "logs": base / "logs",
        "models": base / "models",
        "exports": base / "exports",
    }
    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    return dirs
