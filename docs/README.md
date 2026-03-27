# AURA MCP Documentation

## What is AURA?

**AURA** (Autonomous Unified Resource Architect) is an extensible AI automation
platform built on the Model Context Protocol (MCP). It reads tasks — from Notion,
from the CLI, or from any MCP client — interprets them with AI, and executes
real actions: scaffolding projects, creating GitHub repos, generating
Dockerfiles, and more.

## Key Features

| Feature | Description |
|---------|-------------|
| **Notion integration** | Fetch pending tasks and write results back automatically |
| **AI interpreter** | Converts natural language into structured execution plans |
| **Rule-based fallback** | Deterministic parser runs when LLM is unavailable |
| **Project scaffolder** | Generates real React, Node.js, and FastAPI projects |
| **Plugin system** | Drop-in plugins — no core changes required |
| **GitHub integration** | Create repos and push files via the GitHub API |
| **Docker support** | Auto-generate Dockerfiles for any framework |
| **LLM abstraction** | Swap between OpenAI, local models, or future providers |
| **Config system** | YAML config with environment variable overrides |
| **CLI** | `aura start`, `aura plugins`, `aura doctor`, and more |

## Architecture Overview

```
aura_mcp/
├── cli/            CLI entry points (Typer)
├── config/         YAML config + loader
├── core/           Orchestrator, interpreter, validator, executor
├── integrations/   Notion SDK, LLM providers
├── plugins/        Auto-discovered plugin modules
├── server/         MCP server (FastMCP, stdio transport)
└── utils/          Logger, file helpers
```

### Data Flow

```
Task text ─► Interpreter ─► Validator ─► Executor ─► Filesystem
     │            │                          │
     │       LLM / Rules                     └─► Docker, GitHub
     │                                       
     └─► Notion (read) ──────────────────── Notion (write back)
```

## Quick Start

```bash
# Install
pip install -e .

# Check readiness
aura doctor

# Start the MCP server
aura start

# Or run directly
python -m aura_mcp start
```

## Further Reading

- [Plugin Development Guide](PLUGINS.md)
- [Configuration Reference](CONFIG.md)
