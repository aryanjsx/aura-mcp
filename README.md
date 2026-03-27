<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=40&duration=3000&pause=1000&color=8B5CF6&center=true&vCenter=true&multiline=true&repeat=true&width=600&height=80&lines=AURA+MCP" alt="AURA MCP" />

### ✨ Autonomous Unified Resource Architect ✨

<br/>

> 🧠 *Describe what you want. AURA builds it for you.*

<br/>

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)](LICENSE)
[![Tests: 252](https://img.shields.io/badge/Tests-252%20Passed-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)](#-testing)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](#-docker)
[![MCP](https://img.shields.io/badge/MCP-Compatible-8B5CF6?style=for-the-badge)](https://modelcontextprotocol.io/)
[![Notion](https://img.shields.io/badge/Notion-Integrated-000000?style=for-the-badge&logo=notion&logoColor=white)](https://developers.notion.com/)
[![Version](https://img.shields.io/badge/v0.3.0-blue?style=for-the-badge)]()

<br/>

<p>
An AI-powered <strong>Model Context Protocol</strong> server that interprets natural language tasks,<br/>
validates them for safety, and executes them through a modular plugin architecture.<br/>
Write a task in Notion — or talk to an AI agent — and watch real projects appear on disk.
</p>

<br/>

<img src="https://user-images.githubusercontent.com/placeholder/aura-demo.gif" alt="AURA MCP Demo" width="700"/>

</div>

<br/>

---

<br/>

## 🌟 Overview

Most AI tools give you **text**. AURA gives you **real, running projects**.

You describe what you want — *"Build a FastAPI todo app"* — and AURA handles everything: understanding your intent, choosing the right framework, generating real code with proper structure, and scaffolding the entire project on your filesystem.

AURA works in three ways:

| 💬 **Via Notion** | 🤖 **Via AI Agent** | ⌨️ **Via CLI** |
|:---|:---|:---|
| Write a task in Notion. AURA fetches it, builds it, marks it done. | Claude Desktop, Cursor, or any MCP client calls AURA's tools directly. | Run `aura start` and interact through the command line. |

### 🏗️ Supported Frameworks

<table>
<tr>
<td align="center" width="200">

⚡ **FastAPI**

`main.py` · `routes.py`
`requirements.txt`
Pydantic models · CRUD

</td>
<td align="center" width="200">

🟢 **Node / Express**

`index.js` · `package.json`
Routes · Middleware
CORS · Error handling

</td>
<td align="center" width="200">

⚛️ **React**

`src/App.js` · Components
`package.json`
Styling · HTML template

</td>
</tr>
</table>

Every generated project contains **real, functional code** — not placeholders.

<br/>

---

<br/>

## 🎯 Features

| | Feature | Description |
|:---:|:--------|:------------|
| 🧠 | **AI Task Interpretation** | Understands natural language via OpenAI with a deterministic rule-based fallback |
| 🛡️ | **Safety Chain** | Every plan is validated before execution — bad input never reaches the filesystem |
| 🔌 | **Plugin Architecture** | Drop a file into `aura_mcp/plugins/` and it's discovered automatically |
| 📦 | **Project Scaffolding** | Generates complete FastAPI, Node/Express, and React projects |
| 🔧 | **3 MCP Tools** | `run_aura` · `get_pending_tasks` · `run_single_task` |
| 🧩 | **5 Built-in Plugins** | Notion · Scaffolder · GitHub · Docker · Filesystem |
| 💻 | **CLI Toolkit** | `start` · `plugins` · `config` · `doctor` · `init` |
| ⚙️ | **YAML Config + Env Overrides** | Three-layer configuration with sensible defaults |
| 🐳 | **Docker Support** | Single-stage Dockerfile for containerized deployment |
| ✅ | **252 Automated Tests** | Comprehensive coverage across every subsystem |

<br/>

---

<br/>

## 🏛️ Architecture

<div align="center">

```
              ┌──────────────┐
              │📝 User Task │
              └──────┬───────┘
                     ▼
              ┌──────────────┐
              │ 🧠 Interpreter│──→ LLM or rule-based fallback
              └──────┬───────┘
                     ▼
              ┌──────────────┐
              │ 🛡️ Validator │──→ rejects invalid plans
              └──────┬───────┘
                     ▼
              ┌──────────────┐
              │ 🎯 Orchestrator│──→ coordinates the pipeline
              └──────┬───────┘
                     ▼
              ┌──────────────┐
              │ 🔌 Plugin Mgr │──→ routes to the right plugin
              └──────┬───────┘
                     ▼
        ┌────────────┼────────────┐
        ▼            ▼            ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐
   │📦Scaff.│ │📋 Notion│ │🐙 GitHub│  ...
   └─────────┘ └─────────┘ └─────────┘
        │
        ▼
   ┌──────────────┐
   │ 📁Real Files │
   └──────────────┘
```

</div>

### 🔒 Safety chain detail

The LLM is **never trusted blindly**. Every response passes through validation:

```
Task ──→ LLM (1 call) ──→ JSON parse ──→ Validator ──→ Executor
              │                  │
              ▼ fail             ▼ fail
         Rule-based parser ◄────┘
```

| Scenario | What Happens |
|:---------|:-------------|
| 🔑 No OpenAI key? | Rule-based parser runs automatically |
| 💥 LLM returns bad JSON? | Falls back to rule-based parser |
| 🚫 Validator rejects the plan? | Falls back to rule-based parser |
| ❌ Execution fails? | Notion updated with error details, pipeline continues |

> 💡 The system **never crashes**. Every failure is handled gracefully.

<br/>

---

<br/>

## 📂 Project Structure

```
aura-mcp/
├── 🐍 aura_mcp/                     Python package
│   ├── 💻 cli/                       Typer CLI (start, config, plugins, doctor, init)
│   ├── ⚙️ config/                    YAML config + loader with env overrides
│   ├── 🧠 core/                      Orchestrator, interpreter, executor, validator
│   ├── 🔗 integrations/
│   │   ├── 🤖 llm/                   LLM abstraction (OpenAI, local, factory)
│   │   └── 📋 notion.py              Notion API client
│   ├── 🔌 plugins/                   Auto-discovered plugin system
│   │   ├── base.py                   BasePlugin abstract class
│   │   ├── manager.py               Discovery + registry + dispatch
│   │   ├── scaffolder_plugin.py     Project scaffolding
│   │   ├── notion_plugin.py         Notion integration
│   │   ├── github_plugin.py         GitHub API
│   │   ├── docker_plugin.py         Dockerfile generation
│   │   └── filesystem_plugin.py     File & directory operations
│   ├── 🌐 server/                    FastMCP server (stdio transport)
│   └── 🛠️ utils/                     Logger, file helpers
├── 🧪 tests/                         252 pytest tests
├── 📜 scripts/                        DevOps verification scripts
├── 📚 docs/                           CONFIG.md, PLUGINS.md, README.md
├── 🌍 website/                        Static landing page
├── 📝 examples/                       Demo commands
├── 📦 pyproject.toml                  Package definition
├── 🐳 Dockerfile                      Container build
└── 🔄 .github/workflows/ci.yml       CI pipeline
```

<br/>

---

<br/>

## 🚀 Installation

### From source

```bash
git clone https://github.com/your-username/aura-mcp.git
cd aura-mcp
pip install -e .
```

### With dev dependencies

```bash
pip install -e ".[dev]"
```

### ⚙️ Configure

```bash
cp .env.example .env
```

Edit `.env` with your keys:

```env
NOTION_API_KEY=ntn_your_key
NOTION_DATABASE_ID=your_database_id
OPENAI_API_KEY=sk-your_key          # optional — falls back to rule-based parser
GITHUB_TOKEN=ghp_your_token         # optional — needed for github plugin
```

Or generate a YAML config:

```bash
aura init       # creates aura_config.yaml in the current directory
```

### 📋 Set up Notion

Create a database with these properties:

| Property | Type | Notes |
|:---------|:-----|:------|
| **Name** | Title | Your task description |
| **Status** | Status | `Pending` → `In progress` → `Done` |
| **Output** | Rich text | AURA writes results here |

Then connect your integration: open the database menu (**...**) → **Connections** → add your integration.

<br/>

---

<br/>

## 💻 Usage

### CLI commands

| Command | Description |
|:--------|:------------|
| 🟢 `aura start` | Start the MCP server (stdio transport) |
| 🔌 `aura plugins` | List all discovered plugins with health status |
| ⚙️ `aura config` | Display the active configuration (secrets masked) |
| 🩺 `aura doctor` | Check system readiness — Python, config, env vars, plugins |
| 📄 `aura init` | Initialize a config file in the current directory |
| 🐛 `aura plugins-debug` | Show detailed debug info for every loaded plugin |

### 🩺 Doctor output

```
$ aura doctor

AURA MCP — System Doctor

 Check                Status  Detail
 Python version       ✅ OK    3.11.9
 Config file          ✅ OK    .../aura_mcp/config/config.yaml
 NOTION_API_KEY       ✅ OK    set
 NOTION_DATABASE_ID   ✅ OK    set
 OPENAI_API_KEY       ✅ OK    set
 GITHUB_TOKEN         ⚠️ MISS  missing
 LLM mode             ✅ OK    openai
 Plugins loaded       ✅ OK    docker, filesystem, github, notion, scaffolder
```

<br/>

---

<br/>

## 🔧 MCP Tools

AURA exposes three tools via the **Model Context Protocol**. Any MCP-compatible client — Claude Desktop, Cursor, or your own tooling — can call them directly.

| Tool | Input | Description |
|:-----|:------|:------------|
| 🚀 `run_aura` | — | Full pipeline: fetch Notion tasks → interpret → scaffold → update status |
| 📋 `get_pending_tasks` | — | Return all pending tasks from the connected Notion database |
| ⚡ `run_single_task` | `{ task: "..." }` | Interpret and scaffold from text — no Notion required |

### 🤖 Claude Desktop integration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "aura-mcp": {
      "command": "aura",
      "args": ["start"]
    }
  }
}
```

Then ask Claude:

> 💬 *"Run my pending Notion tasks"*
>
> 💬 *"Scaffold a FastAPI backend for a bookstore"*
>
> 💬 *"What tasks are pending in my Notion?"*

<br/>

---

<br/>

## 📝 Examples

These task strings work with `run_single_task` or as Notion task titles:

```
🔹 create a fastapi todo app
🔹 build a react dashboard for analytics
🔹 setup a node express REST API for a bookstore
🔹 scaffold a fastapi blog backend
🔹 create a react portfolio website
🔹 build a node chat server with express
```

### ▶️ Example pipeline run

```
[AURA] ✅ === AURA MCP — Execution Pipeline ===
[AURA] 📋 Processing 1 task(s)...
[AURA] 📌 ---- Task: "Build a task manager with React" ----
[AURA] 🧠 Interpreting task...
[AURA] ✅ Parsed → action: scaffold_project, framework: react, name: task_manager
[AURA] 📦 Scaffolding react project...
[AURA] 📁 Created 8 file(s)
[AURA] ✅ Task completed
[AURA] 🏁 === Pipeline complete ===
[AURA] 📊 Results: 1 succeeded, 0 failed, 1 total
```

<br/>

---

<br/>

## 🔌 Plugin System

Plugins extend AURA without modifying core code. Every `BasePlugin` subclass inside `aura_mcp/plugins/` is **discovered and registered automatically** at startup.

### Built-in plugins

| Plugin | Emoji | Capabilities |
|:-------|:-----:|:-------------|
| **scaffolder** | 📦 | Generate React, Node.js, and FastAPI projects |
| **notion** | 📋 | Fetch pending tasks, update task status |
| **github** | 🐙 | Create repositories, commit files via the GitHub API |
| **docker** | 🐳 | Generate Dockerfiles for Node, React, and FastAPI |
| **filesystem** | 📁 | Create folders, create files, list directories |

### ✍️ Writing a custom plugin

```python
from aura_mcp.plugins.base import BasePlugin

class MyPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "my_plugin"

    def describe(self) -> str:
        return "Does something useful"

    async def execute(self, intent: dict) -> dict:
        # Your logic here
        return {"status": "ok"}
```

Drop the file into `aura_mcp/plugins/` and it's live on the next startup. No wiring needed.

> 📖 See [docs/PLUGINS.md](docs/PLUGINS.md) for the full plugin development guide.

<br/>

---

<br/>

## ⚙️ Configuration

AURA loads configuration from three layers (last wins):

```
  ① Built-in defaults   →   ② YAML config file   →   ③ Environment variables
       (always)              (if file exists)            (highest priority)
```

### Key settings

| Key | Env Override | Default | Description |
|:----|:-------------|:--------|:------------|
| `workspace` | `AURA_WORKSPACE` | `~/projects` | 📁 Where scaffolded projects are created |
| `llm_mode` | `AURA_LLM_MODE` | `openai` | 🤖 LLM provider: `openai` or `local` |
| `log_level` | `AURA_LOG_LEVEL` | `info` | 📊 Logging verbosity |
| `notion.api_key` | `NOTION_API_KEY` | — | 📋 Notion integration token |
| `notion.database_id` | `NOTION_DATABASE_ID` | — | 📋 Notion database to read tasks from |
| `openai.api_key` | `OPENAI_API_KEY` | — | 🧠 OpenAI API key |
| `openai.model` | `OPENAI_MODEL` | `gpt-3.5-turbo` | 🧠 Model used for task interpretation |
| `github.token` | `GITHUB_TOKEN` | — | 🐙 GitHub personal access token |

### Example config

```yaml
workspace: ~/projects
default_stack: fastapi
log_level: info
llm_mode: openai

openai:
  model: gpt-3.5-turbo
```

> 📖 See [docs/CONFIG.md](docs/CONFIG.md) for the full configuration reference.

<br/>

---

<br/>

## 🧪 Testing

AURA includes a comprehensive test suite with **252 automated tests** covering every subsystem.

```bash
# 🧪 Run the full suite
pytest

# 📋 Verbose output
pytest tests/ -v

# 🎯 Run a specific test file
pytest tests/test_pipeline.py
```

### Test coverage breakdown

| Test File | Tests | Covers |
|:----------|------:|:-------|
| 🔄 `test_pipeline.py` | 39 | Interpreter → Validator → Orchestrator integration |
| 📦 `test_scaffolder.py` | 61 | React, Node, FastAPI project generation |
| 🔌 `test_plugins.py` | 40 | Plugin discovery, registry, execution |
| 💻 `test_cli.py` | 34 | CLI commands (start, plugins, config, doctor, init) |
| ⚙️ `test_config.py` | 36 | Config loading, env overrides, YAML merge |
| 🌐 `test_mcp_server.py` | 28 | MCP server tools and JSON responses |
| 🧠 `test_interpreter.py` | 6 | Rule-based task interpretation |
| 🛡️ `test_validator.py` | 8 | Plan validation and sanitization |

### 🛠️ DevOps verification

```bash
# Full package install + test run
python scripts/test_package_install.py

# Docker build + container verification
bash scripts/test_docker.sh
```

<br/>

---

<br/>

## 🐳 Docker

Build and run AURA in a container:

```bash
# 🏗️ Build the image
docker build -t aura-mcp .

# 🔌 List plugins
docker run --rm aura-mcp plugins

# 🩺 Run system doctor
docker run --rm aura-mcp doctor

# 🚀 Start the MCP server
docker run --rm -i \
  -e NOTION_API_KEY=ntn_your_key \
  -e NOTION_DATABASE_ID=your_db_id \
  aura-mcp start
```

> 💡 The `scripts/test_docker.sh` script automates Docker verification and handles missing Docker gracefully.

<br/>

---

<br/>

## 🤝 Contributing

Contributions are welcome — especially new plugins and integrations!

```
1. 🍴 Fork the repository
2. 🌿 Create a feature branch    →  git checkout -b feature/my-feature
3. ✅ Run linter and tests       →  ruff check aura_mcp/ && pytest
4. 📬 Open a pull request
```

> 📖 Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting.
>
> 🤝 See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for community guidelines.

<br/>

---

<br/>

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

<br/>

---

<br/>

<div align="center">

### 💜 Built [Aryan Kumar](https://github.com/aryanjsx)

<br/>

[📚 Documentation](docs/README.md) · [🔌 Plugin Guide](docs/PLUGINS.md) · [⚙️ Configuration](docs/CONFIG.md) · [🔒 Security](SECURITY.md)

<br/>

⭐ **Star this repo if you find it useful!** ⭐

</div>
