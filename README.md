<div align="center">

# ✨ AURA MCP

### Autonomous Unified Resource Architect

**Write it in Notion. AURA builds it.**

[![Node.js](https://img.shields.io/badge/Node.js-18%2B-339933?style=for-the-badge&logo=node.js&logoColor=white)](https://nodejs.org/)
[![Notion](https://img.shields.io/badge/Notion-API-000000?style=for-the-badge&logo=notion&logoColor=white)](https://developers.notion.com/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-8B5CF6?style=for-the-badge)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)](LICENSE)

<br />

<img src="https://img.shields.io/badge/Status-Hackathon%20MVP-FF6B6B?style=flat-square" />

---

*An MCP server that reads tasks from Notion, interprets them with AI,*
*scaffolds real projects on your machine, and reports results back — automatically.*

</div>

<br />

## 🎯 What is AURA?

> Most AI tools give you text. AURA gives you **real projects.**

You write a task in Notion. AURA reads it, understands it, creates a full project with real code on your filesystem, and updates Notion with the results. No copy-pasting. No boilerplate. Just intent in, execution out.

<br />

## ⚡ How It Works

```
  📝 NOTION                    🧠 AURA MCP                     📁 FILESYSTEM
 ┌─────────────┐            ┌──────────────────┐            ┌──────────────┐
 │             │   read     │                  │   write    │              │
 │  Task:      │ ─────────► │  Interpret task   │ ─────────► │  Real files  │
 │  "Build a   │            │  Validate plan    │            │  Real code   │
 │   React     │            │  Scaffold project │            │  Real project│
 │   app"      │            │                  │            │              │
 │             │ ◄───────── │  Write results    │            │              │
 │  ✅ Done    │   update   │  back to Notion   │            │              │
 └─────────────┘            └──────────────────┘            └──────────────┘
```

<br />

**Three simple steps:**

| Step | What Happens |
|:----:|:------------|
| **1️⃣** | You write a task in Notion → *"Build a task manager with React"* |
| **2️⃣** | AURA interprets it (AI or rules), validates, and scaffolds the project |
| **3️⃣** | Real files appear on disk. Notion updates to **✅ Done** with a summary |

<br />

## 🛠️ MCP Tools

AURA exposes **3 tools** via the Model Context Protocol:

| Tool | Input | What It Does |
|:-----|:------|:-------------|
| 🚀 `run_aura` | — | Full pipeline: Notion → interpret → scaffold → update Notion |
| 📋 `get_pending_tasks` | — | Fetch and return all pending tasks from Notion |
| ⚙️ `run_single_task` | `{ task: "..." }` | Scaffold from text directly — no Notion needed |

<br />

## 📦 Supported Frameworks

<table>
<tr>
<td align="center"><strong>⚛️ React</strong><br/><sub>8 files</sub></td>
<td align="center"><strong>🟩 Node.js</strong><br/><sub>7 files</sub></td>
<td align="center"><strong>🐍 FastAPI</strong><br/><sub>5 files</sub></td>
</tr>
<tr>
<td>
<code>package.json</code><br/>
<code>src/App.js</code><br/>
<code>src/index.js</code><br/>
<code>src/App.css</code><br/>
<code>src/components/Header.js</code><br/>
<code>public/index.html</code><br/>
<code>.gitignore</code><br/>
<code>README.md</code>
</td>
<td>
<code>package.json</code><br/>
<code>index.js</code> (Express + CORS)<br/>
<code>src/routes/index.js</code><br/>
<code>src/middleware/errorHandler.js</code><br/>
<code>.env.example</code><br/>
<code>.gitignore</code><br/>
<code>README.md</code>
</td>
<td>
<code>main.py</code><br/>
<code>routes.py</code> (Pydantic)<br/>
<code>requirements.txt</code><br/>
<code>.gitignore</code><br/>
<code>README.md</code>
</td>
</tr>
</table>

> 💡 All generated files contain **real, functional code** — not placeholders.

<br />

## 🚀 Quick Start

### Prerequisites

- 📗 [Node.js](https://nodejs.org/) v18+
- 📓 A [Notion integration](https://www.notion.so/my-integrations) with API key
- 🤖 (Optional) [OpenAI API key](https://platform.openai.com/api-keys) for AI interpretation

### 1. Install

```bash
cd aura-mcp
npm install
```

### 2. Configure

```bash
cp .env.example .env
```

Edit `.env` with your keys:

```env
NOTION_API_KEY=ntn_your_key
NOTION_DATABASE_ID=your_database_id
OPENAI_API_KEY=sk-your_key          # optional
```

### 3. Setup Notion Database

Create a database with these properties:

| Property | Type | Notes |
|:---------|:-----|:------|
| 📝 **Name** | Title | Your task description |
| 🔄 **Status** | Status | Pending → In progress → Done |
| 📤 **Output** | Text | AURA writes results here |

> Connect your integration: database `...` menu → **Connections** → add your integration

### 4. Run

```bash
# Direct pipeline
npm start

# As MCP server
npm run mcp
```

<br />

## 🖥️ Claude Desktop Integration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "aura-mcp": {
      "command": "node",
      "args": ["src/mcp/server.js"],
      "cwd": "/absolute/path/to/aura-mcp"
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

<br />

## 🏗️ Architecture

```
aura-mcp/
├── 🔌 src/mcp/
│   └── server.js                 MCP server — 3 tools, stdio transport
├── 🧠 src/core/
│   └── orchestrator.js           Pipeline engine
├── ⚙️ src/services/
│   ├── notion.service.js         Notion API read/write
│   ├── interpreter.service.js    LLM-first, rule-based fallback
│   ├── llm.service.js            Single OpenAI call per task
│   ├── validator.service.js      Plan validation + sanitization
│   └── executor.service.js       Project scaffolder (3 frameworks)
├── 🔧 src/utils/
│   ├── logger.js                 [AURA] prefixed logging
│   └── file.utils.js             Safe filesystem helpers
├── 🧪 test/
│   └── notion.test.js            Integration test
└── 📁 output/                    Generated projects land here
```

<br />

## 🛡️ Safety Chain

The LLM is **never trusted blindly**. Every response is validated before execution:

```
📝 Task → 🤖 LLM (1 call) → 📋 JSON parse → ✅ Validator → 🏗️ Executor
               ↓ fail              ↓ fail
           📏 Rule-based  ◄────────┘
```

| Scenario | What Happens |
|:---------|:-------------|
| 🔑 No OpenAI key? | Rule-based parser runs automatically |
| ❌ LLM returns bad JSON? | Falls back to rules |
| ⚠️ Validator rejects plan? | Falls back to rules |
| 💥 Execution fails? | Notion updated with error, system continues |

> **The system never crashes.** Every failure is handled gracefully.

<br />

## 📊 Example Run

```
[AURA] INFO  === AURA MCP — Execution Pipeline ===
[AURA] INFO  Notion client initialized
[AURA] INFO  Fetched 1 pending task(s)
[AURA] INFO  ──── Task: "Build a task manager with React" ────
[AURA] INFO  Task → status: "In progress"
[AURA] INFO  Interpreting task...
[AURA] INFO  Parsed → framework: react, name: task_manager
[AURA] INFO  Scaffolding react project...
[AURA] INFO  Created 8 file(s)
[AURA] INFO  Task → status: "Done"
[AURA] INFO  Task completed ✓
[AURA] INFO  === Pipeline complete ===
[AURA] INFO  Results: 1 succeeded, 0 failed, 1 total
```

<br />

---

<div align="center">

**Built for the [Notion MCP Hackathon](https://notion.so) 🏆**

Made with 🧠 by AURA

</div>
