"""Safe filesystem helpers for project scaffolding."""

from __future__ import annotations

from pathlib import Path


def create_folder(dir_path: str | Path) -> None:
    """Create a directory tree. No-op if it already exists."""
    Path(dir_path).mkdir(parents=True, exist_ok=True)


def create_file(file_path: str | Path, content: str) -> None:
    """Write *content* to *file_path*, creating parent directories as needed."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
