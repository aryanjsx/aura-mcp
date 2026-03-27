"""DevOps readiness: verify the package installs and CLI entry points work.

Usage
-----
    python scripts/test_package_install.py

The script performs an editable install (``pip install -e .``), then
exercises both CLI entry points and the pytest suite.  Each step is
reported as PASS / FAIL with a final exit code of 0 (all green) or 1.
"""

from __future__ import annotations

import subprocess
import sys
import textwrap

from pathlib import Path

REPO_ROOT = str(Path(__file__).resolve().parent.parent)


def _banner(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def _run(label: str, cmd: list[str]) -> bool:
    """Run *cmd*, print output, and return True on success."""
    print(f"\n>> {label}")
    print(f"   $ {' '.join(cmd)}\n")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(textwrap.indent(result.stdout.strip(), "   "))
    if result.returncode != 0 and result.stderr:
        print(textwrap.indent(result.stderr.strip(), "   "))
    status = "PASS" if result.returncode == 0 else "FAIL"
    print(f"\n   [{status}] exit code {result.returncode}")
    return result.returncode == 0


def main() -> None:
    _banner("AURA MCP — Package Install Verification")
    results: list[tuple[str, bool]] = []

    steps: list[tuple[str, list[str]]] = [
        (
            "Editable install (pip install -e .)",
            [sys.executable, "-m", "pip", "install", "-e", ".", "--quiet"],
        ),
        (
            "aura --help",
            ["aura", "--help"],
        ),
        (
            "python -m aura_mcp --help",
            [sys.executable, "-m", "aura_mcp", "--help"],
        ),
        (
            "Import aura_mcp package",
            [sys.executable, "-c", "import aura_mcp; print('aura_mcp imported successfully')"],
        ),
        (
            "Import core modules",
            [
                sys.executable, "-c",
                "from aura_mcp.core.interpreter import parse_task; "
                "from aura_mcp.core.validator import validate_plan; "
                "from aura_mcp.core.orchestrator import run_pipeline; "
                "print('All core modules imported successfully')",
            ],
        ),
        (
            "Import plugin system",
            [
                sys.executable, "-c",
                "from aura_mcp.plugins.manager import plugin_manager; "
                "names = plugin_manager.list_plugins(); "
                "print(f'Plugins discovered: {names}')",
            ],
        ),
        (
            "Run pytest suite",
            [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
        ),
    ]

    for label, cmd in steps:
        ok = _run(label, cmd)
        results.append((label, ok))

    _banner("Summary")
    all_ok = True
    for label, ok in results:
        icon = "PASS" if ok else "FAIL"
        print(f"  [{icon}] {label}")
        if not ok:
            all_ok = False

    print()
    if all_ok:
        print("All checks passed.")
    else:
        print("Some checks FAILED — review output above.")

    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
