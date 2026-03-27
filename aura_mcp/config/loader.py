"""YAML-based configuration loader with environment variable overrides."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

_config: dict[str, Any] | None = None

DEFAULTS: dict[str, Any] = {
    "workspace": os.path.expanduser("~/projects"),
    "default_stack": "fastapi",
    "log_level": "info",
    "llm_mode": "openai",
    "github_enabled": True,
    "docker_enabled": True,
    "notion": {
        "api_key": "",
        "database_id": "",
    },
    "openai": {
        "api_key": "",
        "model": "gpt-3.5-turbo",
    },
    "github": {
        "token": "",
    },
}


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge *override* into *base*, returning a new dict."""
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    """Load configuration from YAML, then apply environment variable overrides.

    Falls back to built-in defaults when no config file is found.
    """
    global _config  # noqa: PLW0603

    if path is None:
        path = Path(__file__).parent / "config.yaml"
    else:
        path = Path(path)

    config: dict[str, Any] = _deep_merge(DEFAULTS, {})

    if path.exists():
        with open(path, encoding="utf-8") as fh:
            user_config = yaml.safe_load(fh) or {}
        config = _deep_merge(config, user_config)

    env_map = [
        ("NOTION_API_KEY", ("notion", "api_key")),
        ("NOTION_DATABASE_ID", ("notion", "database_id")),
        ("OPENAI_API_KEY", ("openai", "api_key")),
        ("OPENAI_MODEL", ("openai", "model")),
        ("GITHUB_TOKEN", ("github", "token")),
        ("AURA_WORKSPACE", ("workspace",)),
        ("AURA_LOG_LEVEL", ("log_level",)),
        ("AURA_LLM_MODE", ("llm_mode",)),
    ]
    for env_var, key_path in env_map:
        value = os.environ.get(env_var)
        if value:
            target = config
            for part in key_path[:-1]:
                target = target.setdefault(part, {})
            target[key_path[-1]] = value

    _config = config
    return config


def get_config() -> dict[str, Any]:
    """Return the current configuration, loading it lazily on first access."""
    if _config is None:
        return load_config()
    return _config
