"""Unit tests for the rule-based interpreter fallback."""

from aura_mcp.core.interpreter import parse_with_rules


class TestParseWithRules:
    def test_detects_react(self):
        plan = parse_with_rules("Build a React portfolio app")
        assert plan["framework"] == "react"
        assert plan["action"] == "scaffold_project"

    def test_detects_fastapi(self):
        plan = parse_with_rules("Create a FastAPI backend for users")
        assert plan["framework"] == "fastapi"

    def test_detects_node(self):
        plan = parse_with_rules("Create an Express REST API")
        assert plan["framework"] == "node"

    def test_defaults_to_node(self):
        plan = parse_with_rules("Build something cool")
        assert plan["framework"] == "node"

    def test_derives_project_name(self):
        plan = parse_with_rules("Build a task manager with React")
        assert "task" in plan["project_name"] or "manager" in plan["project_name"]

    def test_fallback_project_name(self):
        plan = parse_with_rules("Create a simple app")
        assert plan["project_name"]  # non-empty
