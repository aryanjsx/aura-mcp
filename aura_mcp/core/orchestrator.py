"""Main AURA pipeline — the central coordinator.

Fetches pending tasks from Notion, processes each one sequentially
(parse → execute → update Notion), and reports aggregate results.
"""

from __future__ import annotations

from typing import Any

from aura_mcp.core.interpreter import parse_task
from aura_mcp.plugins.manager import PluginManager
from aura_mcp.utils.logger import get_logger


async def run_pipeline(plugin_manager: PluginManager) -> dict[str, Any]:
    """Execute the full AURA pipeline using registered plugins.

    Returns a summary dict: ``{processed, succeeded, failed}``.
    """
    logger = get_logger()
    logger.info("=== AURA MCP — Execution Pipeline ===\n")

    result = await plugin_manager.execute(
        "notion", {"action": "get_pending_tasks"}
    )
    tasks: list[dict[str, str]] = result.get("tasks", [])

    if not tasks:
        logger.warning(
            "No pending tasks found. Add a task in Notion with "
            "Status = 'Pending' and run again."
        )
        return {"processed": 0, "succeeded": 0, "failed": 0}

    logger.info("Processing %d task(s)...\n", len(tasks))

    succeeded = 0
    failed = 0

    for task in tasks:
        logger.info('---- Task: "%s" [%s] ----', task["task"], task["id"])

        try:
            await plugin_manager.execute(
                "notion",
                {"action": "mark_processing", "page_id": task["id"]},
            )

            logger.info("Interpreting task...")
            plan = await parse_task(task["task"])

            logger.info("Executing plan...")
            exec_result = await plugin_manager.execute("scaffolder", plan)

            logger.info("Updating Notion with result...")
            await plugin_manager.execute(
                "notion",
                {
                    "action": "mark_done",
                    "page_id": task["id"],
                    "output": exec_result.get("summary", ""),
                },
            )

            logger.info("Task completed\n")
            succeeded += 1

        except Exception as exc:
            logger.error("Task failed: %s", exc)
            try:
                await plugin_manager.execute(
                    "notion",
                    {
                        "action": "mark_failed",
                        "page_id": task["id"],
                        "error": f"Error: {exc}",
                    },
                )
            except Exception as notion_exc:
                logger.error(
                    "Could not update failed status in Notion: %s", notion_exc
                )
            failed += 1

    logger.info("=== Pipeline complete ===")
    logger.info(
        "Results: %d succeeded, %d failed, %d total",
        succeeded, failed, len(tasks),
    )
    return {"processed": len(tasks), "succeeded": succeeded, "failed": failed}
