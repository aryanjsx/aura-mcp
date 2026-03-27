"""Unit tests for plan validation and sanitization."""

import pytest

from aura_mcp.core.validator import validate_plan


class TestValidatePlan:
    def test_valid_plan_passes(self):
        plan = {
            "action": "scaffold_project",
            "framework": "react",
            "project_name": "my_app",
            "features": ["auth"],
        }
        result = validate_plan(plan)
        assert result["action"] == "scaffold_project"
        assert result["framework"] == "react"
        assert result["project_name"] == "my_app"
        assert result["features"] == ["auth"]

    def test_sanitizes_project_name(self):
        plan = {
            "action": "scaffold_project",
            "framework": "node",
            "project_name": "My Cool App!!!",
        }
        result = validate_plan(plan)
        assert result["project_name"] == "my_cool_app"

    def test_rejects_invalid_action(self):
        plan = {
            "action": "delete_everything",
            "framework": "react",
            "project_name": "app",
        }
        with pytest.raises(ValueError, match="Invalid action"):
            validate_plan(plan)

    def test_rejects_invalid_framework(self):
        plan = {
            "action": "scaffold_project",
            "framework": "django",
            "project_name": "app",
        }
        with pytest.raises(ValueError, match="Invalid framework"):
            validate_plan(plan)

    def test_rejects_empty_project_name(self):
        plan = {
            "action": "scaffold_project",
            "framework": "react",
            "project_name": "",
        }
        with pytest.raises(ValueError, match="non-empty project_name"):
            validate_plan(plan)

    def test_rejects_null_plan(self):
        with pytest.raises(ValueError, match="non-null"):
            validate_plan(None)

    def test_missing_features_defaults_to_empty_list(self):
        plan = {
            "action": "scaffold_project",
            "framework": "fastapi",
            "project_name": "api",
        }
        result = validate_plan(plan)
        assert result["features"] == []

    def test_truncates_long_project_name(self):
        plan = {
            "action": "scaffold_project",
            "framework": "node",
            "project_name": "a" * 200,
        }
        result = validate_plan(plan)
        assert len(result["project_name"]) <= 64
