"""Centralized logging for AURA MCP.

All log output goes to *stderr* so it never interferes with MCP stdio
transport on stdout.
"""

from __future__ import annotations

import logging
import sys

_logger: logging.Logger | None = None


def get_logger() -> logging.Logger:
    """Return the shared ``[AURA]`` logger, creating it on first call."""
    global _logger  # noqa: PLW0603
    if _logger is not None:
        return _logger

    from aura_mcp.config.loader import get_config

    config = get_config()
    level_name = config.get("log_level", "info").upper()
    level = getattr(logging, level_name, logging.INFO)

    logger = logging.getLogger("aura")
    logger.setLevel(level)
    logger.propagate = False

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(level)
        fmt = logging.Formatter(
            "[AURA] %(levelname)-5s [%(asctime)s] %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
        handler.setFormatter(fmt)
        logger.addHandler(handler)

    _logger = logger
    return logger
