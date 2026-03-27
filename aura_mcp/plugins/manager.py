"""Dynamic plugin loader and registry."""

from __future__ import annotations

import importlib
import inspect
import pkgutil
from dataclasses import dataclass, field
from typing import Any

from aura_mcp.plugins.base import BasePlugin
from aura_mcp.utils.logger import get_logger


@dataclass(frozen=True)
class PluginMeta:
    """Metadata captured during plugin discovery for debugging."""

    name: str
    module_path: str
    class_name: str
    description: str


@dataclass
class PluginHealthResult:
    """Result of a single plugin health check."""

    name: str
    has_name: bool = True
    has_execute: bool = True
    execute_is_async: bool = True
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.has_name and self.has_execute and self.execute_is_async


class PluginManager:
    """Discovers, registers, and dispatches work to plugins."""

    def __init__(self) -> None:
        self._registry: dict[str, BasePlugin] = {}
        self._meta: dict[str, PluginMeta] = {}

    # ── Registration ────────────────────────────────────────────────

    def register(
        self,
        plugin: BasePlugin,
        *,
        module_path: str = "",
        class_name: str = "",
    ) -> None:
        """Add a plugin instance to the registry.

        Raises ``RuntimeError`` if a plugin with the same name is already
        registered.
        """
        logger = get_logger()

        if plugin.name in self._registry:
            raise RuntimeError(f"Duplicate plugin detected: {plugin.name}")

        self._registry[plugin.name] = plugin
        self._meta[plugin.name] = PluginMeta(
            name=plugin.name,
            module_path=module_path,
            class_name=class_name or type(plugin).__name__,
            description=plugin.describe(),
        )
        logger.info("Registered plugin: %s", plugin.name)

    # ── Discovery ───────────────────────────────────────────────────

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

            logger.debug("Scanning plugin module: %s", modname)

            try:
                module = importlib.import_module(modname)
            except Exception as exc:
                logger.warning(
                    "Failed to import plugin module %s: %s", modname, exc
                )
                continue

            found_any = False
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, BasePlugin)
                    and attr is not BasePlugin
                ):
                    logger.debug("Found plugin class: %s.%s", modname, attr_name)
                    found_any = True

                    if attr_name in self._registry:
                        continue

                    try:
                        instance = attr()
                        if instance.name not in self._registry:
                            self.register(
                                instance,
                                module_path=modname,
                                class_name=attr_name,
                            )
                    except Exception as exc:
                        logger.warning(
                            "Failed to instantiate plugin %s.%s: %s",
                            modname,
                            attr_name,
                            exc,
                        )

            if not found_any:
                logger.debug(
                    "No BasePlugin subclasses found in %s — skipping", modname
                )

    # ── Execution ───────────────────────────────────────────────────

    async def execute(
        self, plugin_name: str, intent: dict[str, Any]
    ) -> dict[str, Any]:
        """Dispatch *intent* to the named plugin and return its result."""
        plugin = self._registry.get(plugin_name)
        if plugin is None:
            raise ValueError(f"Plugin not found: {plugin_name}")

        result = await plugin.execute(intent)

        if not isinstance(result, dict):
            raise TypeError(
                f"Plugin '{plugin_name}' must return dict, "
                f"got {type(result).__name__}"
            )
        return result

    # ── Lookup ──────────────────────────────────────────────────────

    def list_plugins(self) -> list[str]:
        """Return names of all registered plugins."""
        return list(self._registry.keys())

    def get(self, name: str) -> BasePlugin | None:
        """Look up a single plugin by name (returns ``None`` if missing)."""
        return self._registry.get(name)

    get_plugin = get

    def get_meta(self, name: str) -> PluginMeta | None:
        """Return discovery metadata for a plugin."""
        return self._meta.get(name)

    def all_meta(self) -> list[PluginMeta]:
        """Return metadata for every registered plugin."""
        return list(self._meta.values())

    # ── Health check ────────────────────────────────────────────────

    def check_plugins(self) -> list[PluginHealthResult]:
        """Validate every registered plugin's conformance to the interface."""
        results: list[PluginHealthResult] = []

        for name, plugin in self._registry.items():
            r = PluginHealthResult(name=name)

            if not getattr(plugin, "name", None):
                r.has_name = False
                r.errors.append("Missing 'name' property")

            execute_fn = getattr(plugin, "execute", None)
            if execute_fn is None:
                r.has_execute = False
                r.errors.append("Missing 'execute' method")
            elif not inspect.iscoroutinefunction(execute_fn):
                r.execute_is_async = False
                r.errors.append("'execute' is not async")

            results.append(r)

        return results

    # ── Hot reload ──────────────────────────────────────────────────

    def reload_plugins(self, package_name: str = "aura_mcp.plugins") -> None:
        """Clear the registry and re-run discovery.

        Useful during development to pick up plugin changes without
        restarting the process.  Modules are force-reloaded so that code
        changes take effect.
        """
        logger = get_logger()
        logger.info("Reloading plugins...")

        old_names = list(self._registry.keys())
        self._registry.clear()
        self._meta.clear()

        package = importlib.import_module(package_name)
        prefix = package_name + "."
        for _importer, modname, _ispkg in pkgutil.iter_modules(
            package.__path__, prefix
        ):
            if modname.endswith((".base", ".manager")):
                continue
            if modname in inspect.sys.modules:
                importlib.reload(inspect.sys.modules[modname])

        self.discover(package_name)

        new_names = list(self._registry.keys())
        logger.info(
            "Reload complete — before: %s, after: %s",
            old_names,
            new_names,
        )


# ── Module-level singleton ──────────────────────────────────────────


def _make_plugin_manager() -> PluginManager:
    """Create a singleton ``PluginManager`` with lazy auto-discovery."""
    pm = PluginManager()
    pm.discover()
    return pm


class _LazyPluginManager:
    """Proxy that defers ``PluginManager`` creation until first attribute access.

    This avoids import-time side-effects (logging, module scanning) while
    still providing a module-level ``plugin_manager`` singleton.
    """

    def __init__(self) -> None:
        self._instance: PluginManager | None = None

    def _ensure(self) -> PluginManager:
        if self._instance is None:
            self._instance = _make_plugin_manager()
        return self._instance

    def __getattr__(self, name: str) -> Any:
        return getattr(self._ensure(), name)


plugin_manager: PluginManager = _LazyPluginManager()  # type: ignore[assignment]
