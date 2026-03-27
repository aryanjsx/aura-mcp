"""Comprehensive tests for the AURA AI automation pipeline.

Covers the three core pipeline stages — interpretation, validation, and
orchestrated execution — plus edge cases like empty input, malformed intents,
and unsupported frameworks.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from aura_mcp.core.interpreter import parse_task, parse_with_rules
from aura_mcp.core.orchestrator import run_pipeline
from aura_mcp.core.validator import ALLOWED_FRAMEWORKS, validate_plan
from aura_mcp.plugins.base import BasePlugin
from aura_mcp.plugins.manager import PluginManager


# ── Helpers ──────────────────────────────────────────────────────────


class _FakeNotionPlugin(BasePlugin):
    """Simulates Notion returning a single pending task."""

    def __init__(self, tasks: list[dict[str, str]] | None = None) -> None:
        self._tasks = tasks or []
        self.calls: list[dict[str, Any]] = []

    @property
    def name(self) -> str:
        return "notion"

    async def execute(self, intent: dict[str, Any]) -> dict[str, Any]:
        self.calls.append(intent)
        action = intent.get("action")
        if action == "get_pending_tasks":
            return {"tasks": self._tasks}
        return {"status": "ok"}


class _SpyScaffolderPlugin(BasePlugin):
    """Records the plan it receives instead of writing to disk."""

    def __init__(self) -> None:
        self.received_plans: list[dict[str, Any]] = []

    @property
    def name(self) -> str:
        return "scaffolder"

    async def execute(self, intent: dict[str, Any]) -> dict[str, Any]:
        self.received_plans.append(intent)
        return {"status": "ok", "summary": f"Scaffolded {intent.get('project_name')}"}


def _pm_with(
    tasks: list[dict[str, str]] | None = None,
) -> tuple[PluginManager, _FakeNotionPlugin, _SpyScaffolderPlugin]:
    """Build a PluginManager wired with fake Notion + spy scaffolder."""
    pm = PluginManager()
    notion = _FakeNotionPlugin(tasks)
    scaffolder = _SpyScaffolderPlugin()
    pm.register(notion)
    pm.register(scaffolder)
    return pm, notion, scaffolder


# ═════════════════════════════════════════════════════════════════════
# A) Interpreter
# ═════════════════════════════════════════════════════════════════════


class TestInterpreterRuleBased:
    """Verify the deterministic rule-based parser produces correct intents."""

    def test_fastapi_todo_app(self):
        plan = parse_with_rules("create a fastapi todo app")
        assert plan["action"] == "scaffold_project"
        assert plan["framework"] == "fastapi"

    def test_react_detection(self):
        plan = parse_with_rules("build a react dashboard")
        assert plan["framework"] == "react"

    def test_node_express_detection(self):
        plan = parse_with_rules("set up an express api service")
        assert plan["framework"] == "node"

    def test_project_name_derived_from_input(self):
        plan = parse_with_rules("create a fastapi todo app")
        assert plan["project_name"]
        assert "todo" in plan["project_name"]

    def test_features_defaults_to_empty(self):
        plan = parse_with_rules("create a fastapi todo app")
        assert plan["features"] == []

    def test_unknown_framework_defaults_to_node(self):
        plan = parse_with_rules("make a cool thing")
        assert plan["framework"] == "node"


class TestInterpreterAsync:
    """Verify the async ``parse_task`` entry-point (LLM disabled)."""

    async def test_falls_back_to_rules_without_api_key(self):
        with patch.dict("os.environ", {"OPENAI_API_KEY": ""}, clear=False):
            plan = await parse_task("create a fastapi todo app")
        assert plan["action"] == "scaffold_project"
        assert plan["framework"] == "fastapi"

    async def test_falls_back_on_llm_failure(self):
        with patch(
            "aura_mcp.core.interpreter.interpret_with_llm",
            side_effect=RuntimeError("LLM unavailable"),
        ):
            plan = await parse_task("build a react app")
        assert plan["framework"] == "react"
        assert plan["action"] == "scaffold_project"

    async def test_uses_validated_llm_result_when_available(self):
        fake_llm_plan = {
            "action": "scaffold_project",
            "framework": "fastapi",
            "project_name": "llm_todo",
            "features": ["auth"],
        }
        with patch(
            "aura_mcp.core.interpreter.interpret_with_llm",
            new_callable=AsyncMock,
            return_value=fake_llm_plan,
        ), patch.dict(
            "os.environ", {"OPENAI_API_KEY": "test-key"}, clear=False
        ):
            plan = await parse_task("create a fastapi todo app")
        assert plan["project_name"] == "llm_todo"
        assert plan["features"] == ["auth"]


# ═════════════════════════════════════════════════════════════════════
# B) Validator
# ═════════════════════════════════════════════════════════════════════


class TestValidatorRejectsInvalidFramework:
    """The validator must reject frameworks not in the allow-list."""

    def test_django_rejected(self):
        plan = {
            "action": "scaffold_project",
            "framework": "django",
            "project_name": "app",
        }
        with pytest.raises(ValueError, match="Invalid framework"):
            validate_plan(plan)

    @pytest.mark.parametrize("framework", ["spring", "rails", "laravel", "flutter"])
    def test_other_unsupported_frameworks_rejected(self, framework: str):
        plan = {
            "action": "scaffold_project",
            "framework": framework,
            "project_name": "app",
        }
        with pytest.raises(ValueError, match="Invalid framework"):
            validate_plan(plan)

    @pytest.mark.parametrize("framework", ALLOWED_FRAMEWORKS)
    def test_allowed_frameworks_pass(self, framework: str):
        plan = {
            "action": "scaffold_project",
            "framework": framework,
            "project_name": "app",
        }
        result = validate_plan(plan)
        assert result["framework"] == framework


class TestValidatorEdgeCases:
    """Additional validation edge cases beyond existing test_validator.py."""

    def test_rejects_none_plan(self):
        with pytest.raises(ValueError, match="non-null"):
            validate_plan(None)

    def test_rejects_empty_dict(self):
        with pytest.raises(ValueError):
            validate_plan({})

    def test_rejects_non_dict(self):
        with pytest.raises(ValueError, match="non-null"):
            validate_plan("not a dict")

    def test_rejects_missing_action(self):
        plan = {"framework": "react", "project_name": "app"}
        with pytest.raises(ValueError, match="Invalid action"):
            validate_plan(plan)

    def test_rejects_unknown_action(self):
        plan = {
            "action": "deploy_to_mars",
            "framework": "react",
            "project_name": "app",
        }
        with pytest.raises(ValueError, match="Invalid action"):
            validate_plan(plan)

    def test_non_list_features_coerced_to_empty_list(self):
        plan = {
            "action": "scaffold_project",
            "framework": "react",
            "project_name": "app",
            "features": "not-a-list",
        }
        result = validate_plan(plan)
        assert result["features"] == []

    def test_special_characters_in_project_name_sanitized(self):
        plan = {
            "action": "scaffold_project",
            "framework": "node",
            "project_name": "My App!! @#$%",
        }
        result = validate_plan(plan)
        assert result["project_name"].isascii()
        assert " " not in result["project_name"]
        assert "@" not in result["project_name"]


# ═════════════════════════════════════════════════════════════════════
# C) Pipeline Integration  — Interpreter → Validator → Orchestrator
# ═════════════════════════════════════════════════════════════════════


class TestPipelineIntegration:
    """End-to-end: Notion task → interpret → validate → scaffold plugin."""

    async def test_valid_task_reaches_scaffolder(self):
        pm, notion, scaffolder = _pm_with(
            tasks=[{"id": "page-1", "task": "create a fastapi todo app"}]
        )

        with patch.dict("os.environ", {"OPENAI_API_KEY": ""}, clear=False):
            result = await run_pipeline(pm)

        assert result["processed"] == 1
        assert result["succeeded"] == 1
        assert result["failed"] == 0

        assert len(scaffolder.received_plans) == 1
        executed_plan = scaffolder.received_plans[0]
        assert executed_plan["action"] == "scaffold_project"
        assert executed_plan["framework"] == "fastapi"

    async def test_notion_marks_task_processing_then_done(self):
        pm, notion, _scaffolder = _pm_with(
            tasks=[{"id": "page-2", "task": "build a react dashboard"}]
        )

        with patch.dict("os.environ", {"OPENAI_API_KEY": ""}, clear=False):
            await run_pipeline(pm)

        actions = [c["action"] for c in notion.calls]
        assert actions[0] == "get_pending_tasks"
        assert "mark_processing" in actions
        assert "mark_done" in actions

    async def test_pipeline_handles_multiple_tasks(self):
        pm, _notion, scaffolder = _pm_with(
            tasks=[
                {"id": "p1", "task": "create a fastapi api"},
                {"id": "p2", "task": "build a react app"},
            ]
        )

        with patch.dict("os.environ", {"OPENAI_API_KEY": ""}, clear=False):
            result = await run_pipeline(pm)

        assert result["processed"] == 2
        assert result["succeeded"] == 2
        assert len(scaffolder.received_plans) == 2
        frameworks = {p["framework"] for p in scaffolder.received_plans}
        assert frameworks == {"fastapi", "react"}

    async def test_empty_task_list_returns_zero_processed(self):
        pm, _notion, scaffolder = _pm_with(tasks=[])

        result = await run_pipeline(pm)

        assert result["processed"] == 0
        assert result["succeeded"] == 0
        assert result["failed"] == 0
        assert scaffolder.received_plans == []

    async def test_failed_task_counted_and_notion_updated(self):
        pm, notion, _scaffolder = _pm_with(
            tasks=[{"id": "bad-1", "task": ""}]
        )

        with patch.dict("os.environ", {"OPENAI_API_KEY": ""}, clear=False):
            result = await run_pipeline(pm)

        assert result["failed"] == 1
        assert result["succeeded"] == 0
        failed_calls = [c for c in notion.calls if c.get("action") == "mark_failed"]
        assert len(failed_calls) == 1
        assert "bad-1" in failed_calls[0]["page_id"]


# ═════════════════════════════════════════════════════════════════════
# Edge Cases — empty input, malformed intent, unsupported framework
# ═════════════════════════════════════════════════════════════════════


class TestEmptyUserInput:
    """parse_task must reject blank / None / whitespace-only input."""

    @pytest.mark.parametrize("bad_input", ["", "   ", None, 42])
    async def test_parse_task_raises_on_empty_or_invalid(self, bad_input):
        with pytest.raises((ValueError, TypeError)):
            await parse_task(bad_input)


class TestMalformedIntent:
    """Validator must refuse plans that are structurally broken."""

    def test_plan_missing_all_keys(self):
        with pytest.raises(ValueError):
            validate_plan({"random_key": True})

    def test_plan_with_none_framework(self):
        plan = {
            "action": "scaffold_project",
            "framework": None,
            "project_name": "app",
        }
        with pytest.raises(ValueError, match="Invalid framework"):
            validate_plan(plan)

    def test_plan_with_numeric_project_name(self):
        plan = {
            "action": "scaffold_project",
            "framework": "react",
            "project_name": 12345,
        }
        with pytest.raises(ValueError, match="non-empty project_name"):
            validate_plan(plan)

    def test_plan_with_empty_string_action(self):
        plan = {
            "action": "",
            "framework": "react",
            "project_name": "app",
        }
        with pytest.raises(ValueError, match="Invalid action"):
            validate_plan(plan)


class TestUnsupportedFrameworkThroughPipeline:
    """When the LLM returns an unsupported framework, the pipeline should
    fall back to the rule-based parser (which always picks an allowed one)."""

    async def test_llm_unsupported_framework_triggers_fallback(self):
        bad_plan = {
            "action": "scaffold_project",
            "framework": "django",
            "project_name": "app",
        }
        with patch(
            "aura_mcp.core.interpreter.interpret_with_llm",
            new_callable=AsyncMock,
            return_value=bad_plan,
        ), patch.dict(
            "os.environ", {"OPENAI_API_KEY": "test-key"}, clear=False
        ):
            plan = await parse_task("create a django app")

        assert plan["framework"] in ALLOWED_FRAMEWORKS

    async def test_pipeline_survives_unsupported_framework_from_llm(self):
        bad_plan = {
            "action": "scaffold_project",
            "framework": "django",
            "project_name": "app",
        }
        pm, _notion, scaffolder = _pm_with(
            tasks=[{"id": "p1", "task": "create a django app"}]
        )
        with patch(
            "aura_mcp.core.interpreter.interpret_with_llm",
            new_callable=AsyncMock,
            return_value=bad_plan,
        ), patch.dict(
            "os.environ", {"OPENAI_API_KEY": "test-key"}, clear=False
        ):
            result = await run_pipeline(pm)

        assert result["succeeded"] == 1
        assert scaffolder.received_plans[0]["framework"] in ALLOWED_FRAMEWORKS
