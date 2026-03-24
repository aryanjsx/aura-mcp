# 📋 Changelog

All notable changes to AURA MCP will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [0.1.0] — 2026-03-24

### 🎉 Initial Release — Hackathon MVP

#### Added

- **MCP Server** with 3 tools: `run_aura`, `get_pending_tasks`, `run_single_task`
- **Notion Integration** — read pending tasks, update status (In progress / Done / To-do), write output summaries
- **AI Interpreter** — single OpenAI API call per task to convert natural language into structured JSON plans
- **Rule-Based Fallback** — keyword-based parser activates automatically when LLM is unavailable or fails
- **Plan Validator** — validates framework, action, and project name; sanitizes names to prevent filesystem issues
- **Project Scaffolder** with 3 framework templates:
  - ⚛️ React (8 files) — App, components, CSS, HTML, package.json
  - 🟩 Node.js/Express (7 files) — Express server, routes, error middleware, CORS
  - 🐍 FastAPI (5 files) — FastAPI app, Pydantic routes, requirements
- **Orchestrator** — sequential pipeline engine: fetch → interpret → validate → execute → report
- **Logger** — `[AURA]` prefixed logging with timestamps
- **Stdio Transport** — stdout reserved for MCP protocol, logs redirected to stderr
- **Claude Desktop config** example for easy MCP client setup

#### Security

- Project names are sanitized (lowercase, special chars stripped, max 64 chars)
- Framework whitelist validation (react, node, fastapi)
- No arbitrary code execution — only predefined project structures
- API keys loaded from environment variables, never hardcoded

---

## [Unreleased]

### Planned

- Additional framework templates (Django, Next.js, Go)
- Richer project scaffolding based on LLM features array
- Multiple Notion database support
- Configurable output directory
- Task queue with priority support
