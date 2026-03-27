"""Tests for the MCP server — initialization, tool registration, and tool handlers.

Each tool handler is invoked directly as an async function with the
necessary dependencies mocked (Notion, LLM, filesystem) so that tests
run offline and never touch real external services.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from aura_mcp.plugins.base import BasePlugin
from aura_mcp.plugins.manager import PluginManager
from aura_mcp.server.mcp_server import (
    get_pending_tasks,
    mcp_app,
    run_aura,
    run_single_task,
)


# ── Helpers ──────────────────────────────────────────────────────────


class _FakeNotionPlugin(BasePlugin):
    def __init__(self, tasks: list[dict[str, str]] | None = None) -> None:
        self._tasks = tasks or []

    @property
    def name(self) -> str:
        return "notion"

    async def execute(self, intent: dict[str, Any]) -> dict[str, Any]:
        action = intent.get("action")
        if action == "get_pending_tasks":
            return {"tasks": self._tasks}
        return {"status": "ok"}


class _SpyScaffolderPlugin(BasePlugin):
    def __init__(self) -> None:
        self.received: list[dict[str, Any]] = []

    @property
    def name(self) -> str:
        return "scaffolder"

    async def execute(self, intent: dict[str, Any]) -> dict[str, Any]:
        self.received.append(intent)
        return {"status": "ok", "summary": f"Scaffolded {intent.get('project_name')}"}


def _build_pm(
    tasks: list[dict[str, str]] | None = None,
) -> PluginManager:
    pm = PluginManager()
    pm.register(_FakeNotionPlugin(tasks))
    pm.register(_SpyScaffolderPlugin())
    return pm


# ═════════════════════════════════════════════════════════════════════
# Server initialization
# ═════════════════════════════════════════════════════════════════════


class TestServerInit:
    def test_mcp_app_exists(self) -> None:
        assert mcp_app is not None

    def test_mcp_app_has_name(self) -> None:
        assert mcp_app.name == "aura-mcp"

    def test_tool_functions_are_importable(self) -> None:
        assert callable(run_aura)
        assert callable(get_pending_tasks)
        assert callable(run_single_task)


# ═════════════════════════════════════════════════════════════════════
# Tool registration
# ═════════════════════════════════════════════════════════════════════


class TestToolRegistration:
    async def test_server_lists_registered_tools(self) -> None:
        tools = await mcp_app.list_tools()
        tool_names = {t.name for t in tools}
        assert "run_aura" in tool_names
        assert "get_pending_tasks" in tool_names
        assert "run_single_task" in tool_names

    async def test_exactly_three_tools_registered(self) -> None:
        tools = await mcp_app.list_tools()
        assert len(tools) == 3

    async def test_run_single_task_has_task_parameter(self) -> None:
        tools = await mcp_app.list_tools()
        rst = next(t for t in tools if t.name == "run_single_task")
        schema = rst.inputSchema
        assert "task" in schema.get("properties", {})

    async def test_each_tool_has_description(self) -> None:
        tools = await mcp_app.list_tools()
        for t in tools:
            assert t.description, f"Tool '{t.name}' has no description"


# ═════════════════════════════════════════════════════════════════════
# run_aura — full pipeline tool
# ═════════════════════════════════════════════════════════════════════


class TestRunAura:
    async def test_returns_valid_json(self) -> None:
        pm = _build_pm(tasks=[{"id": "t1", "task": "create a fastapi app"}])
        with patch(
            "aura_mcp.server.mcp_server.plugin_manager", pm
        ), patch.dict("os.environ", {"OPENAI_API_KEY": ""}, clear=False):
            raw = await run_aura()
        data = json.loads(raw)
        assert isinstance(data, dict)

    async def test_success_status_with_pending_tasks(self) -> None:
        pm = _build_pm(tasks=[{"id": "t1", "task": "create a fastapi app"}])
        with patch(
            "aura_mcp.server.mcp_server.plugin_manager", pm
        ), patch.dict("os.environ", {"OPENAI_API_KEY": ""}, clear=False):
            raw = await run_aura()
        data = json.loads(raw)
        assert data["status"] == "success"
        assert data["processed"] == 1
        assert data["succeeded"] == 1

    async def test_success_with_zero_tasks(self) -> None:
        pm = _build_pm(tasks=[])
        with patch("aura_mcp.server.mcp_server.plugin_manager", pm):
            raw = await run_aura()
        data = json.loads(raw)
        assert data["status"] == "success"
        assert data["processed"] == 0

    async def test_error_is_caught_and_returned_as_json(self) -> None:
        with patch(
            "aura_mcp.server.mcp_server.run_pipeline",
            side_effect=RuntimeError("boom"),
        ):
            raw = await run_aura()
        data = json.loads(raw)
        assert "error" in data
        assert "boom" in data["error"]


# ═════════════════════════════════════════════════════════════════════
# get_pending_tasks — Notion fetch tool
# ═════════════════════════════════════════════════════════════════════


class TestGetPendingTasks:
    async def test_returns_valid_json(self) -> None:
        pm = _build_pm(tasks=[{"id": "p1", "task": "something"}])
        with patch("aura_mcp.server.mcp_server.plugin_manager", pm):
            raw = await get_pending_tasks()
        data = json.loads(raw)
        assert isinstance(data, dict)

    async def test_success_with_tasks(self) -> None:
        tasks = [
            {"id": "p1", "task": "build react app"},
            {"id": "p2", "task": "build node api"},
        ]
        pm = _build_pm(tasks=tasks)
        with patch("aura_mcp.server.mcp_server.plugin_manager", pm):
            raw = await get_pending_tasks()
        data = json.loads(raw)
        assert data["status"] == "success"
        assert data["count"] == 2
        assert len(data["tasks"]) == 2

    async def test_success_with_no_tasks(self) -> None:
        pm = _build_pm(tasks=[])
        with patch("aura_mcp.server.mcp_server.plugin_manager", pm):
            raw = await get_pending_tasks()
        data = json.loads(raw)
        assert data["status"] == "success"
        assert data["count"] == 0
        assert data["tasks"] == []

    async def test_error_is_caught_and_returned_as_json(self) -> None:
        mock_pm = AsyncMock()
        mock_pm.execute = AsyncMock(side_effect=RuntimeError("notion down"))
        with patch("aura_mcp.server.mcp_server.plugin_manager", mock_pm):
            raw = await get_pending_tasks()
        data = json.loads(raw)
        assert "error" in data
        assert "notion down" in data["error"]


# ═════════════════════════════════════════════════════════════════════
# run_single_task — interpret & scaffold tool
# ═════════════════════════════════════════════════════════════════════


class TestRunSingleTask:
    @pytest.fixture()
    def workspace(self, tmp_path: Path):
        with patch("aura_mcp.core.executor._output_dir", return_value=tmp_path):
            yield tmp_path

    async def test_returns_valid_json(self, workspace: Path) -> None:
        with patch.dict("os.environ", {"OPENAI_API_KEY": ""}, clear=False):
            raw = await run_single_task("create a fastapi todo app")
        data = json.loads(raw)
        assert isinstance(data, dict)

    async def test_success_status(self, workspace: Path) -> None:
        with patch.dict("os.environ", {"OPENAI_API_KEY": ""}, clear=False):
            raw = await run_single_task("create a fastapi todo app")
        data = json.loads(raw)
        assert data["status"] == "success"

    async def test_plan_contains_action_and_framework(self, workspace: Path) -> None:
        with patch.dict("os.environ", {"OPENAI_API_KEY": ""}, clear=False):
            raw = await run_single_task("create a fastapi todo app")
        data = json.loads(raw)
        assert data["plan"]["action"] == "scaffold_project"
        assert data["plan"]["framework"] == "fastapi"

    async def test_plan_contains_project_name(self, workspace: Path) -> None:
        with patch.dict("os.environ", {"OPENAI_API_KEY": ""}, clear=False):
            raw = await run_single_task("create a fastapi todo app")
        data = json.loads(raw)
        assert isinstance(data["plan"]["project_name"], str)
        assert len(data["plan"]["project_name"]) > 0

    async def test_output_field_is_summary_string(self, workspace: Path) -> None:
        with patch.dict("os.environ", {"OPENAI_API_KEY": ""}, clear=False):
            raw = await run_single_task("create a fastapi todo app")
        data = json.loads(raw)
        assert isinstance(data["output"], str)
        assert "AURA MCP" in data["output"]

    async def test_creates_project_on_disk(self, workspace: Path) -> None:
        with patch.dict("os.environ", {"OPENAI_API_KEY": ""}, clear=False):
            raw = await run_single_task("create a fastapi todo app")
        data = json.loads(raw)
        project_name = data["plan"]["project_name"]
        assert (workspace / project_name).is_dir()
        assert (workspace / project_name / "main.py").is_file()

    async def test_react_task(self, workspace: Path) -> None:
        with patch.dict("os.environ", {"OPENAI_API_KEY": ""}, clear=False):
            raw = await run_single_task("build a react dashboard")
        data = json.loads(raw)
        assert data["status"] == "success"
        assert data["plan"]["framework"] == "react"

    async def test_node_task(self, workspace: Path) -> None:
        with patch.dict("os.environ", {"OPENAI_API_KEY": ""}, clear=False):
            raw = await run_single_task("set up an express api")
        data = json.loads(raw)
        assert data["status"] == "success"
        assert data["plan"]["framework"] == "node"

    async def test_empty_task_returns_error_json(self, workspace: Path) -> None:
        raw = await run_single_task("")
        data = json.loads(raw)
        assert "error" in data

    async def test_error_is_caught_and_returned_as_json(self) -> None:
        with patch(
            "aura_mcp.server.mcp_server.parse_task",
            side_effect=RuntimeError("parse exploded"),
        ):
            raw = await run_single_task("anything")
        data = json.loads(raw)
        assert "error" in data
        assert "parse exploded" in data["error"]


# ═════════════════════════════════════════════════════════════════════
# All handlers return valid JSON — cross-cutting
# ═════════════════════════════════════════════════════════════════════


class TestAllHandlersReturnValidJSON:
    """Every tool must return a parseable JSON string, even on errors."""

    async def test_run_aura_on_error(self) -> None:
        with patch(
            "aura_mcp.server.mcp_server.run_pipeline",
            side_effect=Exception("fail"),
        ):
            raw = await run_aura()
        json.loads(raw)

    async def test_get_pending_tasks_on_error(self) -> None:
        mock_pm = AsyncMock()
        mock_pm.execute = AsyncMock(side_effect=Exception("fail"))
        with patch("aura_mcp.server.mcp_server.plugin_manager", mock_pm):
            raw = await get_pending_tasks()
        json.loads(raw)

    async def test_run_single_task_on_error(self) -> None:
        with patch(
            "aura_mcp.server.mcp_server.parse_task",
            side_effect=Exception("fail"),
        ):
            raw = await run_single_task("anything")
        json.loads(raw)
