"""Filesystem plugin — safe file and directory operations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aura_mcp.plugins.base import BasePlugin
from aura_mcp.utils.file_utils import create_file, create_folder
from aura_mcp.utils.logger import get_logger


class FilesystemPlugin(BasePlugin):
    """Create files, create folders, and list directories."""

    @property
    def name(self) -> str:
        return "filesystem"

    async def execute(self, intent: dict[str, Any]) -> dict[str, Any]:
        logger = get_logger()
        action = intent.get("action", "")
        logger.info("Filesystem plugin executing action: %s", action)

        if action == "create_folder":
            return self._create_folder(intent["path"])

        if action == "create_file":
            return self._create_file(intent["path"], intent["content"])

        if action == "list_directory":
            return self._list_directory(intent["path"])

        raise ValueError(f'FilesystemPlugin: unknown action "{action}"')

    @staticmethod
    def _create_folder(dir_path: str) -> dict[str, Any]:
        logger = get_logger()
        create_folder(dir_path)
        logger.info("Created folder: %s", dir_path)
        return {"status": "ok", "path": dir_path}

    @staticmethod
    def _create_file(file_path: str, content: str) -> dict[str, Any]:
        logger = get_logger()
        create_file(file_path, content)
        logger.info("Created file: %s", file_path)
        return {"status": "ok", "path": file_path}

    @staticmethod
    def _list_directory(dir_path: str) -> dict[str, Any]:
        logger = get_logger()
        p = Path(dir_path)
        if not p.is_dir():
            raise FileNotFoundError(f"Directory not found: {dir_path}")
        entries = sorted(
            ({"name": e.name, "type": "dir" if e.is_dir() else "file"}
             for e in p.iterdir()),
            key=lambda entry: entry["name"],
        )
        logger.info("Listed %d entries in %s", len(entries), dir_path)
        return {"status": "ok", "entries": entries}

    def describe(self) -> str:
        return "Filesystem — create files/folders, list directories"
