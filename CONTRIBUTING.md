# 🤝 Contributing to AURA MCP

First off, thanks for taking the time to contribute! 🎉

AURA MCP is an open-source project and we love receiving contributions from the community. Whether it's a bug fix, new feature, documentation improvement, or a new framework template — every contribution matters.

---

## 📋 Table of Contents

- [Code of Conduct](#-code-of-conduct)
- [How Can I Contribute?](#-how-can-i-contribute)
- [Getting Started](#-getting-started)
- [Development Workflow](#-development-workflow)
- [Project Structure](#-project-structure)
- [Adding a New Framework Template](#-adding-a-new-framework-template)
- [Commit Guidelines](#-commit-guidelines)
- [Pull Request Process](#-pull-request-process)

---

## 📜 Code of Conduct

This project follows our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code. Please report unacceptable behavior via GitHub Issues.

---

## 💡 How Can I Contribute?

### 🐛 Report Bugs

- Use the [Bug Report issue template](.github/ISSUE_TEMPLATE/bug_report.md)
- Include steps to reproduce, expected behavior, and actual behavior
- Include your Node.js version and OS

### ✨ Suggest Features

- Use the [Feature Request issue template](.github/ISSUE_TEMPLATE/feature_request.md)
- Explain the use case and why it would be valuable
- Keep scope focused — small, impactful features are best

### 🏗️ Add a Framework Template

This is one of the highest-impact contributions! See [Adding a New Framework Template](#-adding-a-new-framework-template) below.

### 📝 Improve Documentation

- Fix typos, clarify explanations, add examples
- No issue needed — just open a PR

### 🧹 Code Quality

- Refactoring, better error messages, edge case handling
- Open an issue first to discuss approach

---

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- A Notion integration and database (see [README](README.md))
- (Optional) OpenAI API key

### Setup

```bash
git clone https://github.com/your-username/aura-mcp.git
cd aura-mcp
npm install
cp .env.example .env
# Fill in your .env values
```

### Verify it works

```bash
npm start
```

---

## 🔄 Development Workflow

1. **Fork** the repository
2. **Create a branch** from `master`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** — keep them focused and minimal
4. **Test** your changes:
   ```bash
   # Run the pipeline
   npm start

   # Or test a specific module
   node -e "const m = require('./src/services/your-module'); ..."
   ```
5. **Commit** using the [commit guidelines](#-commit-guidelines)
6. **Push** and open a Pull Request

---

## 🗂️ Project Structure

```
src/
├── mcp/
│   └── server.js              ← MCP tool registration (touch rarely)
├── core/
│   └── orchestrator.js        ← Pipeline engine (touch rarely)
├── services/
│   ├── notion.service.js      ← Notion API (modify for new properties)
│   ├── interpreter.service.js ← Parser logic (modify for better parsing)
│   ├── llm.service.js         ← LLM prompt (modify for better prompts)
│   ├── validator.service.js   ← Validation rules (modify for new actions)
│   └── executor.service.js    ← 🎯 Templates live here (most contributions)
└── utils/
    ├── logger.js              ← Logging (stable, rarely needs changes)
    └── file.utils.js          ← File helpers (stable)
```

> **Most contributions happen in `executor.service.js`** (new templates) and `interpreter.service.js` (better parsing).

---

## 🆕 Adding a New Framework Template

This is the easiest and most impactful way to contribute. Here's how:

### 1. Add the template generator in `executor.service.js`

```javascript
function generateDjangoProject(root, name) {
  const files = [];

  files.push(write(root, "manage.py", `...`));
  files.push(write(root, "requirements.txt", `django>=4.2\n`));
  files.push(write(root, "README.md", `# ${name}\n\n...`));

  return files;
}
```

### 2. Register it in the `TEMPLATES` map

```javascript
const TEMPLATES = {
  react: generateReactProject,
  node: generateNodeProject,
  fastapi: generateFastAPIProject,
  django: generateDjangoProject,  // ← add here
};
```

### 3. Add keywords in `interpreter.service.js`

```javascript
const FRAMEWORK_RULES = [
  // ...existing rules
  { keywords: ["django"], framework: "django" },
];
```

### 4. Add to the validator's allowed list in `validator.service.js`

```javascript
const ALLOWED_FRAMEWORKS = ["react", "node", "fastapi", "django"];
```

### 5. Update the LLM prompt in `llm.service.js`

Add `"django"` to the framework options in the system prompt.

### 6. Test it

```bash
node -e "
  const i = require('./src/services/interpreter.service');
  const e = require('./src/services/executor.service');
  const plan = i.parseWithRules('Create a Django blog');
  console.log(e.executeTask(plan));
"
```

---

## 📝 Commit Guidelines

Use clear, descriptive commit messages:

```
<type>: <short description>

<optional body>
```

### Types

| Type | When to use |
|:-----|:------------|
| `feat` | New feature or template |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `test` | Adding or updating tests |
| `chore` | Tooling, configs, dependencies |

### Examples

```
feat: add Django project template
fix: handle empty task titles gracefully
docs: add setup instructions for Windows
refactor: extract template helpers into shared module
```

---

## 🔀 Pull Request Process

1. **Fill out the PR template** — describe what changed and why
2. **Keep PRs small** — one feature or fix per PR
3. **Test your changes** — include the test command output if possible
4. **Update docs** if your change affects setup, usage, or supported frameworks
5. **Be responsive** — address review feedback promptly

### PR will be reviewed for:

- ✅ Does it work?
- ✅ Is it clean and readable?
- ✅ Does it follow existing patterns?
- ✅ Does it include relevant doc updates?
- ✅ Is the scope focused?

---

## 🙏 Thank You

Every contribution makes AURA better. Whether it's a typo fix or a whole new framework template — **you're awesome for contributing**. 💜
