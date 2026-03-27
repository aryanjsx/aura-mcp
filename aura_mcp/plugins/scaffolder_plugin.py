"""Plugin wrapper for the project scaffolder.

Delegates ``scaffold_project`` intents to the core executor so that
new scaffold targets can be added without touching the orchestrator.
"""

from __future__ import annotations

from typing import Any

from aura_mcp.core.executor import execute_task
from aura_mcp.plugins.base import BasePlugin


class ScaffolderPlugin(BasePlugin):
    """Scaffold real project trees on disk (React, Node, FastAPI)."""

    @property
    def name(self) -> str:
        return "scaffolder"

    async def execute(self, intent: dict[str, Any]) -> dict[str, Any]:
        summary = execute_task(intent)
        return {"status": "ok", "summary": summary}

    def describe(self) -> str:
        return "Project scaffolder — React, Node.js, FastAPI"
