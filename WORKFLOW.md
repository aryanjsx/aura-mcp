<div align="center">

# 🔄 AURA MCP — Project Workflow

### Complete System Flow: From Notion Task to Real Project

</div>

---

## 🗺️ High-Level Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   👤 USER                                                           │
│   Writes a task in Notion                                           │
│   "Build a task manager with React"                                 │
│                                                                     │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   📝 NOTION DATABASE                                                │
│   ┌───────────────────────────────────────────────┐                 │
│   │ Name: "Build a task manager with React"       │                 │
│   │ Status: 🟡 Pending                            │                 │
│   │ Output: (empty)                               │                 │
│   └───────────────────────────────────────────────┘                 │
│                                                                     │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   🧠 AURA MCP SERVER                                                │
│                                                                     │
│   Step 1: 📥 Read pending tasks from Notion                         │
│   Step 2: 🔄 Mark task as "In progress"                             │
│   Step 3: 🤖 Interpret task (AI or rules)                           │
│   Step 4: ✅ Validate the plan                                      │
│   Step 5: 🏗️  Scaffold the project on disk                          │
│   Step 6: 📤 Write results back to Notion                           │
│                                                                     │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   📁 OUTPUT                                                         │
│                                                                     │
│   Filesystem:                    Notion:                            │
│   output/task_manager/           ┌──────────────────────────────┐   │
│   ├── package.json               │ Status: ✅ Done              │   │
│   ├── src/App.js                 │ Output: "✅ Project          │   │
│   ├── src/index.js               │  scaffolded: task_manager    │   │
│   ├── src/App.css                │  Framework: react            │   │
│   ├── src/components/Header.js   │  Files (8): ..."            │   │
│   ├── public/index.html          └──────────────────────────────┘   │
│   ├── .gitignore                                                    │
│   └── README.md                                                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔍 Detailed Step-by-Step Flow

### Phase A — Trigger

```
┌──────────────┐         ┌──────────────────┐
│              │         │                  │
│  npm start   │───OR───►│  npm run mcp     │
│  (direct)    │         │  (MCP server)    │
│              │         │                  │
└──────┬───────┘         └────────┬─────────┘
       │                          │
       ▼                          ▼
  Runs pipeline             Waits for MCP
  immediately               client to call
                            run_aura tool
       │                          │
       └────────────┬─────────────┘
                    ▼
           orchestrator.js
            runAURA()
```

---

### Phase B — Read from Notion

```
  orchestrator.js
       │
       ▼
  ┌─────────────────────────────────────┐
  │  📥 notion.service.getPendingTasks() │
  │                                     │
  │  Query: Status === "Pending"        │
  │  Extract: { id, task } for each row │
  └──────────────────┬──────────────────┘
                     │
              ┌──────┴──────┐
              │             │
              ▼             ▼
        Tasks found    No tasks found
              │             │
              ▼             ▼
        Continue        ⚠️ Log warning
        processing      and exit
```

---

### Phase C — Task Lifecycle (per task)

```
  For each task:
       │
       ▼
  ┌──────────────────────────────┐
  │  🔄 Mark as "In progress"    │──────────► Notion updates immediately
  └──────────────┬───────────────┘
                 │
                 ▼
  ┌──────────────────────────────┐
  │  🧠 INTERPRET TASK            │
  │                              │
  │  Input:                      │
  │  "Build a task manager       │
  │   with React"                │
  │                              │
  │         ┌────────┐           │
  │         │ OpenAI │           │
  │         │  key?  │           │
  │         └───┬────┘           │
  │          Y/ \N               │
  │          /   \               │
  │         ▼     ▼              │
  │     ┌──────┐ ┌──────────┐   │
  │     │ 🤖   │ │ 📏 Rules  │   │
  │     │ LLM  │ │ (keyword  │   │
  │     │ call │ │  detect)  │   │
  │     └──┬───┘ └────┬─────┘   │
  │        │          │          │
  │        ▼          │          │
  │   ┌─────────┐    │          │
  │   │Valid     │    │          │
  │   │JSON?     │    │          │
  │   └──┬──┬───┘    │          │
  │    Y/   \N       │          │
  │    /     \       │          │
  │   ▼      ▼      │          │
  │  ┌───┐ ┌──────┐  │          │
  │  │ ✅ │ │Fallback├─┘         │
  │  └─┬─┘ └──────┘             │
  │    │                         │
  └────┼─────────────────────────┘
       │
       ▼
  ┌──────────────────────────────┐
  │  ✅ VALIDATE PLAN             │
  │                              │
  │  Check:                      │
  │  ├── action = scaffold_project│
  │  ├── framework ∈ {react,     │
  │  │    node, fastapi}         │
  │  ├── project_name exists     │
  │  └── sanitize name           │
  │      (no path traversal)     │
  │                              │
  │  Output:                     │
  │  {                           │
  │    action: "scaffold_project"│
  │    framework: "react"        │
  │    project_name: "task_man.."│
  │    features: [...]           │
  │  }                           │
  └──────────────┬───────────────┘
                 │
                 ▼
  ┌──────────────────────────────┐
  │  🏗️  EXECUTE                  │
  │                              │
  │  1. Create output/{name}/    │
  │  2. Select template (react)  │
  │  3. Generate each file       │
  │     with real code           │
  │  4. Return summary string    │
  └──────────────┬───────────────┘
                 │
                 ▼
  ┌──────────────────────────────┐
  │  📤 UPDATE NOTION             │
  │                              │
  │  Status → ✅ Done             │
  │  Output → File tree +        │
  │           framework info +   │
  │           timestamp          │
  └──────────────────────────────┘
```

---

### Phase D — Error Handling

```
  Any step fails?
       │
       ▼
  ┌──────────────────────────────┐
  │  ❌ CATCH ERROR               │
  │                              │
  │  1. Log error message        │
  │  2. Update Notion:           │
  │     Status → To-do           │
  │     Output → "Error: ..."    │
  │  3. Continue to next task    │
  │     (never crash)            │
  └──────────────────────────────┘
```

---

## 🔀 Interpreter Decision Tree

```
                    📝 Task Text
                         │
                         ▼
                ┌────────────────┐
                │  OPENAI_API_KEY │
                │  exists in env? │
                └───────┬────────┘
                   YES/   \NO
                   /       \
                  ▼         ▼
          ┌────────────┐  ┌────────────────┐
          │ 🤖 Call LLM │  │ 📏 Rule-based   │
          │             │  │                │
          │ System:     │  │ Scan for:      │
          │ "Return     │  │ • "react"      │
          │  JSON only" │  │ • "node"       │
          │             │  │ • "express"    │
          │ Temp: 0     │  │ • "fastapi"    │
          │ Max: 256    │  │ • "python"     │
          └──────┬──────┘  │                │
                 │         │ Default: node  │
                 ▼         └───────┬────────┘
          ┌────────────┐           │
          │ Parse JSON  │           │
          └──────┬──────┘           │
            OK/   \FAIL             │
            /      \                │
           ▼        ▼               │
    ┌──────────┐  ┌─────────┐      │
    │ Validate  │  │Fallback │──────┘
    │ plan      │  │to rules │
    └─────┬────┘  └─────────┘
     OK/   \FAIL
     /      \
    ▼        ▼
  ┌───┐  ┌─────────┐
  │ ✅ │  │Fallback │──────────────►  📏 Rule-based
  │USE│  │to rules │
  └───┘  └─────────┘
```

---

## 🗂️ Data Flow Map

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   NOTION    │     │ INTERPRETER  │     │  VALIDATOR    │     │  EXECUTOR    │
│   API       │     │              │     │              │     │              │
│             │     │              │     │              │     │              │
│  { id,      │────►│  { action,   │────►│  { action,   │────►│  Creates     │
│    task }   │     │    framework,│     │    framework,│     │  real files  │
│             │     │    project,  │     │    project,  │     │  on disk     │
│             │     │    features }│     │    features }│     │              │
│             │     │              │     │  (sanitized) │     │  Returns     │
│             │◄────│              │     │              │     │  summary     │
│  Status:    │     │              │     │              │     │  string      │
│  Done ✅    │     │              │     │              │     │              │
│  Output:    │     │              │     │              │     │              │
│  summary    │     │              │     │              │     │              │
└─────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

---

## 🎬 MCP Server Request Flow

```
  Claude Desktop / MCP Client
       │
       │  JSON-RPC over stdio
       ▼
  ┌──────────────────────────────────────────┐
  │            AURA MCP SERVER               │
  │                                          │
  │  tools/list                              │
  │  ├── 🚀 run_aura                         │
  │  ├── 📋 get_pending_tasks                │
  │  └── ⚙️  run_single_task                  │
  │                                          │
  │  tools/call "run_aura"                   │
  │  ┌────────────────────────────────────┐  │
  │  │ 1. runAURA()                       │  │
  │  │ 2. Return JSON:                    │  │
  │  │    { status, processed,            │  │
  │  │      succeeded, failed }           │  │
  │  └────────────────────────────────────┘  │
  │                                          │
  │  tools/call "run_single_task"            │
  │  ┌────────────────────────────────────┐  │
  │  │ Input: { task: "..." }             │  │
  │  │ 1. parseTask(task)                 │  │
  │  │ 2. executeTask(plan)               │  │
  │  │ 3. Return JSON:                    │  │
  │  │    { status, plan, output }        │  │
  │  └────────────────────────────────────┘  │
  │                                          │
  │  ⚠️ stdout reserved for MCP protocol     │
  │  📋 All logs redirected to stderr        │
  └──────────────────────────────────────────┘
```

---

## 📊 Task State Machine

```
                    ┌──────────┐
                    │          │
         ┌─────────┤ PENDING  │
         │         │  🟡      │
         │         └──────────┘
         │
         │  AURA picks up task
         ▼
    ┌───────────┐
    │           │
    │IN PROGRESS│
    │  🔵      │
    │           │
    └─────┬─────┘
          │
     ┌────┴────┐
     │         │
  Success    Failure
     │         │
     ▼         ▼
┌─────────┐ ┌─────────┐
│         │ │         │
│  DONE   │ │  TO-DO  │
│  ✅     │ │  🔴     │
│         │ │         │
│ + Output│ │ + Error │
│ summary │ │ message │
└─────────┘ └─────────┘
```

---

<div align="center">

### 🔁 The Cycle

**Write → Execute → Report → Repeat**

Every task you write in Notion becomes a real project.
No terminal. No boilerplate. Just intent in, execution out.

</div>
