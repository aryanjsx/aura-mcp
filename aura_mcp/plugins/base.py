"""Abstract base class that every AURA plugin must implement."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BasePlugin(ABC):
    """Base class for all AURA plugins.

    Subclasses must define ``name`` and implement ``execute``.
    Drop a new module into ``aura_mcp/plugins/`` and the plugin manager
    will discover it automatically — no core changes required.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this plugin."""
        ...

    @abstractmethod
    async def execute(self, intent: dict[str, Any]) -> dict[str, Any]:
        """Run the plugin with the given *intent* payload.

        Parameters
        ----------
        intent:
            A dict whose ``action`` key selects what the plugin should do.
            Additional keys carry action-specific data.

        Returns
        -------
        dict with at least a ``status`` key (``"ok"`` or ``"error"``).
        """
        ...

    def describe(self) -> str:
        """Human-readable one-liner shown in ``aura plugins``."""
        return f"Plugin: {self.name}"
