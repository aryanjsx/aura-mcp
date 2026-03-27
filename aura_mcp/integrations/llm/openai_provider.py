"""OpenAI-backed LLM provider."""

from __future__ import annotations

import os

from openai import AsyncOpenAI

from aura_mcp.config.loader import get_config
from aura_mcp.integrations.llm.base import BaseLLM
from aura_mcp.utils.logger import get_logger


class OpenAIProvider(BaseLLM):
    """Calls the OpenAI chat-completions API."""

    async def generate(self, prompt: str, *, system: str = "") -> str:
        config = get_config()
        logger = get_logger()

        api_key = (
            config.get("openai", {}).get("api_key")
            or os.environ.get("OPENAI_API_KEY", "")
        )
        if not api_key:
            raise RuntimeError("Missing OPENAI_API_KEY in environment / config")

        model = (
            config.get("openai", {}).get("model")
            or os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
        )

        client = AsyncOpenAI(api_key=api_key)

        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        logger.info("Sending task to LLM (%s)...", model)

        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0,
            max_tokens=256,
        )

        raw = (response.choices[0].message.content or "").strip()
        if not raw:
            raise RuntimeError("LLM returned empty response")

        logger.info("LLM response received")
        return raw
