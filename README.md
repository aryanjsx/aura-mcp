# AURA MCP

> *"Write it in Notion. AURA builds it."*

**AURA** (Autonomous Unified Resource Architect) is an MCP server that reads tasks from a Notion database, interprets them using AI, scaffolds real projects on your machine, and reports results back to Notion.

Notion becomes your command center — not just for planning, but for execution.

---

## How It Works

```
┌──────────────┐       ┌──────────────────────────────┐       ┌──────────────┐
│    NOTION    │       │         AURA MCP SERVER       │       │  FILESYSTEM  │
│              │ read  │                               │ write │              │
│ Task:Pending ├──────►│ Interpret → Validate → Build  ├──────►│ Real project │
│              │       │                               │       │ with code    │
│ Task:Done ✅ │◄──────┤ Status + summary writeback    │       │              │
└──────────────┘ write └──────────────────────────────┘       └──────────────┘
```

1. You write a task in Notion — *"Build a task manager with React"*
2. AURA reads it, interprets it (LLM or rule-based), and builds the project
3. Real files appear on disk. Notion task updates to **Done** with a file tree summary.

---

## MCP Tools

AURA exposes three tools via the Model Context Protocol:

| Tool | Input | Description |
|------|-------|-------------|
| `run_aura` | — | Full pipeline: fetch pending Notion tasks → interpret → scaffold → update Notion |
| `get_pending_tasks` | — | Return all pending tasks from the Notion database |
| `run_single_task` | `{ task: "..." }` | Interpret and scaffold from text — no Notion required |

---

## Prerequisites

- [Node.js](https://nodejs.org/) v18+
- A [Notion integration](https://www.notion.so/my-integrations) with an API key
- (Optional) An [OpenAI API key](https://platform.openai.com/api-keys) for LLM-powered interpretation

### Notion Database Setup

Create a Notion database with these properties:

| Property | Type   | Notes                             |
|----------|--------|-----------------------------------|
| Name     | Title  | The task description              |
| Status   | Status | Uses: Pending, In progress, Done  |
| Output   | Text   | AURA writes results here          |

Connect your integration: open the database → click `...` → **Connections** → add your integration.

---

## Setup

```bash
cd aura-mcp
npm install
cp .env.example .env
```

Fill in your `.env`:

```
NOTION_API_KEY=ntn_your_key
NOTION_DATABASE_ID=your_database_id
OPENAI_API_KEY=sk-your_key        # optional
```

---

## Usage

### Run the pipeline directly

Create a task in Notion with Status = **Pending**, then:

```bash
npm start
```

AURA fetches pending tasks, interprets them, scaffolds projects into `output/`, and updates Notion.

### Run as MCP server

```bash
npm run mcp
```

Starts AURA as an MCP server over stdio for any MCP client.

### Use with Claude Desktop

Copy `claude_desktop_config.example.json` into your Claude Desktop config directory, update the `cwd` path, and restart Claude Desktop.

Then ask Claude:
- *"Run my pending Notion tasks"*
- *"Scaffold a FastAPI backend for a bookstore"*
- *"What tasks are pending in my Notion?"*

---

## Supported Frameworks

| Keywords in task | Framework | Files generated |
|------------------|-----------|-----------------|
| react            | React     | package.json, App.js, index.js, App.css, Header component, index.html, .gitignore, README (8 files) |
| node, express    | Node.js   | package.json, index.js (Express + CORS), routes, error middleware, .env.example, .gitignore, README (7 files) |
| fastapi, python  | FastAPI   | main.py, routes.py (Pydantic models), requirements.txt, .gitignore, README (5 files) |

All generated files contain real, functional code — not placeholders.

---

## Architecture

```
aura-mcp/
├── src/
│   ├── mcp/
│   │   └── server.js                ← MCP server (3 tools, stdio transport)
│   ├── core/
│   │   └── orchestrator.js          ← Pipeline engine
│   ├── services/
│   │   ├── notion.service.js        ← Notion API read/write
│   │   ├── interpreter.service.js   ← LLM-first, rule-based fallback
│   │   ├── llm.service.js           ← Single OpenAI call per task
│   │   ├── validator.service.js     ← Plan validation + sanitization
│   │   └── executor.service.js      ← Project scaffolder (3 frameworks)
│   └── utils/
│       ├── logger.js                ← [AURA] prefixed logging
│       └── file.utils.js            ← Safe filesystem helpers
├── test/
│   └── notion.test.js               ← Runs full pipeline
├── output/                           ← Generated projects
├── .env.example
├── claude_desktop_config.example.json
└── package.json
```

### Safety Chain

The LLM is never trusted blindly:

```
Task text → LLM (1 call) → JSON parse → Validator → Executor
                 ↓ fail         ↓ fail
             Rule-based ←───────┘
```

- No `OPENAI_API_KEY`? Rule-based parser runs automatically.
- LLM returns bad JSON? Falls back to rules.
- Validator rejects the plan? Falls back to rules.
- The system never crashes.

---

## License

MIT
