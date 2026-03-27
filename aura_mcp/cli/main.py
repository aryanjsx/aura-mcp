"""CLI entry point — ``aura start | config | plugins | doctor | init``."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import typer
from rich import print as rprint
from rich.table import Table

app = typer.Typer(
    name="aura",
    help="AURA MCP — Autonomous Unified Resource Architect",
    add_completion=False,
)

_SECRET_PATHS = [
    ("notion", "api_key"),
    ("openai", "api_key"),
    ("github", "token"),
]


def _mask(value: str) -> str:
    if len(value) <= 12:
        return "***"
    return value[:8] + "..." + value[-4:]


def _mask_secrets(cfg: dict) -> dict:
    safe = json.loads(json.dumps(cfg))
    for section, key in _SECRET_PATHS:
        val = safe.get(section, {}).get(key, "")
        if val:
            safe[section][key] = _mask(val)
    return safe


# ── Commands ─────────────────────────────────────────────────────────


@app.command()
def start() -> None:
    """Start the AURA MCP server (stdio transport)."""
    from dotenv import load_dotenv

    from aura_mcp.server.mcp_server import start_server

    load_dotenv()
    start_server()


@app.command("config")
def show_config() -> None:
    """Display the active configuration (secrets masked)."""
    from dotenv import load_dotenv

    from aura_mcp.config.loader import load_config

    load_dotenv()
    cfg = load_config()

    rprint("[bold]AURA MCP — Active Configuration[/bold]\n")
    rprint(json.dumps(_mask_secrets(cfg), indent=2))


@app.command()
def plugins() -> None:
    """List all discovered plugins with descriptions."""
    from dotenv import load_dotenv

    from aura_mcp.config.loader import load_config
    from aura_mcp.plugins.manager import plugin_manager

    load_dotenv()
    load_config()

    table = Table(title="Loaded Plugins")
    table.add_column("Name", style="cyan", min_width=14)
    table.add_column("Description")
    table.add_column("Status", justify="center")

    health = {r.name: r for r in plugin_manager.check_plugins()}

    for name in plugin_manager.list_plugins():
        plugin = plugin_manager.get(name)
        desc = plugin.describe() if plugin else ""
        ok = health.get(name)
        status = "[green]OK[/green]" if ok and ok.ok else "[red]FAIL[/red]"
        table.add_row(name, desc, status)

    rprint(table)


@app.command("plugins-debug")
def plugins_debug() -> None:
    """Show detailed debug info for every loaded plugin."""
    from dotenv import load_dotenv

    from aura_mcp.config.loader import load_config
    from aura_mcp.plugins.manager import plugin_manager

    load_dotenv()
    load_config()

    health = {r.name: r for r in plugin_manager.check_plugins()}

    for meta in plugin_manager.all_meta():
        hr = health.get(meta.name)
        status = "[green]OK[/green]" if hr and hr.ok else "[red]FAIL[/red]"
        rprint(f"\n[bold cyan]{meta.name}[/bold cyan]  {status}")
        rprint(f"  module:      {meta.module_path}")
        rprint(f"  class:       {meta.class_name}")
        rprint(f"  description: {meta.description}")
        if hr and hr.errors:
            for err in hr.errors:
                rprint(f"  [red]error:[/red]       {err}")


@app.command()
def doctor() -> None:
    """Check system readiness — environment variables, config, and plugins."""
    import os

    from dotenv import load_dotenv

    from aura_mcp.config.loader import load_config
    from aura_mcp.plugins.manager import plugin_manager

    load_dotenv()
    cfg = load_config()

    rprint("[bold]AURA MCP — System Doctor[/bold]\n")

    checks: list[tuple[str, bool, str]] = []

    # Python version
    import sys

    py = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    checks.append(("Python version", sys.version_info >= (3, 11), py))

    # Config file
    cfg_path = Path(__file__).parent.parent / "config" / "config.yaml"
    checks.append(("Config file", cfg_path.exists(), str(cfg_path)))

    # Required env vars
    for env_var in ("NOTION_API_KEY", "NOTION_DATABASE_ID", "OPENAI_API_KEY"):
        present = bool(os.environ.get(env_var))
        checks.append((env_var, present, "set" if present else "missing"))

    # Optional env vars
    gh = bool(os.environ.get("GITHUB_TOKEN"))
    checks.append(("GITHUB_TOKEN (optional)", gh, "set" if gh else "missing"))

    # LLM mode
    mode = cfg.get("llm_mode", "openai")
    checks.append(("LLM mode", True, mode))

    # Plugins
    names = plugin_manager.list_plugins()
    checks.append(("Plugins loaded", len(names) > 0, ", ".join(names)))

    table = Table()
    table.add_column("Check", style="bold")
    table.add_column("Status")
    table.add_column("Detail")

    for label, ok, detail in checks:
        icon = "[green]OK[/green]" if ok else "[red]MISSING[/red]"
        table.add_row(label, icon, detail)

    rprint(table)


@app.command()
def init() -> None:
    """Initialize an AURA config file in the current directory."""
    src = Path(__file__).parent.parent / "config" / "config.yaml"
    dest = Path.cwd() / "aura_config.yaml"

    if dest.exists():
        rprint(f"[yellow]Config already exists:[/yellow] {dest}")
        raise typer.Exit()

    shutil.copy2(src, dest)
    rprint(f"[green]Created config:[/green] {dest}")
    rprint("Edit it, then set [bold]AURA_CONFIG=[/bold] to point at it.")


if __name__ == "__main__":
    app()
