"""Factory that returns the correct LLM provider and a backward-compatible helper."""

from __future__ import annotations

import json
import re

from aura_mcp.config.loader import get_config
from aura_mcp.integrations.llm.base import BaseLLM
from aura_mcp.utils.logger import get_logger

SYSTEM_PROMPT = """\
You are an AI that converts user task descriptions into structured JSON commands \
for a project scaffolding system.

Rules:
- Return ONLY valid JSON. No explanation, no markdown, no extra text.
- The JSON must match this exact schema:

{
  "action": "scaffold_project",
  "framework": "react" | "node" | "fastapi",
  "project_name": "snake_case_name",
  "features": ["optional", "feature", "keywords"]
}

Guidelines for project_name:
- Use snake_case
- Keep it short and descriptive (e.g. "bookstore_api", "portfolio_site")
- Derive it from the user's intent, not the framework name alone

Guidelines for framework:
- "react" for any React, frontend, or UI project
- "node" for any Node.js, Express, or JavaScript API/backend project
- "fastapi" for any Python, FastAPI, or Flask project
- Default to "node" if unclear\
"""


def get_llm() -> BaseLLM:
    """Return the LLM provider indicated by ``llm_mode`` in config."""
    config = get_config()
    mode = config.get("llm_mode", "openai")

    if mode == "local":
        from aura_mcp.integrations.llm.local_provider import LocalProvider

        return LocalProvider()

    from aura_mcp.integrations.llm.openai_provider import OpenAIProvider

    return OpenAIProvider()


async def interpret_with_llm(task_text: str) -> dict:
    """Backward-compatible wrapper used by the interpreter.

    Sends *task_text* through the active LLM provider and parses the
    returned JSON into a plan dict.
    """
    logger = get_logger()
    llm = get_llm()

    raw = await llm.generate(
        f'Convert this task into JSON:\n\nTask: "{task_text}"',
        system=SYSTEM_PROMPT,
    )

    logger.info("Parsing JSON from LLM response...")

    cleaned = re.sub(r"```json\s*", "", raw)
    cleaned = re.sub(r"```\s*", "", cleaned).strip()

    try:
        plan = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"LLM returned invalid JSON: {cleaned[:200]}"
        ) from exc

    return plan
