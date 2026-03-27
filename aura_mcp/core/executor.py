"""Project scaffolder — generates real, functional project trees on disk.

Supported frameworks: React, Node.js/Express, FastAPI.
Each generator writes ready-to-run code, not placeholders.
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path

from aura_mcp.config.loader import get_config
from aura_mcp.utils.file_utils import create_file, create_folder
from aura_mcp.utils.logger import get_logger


def _output_dir() -> Path:
    config = get_config()
    workspace = config.get("workspace", "")
    if workspace:
        return Path(os.path.expanduser(workspace))
    return Path.cwd() / "output"


# ── Public API ───────────────────────────────────────────────────────


def execute_task(plan: dict) -> str:
    """Scaffold a project described by *plan* and return a human-readable summary."""
    logger = get_logger()

    if plan.get("action") != "scaffold_project":
        raise ValueError(f"Unknown action: \"{plan.get('action')}\"")

    generators = {
        "react": _generate_react_project,
        "node": _generate_node_project,
        "fastapi": _generate_fastapi_project,
    }

    generator = generators.get(plan["framework"])
    if generator is None:
        raise ValueError(f"No template for framework: \"{plan['framework']}\"")

    project_root = _output_dir() / plan["project_name"]
    create_folder(project_root)

    logger.info("Scaffolding %s project at %s", plan["framework"], project_root)
    files = generator(project_root, plan["project_name"])
    logger.info("Created %d file(s)", len(files))

    return _format_summary(plan, str(project_root), files)


# ── Template generators ──────────────────────────────────────────────


def _generate_react_project(root: Path, name: str) -> list[str]:
    files: list[str] = []

    files.append(_write(root, "package.json", json.dumps({
        "name": name,
        "version": "1.0.0",
        "private": True,
        "scripts": {
            "start": "react-scripts start",
            "build": "react-scripts build",
            "test": "react-scripts test",
        },
        "dependencies": {
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "react-scripts": "5.0.1",
        },
    }, indent=2)))

    files.append(_write(root, "public/index.html", (
        '<!DOCTYPE html>\n'
        '<html lang="en">\n'
        '<head>\n'
        '  <meta charset="UTF-8" />\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0" />\n'
        f'  <title>{name}</title>\n'
        '</head>\n'
        '<body>\n'
        '  <div id="root"></div>\n'
        '</body>\n'
        '</html>'
    )))

    files.append(_write(root, "src/index.js", (
        'import React from "react";\n'
        'import ReactDOM from "react-dom/client";\n'
        'import App from "./App";\n'
        'import "./App.css";\n'
        '\n'
        'const root = ReactDOM.createRoot(document.getElementById("root"));\n'
        'root.render(<App />);'
    )))

    files.append(_write(root, "src/App.js", (
        'import React, { useState } from "react";\n'
        '\n'
        'function App() {\n'
        '  const [count, setCount] = useState(0);\n'
        '\n'
        '  return (\n'
        '    <div className="app">\n'
        '      <header className="header">\n'
        f'        <h1>{name}</h1>\n'
        '        <p>Scaffolded by AURA MCP</p>\n'
        '      </header>\n'
        '      <main className="main">\n'
        '        <div className="card">\n'
        '          <p>Counter: {count}</p>\n'
        '          <button onClick={() => setCount(c => c + 1)}>Increment</button>\n'
        '        </div>\n'
        '      </main>\n'
        '      <footer className="footer">\n'
        '        <p>Built with React</p>\n'
        '      </footer>\n'
        '    </div>\n'
        '  );\n'
        '}\n'
        '\n'
        'export default App;'
    )))

    files.append(_write(root, "src/App.css", (
        '* { margin: 0; padding: 0; box-sizing: border-box; }\n'
        '\n'
        'body {\n'
        '  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;\n'
        '  background: #f5f5f5;\n'
        '  color: #1a1a2e;\n'
        '}\n'
        '\n'
        '.app { max-width: 800px; margin: 0 auto; padding: 2rem; }\n'
        '\n'
        '.header { text-align: center; margin-bottom: 2rem; }\n'
        '.header h1 { font-size: 2rem; margin-bottom: 0.5rem; }\n'
        '.header p { color: #666; }\n'
        '\n'
        '.main { display: flex; justify-content: center; }\n'
        '\n'
        '.card {\n'
        '  background: white;\n'
        '  border-radius: 8px;\n'
        '  padding: 2rem;\n'
        '  box-shadow: 0 2px 8px rgba(0,0,0,0.1);\n'
        '  text-align: center;\n'
        '}\n'
        '.card p { font-size: 1.5rem; margin-bottom: 1rem; }\n'
        '.card button {\n'
        '  background: #4361ee;\n'
        '  color: white;\n'
        '  border: none;\n'
        '  padding: 0.75rem 1.5rem;\n'
        '  border-radius: 6px;\n'
        '  font-size: 1rem;\n'
        '  cursor: pointer;\n'
        '}\n'
        '.card button:hover { background: #3a56d4; }\n'
        '\n'
        '.footer { text-align: center; margin-top: 2rem; color: #999; font-size: 0.9rem; }'
    )))

    files.append(_write(root, "src/components/Header.js", (
        'import React from "react";\n'
        '\n'
        'function Header({ title }) {\n'
        '  return (\n'
        '    <header className="header">\n'
        '      <h1>{title}</h1>\n'
        '    </header>\n'
        '  );\n'
        '}\n'
        '\n'
        'export default Header;'
    )))

    files.append(_write(root, ".gitignore", "node_modules/\nbuild/\n.env\n"))

    files.append(_write(root, "README.md", (
        f"# {name}\n\n"
        "React project scaffolded by AURA MCP.\n\n"
        "## Getting Started\n\n"
        "```bash\nnpm install\nnpm start\n```\n\n"
        "Open [http://localhost:3000](http://localhost:3000) to view in browser.\n"
    )))

    return files


def _generate_node_project(root: Path, name: str) -> list[str]:
    files: list[str] = []

    files.append(_write(root, "package.json", json.dumps({
        "name": name,
        "version": "1.0.0",
        "scripts": {
            "start": "node index.js",
            "dev": "node --watch index.js",
        },
        "dependencies": {
            "express": "^4.18.0",
            "cors": "^2.8.5",
        },
    }, indent=2)))

    files.append(_write(root, "index.js", (
        'const express = require("express");\n'
        'const cors = require("cors");\n'
        'const apiRoutes = require("./src/routes");\n'
        'const errorHandler = require("./src/middleware/errorHandler");\n'
        '\n'
        'const app = express();\n'
        'const PORT = process.env.PORT || 3000;\n'
        '\n'
        'app.use(cors());\n'
        'app.use(express.json());\n'
        '\n'
        'app.get("/health", (req, res) => {\n'
        '  res.json({ status: "ok", uptime: process.uptime(),'
        ' timestamp: new Date().toISOString() });\n'
        '});\n'
        '\n'
        'app.use("/api", apiRoutes);\n'
        '\n'
        'app.use(errorHandler);\n'
        '\n'
        'app.listen(PORT, () => {\n'
        f'  console.log(`{name} running on http://localhost:${{PORT}}`);\n'
        '});'
    )))

    files.append(_write(root, "src/routes/index.js", (
        'const router = require("express").Router();\n'
        '\n'
        'router.get("/", (req, res) => {\n'
        f'  res.json({{ message: "Welcome to {name} API", version: "1.0.0" }});\n'
        '});\n'
        '\n'
        'router.get("/items", (req, res) => {\n'
        '  res.json({ items: [], total: 0 });\n'
        '});\n'
        '\n'
        'router.post("/items", (req, res) => {\n'
        '  const { name } = req.body;\n'
        '  if (!name) {\n'
        '    return res.status(400).json({ error: "name is required" });\n'
        '  }\n'
        '  res.status(201).json({ id: Date.now(), name, created: new Date().toISOString() });\n'
        '});\n'
        '\n'
        'module.exports = router;'
    )))

    files.append(_write(root, "src/middleware/errorHandler.js", (
        'function errorHandler(err, req, res, _next) {\n'
        '  console.error(err.stack);\n'
        '  res.status(500).json({ error: "Internal server error" });\n'
        '}\n'
        '\n'
        'module.exports = errorHandler;'
    )))

    files.append(_write(root, ".env.example", "PORT=3000\n"))
    files.append(_write(root, ".gitignore", "node_modules/\n.env\n"))

    files.append(_write(root, "README.md", (
        f"# {name}\n\n"
        "Node.js Express API scaffolded by AURA MCP.\n\n"
        "## Getting Started\n\n"
        "```bash\nnpm install\nnpm start\n```\n\n"
        "## Endpoints\n\n"
        "| Method | Path | Description |\n"
        "|--------|------|-------------|\n"
        "| GET | /health | Health check |\n"
        "| GET | /api | API info |\n"
        "| GET | /api/items | List items |\n"
        "| POST | /api/items | Create item |\n"
    )))

    return files


def _generate_fastapi_project(root: Path, name: str) -> list[str]:
    files: list[str] = []

    files.append(_write(root, "main.py", (
        'from fastapi import FastAPI\n'
        'from fastapi.middleware.cors import CORSMiddleware\n'
        'from routes import router\n'
        '\n'
        f'app = FastAPI(title="{name}", version="1.0.0")\n'
        '\n'
        'app.add_middleware(\n'
        '    CORSMiddleware,\n'
        '    allow_origins=["*"],\n'
        '    allow_methods=["*"],\n'
        '    allow_headers=["*"],\n'
        ')\n'
        '\n'
        'app.include_router(router, prefix="/api")\n'
        '\n'
        '\n'
        '@app.get("/health")\n'
        'def health_check():\n'
        '    return {"status": "ok"}\n'
        '\n'
        '\n'
        '@app.get("/")\n'
        'def root():\n'
        f'    return {{"message": "Welcome to {name} API", "docs": "/docs"}}\n'
        '\n'
        '\n'
        'if __name__ == "__main__":\n'
        '    import uvicorn\n'
        '    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)'
    )))

    files.append(_write(root, "routes.py", (
        'from fastapi import APIRouter, HTTPException\n'
        'from pydantic import BaseModel\n'
        'from typing import Optional\n'
        '\n'
        'router = APIRouter()\n'
        '\n'
        'items = []\n'
        '\n'
        '\n'
        'class ItemCreate(BaseModel):\n'
        '    name: str\n'
        '    description: Optional[str] = None\n'
        '\n'
        '\n'
        '@router.get("/items")\n'
        'def list_items():\n'
        '    return {"items": items, "total": len(items)}\n'
        '\n'
        '\n'
        '@router.post("/items", status_code=201)\n'
        'def create_item(item: ItemCreate):\n'
        '    new_item = {"id": len(items) + 1, **item.model_dump()}\n'
        '    items.append(new_item)\n'
        '    return new_item\n'
        '\n'
        '\n'
        '@router.get("/items/{item_id}")\n'
        'def get_item(item_id: int):\n'
        '    for item in items:\n'
        '        if item["id"] == item_id:\n'
        '            return item\n'
        '    raise HTTPException(status_code=404, detail="Item not found")'
    )))

    files.append(_write(root, "requirements.txt",
                         "fastapi>=0.100.0\nuvicorn>=0.23.0\npydantic>=2.0.0\n"))
    files.append(_write(root, ".gitignore", "__pycache__/\n*.pyc\n.env\nvenv/\n"))

    files.append(_write(root, "README.md", (
        f"# {name}\n\n"
        "FastAPI project scaffolded by AURA MCP.\n\n"
        "## Getting Started\n\n"
        "```bash\npip install -r requirements.txt\npython main.py\n```\n\n"
        "Open [http://localhost:8000/docs](http://localhost:8000/docs) "
        "for interactive API docs.\n\n"
        "## Endpoints\n\n"
        "| Method | Path | Description |\n"
        "|--------|------|-------------|\n"
        "| GET | /health | Health check |\n"
        "| GET | /api/items | List items |\n"
        "| POST | /api/items | Create item |\n"
        "| GET | /api/items/:id | Get item |\n"
    )))

    return files


# ── Helpers ──────────────────────────────────────────────────────────


def _write(root: Path, relative_path: str, content: str) -> str:
    create_file(root / relative_path, content)
    return relative_path


def _format_summary(plan: dict, project_root: str, files: list[str]) -> str:
    tree = "\n".join(f"  - {f}" for f in files)
    now = datetime.now(UTC).isoformat()
    return (
        f"Project scaffolded: {plan['project_name']}\n"
        f"Framework: {plan['framework']}\n"
        f"Location: {project_root}\n"
        f"Files ({len(files)}):\n{tree}\n"
        f"\nGenerated by AURA MCP at {now}"
    )
