<div align="center">

# 📄 AURA MCP — Project Description

</div>

---

## 🧩 What is AURA MCP?

**AURA MCP** (Autonomous Unified Resource Architect) is an intelligent execution engine built on the **Model Context Protocol (MCP)**. It bridges the gap between planning and doing — turning your Notion database into a command center that doesn't just track tasks, but **executes them**.

Instead of writing a project spec in Notion and then manually opening a terminal to scaffold files, AURA reads your task, understands what you want, creates a fully functional project with real code, and reports the results back to Notion — all automatically.

---

## ❓ The Problem

Every developer knows this cycle:

1. **Plan** in Notion — write a spec, list features, describe the project
2. **Leave** Notion — open terminal, run CLI tools, create folders, write boilerplate
3. **Return** to Notion — manually update the task as "done"

The planning and execution are completely disconnected. Notion captures your intent beautifully, but it can't act on it. You become the middleware between your own plans and your tools.

Existing solutions don't solve this:

| Tool | Limitation |
|:-----|:-----------|
| 🔗 **Zapier / Make** | Can trigger simple actions but can't interpret a project description and produce real code |
| 💬 **AI Chatbots** | Generate text in a chat window — not real files on your machine |
| 🧑‍💻 **Copilot / Cursor** | Help while you're already coding — don't bridge planning to execution |
| 🔄 **Notion Integrations** | Sync data between apps — don't perform intelligent execution |

---

## 💡 The Solution

AURA MCP makes Notion the place where things actually get **done**.

You write **one sentence** in Notion. AURA reads it, interprets it using AI (with a deterministic fallback), scaffolds a real project with functional code on your filesystem, and updates the Notion task with the results — status, file tree, and timestamp.

**One sentence in. Real project out.**

### What makes it different:

| Typical AI Tool | AURA MCP |
|:----------------|:---------|
| You ask, it responds with text | You write in Notion, it executes real actions |
| Output lives in a chat window | Output lives on your filesystem AND in Notion |
| You copy-paste results manually | Results are written back automatically |
| Stateless — no project context | Reads context from your Notion workspace |
| Requires human to orchestrate | Runs the full pipeline autonomously |

---

## 🏗️ How It Works (Short Version)

```
📝 Write task in Notion  →  🧠 AURA interprets  →  📁 Project created  →  ✅ Notion updated
```

1. User writes a task: *"Build a task manager with React"*
2. AURA fetches it from the Notion database
3. AI interprets the task into a structured plan (framework, name, features)
4. The executor scaffolds a real project with functional code
5. Notion is updated: Status → **Done**, Output → file tree and summary

---

## 🎯 Core Features

| # | Feature | Description |
|:-:|:--------|:------------|
| 1 | 📥 **Notion Task Reader** | Connects to a Notion database and fetches all pending tasks via the official API |
| 2 | 🤖 **AI Interpreter** | Converts natural language task descriptions into structured execution plans using OpenAI |
| 3 | 📏 **Rule-Based Fallback** | Keyword-based parser that activates automatically if the LLM fails or no API key is set |
| 4 | ✅ **Plan Validator** | Validates and sanitizes every plan before execution — framework whitelist, name sanitization, path traversal prevention |
| 5 | 🏗️ **Project Scaffolder** | Creates real projects on disk with functional code for React, Node.js/Express, and FastAPI |
| 6 | 📤 **Notion Writer** | Updates the original task with status (Done/Failed) and a detailed execution summary |
| 7 | 🔌 **MCP Server** | Exposes 3 tools via the Model Context Protocol for use with Claude Desktop or any MCP client |

---

## 🔌 MCP Tools

| Tool | Description |
|:-----|:------------|
| 🚀 `run_aura` | Execute the full pipeline — fetch pending Notion tasks, interpret, scaffold, and update Notion |
| 📋 `get_pending_tasks` | Read and return all pending tasks from the configured Notion database |
| ⚙️ `run_single_task` | Interpret and scaffold a project from raw text input — no Notion needed |

---

## 🛡️ Safety & Reliability

- **Single LLM call** per task — no chains, no agents, no runaway costs
- **Strict validation** — every AI output is validated before execution
- **Automatic fallback** — rule-based parser takes over on any LLM failure
- **Project name sanitization** — prevents path traversal and filesystem issues
- **Graceful error handling** — failures are reported to Notion, system never crashes
- **No arbitrary code execution** — only creates predefined project structures

---

<div align="center">

# 🧰 Technologies Used

</div>

---

## ⚙️ Core Runtime

| Technology | Version | Purpose |
|:-----------|:--------|:--------|
| ![Node.js](https://img.shields.io/badge/Node.js-339933?style=flat-square&logo=node.js&logoColor=white) **Node.js** | 18+ | Runtime environment for the entire server |
| ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black) **JavaScript (CommonJS)** | ES2022 | Primary language — clean, modular, async/await throughout |

---

## 🔌 APIs & Protocols

| Technology | Purpose |
|:-----------|:--------|
| ![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-8B5CF6?style=flat-square) **Model Context Protocol** | Standard protocol for exposing tools to AI clients (Claude Desktop) |
| ![Notion](https://img.shields.io/badge/Notion-API-000000?style=flat-square&logo=notion&logoColor=white) **Notion API** | Read tasks from and write results back to Notion databases |
| ![OpenAI](https://img.shields.io/badge/OpenAI-API-412991?style=flat-square&logo=openai&logoColor=white) **OpenAI API** | Single LLM call per task to interpret natural language into structured plans |

---

## 📦 Key Dependencies

| Package | Version | What It Does |
|:--------|:--------|:-------------|
| `@modelcontextprotocol/sdk` | ^1.27 | MCP server framework — tool registration, stdio transport, JSON-RPC |
| `@notionhq/client` | ^2.2 | Official Notion SDK — database queries, page updates |
| `openai` | ^6.32 | Official OpenAI SDK — chat completions for task interpretation |
| `zod` | ^4.3 | Schema validation for MCP tool input parameters |
| `dotenv` | ^16.4 | Environment variable loading from `.env` files |

---

## 🧱 Built-In Node.js Modules

| Module | Purpose |
|:-------|:--------|
| `fs` | Filesystem operations — creating project directories and files |
| `path` | Safe cross-platform path construction and resolution |

---

## 📁 Project Scaffolding Templates

AURA generates real projects using these technologies:

| Framework | Generated Stack |
|:----------|:----------------|
| ⚛️ **React** | React 18, ReactDOM, React Scripts, CSS, component architecture |
| 🟩 **Node.js** | Express 4, CORS middleware, error handling middleware, RESTful routes |
| 🐍 **FastAPI** | FastAPI, Uvicorn, Pydantic v2 models, CORS middleware, auto-docs |

---

## 🏛️ Architecture Patterns

| Pattern | Where It's Used |
|:--------|:---------------|
| **Service Layer** | Each concern (Notion, LLM, validation, execution) is a separate service module |
| **Orchestrator** | Central pipeline engine that coordinates all services sequentially |
| **Fallback Chain** | LLM → Validator → Rule-based parser — each layer catches failures from the previous |
| **MCP Tool Pattern** | Clean tool registration with typed inputs and structured JSON responses |
| **Stdio Transport** | MCP communication over stdin/stdout with diagnostic logs redirected to stderr |

---

## 🧪 Development & Tooling

| Tool | Purpose |
|:-----|:--------|
| ![Git](https://img.shields.io/badge/Git-F05032?style=flat-square&logo=git&logoColor=white) **Git** | Version control |
| ![npm](https://img.shields.io/badge/npm-CB3837?style=flat-square&logo=npm&logoColor=white) **npm** | Package management |
| **Claude Desktop** | MCP client for testing and demo |

---

<div align="center">

### 📊 By The Numbers

| Metric | Value |
|:-------|:------|
| Total source files | **9** |
| Lines of code | **~600** |
| External dependencies | **5** |
| MCP tools | **3** |
| Supported frameworks | **3** |
| LLM calls per task | **1** (max) |
| Test coverage | End-to-end integration |

---

*Built for the Notion MCP Hackathon 🏆*

</div>
