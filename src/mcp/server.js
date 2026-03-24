// MCP protocol uses stdout for communication.
// Redirect console.log to stderr so logger output doesn't corrupt the protocol.
const _origLog = console.log;
console.log = (...args) => console.error(...args);

require("dotenv").config();

const { McpServer } = require("@modelcontextprotocol/sdk/server/mcp.js");
const { StdioServerTransport } = require("@modelcontextprotocol/sdk/server/stdio.js");
const { z } = require("zod");

const logger = require("../utils/logger");
const notionService = require("../services/notion.service");
const interpreter = require("../services/interpreter.service");
const executor = require("../services/executor.service");
const { runAURA } = require("../core/orchestrator");

const server = new McpServer({
  name: "aura-mcp",
  version: "1.0.0",
});

// ─── Tool 1: run_aura ──────────────────────────────────────────────

server.tool(
  "run_aura",
  "Run the full AURA pipeline: fetch pending Notion tasks, interpret them, scaffold projects on disk, and update Notion with results",
  async () => {
    try {
      const result = await runAURA();
      return {
        content: [{
          type: "text",
          text: JSON.stringify({ status: "success", ...result }, null, 2),
        }],
      };
    } catch (err) {
      return {
        content: [{ type: "text", text: JSON.stringify({ error: err.message }) }],
        isError: true,
      };
    }
  }
);

// ─── Tool 2: get_pending_tasks ──────────────────────────────────────

server.tool(
  "get_pending_tasks",
  "Fetch and return all pending tasks from the configured Notion database",
  async () => {
    try {
      notionService.init();
      const tasks = await notionService.getPendingTasks();
      return {
        content: [{
          type: "text",
          text: JSON.stringify({ status: "success", count: tasks.length, tasks }, null, 2),
        }],
      };
    } catch (err) {
      return {
        content: [{ type: "text", text: JSON.stringify({ error: err.message }) }],
        isError: true,
      };
    }
  }
);

// ─── Tool 3: run_single_task ────────────────────────────────────────

server.tool(
  "run_single_task",
  "Execute a single task from text input — interprets and scaffolds a project without reading from Notion",
  {
    task: z.string().describe("Task description, e.g. 'Create a React portfolio app'"),
  },
  async ({ task }) => {
    try {
      const plan = await interpreter.parseTask(task);
      const result = executor.executeTask(plan);
      return {
        content: [{
          type: "text",
          text: JSON.stringify({
            status: "success",
            plan: { action: plan.action, framework: plan.framework, project_name: plan.project_name },
            output: result,
          }, null, 2),
        }],
      };
    } catch (err) {
      return {
        content: [{ type: "text", text: JSON.stringify({ error: err.message }) }],
        isError: true,
      };
    }
  }
);

// ─── Start ──────────────────────────────────────────────────────────

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  logger.info("AURA MCP server running on stdio");
}

main().catch((err) => {
  logger.error("MCP server failed to start:", err.message);
  process.exit(1);
});
