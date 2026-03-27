"""Local / offline LLM provider stub.

Returns a deterministic JSON response so the pipeline can run without
any network calls.  Replace the body of ``generate`` with a real local
inference backend (llama.cpp, Ollama, etc.) when ready.
"""

from __future__ import annotations

import json

from aura_mcp.integrations.llm.base import BaseLLM
from aura_mcp.utils.logger import get_logger


class LocalProvider(BaseLLM):
    """Offline stub that returns a best-effort scaffold plan."""

    async def generate(self, prompt: str, *, system: str = "") -> str:
        logger = get_logger()
        logger.info("Using local LLM stub (offline mode)")

        return json.dumps({
            "action": "scaffold_project",
            "framework": "node",
            "project_name": "local_project",
            "features": [],
        })
