"""Tests for the plugin system — discovery, registry, execution, and guards.

Uses the module-level ``plugin_manager`` singleton for discovery assertions
and a ``tmp_path``-backed workspace for scaffolder execution so nothing
touches the real filesystem.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from aura_mcp.plugins.base import BasePlugin
from aura_mcp.plugins.manager import PluginManager, plugin_manager


# ── Helpers ──────────────────────────────────────────────────────────


class _StubPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "stub"

    async def execute(self, intent: dict[str, Any]) -> dict[str, Any]:
        return {"status": "ok", "echo": intent}

    def describe(self) -> str:
        return "Stub plugin for tests"


class _BadReturnPlugin(BasePlugin):
    """Returns a non-dict from execute — should trigger TypeError."""

    @property
    def name(self) -> str:
        return "bad_return"

    async def execute(self, intent: dict[str, Any]) -> dict[str, Any]:
        return "not a dict"  # type: ignore[return-value]


class _FailingPlugin(BasePlugin):
    """Raises during execute to verify error propagation."""

    @property
    def name(self) -> str:
        return "failing"

    async def execute(self, intent: dict[str, Any]) -> dict[str, Any]:
        raise RuntimeError("intentional test explosion")


# ═════════════════════════════════════════════════════════════════════
# Discovery — via the module-level singleton
# ═════════════════════════════════════════════════════════════════════


class TestPluginDiscovery:
    def test_singleton_lists_scaffolder(self) -> None:
        names = plugin_manager.list_plugins()
        assert "scaffolder" in names

    def test_singleton_lists_all_builtin_plugins(self) -> None:
        expected = {"docker", "filesystem", "github", "notion", "scaffolder"}
        assert expected == set(plugin_manager.list_plugins())

    def test_scaffolder_plugin_has_correct_name(self) -> None:
        plugin = plugin_manager.get("scaffolder")
        assert plugin is not None
        assert plugin.name == "scaffolder"

    def test_fresh_manager_discover_loads_scaffolder(self) -> None:
        pm = PluginManager()
        pm.discover()
        assert "scaffolder" in pm.list_plugins()

    def test_discover_skips_base_and_manager_modules(self) -> None:
        pm = PluginManager()
        pm.discover()
        assert pm.get("base") is None
        assert pm.get("manager") is None

    def test_discover_against_missing_package_is_safe(self) -> None:
        pm = PluginManager()
        pm.discover("nonexistent.package.path")
        assert pm.list_plugins() == []


# ═════════════════════════════════════════════════════════════════════
# Registry
# ═════════════════════════════════════════════════════════════════════


class TestPluginRegistry:
    def test_register_then_list(self) -> None:
        pm = PluginManager()
        pm.register(_StubPlugin(), module_path="tests", class_name="_StubPlugin")
        assert pm.list_plugins() == ["stub"]

    def test_get_returns_same_instance(self) -> None:
        pm = PluginManager()
        plugin = _StubPlugin()
        pm.register(plugin, module_path="tests", class_name="_StubPlugin")
        assert pm.get("stub") is plugin

    def test_get_plugin_alias(self) -> None:
        pm = PluginManager()
        pm.register(_StubPlugin(), module_path="tests", class_name="_StubPlugin")
        assert pm.get_plugin("stub") is pm.get("stub")

    def test_get_returns_none_for_missing(self) -> None:
        pm = PluginManager()
        assert pm.get("nonexistent") is None

    def test_duplicate_name_raises(self) -> None:
        pm = PluginManager()
        pm.register(_StubPlugin(), module_path="tests", class_name="_StubPlugin")
        with pytest.raises(RuntimeError, match="Duplicate plugin detected: stub"):
            pm.register(_StubPlugin(), module_path="tests", class_name="_StubPlugin")

    def test_multiple_plugins_coexist(self) -> None:
        pm = PluginManager()
        pm.register(_StubPlugin())
        pm.register(_BadReturnPlugin())
        assert set(pm.list_plugins()) == {"stub", "bad_return"}


# ═════════════════════════════════════════════════════════════════════
# Execution — stub-level
# ═════════════════════════════════════════════════════════════════════


class TestPluginExecution:
    async def test_execute_calls_correct_plugin(self) -> None:
        pm = PluginManager()
        pm.register(_StubPlugin(), module_path="tests", class_name="_StubPlugin")
        result = await pm.execute("stub", {"action": "ping"})
        assert result["status"] == "ok"
        assert result["echo"] == {"action": "ping"}

    async def test_execute_raises_for_unknown_plugin(self) -> None:
        pm = PluginManager()
        with pytest.raises(ValueError, match="Plugin not found: ghost"):
            await pm.execute("ghost", {})

    async def test_execute_fake_plugin_raises_value_error(self) -> None:
        pm = PluginManager()
        pm.discover()
        with pytest.raises(ValueError, match="Plugin not found: fake_plugin"):
            await pm.execute("fake_plugin", {})

    async def test_execute_raises_on_bad_return_type(self) -> None:
        pm = PluginManager()
        pm.register(_BadReturnPlugin(), module_path="tests", class_name="_BadReturnPlugin")
        with pytest.raises(TypeError, match="must return dict"):
            await pm.execute("bad_return", {})

    async def test_execute_propagates_plugin_exception(self) -> None:
        pm = PluginManager()
        pm.register(_FailingPlugin())
        with pytest.raises(RuntimeError, match="intentional test explosion"):
            await pm.execute("failing", {})


# ═════════════════════════════════════════════════════════════════════
# Scaffolder plugin — real execution against tmp_path
# ═════════════════════════════════════════════════════════════════════


class TestScaffolderPluginExecution:
    @pytest.fixture()
    def workspace(self, tmp_path: Path):
        with patch("aura_mcp.core.executor._output_dir", return_value=tmp_path):
            yield tmp_path

    async def test_scaffolder_returns_ok(self, workspace: Path) -> None:
        pm = PluginManager()
        pm.discover()
        result = await pm.execute("scaffolder", {
            "action": "scaffold_project",
            "framework": "fastapi",
            "project_name": "plugin_test_app",
            "features": [],
        })
        assert result["status"] == "ok"

    async def test_scaffolder_summary_mentions_project(self, workspace: Path) -> None:
        pm = PluginManager()
        pm.discover()
        result = await pm.execute("scaffolder", {
            "action": "scaffold_project",
            "framework": "fastapi",
            "project_name": "plugin_test_app",
            "features": [],
        })
        assert "plugin_test_app" in result["summary"]

    async def test_scaffolder_creates_files_on_disk(self, workspace: Path) -> None:
        pm = PluginManager()
        pm.discover()
        await pm.execute("scaffolder", {
            "action": "scaffold_project",
            "framework": "fastapi",
            "project_name": "plugin_test_app",
            "features": [],
        })
        project = workspace / "plugin_test_app"
        assert project.is_dir()
        assert (project / "main.py").is_file()
        assert (project / "requirements.txt").is_file()

    async def test_scaffolder_node_via_plugin(self, workspace: Path) -> None:
        pm = PluginManager()
        pm.discover()
        result = await pm.execute("scaffolder", {
            "action": "scaffold_project",
            "framework": "node",
            "project_name": "node_plugin_test",
            "features": [],
        })
        assert result["status"] == "ok"
        assert (workspace / "node_plugin_test" / "package.json").is_file()
        assert (workspace / "node_plugin_test" / "index.js").is_file()

    async def test_scaffolder_react_via_plugin(self, workspace: Path) -> None:
        pm = PluginManager()
        pm.discover()
        result = await pm.execute("scaffolder", {
            "action": "scaffold_project",
            "framework": "react",
            "project_name": "react_plugin_test",
            "features": [],
        })
        assert result["status"] == "ok"
        assert (workspace / "react_plugin_test" / "src").is_dir()
        assert (workspace / "react_plugin_test" / "package.json").is_file()

    async def test_scaffolder_rejects_unknown_action(self, workspace: Path) -> None:
        pm = PluginManager()
        pm.discover()
        with pytest.raises(ValueError, match="Unknown action"):
            await pm.execute("scaffolder", {
                "action": "deploy",
                "framework": "fastapi",
                "project_name": "x",
            })

    async def test_scaffolder_rejects_unknown_framework(self, workspace: Path) -> None:
        pm = PluginManager()
        pm.discover()
        with pytest.raises(ValueError, match="No template for framework"):
            await pm.execute("scaffolder", {
                "action": "scaffold_project",
                "framework": "django",
                "project_name": "x",
            })


# ═════════════════════════════════════════════════════════════════════
# Filesystem plugin — real execution against tmp_path
# ═════════════════════════════════════════════════════════════════════


class TestFilesystemPluginExecution:
    async def test_create_folder(self, tmp_path: Path) -> None:
        pm = PluginManager()
        pm.discover()
        target = str(tmp_path / "new_dir")
        result = await pm.execute("filesystem", {
            "action": "create_folder",
            "path": target,
        })
        assert result["status"] == "ok"
        assert Path(target).is_dir()

    async def test_create_file(self, tmp_path: Path) -> None:
        pm = PluginManager()
        pm.discover()
        target = str(tmp_path / "hello.txt")
        result = await pm.execute("filesystem", {
            "action": "create_file",
            "path": target,
            "content": "hello world",
        })
        assert result["status"] == "ok"
        assert Path(target).read_text(encoding="utf-8") == "hello world"

    async def test_list_directory(self, tmp_path: Path) -> None:
        (tmp_path / "a.txt").write_text("a", encoding="utf-8")
        (tmp_path / "subdir").mkdir()

        pm = PluginManager()
        pm.discover()
        result = await pm.execute("filesystem", {
            "action": "list_directory",
            "path": str(tmp_path),
        })
        assert result["status"] == "ok"
        names = {e["name"] for e in result["entries"]}
        assert "a.txt" in names
        assert "subdir" in names

    async def test_unknown_action_raises(self) -> None:
        pm = PluginManager()
        pm.discover()
        with pytest.raises(ValueError, match="unknown action"):
            await pm.execute("filesystem", {"action": "delete_everything"})


# ═════════════════════════════════════════════════════════════════════
# Docker plugin — real execution against tmp_path
# ═════════════════════════════════════════════════════════════════════


class TestDockerPluginExecution:
    @pytest.mark.parametrize("framework", ["node", "react", "fastapi"])
    async def test_generates_dockerfile(self, tmp_path: Path, framework: str) -> None:
        pm = PluginManager()
        pm.discover()
        result = await pm.execute("docker", {
            "action": "generate_dockerfile",
            "framework": framework,
            "project_path": str(tmp_path),
        })
        assert result["status"] == "ok"
        assert (tmp_path / "Dockerfile").is_file()
        content = (tmp_path / "Dockerfile").read_text(encoding="utf-8")
        assert "FROM" in content

    async def test_unknown_framework_raises(self, tmp_path: Path) -> None:
        pm = PluginManager()
        pm.discover()
        with pytest.raises(ValueError, match="No Dockerfile template"):
            await pm.execute("docker", {
                "action": "generate_dockerfile",
                "framework": "ruby",
                "project_path": str(tmp_path),
            })


# ═════════════════════════════════════════════════════════════════════
# Health check
# ═════════════════════════════════════════════════════════════════════


class TestPluginHealthCheck:
    def test_healthy_plugin_passes(self) -> None:
        pm = PluginManager()
        pm.register(_StubPlugin(), module_path="tests", class_name="_StubPlugin")
        results = pm.check_plugins()
        assert len(results) == 1
        assert results[0].ok is True
        assert results[0].errors == []

    def test_all_builtins_pass_health_check(self) -> None:
        pm = PluginManager()
        pm.discover()
        results = pm.check_plugins()
        assert len(results) == len(pm.list_plugins())
        for r in results:
            assert r.ok is True, f"Plugin '{r.name}' failed: {r.errors}"


# ═════════════════════════════════════════════════════════════════════
# Metadata
# ═════════════════════════════════════════════════════════════════════


class TestPluginMeta:
    def test_meta_captured_on_register(self) -> None:
        pm = PluginManager()
        pm.register(
            _StubPlugin(), module_path="tests.test_plugins", class_name="_StubPlugin"
        )
        meta = pm.get_meta("stub")
        assert meta is not None
        assert meta.name == "stub"
        assert meta.module_path == "tests.test_plugins"
        assert meta.class_name == "_StubPlugin"
        assert meta.description == "Stub plugin for tests"

    def test_get_meta_returns_none_for_missing(self) -> None:
        pm = PluginManager()
        assert pm.get_meta("ghost") is None

    def test_all_meta_after_discover(self) -> None:
        pm = PluginManager()
        pm.discover()
        metas = pm.all_meta()
        assert len(metas) == len(pm.list_plugins())
        names = {m.name for m in metas}
        assert "scaffolder" in names

    def test_describe_on_each_builtin(self) -> None:
        pm = PluginManager()
        pm.discover()
        for name in pm.list_plugins():
            plugin = pm.get(name)
            desc = plugin.describe()
            assert isinstance(desc, str) and len(desc) > 0


# ═════════════════════════════════════════════════════════════════════
# Reload
# ═════════════════════════════════════════════════════════════════════


class TestPluginReload:
    def test_reload_clears_and_rediscovers(self) -> None:
        pm = PluginManager()
        pm.discover()
        original = set(pm.list_plugins())
        assert len(original) > 0

        pm.reload_plugins()
        reloaded = set(pm.list_plugins())
        assert reloaded == original

    def test_reload_preserves_plugin_count(self) -> None:
        pm = PluginManager()
        pm.discover()
        count_before = len(pm.list_plugins())
        pm.reload_plugins()
        assert len(pm.list_plugins()) == count_before
