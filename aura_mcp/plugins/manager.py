"""Dynamic plugin loader and registry."""

from __future__ import annotations

import importlib
import pkgutil
from typing import Any

from aura_mcp.plugins.base import BasePlugin
from aura_mcp.utils.logger import get_logger


class PluginManager:
    """Discovers, registers, and dispatches work to plugins."""

    def __init__(self) -> None:
        self._registry: dict[str, BasePlugin] = {}

    def register(self, plugin: BasePlugin) -> None:
        """Add a plugin instance to the registry."""
        logger = get_logger()
        self._registry[plugin.name] = plugin
        logger.info("Registered plugin: %s", plugin.name)

    def discover(self, package_name: str = "aura_mcp.plugins") -> None:
        """Auto-discover all ``BasePlugin`` subclasses inside *package_name*."""
        logger = get_logger()
        try:
            package = importlib.import_module(package_name)
        except ImportError:
            logger.warning("Could not import plugin package: %s", package_name)
            return

        prefix = package_name + "."
        for _importer, modname, _ispkg in pkgutil.iter_modules(
            package.__path__, prefix
        ):
            if modname.endswith((".base", ".manager")):
                continue
            try:
                module = importlib.import_module(modname)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, BasePlugin)
                        and attr is not BasePlugin
                    ):
                        instance = attr()
                        if instance.name not in self._registry:
                            self.register(instance)
            except Exception as exc:
                logger.warning("Failed to load plugin %s: %s", modname, exc)

    async def execute(
        self, plugin_name: str, intent: dict[str, Any]
    ) -> dict[str, Any]:
        """Dispatch *intent* to the named plugin and return its result."""
        plugin = self._registry.get(plugin_name)
        if plugin is None:
            raise ValueError(f"Plugin not found: {plugin_name}")
        return await plugin.execute(intent)

    def list_plugins(self) -> list[str]:
        """Return names of all registered plugins."""
        return list(self._registry.keys())

    def get_plugin(self, name: str) -> BasePlugin | None:
        """Look up a single plugin by name (returns ``None`` if missing)."""
        return self._registry.get(name)
