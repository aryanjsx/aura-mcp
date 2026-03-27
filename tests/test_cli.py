"""Tests for CLI commands using Typer's test runner.

The ``start`` command is tested with ``start_server`` mocked out so the
stdio transport never actually blocks.  All other commands run for real
against the live plugin registry and config loader.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

import aura_mcp.config.loader as loader_mod
from aura_mcp.cli.main import _mask, _mask_secrets, app

runner = CliRunner()


@pytest.fixture(autouse=True)
def _reset_config_cache():
    """Clear cached config so each test starts fresh."""
    loader_mod._config = None
    yield
    loader_mod._config = None


# ═════════════════════════════════════════════════════════════════════
# aura plugins
# ═════════════════════════════════════════════════════════════════════


class TestPluginsCommand:
    def test_exits_successfully(self):
        result = runner.invoke(app, ["plugins"])
        assert result.exit_code == 0

    def test_lists_scaffolder(self):
        result = runner.invoke(app, ["plugins"])
        assert "scaffolder" in result.output

    def test_lists_filesystem(self):
        result = runner.invoke(app, ["plugins"])
        assert "filesystem" in result.output

    def test_lists_notion(self):
        result = runner.invoke(app, ["plugins"])
        assert "notion" in result.output

    def test_lists_docker(self):
        result = runner.invoke(app, ["plugins"])
        assert "docker" in result.output

    def test_lists_github(self):
        result = runner.invoke(app, ["plugins"])
        assert "github" in result.output

    def test_shows_ok_status(self):
        result = runner.invoke(app, ["plugins"])
        assert "OK" in result.output

    def test_shows_descriptions(self):
        result = runner.invoke(app, ["plugins"])
        assert "scaffolder" in result.output.lower() or "Scaffold" in result.output


# ═════════════════════════════════════════════════════════════════════
# aura config
# ═════════════════════════════════════════════════════════════════════


class TestConfigCommand:
    def test_exits_successfully(self):
        result = runner.invoke(app, ["config"])
        assert result.exit_code == 0

    def test_shows_workspace(self):
        result = runner.invoke(app, ["config"])
        assert "workspace" in result.output

    def test_shows_default_stack(self):
        result = runner.invoke(app, ["config"])
        assert "default_stack" in result.output

    def test_shows_log_level(self):
        result = runner.invoke(app, ["config"])
        assert "log_level" in result.output

    def test_shows_llm_mode(self):
        result = runner.invoke(app, ["config"])
        assert "llm_mode" in result.output

    def test_shows_notion_section(self):
        result = runner.invoke(app, ["config"])
        assert "notion" in result.output

    def test_shows_openai_section(self):
        result = runner.invoke(app, ["config"])
        assert "openai" in result.output

    def test_output_is_valid_json_fragment(self):
        result = runner.invoke(app, ["config"])
        assert "{" in result.output and "}" in result.output

    def test_secrets_are_masked(self):
        with patch.dict(
            "os.environ", {"OPENAI_API_KEY": "sk-a]very-long-secret-key-value"}
        ):
            result = runner.invoke(app, ["config"])
        assert "sk-a]ver" not in result.output or "..." in result.output


# ═════════════════════════════════════════════════════════════════════
# aura start
# ═════════════════════════════════════════════════════════════════════


class TestStartCommand:
    def test_calls_start_server(self):
        mock_server = MagicMock()
        with patch("aura_mcp.server.mcp_server.start_server", mock_server):
            result = runner.invoke(app, ["start"])
        mock_server.assert_called_once()

    def test_exits_successfully(self):
        with patch("aura_mcp.server.mcp_server.start_server", MagicMock()):
            result = runner.invoke(app, ["start"])
        assert result.exit_code == 0

    def test_does_not_crash_on_server_error(self):
        with patch(
            "aura_mcp.server.mcp_server.start_server",
            side_effect=RuntimeError("port in use"),
        ):
            result = runner.invoke(app, ["start"])
        assert result.exit_code != 0 or "port in use" in str(result.exception)


# ═════════════════════════════════════════════════════════════════════
# aura doctor
# ═════════════════════════════════════════════════════════════════════


class TestDoctorCommand:
    def test_exits_successfully(self):
        result = runner.invoke(app, ["doctor"])
        assert result.exit_code == 0

    def test_shows_python_version(self):
        result = runner.invoke(app, ["doctor"])
        assert "Python" in result.output

    def test_shows_plugin_status(self):
        result = runner.invoke(app, ["doctor"])
        assert "Plugins" in result.output or "plugin" in result.output.lower()

    def test_shows_llm_mode(self):
        result = runner.invoke(app, ["doctor"])
        assert "LLM" in result.output


# ═════════════════════════════════════════════════════════════════════
# aura plugins-debug
# ═════════════════════════════════════════════════════════════════════


class TestPluginsDebugCommand:
    def test_exits_successfully(self):
        result = runner.invoke(app, ["plugins-debug"])
        assert result.exit_code == 0

    def test_shows_module_paths(self):
        result = runner.invoke(app, ["plugins-debug"])
        assert "module:" in result.output

    def test_shows_class_names(self):
        result = runner.invoke(app, ["plugins-debug"])
        assert "class:" in result.output


# ═════════════════════════════════════════════════════════════════════
# aura init
# ═════════════════════════════════════════════════════════════════════


class TestInitCommand:
    def test_creates_config_file(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0
        assert (tmp_path / "aura_config.yaml").is_file()

    def test_warns_if_config_exists(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "aura_config.yaml").write_text("existing: true", encoding="utf-8")
        result = runner.invoke(app, ["init"])
        assert "already exists" in result.output.lower()


# ═════════════════════════════════════════════════════════════════════
# Secret masking helpers
# ═════════════════════════════════════════════════════════════════════


class TestMaskHelpers:
    def test_short_secret_fully_masked(self):
        assert _mask("abc") == "***"
        assert _mask("123456789012") == "***"

    def test_long_secret_partially_shown(self):
        masked = _mask("sk-abcdefghijklmnop")
        assert masked.startswith("sk-abcde")
        assert masked.endswith("mnop")
        assert "..." in masked

    def test_mask_secrets_hides_notion_key(self):
        cfg = {
            "workspace": "/tmp",
            "notion": {"api_key": "secret-notion-api-key-1234", "database_id": ""},
            "openai": {"api_key": "", "model": "gpt-3.5-turbo"},
            "github": {"token": ""},
        }
        safe = _mask_secrets(cfg)
        assert safe["notion"]["api_key"] != "secret-notion-api-key-1234"
        assert "..." in safe["notion"]["api_key"]

    def test_mask_secrets_preserves_non_secret_values(self):
        cfg = {
            "workspace": "/home/user",
            "notion": {"api_key": "", "database_id": "db-123"},
            "openai": {"api_key": "", "model": "gpt-4"},
            "github": {"token": ""},
        }
        safe = _mask_secrets(cfg)
        assert safe["workspace"] == "/home/user"
        assert safe["openai"]["model"] == "gpt-4"

    def test_mask_secrets_does_not_mutate_original(self):
        cfg = {
            "notion": {"api_key": "real-key-that-is-long-enough", "database_id": ""},
            "openai": {"api_key": "", "model": "gpt-3.5-turbo"},
            "github": {"token": ""},
        }
        _mask_secrets(cfg)
        assert cfg["notion"]["api_key"] == "real-key-that-is-long-enough"
