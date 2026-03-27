"""MCP server exposing AURA tools over stdio transport.

Tools
-----
- ``run_aura``         — full Notion → interpret → scaffold → update pipeline
- ``get_pending_tasks`` — fetch pending tasks from Notion
- ``run_single_task``  — interpret & scaffold from raw text (no Notion)
"""

from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from aura_mcp.core.executor import execute_task
from aura_mcp.core.interpreter import parse_task
from aura_mcp.core.orchestrator import run_pipeline
from aura_mcp.plugins.manager import plugin_manager
from aura_mcp.utils.logger import get_logger

mcp_app = FastMCP("aura-mcp")


@mcp_app.tool()
async def run_aura() -> str:
    """Run the full AURA pipeline: fetch pending Notion tasks, interpret, scaffold, and update."""
    try:
        result = await run_pipeline(plugin_manager)
        return json.dumps({"status": "success", **result}, indent=2)
    except Exception as exc:
        return json.dumps({"error": str(exc)})


@mcp_app.tool()
async def get_pending_tasks() -> str:
    """Fetch and return all pending tasks from the configured Notion database."""
    try:
        result = await plugin_manager.execute("notion", {"action": "get_pending_tasks"})
        tasks = result.get("tasks", [])
        return json.dumps(
            {"status": "success", "count": len(tasks), "tasks": tasks}, indent=2
        )
    except Exception as exc:
        return json.dumps({"error": str(exc)})


@mcp_app.tool()
async def run_single_task(task: str) -> str:
    """Interpret and scaffold a project from raw text input (no Notion needed)."""
    try:
        plan = await parse_task(task)
        result = execute_task(plan)
        return json.dumps(
            {
                "status": "success",
                "plan": {
                    "action": plan["action"],
                    "framework": plan["framework"],
                    "project_name": plan["project_name"],
                },
                "output": result,
            },
            indent=2,
        )
    except Exception as exc:
        return json.dumps({"error": str(exc)})


def start_server() -> None:
    """Entry point called by the CLI ``aura start`` command.

    Ensures dotenv and config are loaded before the server starts,
    regardless of how the server is invoked.
    """
    from dotenv import load_dotenv

    from aura_mcp.config.loader import load_config

    load_dotenv()
    load_config()

    logger = get_logger()
    logger.info("AURA MCP server starting on stdio")
    plugin_manager.list_plugins()  # trigger lazy discovery
    mcp_app.run(transport="stdio")
