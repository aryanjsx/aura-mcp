"""Abstract interface every LLM provider must implement."""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseLLM(ABC):
    """Minimal contract for an LLM backend."""

    @abstractmethod
    async def generate(self, prompt: str, *, system: str = "") -> str:
        """Send *prompt* (with optional *system* message) and return the raw text."""
        ...
