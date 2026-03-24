const path = require("path");
const logger = require("../utils/logger");
const { createFolder, createFile } = require("../utils/file.utils");

const OUTPUT_DIR = path.join(process.cwd(), "output");

// ─── Template definitions ───────────────────────────────────────────

const TEMPLATES = {
  react: generateReactProject,
  node: generateNodeProject,
  fastapi: generateFastAPIProject,
};

// ─── Public API ─────────────────────────────────────────────────────

/**
 * Execute a parsed plan by scaffolding the project on disk.
 *
 * @param {{ action: string, framework: string, project_name: string }} plan
 * @returns {string} Human-readable summary of what was created
 */
function executeTask(plan) {
  if (plan.action !== "scaffold_project") {
    throw new Error(`Unknown action: "${plan.action}"`);
  }

  const generator = TEMPLATES[plan.framework];
  if (!generator) {
    throw new Error(`No template for framework: "${plan.framework}"`);
  }

  const projectRoot = path.join(OUTPUT_DIR, plan.project_name);
  createFolder(projectRoot);

  logger.info(`Scaffolding ${plan.framework} project at ${projectRoot}`);
  const files = generator(projectRoot, plan.project_name);
  logger.info(`Created ${files.length} file(s)`);

  return formatSummary(plan, projectRoot, files);
}

// ─── Template generators ────────────────────────────────────────────

function generateReactProject(root, name) {
  const files = [];

  files.push(write(root, "package.json", JSON.stringify({
    name,
    version: "1.0.0",
    private: true,
    scripts: {
      start: "react-scripts start",
      build: "react-scripts build",
      test: "react-scripts test",
    },
    dependencies: {
      react: "^18.2.0",
      "react-dom": "^18.2.0",
      "react-scripts": "5.0.1",
    },
  }, null, 2)));

  files.push(write(root, "public/index.html", `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>${name}</title>
</head>
<body>
  <div id="root"></div>
</body>
</html>`));

  files.push(write(root, "src/index.js", `import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./App.css";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);`));

  files.push(write(root, "src/App.js", `import React, { useState } from "react";

function App() {
  const [count, setCount] = useState(0);

  return (
    <div className="app">
      <header className="header">
        <h1>${name}</h1>
        <p>Scaffolded by AURA MCP</p>
      </header>
      <main className="main">
        <div className="card">
          <p>Counter: {count}</p>
          <button onClick={() => setCount(c => c + 1)}>Increment</button>
        </div>
      </main>
      <footer className="footer">
        <p>Built with React</p>
      </footer>
    </div>
  );
}

export default App;`));

  files.push(write(root, "src/App.css", `* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  background: #f5f5f5;
  color: #1a1a2e;
}

.app { max-width: 800px; margin: 0 auto; padding: 2rem; }

.header { text-align: center; margin-bottom: 2rem; }
.header h1 { font-size: 2rem; margin-bottom: 0.5rem; }
.header p { color: #666; }

.main { display: flex; justify-content: center; }

.card {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  text-align: center;
}
.card p { font-size: 1.5rem; margin-bottom: 1rem; }
.card button {
  background: #4361ee;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
}
.card button:hover { background: #3a56d4; }

.footer { text-align: center; margin-top: 2rem; color: #999; font-size: 0.9rem; }`));

  files.push(write(root, "src/components/Header.js", `import React from "react";

function Header({ title }) {
  return (
    <header className="header">
      <h1>{title}</h1>
    </header>
  );
}

export default Header;`));

  files.push(write(root, ".gitignore", "node_modules/\nbuild/\n.env\n"));

  files.push(write(root, "README.md", `# ${name}\n\nReact project scaffolded by AURA MCP.\n\n## Getting Started\n\n\`\`\`bash\nnpm install\nnpm start\n\`\`\`\n\nOpen [http://localhost:3000](http://localhost:3000) to view in browser.\n`));

  return files;
}

function generateNodeProject(root, name) {
  const files = [];

  files.push(write(root, "package.json", JSON.stringify({
    name,
    version: "1.0.0",
    scripts: {
      start: "node index.js",
      dev: "node --watch index.js",
    },
    dependencies: {
      express: "^4.18.0",
      cors: "^2.8.5",
    },
  }, null, 2)));

  files.push(write(root, "index.js", `const express = require("express");
const cors = require("cors");
const apiRoutes = require("./src/routes");
const errorHandler = require("./src/middleware/errorHandler");

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

app.get("/health", (req, res) => {
  res.json({ status: "ok", uptime: process.uptime(), timestamp: new Date().toISOString() });
});

app.use("/api", apiRoutes);

app.use(errorHandler);

app.listen(PORT, () => {
  console.log(\`${name} running on http://localhost:\${PORT}\`);
});`));

  files.push(write(root, "src/routes/index.js", `const router = require("express").Router();

router.get("/", (req, res) => {
  res.json({ message: "Welcome to ${name} API", version: "1.0.0" });
});

router.get("/items", (req, res) => {
  res.json({ items: [], total: 0 });
});

router.post("/items", (req, res) => {
  const { name } = req.body;
  if (!name) {
    return res.status(400).json({ error: "name is required" });
  }
  res.status(201).json({ id: Date.now(), name, created: new Date().toISOString() });
});

module.exports = router;`));

  files.push(write(root, "src/middleware/errorHandler.js", `function errorHandler(err, req, res, _next) {
  console.error(err.stack);
  res.status(500).json({ error: "Internal server error" });
}

module.exports = errorHandler;`));

  files.push(write(root, ".env.example", "PORT=3000\n"));
  files.push(write(root, ".gitignore", "node_modules/\n.env\n"));

  files.push(write(root, "README.md", `# ${name}\n\nNode.js Express API scaffolded by AURA MCP.\n\n## Getting Started\n\n\`\`\`bash\nnpm install\nnpm start\n\`\`\`\n\n## Endpoints\n\n| Method | Path | Description |\n|--------|------|-------------|\n| GET | /health | Health check |\n| GET | /api | API info |\n| GET | /api/items | List items |\n| POST | /api/items | Create item |\n`));

  return files;
}

function generateFastAPIProject(root, name) {
  const files = [];

  files.push(write(root, "main.py", `from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router

app = FastAPI(title="${name}", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "Welcome to ${name} API", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)`));

  files.push(write(root, "routes.py", `from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

items = []


class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None


@router.get("/items")
def list_items():
    return {"items": items, "total": len(items)}


@router.post("/items", status_code=201)
def create_item(item: ItemCreate):
    new_item = {"id": len(items) + 1, **item.model_dump()}
    items.append(new_item)
    return new_item


@router.get("/items/{item_id}")
def get_item(item_id: int):
    for item in items:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")`));

  files.push(write(root, "requirements.txt", "fastapi>=0.100.0\nuvicorn>=0.23.0\npydantic>=2.0.0\n"));
  files.push(write(root, ".gitignore", "__pycache__/\n*.pyc\n.env\nvenv/\n"));

  files.push(write(root, "README.md", `# ${name}\n\nFastAPI project scaffolded by AURA MCP.\n\n## Getting Started\n\n\`\`\`bash\npip install -r requirements.txt\npython main.py\n\`\`\`\n\nOpen [http://localhost:8000/docs](http://localhost:8000/docs) for interactive API docs.\n\n## Endpoints\n\n| Method | Path | Description |\n|--------|------|-------------|\n| GET | /health | Health check |\n| GET | /api/items | List items |\n| POST | /api/items | Create item |\n| GET | /api/items/:id | Get item |\n`));

  return files;
}

// ─── Helpers ────────────────────────────────────────────────────────

/**
 * Write a file relative to the project root and return its relative path.
 */
function write(root, relativePath, content) {
  createFile(path.join(root, relativePath), content);
  return relativePath;
}

/**
 * Build a human-readable summary for Notion output.
 */
function formatSummary(plan, projectRoot, files) {
  const tree = files.map((f) => `  • ${f}`).join("\n");
  return [
    `✅ Project scaffolded: ${plan.project_name}`,
    `Framework: ${plan.framework}`,
    `Location: ${projectRoot}`,
    `Files (${files.length}):`,
    tree,
    `\nGenerated by AURA MCP at ${new Date().toISOString()}`,
  ].join("\n");
}

module.exports = { executeTask };
