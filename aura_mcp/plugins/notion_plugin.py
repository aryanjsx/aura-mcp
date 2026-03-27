"""Plugin wrapper for the Notion integration.

Translates intent dicts into NotionService method calls so the
orchestrator never touches the Notion SDK directly.
"""

from __future__ import annotations

from typing import Any

from aura_mcp.integrations.notion import NotionService
from aura_mcp.plugins.base import BasePlugin


class NotionPlugin(BasePlugin):
    """Read tasks from and write results back to Notion."""

    def __init__(self) -> None:
        self._service = NotionService()
        self._initialized = False

    @property
    def name(self) -> str:
        return "notion"

    def _ensure_init(self) -> None:
        if not self._initialized:
            self._service.init()
            self._initialized = True

    async def execute(self, intent: dict[str, Any]) -> dict[str, Any]:
        self._ensure_init()
        action = intent.get("action", "")

        if action == "get_pending_tasks":
            tasks = await self._service.get_pending_tasks()
            return {"status": "ok", "tasks": tasks}

        if action == "mark_processing":
            await self._service.mark_as_processing(intent["page_id"])
            return {"status": "ok"}

        if action == "mark_done":
            await self._service.mark_as_done(
                intent["page_id"], intent.get("output", "")
            )
            return {"status": "ok"}

        if action == "mark_failed":
            await self._service.mark_as_failed(
                intent["page_id"], intent.get("error", "")
            )
            return {"status": "ok"}

        raise ValueError(f"NotionPlugin: unknown action \"{action}\"")

    def describe(self) -> str:
        return "Notion integration — read tasks & write results"
