const OpenAI = require("openai");
const logger = require("../utils/logger");

const SYSTEM_PROMPT = `You are an AI that converts user task descriptions into structured JSON commands for a project scaffolding system.

Rules:
- Return ONLY valid JSON. No explanation, no markdown, no extra text.
- The JSON must match this exact schema:

{
  "action": "scaffold_project",
  "framework": "react" | "node" | "fastapi",
  "project_name": "snake_case_name",
  "features": ["optional", "feature", "keywords"]
}

Guidelines for project_name:
- Use snake_case
- Keep it short and descriptive (e.g. "bookstore_api", "portfolio_site")
- Derive it from the user's intent, not the framework name alone

Guidelines for framework:
- "react" for any React, frontend, or UI project
- "node" for any Node.js, Express, or JavaScript API/backend project
- "fastapi" for any Python, FastAPI, or Flask project
- Default to "node" if unclear`;

/**
 * Send a single LLM call to interpret a task description into a structured plan.
 *
 * @param {string} taskText — raw task title from Notion
 * @returns {object} Parsed JSON plan from the LLM
 */
async function interpretWithLLM(taskText) {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    throw new Error("Missing OPENAI_API_KEY in environment variables");
  }

  const client = new OpenAI({ apiKey });

  logger.info("Sending task to LLM...");

  const response = await client.chat.completions.create({
    model: process.env.OPENAI_MODEL || "gpt-3.5-turbo",
    messages: [
      { role: "system", content: SYSTEM_PROMPT },
      { role: "user", content: `Convert this task into JSON:\n\nTask: "${taskText}"` },
    ],
    temperature: 0,
    max_tokens: 256,
  });

  const raw = response.choices[0]?.message?.content;
  if (!raw) {
    throw new Error("LLM returned empty response");
  }

  logger.info("LLM response received, parsing JSON...");

  const cleaned = raw.replace(/```json\s*/g, "").replace(/```\s*/g, "").trim();

  let plan;
  try {
    plan = JSON.parse(cleaned);
  } catch (parseErr) {
    throw new Error(`LLM returned invalid JSON: ${cleaned.slice(0, 200)}`);
  }

  return plan;
}

module.exports = { interpretWithLLM };
