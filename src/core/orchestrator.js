const logger = require("../utils/logger");
const notionService = require("../services/notion.service");
const interpreter = require("../services/interpreter.service");
const executor = require("../services/executor.service");

/**
 * Main AURA pipeline.
 * Fetches pending tasks from Notion, processes each one sequentially:
 *   parse → execute → update Notion
 */
async function runAURA() {
  logger.info("=== AURA MCP — Execution Pipeline ===\n");

  notionService.init();

  const tasks = await notionService.getPendingTasks();

  if (tasks.length === 0) {
    logger.warn("No pending tasks found. Add a task in Notion with Status = 'pending' and run again.");
    return { processed: 0, succeeded: 0, failed: 0 };
  }

  logger.info(`Processing ${tasks.length} task(s)...\n`);

  let succeeded = 0;
  let failed = 0;

  for (const task of tasks) {
    logger.info(`──── Task: "${task.task}" [${task.id}] ────`);

    try {
      await notionService.markAsProcessing(task.id);

      logger.info("Interpreting task...");
      const plan = await interpreter.parseTask(task.task);

      logger.info("Executing plan...");
      const result = executor.executeTask(plan);

      logger.info("Updating Notion with result...");
      await notionService.markAsDone(task.id, result);

      logger.info("Task completed ✓\n");
      succeeded++;
    } catch (err) {
      logger.error(`Task failed: ${err.message}`);
      try {
        await notionService.markAsFailed(task.id, `Error: ${err.message}`);
      } catch (notionErr) {
        logger.error(`Could not update failed status in Notion: ${notionErr.message}`);
      }
      failed++;
    }
  }

  logger.info("=== Pipeline complete ===");
  logger.info(`Results: ${succeeded} succeeded, ${failed} failed, ${tasks.length} total`);

  return { processed: tasks.length, succeeded, failed };
}

module.exports = { runAURA };
