"""LLM provider abstraction layer.

Public API
----------
- ``get_llm()``            — returns the active provider based on config
- ``interpret_with_llm()`` — backward-compatible helper used by the interpreter
"""

from aura_mcp.integrations.llm.factory import get_llm, interpret_with_llm

__all__ = ["get_llm", "interpret_with_llm"]
