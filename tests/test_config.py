"""Tests for configuration loading, defaults, YAML merging, and env overrides.

Every test resets the module-level ``_config`` cache so that ``get_config``
and ``load_config`` behave deterministically regardless of test ordering.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

import aura_mcp.config.loader as loader_mod
from aura_mcp.config.loader import DEFAULTS, _deep_merge, get_config, load_config


# ── Fixtures ─────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _reset_config_cache():
    """Clear the cached config before and after every test."""
    loader_mod._config = None
    yield
    loader_mod._config = None


# ═════════════════════════════════════════════════════════════════════
# Default config load
# ═════════════════════════════════════════════════════════════════════


class TestDefaultConfig:
    def test_get_config_returns_dict(self):
        config = get_config()
        assert isinstance(config, dict)

    def test_workspace_key_exists(self):
        config = get_config()
        assert "workspace" in config

    def test_default_stack_key_exists(self):
        config = get_config()
        assert "default_stack" in config

    def test_log_level_key_exists(self):
        config = get_config()
        assert "log_level" in config

    def test_default_stack_is_fastapi(self):
        config = load_config()
        assert config["default_stack"] == "fastapi"

    def test_log_level_is_info(self):
        config = load_config()
        assert config["log_level"] == "info"

    def test_llm_mode_key_exists(self):
        config = get_config()
        assert "llm_mode" in config

    def test_feature_flags_exist(self):
        config = get_config()
        assert "github_enabled" in config
        assert "docker_enabled" in config

    def test_nested_notion_section(self):
        config = get_config()
        assert "notion" in config
        assert "api_key" in config["notion"]
        assert "database_id" in config["notion"]

    def test_nested_openai_section(self):
        config = get_config()
        assert "openai" in config
        assert "api_key" in config["openai"]
        assert "model" in config["openai"]

    def test_nested_github_section(self):
        config = get_config()
        assert "github" in config
        assert "token" in config["github"]


# ═════════════════════════════════════════════════════════════════════
# Environment variable overrides
# ═════════════════════════════════════════════════════════════════════


class TestEnvOverrides:
    def test_aura_workspace_override(self):
        with patch.dict("os.environ", {"AURA_WORKSPACE": "/tmp/test_workspace"}):
            config = load_config()
        assert config["workspace"] == "/tmp/test_workspace"

    def test_aura_log_level_override(self):
        with patch.dict("os.environ", {"AURA_LOG_LEVEL": "debug"}):
            config = load_config()
        assert config["log_level"] == "debug"

    def test_aura_llm_mode_override(self):
        with patch.dict("os.environ", {"AURA_LLM_MODE": "local"}):
            config = load_config()
        assert config["llm_mode"] == "local"

    def test_notion_api_key_override(self):
        with patch.dict("os.environ", {"NOTION_API_KEY": "secret-notion-key"}):
            config = load_config()
        assert config["notion"]["api_key"] == "secret-notion-key"

    def test_notion_database_id_override(self):
        with patch.dict("os.environ", {"NOTION_DATABASE_ID": "db-123"}):
            config = load_config()
        assert config["notion"]["database_id"] == "db-123"

    def test_openai_api_key_override(self):
        with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
            config = load_config()
        assert config["openai"]["api_key"] == "sk-test"

    def test_openai_model_override(self):
        with patch.dict("os.environ", {"OPENAI_MODEL": "gpt-4"}):
            config = load_config()
        assert config["openai"]["model"] == "gpt-4"

    def test_github_token_override(self):
        with patch.dict("os.environ", {"GITHUB_TOKEN": "ghp_test123"}):
            config = load_config()
        assert config["github"]["token"] == "ghp_test123"

    def test_multiple_env_overrides_at_once(self):
        env = {
            "AURA_WORKSPACE": "/opt/aura",
            "AURA_LOG_LEVEL": "warning",
            "OPENAI_API_KEY": "sk-multi",
        }
        with patch.dict("os.environ", env):
            config = load_config()
        assert config["workspace"] == "/opt/aura"
        assert config["log_level"] == "warning"
        assert config["openai"]["api_key"] == "sk-multi"

    def test_empty_env_var_does_not_override(self):
        with patch.dict("os.environ", {"AURA_WORKSPACE": ""}, clear=False):
            config = load_config()
        assert config["workspace"] != ""


# ═════════════════════════════════════════════════════════════════════
# Missing config file — fallback to DEFAULTS
# ═════════════════════════════════════════════════════════════════════


class TestMissingConfigFallback:
    def test_nonexistent_path_uses_defaults(self, tmp_path: Path):
        config = load_config(tmp_path / "does_not_exist.yaml")
        assert config["default_stack"] == DEFAULTS["default_stack"]
        assert config["log_level"] == DEFAULTS["log_level"]
        assert config["llm_mode"] == DEFAULTS["llm_mode"]

    def test_nonexistent_path_preserves_all_default_keys(self, tmp_path: Path):
        config = load_config(tmp_path / "missing.yaml")
        for key in DEFAULTS:
            assert key in config

    def test_nonexistent_path_preserves_nested_defaults(self, tmp_path: Path):
        config = load_config(tmp_path / "gone.yaml")
        assert config["notion"]["api_key"] == DEFAULTS["notion"]["api_key"]
        assert config["openai"]["model"] == DEFAULTS["openai"]["model"]
        assert config["github"]["token"] == DEFAULTS["github"]["token"]


# ═════════════════════════════════════════════════════════════════════
# Custom YAML file loading
# ═════════════════════════════════════════════════════════════════════


class TestCustomYAML:
    def test_yaml_values_override_defaults(self, tmp_path: Path):
        yaml_file = tmp_path / "custom.yaml"
        yaml_file.write_text(
            "workspace: /custom/path\nlog_level: debug\n", encoding="utf-8"
        )
        config = load_config(yaml_file)
        assert config["workspace"] == "/custom/path"
        assert config["log_level"] == "debug"

    def test_yaml_keeps_unset_defaults(self, tmp_path: Path):
        yaml_file = tmp_path / "partial.yaml"
        yaml_file.write_text("log_level: warning\n", encoding="utf-8")
        config = load_config(yaml_file)
        assert config["log_level"] == "warning"
        assert config["default_stack"] == DEFAULTS["default_stack"]
        assert config["llm_mode"] == DEFAULTS["llm_mode"]

    def test_yaml_nested_merge(self, tmp_path: Path):
        yaml_file = tmp_path / "nested.yaml"
        yaml_file.write_text(
            "openai:\n  model: gpt-4-turbo\n", encoding="utf-8"
        )
        config = load_config(yaml_file)
        assert config["openai"]["model"] == "gpt-4-turbo"
        assert config["openai"]["api_key"] == DEFAULTS["openai"]["api_key"]

    def test_empty_yaml_uses_defaults(self, tmp_path: Path):
        yaml_file = tmp_path / "empty.yaml"
        yaml_file.write_text("", encoding="utf-8")
        config = load_config(yaml_file)
        for key in DEFAULTS:
            assert key in config

    def test_env_overrides_yaml(self, tmp_path: Path):
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text("workspace: /from/yaml\n", encoding="utf-8")
        with patch.dict("os.environ", {"AURA_WORKSPACE": "/from/env"}):
            config = load_config(yaml_file)
        assert config["workspace"] == "/from/env"


# ═════════════════════════════════════════════════════════════════════
# get_config caching behaviour
# ═════════════════════════════════════════════════════════════════════


class TestGetConfigCache:
    def test_get_config_caches_result(self):
        first = get_config()
        second = get_config()
        assert first is second

    def test_load_config_refreshes_cache(self):
        first = get_config()
        reloaded = load_config()
        assert reloaded is not first
        assert get_config() is reloaded


# ═════════════════════════════════════════════════════════════════════
# _deep_merge helper
# ═════════════════════════════════════════════════════════════════════


class TestDeepMerge:
    def test_flat_override(self):
        result = _deep_merge({"a": 1}, {"a": 2})
        assert result == {"a": 2}

    def test_adds_new_keys(self):
        result = _deep_merge({"a": 1}, {"b": 2})
        assert result == {"a": 1, "b": 2}

    def test_recursive_dict_merge(self):
        base = {"x": {"y": 1, "z": 2}}
        over = {"x": {"z": 99}}
        result = _deep_merge(base, over)
        assert result == {"x": {"y": 1, "z": 99}}

    def test_does_not_mutate_base(self):
        base = {"a": {"b": 1}}
        _deep_merge(base, {"a": {"b": 2}})
        assert base["a"]["b"] == 1

    def test_empty_override_returns_copy(self):
        base = {"a": 1}
        result = _deep_merge(base, {})
        assert result == base
        assert result is not base
