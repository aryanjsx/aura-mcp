# Plugin Development Guide

AURA uses a plugin architecture that lets you add new capabilities without
modifying any core code. Drop a Python module into `aura_mcp/plugins/` and
the plugin manager discovers it automatically at startup.

## Built-in Plugins

| Plugin | File | Capabilities |
|--------|------|-------------|
| **notion** | `notion_plugin.py` | Read tasks, update status |
| **scaffolder** | `scaffolder_plugin.py` | Generate React / Node / FastAPI projects |
| **github** | `github_plugin.py` | Create repos, push files |
| **docker** | `docker_plugin.py` | Generate Dockerfiles |
| **filesystem** | `filesystem_plugin.py` | Create files/folders, list directories |

## Creating a New Plugin

### 1. Create the file

Create `aura_mcp/plugins/my_plugin.py`:

```python
from __future__ import annotations
from typing import Any
from aura_mcp.plugins.base import BasePlugin
from aura_mcp.utils.logger import get_logger


class MyPlugin(BasePlugin):

    @property
    def name(self) -> str:
        return "my_plugin"

    async def execute(self, intent: dict[str, Any]) -> dict[str, Any]:
        logger = get_logger()
        action = intent.get("action", "")

        if action == "greet":
            logger.info("Hello from my plugin!")
            return {"status": "ok", "message": "Hello!"}

        raise ValueError(f"Unknown action: {action}")

    def describe(self) -> str:
        return "My custom plugin"
```

### 2. That's it

The plugin manager scans every module in `aura_mcp/plugins/` (skipping
`base.py` and `manager.py`), finds classes that inherit from `BasePlugin`,
and registers an instance automatically.

Verify with:

```bash
aura plugins
```

## Plugin API

### `BasePlugin` (abstract)

| Method | Required | Purpose |
|--------|----------|---------|
| `name` (property) | Yes | Unique string identifier |
| `execute(intent)` | Yes | Dispatch on `intent["action"]` |
| `describe()` | No | One-line description for `aura plugins` |

### `intent` dict

Every call to `execute` receives an intent dict. The only mandatory key is
`action` — additional keys are action-specific.

```python
intent = {
    "action": "create_file",
    "path": "/tmp/hello.txt",
    "content": "Hello, world!",
}
```

### Return value

Return a dict with at least `{"status": "ok"}` on success.

## Calling Plugins from the Orchestrator

```python
result = await plugin_manager.execute("my_plugin", {"action": "greet"})
```
