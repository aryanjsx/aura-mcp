"""Notion API integration — read tasks and write results back."""

from __future__ import annotations

import os
from typing import Any

from notion_client import AsyncClient

from aura_mcp.config.loader import get_config
from aura_mcp.utils.logger import get_logger

VALID_STATUSES = ("Pending", "In progress", "Done", "To-do", "Complete")


class NotionService:
    """Async wrapper around the Notion SDK for task management."""

    def __init__(self) -> None:
        self._client: AsyncClient | None = None
        self._database_id: str = ""

    def init(self) -> None:
        """Create the Notion client from config / environment variables."""
        config = get_config()
        logger = get_logger()

        api_key = (
            config.get("notion", {}).get("api_key")
            or os.environ.get("NOTION_API_KEY", "")
        )
        self._database_id = (
            config.get("notion", {}).get("database_id")
            or os.environ.get("NOTION_DATABASE_ID", "")
        )

        if not api_key or not self._database_id:
            raise RuntimeError(
                "Missing NOTION_API_KEY or NOTION_DATABASE_ID. "
                "Set them in config.yaml or as environment variables."
            )

        self._client = AsyncClient(auth=api_key)
        logger.info("Notion client initialized")

    @staticmethod
    def _extract_title(title_property: list[dict[str, Any]] | None) -> str:
        if not title_property or not isinstance(title_property, list):
            return ""
        return "".join(t.get("plain_text", "") for t in title_property)

    async def get_pending_tasks(self) -> list[dict[str, str]]:
        """Fetch all tasks whose Status equals 'Pending'."""
        logger = get_logger()
        if self._client is None:
            raise RuntimeError("Notion client not initialized — call init() first.")

        # notion-client v3 removed databases.query(); use raw request instead.
        response = await self._client.request(
            path=f"databases/{self._database_id}/query",
            method="POST",
            body={"filter": {"property": "Status", "status": {"equals": "Pending"}}},
        )

        tasks = [
            {
                "id": page["id"],
                "task": self._extract_title(
                    page.get("properties", {}).get("Name", {}).get("title")
                ),
            }
            for page in response.get("results", [])
        ]

        logger.info("Fetched %d pending task(s)", len(tasks))
        return tasks

    async def update_task_status(
        self,
        page_id: str,
        status: str,
        output: str | None = None,
    ) -> None:
        """Set a task's Status (and optionally Output) in Notion."""
        logger = get_logger()
        if self._client is None:
            raise RuntimeError("Notion client not initialized — call init() first.")

        if status not in VALID_STATUSES:
            raise ValueError(
                f'Invalid status "{status}". '
                f"Must be one of: {', '.join(VALID_STATUSES)}"
            )

        properties: dict[str, Any] = {
            "Status": {"status": {"name": status}},
        }
        if output is not None:
            properties["Output"] = {
                "rich_text": [
                    {"type": "text", "text": {"content": str(output)[:2000]}}
                ],
            }

        await self._client.pages.update(page_id=page_id, properties=properties)
        logger.info('Task %s → status: "%s"', page_id, status)

    async def mark_as_processing(self, page_id: str) -> None:
        await self.update_task_status(page_id, "In progress")

    async def mark_as_done(self, page_id: str, output: str) -> None:
        await self.update_task_status(page_id, "Done", output)

    async def mark_as_failed(self, page_id: str, error_message: str) -> None:
        await self.update_task_status(page_id, "To-do", error_message)
