"""Tests for the project scaffolding system.

Every test uses pytest's ``tmp_path`` fixture so nothing is written to the
real filesystem.  The ``_output_dir`` helper inside the executor is patched
to point at the temp directory, letting ``execute_task`` run end-to-end
against real disk I/O in an isolated sandbox.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from aura_mcp.core.executor import execute_task


# ── Fixtures ─────────────────────────────────────────────────────────


@pytest.fixture()
def workspace(tmp_path: Path):
    """Patch ``_output_dir`` so every scaffold writes into *tmp_path*."""
    with patch("aura_mcp.core.executor._output_dir", return_value=tmp_path):
        yield tmp_path


def _plan(framework: str, name: str = "test_app") -> dict:
    return {
        "action": "scaffold_project",
        "framework": framework,
        "project_name": name,
        "features": [],
    }


# ═════════════════════════════════════════════════════════════════════
# FastAPI
# ═════════════════════════════════════════════════════════════════════


class TestFastAPIScaffold:
    def test_creates_project_directory(self, workspace: Path):
        execute_task(_plan("fastapi"))
        assert (workspace / "test_app").is_dir()

    def test_main_py_exists(self, workspace: Path):
        execute_task(_plan("fastapi"))
        assert (workspace / "test_app" / "main.py").is_file()

    def test_routes_py_exists(self, workspace: Path):
        execute_task(_plan("fastapi"))
        assert (workspace / "test_app" / "routes.py").is_file()

    def test_requirements_txt_exists(self, workspace: Path):
        execute_task(_plan("fastapi"))
        assert (workspace / "test_app" / "requirements.txt").is_file()

    def test_gitignore_exists(self, workspace: Path):
        execute_task(_plan("fastapi"))
        assert (workspace / "test_app" / ".gitignore").is_file()

    def test_readme_exists(self, workspace: Path):
        execute_task(_plan("fastapi"))
        assert (workspace / "test_app" / "README.md").is_file()

    def test_main_py_imports_fastapi(self, workspace: Path):
        execute_task(_plan("fastapi"))
        content = (workspace / "test_app" / "main.py").read_text(encoding="utf-8")
        assert "from fastapi import FastAPI" in content

    def test_main_py_embeds_project_name(self, workspace: Path):
        execute_task(_plan("fastapi", "my_api"))
        content = (workspace / "my_api" / "main.py").read_text(encoding="utf-8")
        assert "my_api" in content

    def test_routes_defines_crud_endpoints(self, workspace: Path):
        execute_task(_plan("fastapi"))
        content = (workspace / "test_app" / "routes.py").read_text(encoding="utf-8")
        assert "@router.get" in content
        assert "@router.post" in content

    def test_requirements_lists_core_deps(self, workspace: Path):
        execute_task(_plan("fastapi"))
        content = (workspace / "test_app" / "requirements.txt").read_text(encoding="utf-8")
        assert "fastapi" in content
        assert "uvicorn" in content
        assert "pydantic" in content

    def test_gitignore_excludes_pycache(self, workspace: Path):
        execute_task(_plan("fastapi"))
        content = (workspace / "test_app" / ".gitignore").read_text(encoding="utf-8")
        assert "__pycache__/" in content

    def test_total_file_count(self, workspace: Path):
        execute_task(_plan("fastapi"))
        root = workspace / "test_app"
        files = [p for p in root.rglob("*") if p.is_file()]
        assert len(files) == 5


# ═════════════════════════════════════════════════════════════════════
# Node / Express
# ═════════════════════════════════════════════════════════════════════


class TestNodeScaffold:
    def test_creates_project_directory(self, workspace: Path):
        execute_task(_plan("node"))
        assert (workspace / "test_app").is_dir()

    def test_package_json_exists(self, workspace: Path):
        execute_task(_plan("node"))
        assert (workspace / "test_app" / "package.json").is_file()

    def test_index_js_exists(self, workspace: Path):
        execute_task(_plan("node"))
        assert (workspace / "test_app" / "index.js").is_file()

    def test_src_routes_exists(self, workspace: Path):
        execute_task(_plan("node"))
        assert (workspace / "test_app" / "src" / "routes" / "index.js").is_file()

    def test_src_middleware_exists(self, workspace: Path):
        execute_task(_plan("node"))
        assert (workspace / "test_app" / "src" / "middleware" / "errorHandler.js").is_file()

    def test_env_example_exists(self, workspace: Path):
        execute_task(_plan("node"))
        assert (workspace / "test_app" / ".env.example").is_file()

    def test_package_json_is_valid_json(self, workspace: Path):
        execute_task(_plan("node"))
        raw = (workspace / "test_app" / "package.json").read_text(encoding="utf-8")
        pkg = json.loads(raw)
        assert isinstance(pkg, dict)

    def test_package_json_has_express_dep(self, workspace: Path):
        execute_task(_plan("node"))
        raw = (workspace / "test_app" / "package.json").read_text(encoding="utf-8")
        pkg = json.loads(raw)
        assert "express" in pkg.get("dependencies", {})

    def test_package_json_has_start_script(self, workspace: Path):
        execute_task(_plan("node"))
        raw = (workspace / "test_app" / "package.json").read_text(encoding="utf-8")
        pkg = json.loads(raw)
        assert "start" in pkg.get("scripts", {})

    def test_package_json_embeds_project_name(self, workspace: Path):
        execute_task(_plan("node", "my_express"))
        raw = (workspace / "my_express" / "package.json").read_text(encoding="utf-8")
        pkg = json.loads(raw)
        assert pkg["name"] == "my_express"

    def test_index_js_sets_up_express(self, workspace: Path):
        execute_task(_plan("node"))
        content = (workspace / "test_app" / "index.js").read_text(encoding="utf-8")
        assert 'require("express")' in content
        assert "app.listen" in content

    def test_routes_define_api_endpoints(self, workspace: Path):
        execute_task(_plan("node"))
        content = (
            workspace / "test_app" / "src" / "routes" / "index.js"
        ).read_text(encoding="utf-8")
        assert "router.get" in content
        assert "router.post" in content

    def test_total_file_count(self, workspace: Path):
        execute_task(_plan("node"))
        root = workspace / "test_app"
        files = [p for p in root.rglob("*") if p.is_file()]
        assert len(files) == 7


# ═════════════════════════════════════════════════════════════════════
# React
# ═════════════════════════════════════════════════════════════════════


class TestReactScaffold:
    def test_creates_project_directory(self, workspace: Path):
        execute_task(_plan("react"))
        assert (workspace / "test_app").is_dir()

    def test_package_json_exists(self, workspace: Path):
        execute_task(_plan("react"))
        assert (workspace / "test_app" / "package.json").is_file()

    def test_src_directory_exists(self, workspace: Path):
        execute_task(_plan("react"))
        assert (workspace / "test_app" / "src").is_dir()

    def test_public_directory_exists(self, workspace: Path):
        execute_task(_plan("react"))
        assert (workspace / "test_app" / "public").is_dir()

    def test_index_html_exists(self, workspace: Path):
        execute_task(_plan("react"))
        assert (workspace / "test_app" / "public" / "index.html").is_file()

    def test_app_js_exists(self, workspace: Path):
        execute_task(_plan("react"))
        assert (workspace / "test_app" / "src" / "App.js").is_file()

    def test_app_css_exists(self, workspace: Path):
        execute_task(_plan("react"))
        assert (workspace / "test_app" / "src" / "App.css").is_file()

    def test_index_js_exists(self, workspace: Path):
        execute_task(_plan("react"))
        assert (workspace / "test_app" / "src" / "index.js").is_file()

    def test_header_component_exists(self, workspace: Path):
        execute_task(_plan("react"))
        assert (
            workspace / "test_app" / "src" / "components" / "Header.js"
        ).is_file()

    def test_package_json_is_valid_json(self, workspace: Path):
        execute_task(_plan("react"))
        raw = (workspace / "test_app" / "package.json").read_text(encoding="utf-8")
        pkg = json.loads(raw)
        assert isinstance(pkg, dict)

    def test_package_json_has_react_dep(self, workspace: Path):
        execute_task(_plan("react"))
        raw = (workspace / "test_app" / "package.json").read_text(encoding="utf-8")
        pkg = json.loads(raw)
        deps = pkg.get("dependencies", {})
        assert "react" in deps
        assert "react-dom" in deps

    def test_package_json_embeds_project_name(self, workspace: Path):
        execute_task(_plan("react", "cool_ui"))
        raw = (workspace / "cool_ui" / "package.json").read_text(encoding="utf-8")
        pkg = json.loads(raw)
        assert pkg["name"] == "cool_ui"

    def test_index_html_has_root_div(self, workspace: Path):
        execute_task(_plan("react"))
        content = (
            workspace / "test_app" / "public" / "index.html"
        ).read_text(encoding="utf-8")
        assert 'id="root"' in content

    def test_index_html_embeds_project_title(self, workspace: Path):
        execute_task(_plan("react", "dashboard"))
        content = (
            workspace / "dashboard" / "public" / "index.html"
        ).read_text(encoding="utf-8")
        assert "<title>dashboard</title>" in content

    def test_app_js_imports_react(self, workspace: Path):
        execute_task(_plan("react"))
        content = (workspace / "test_app" / "src" / "App.js").read_text(encoding="utf-8")
        assert "import React" in content

    def test_total_file_count(self, workspace: Path):
        execute_task(_plan("react"))
        root = workspace / "test_app"
        files = [p for p in root.rglob("*") if p.is_file()]
        assert len(files) == 8


# ═════════════════════════════════════════════════════════════════════
# Summary return value
# ═════════════════════════════════════════════════════════════════════


class TestScaffoldSummary:
    def test_summary_contains_project_name(self, workspace: Path):
        summary = execute_task(_plan("fastapi", "my_api"))
        assert "my_api" in summary

    def test_summary_contains_framework(self, workspace: Path):
        summary = execute_task(_plan("node", "srv"))
        assert "node" in summary.lower()

    def test_summary_lists_files(self, workspace: Path):
        summary = execute_task(_plan("react"))
        assert "package.json" in summary
        assert "App.js" in summary

    def test_summary_mentions_aura(self, workspace: Path):
        summary = execute_task(_plan("fastapi"))
        assert "AURA MCP" in summary


# ═════════════════════════════════════════════════════════════════════
# Error handling
# ═════════════════════════════════════════════════════════════════════


class TestScaffoldErrors:
    def test_unknown_action_raises(self, workspace: Path):
        plan = {
            "action": "deploy_app",
            "framework": "react",
            "project_name": "app",
            "features": [],
        }
        with pytest.raises(ValueError, match="Unknown action"):
            execute_task(plan)

    def test_unsupported_framework_raises(self, workspace: Path):
        plan = {
            "action": "scaffold_project",
            "framework": "django",
            "project_name": "app",
            "features": [],
        }
        with pytest.raises(ValueError, match="No template for framework"):
            execute_task(plan)

    def test_missing_action_raises(self, workspace: Path):
        plan = {"framework": "react", "project_name": "app", "features": []}
        with pytest.raises(ValueError, match="Unknown action"):
            execute_task(plan)


# ═════════════════════════════════════════════════════════════════════
# Cross-framework checks
# ═════════════════════════════════════════════════════════════════════


class TestCrossFramework:
    @pytest.mark.parametrize("framework", ["react", "node", "fastapi"])
    def test_every_framework_creates_readme(self, workspace: Path, framework: str):
        execute_task(_plan(framework))
        assert (workspace / "test_app" / "README.md").is_file()

    @pytest.mark.parametrize("framework", ["react", "node", "fastapi"])
    def test_every_framework_creates_gitignore(self, workspace: Path, framework: str):
        execute_task(_plan(framework))
        assert (workspace / "test_app" / ".gitignore").is_file()

    @pytest.mark.parametrize("framework", ["react", "node", "fastapi"])
    def test_readme_mentions_framework(self, workspace: Path, framework: str):
        execute_task(_plan(framework))
        content = (workspace / "test_app" / "README.md").read_text(encoding="utf-8")
        assert "AURA MCP" in content

    @pytest.mark.parametrize("framework", ["react", "node", "fastapi"])
    def test_no_empty_files_generated(self, workspace: Path, framework: str):
        execute_task(_plan(framework))
        root = workspace / "test_app"
        for path in root.rglob("*"):
            if path.is_file():
                assert path.stat().st_size > 0, f"{path.name} is empty"

    def test_different_names_produce_separate_trees(self, workspace: Path):
        execute_task(_plan("react", "alpha"))
        execute_task(_plan("node", "beta"))
        assert (workspace / "alpha").is_dir()
        assert (workspace / "beta").is_dir()
        assert (workspace / "alpha" / "src").is_dir()
        assert (workspace / "beta" / "index.js").is_file()
