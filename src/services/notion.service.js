const { Client } = require("@notionhq/client");
const logger = require("../utils/logger");

const VALID_STATUSES = ["Pending", "In progress", "Done", "To-do", "Complete"];

let notion;
let databaseId;

/**
 * Initialize the Notion client. Must be called before any other function.
 * Reads NOTION_API_KEY and NOTION_DATABASE_ID from environment.
 */
function init() {
  const apiKey = process.env.NOTION_API_KEY;
  databaseId = process.env.NOTION_DATABASE_ID;

  if (!apiKey || !databaseId) {
    throw new Error(
      "Missing NOTION_API_KEY or NOTION_DATABASE_ID in environment variables"
    );
  }

  notion = new Client({ auth: apiKey });
  logger.info("Notion client initialized");
}

/**
 * Extract the plain-text title from a Notion title property.
 * Returns empty string if the title array is missing or empty.
 */
function extractTitle(titleProperty) {
  if (!titleProperty || !Array.isArray(titleProperty) || titleProperty.length === 0) {
    return "";
  }
  return titleProperty.map((t) => t.plain_text).join("");
}

/**
 * Fetch all tasks where Status = "pending".
 * Returns an array of clean objects: { id, task }
 */
async function getPendingTasks() {
  try {
    const response = await notion.databases.query({
      database_id: databaseId,
      filter: {
        property: "Status",
        status: {
          equals: "Pending",
        },
      },
    });

    const tasks = response.results.map((page) => ({
      id: page.id,
      task: extractTitle(page.properties.Name?.title),
    }));

    logger.info(`Fetched ${tasks.length} pending task(s)`);
    return tasks;
  } catch (err) {
    logger.error("Failed to fetch pending tasks:", err.message);
    throw err;
  }
}

/**
 * Update a task's Status and optionally its Output.
 *
 * @param {string} pageId  — Notion page ID
 * @param {string} status  — One of: pending, processing, done, failed
 * @param {string} [output] — Optional text to write into the Output property
 */
async function updateTaskStatus(pageId, status, output) {
  if (!VALID_STATUSES.includes(status)) {
    throw new Error(
      `Invalid status "${status}". Must be one of: ${VALID_STATUSES.join(", ")}`
    );
  }

  const properties = {
    Status: {
      status: { name: status },
    },
  };

  if (output !== undefined && output !== null) {
    properties.Output = {
      rich_text: [
        {
          type: "text",
          text: { content: String(output).slice(0, 2000) },
        },
      ],
    };
  }

  try {
    await notion.pages.update({
      page_id: pageId,
      properties,
    });
    logger.info(`Task ${pageId} → status: "${status}"`);
  } catch (err) {
    logger.error(`Failed to update task ${pageId}:`, err.message);
    throw err;
  }
}

/**
 * Convenience wrapper: mark a task as "processing".
 */
async function markAsProcessing(pageId) {
  return updateTaskStatus(pageId, "In progress");
}

/**
 * Convenience wrapper: mark a task as "Done" with an output summary.
 */
async function markAsDone(pageId, output) {
  return updateTaskStatus(pageId, "Done", output);
}

/**
 * Convenience wrapper: mark a task as "To-do" with an error message.
 */
async function markAsFailed(pageId, errorMessage) {
  return updateTaskStatus(pageId, "To-do", errorMessage);
}

module.exports = {
  init,
  getPendingTasks,
  updateTaskStatus,
  markAsProcessing,
  markAsDone,
  markAsFailed,
};
