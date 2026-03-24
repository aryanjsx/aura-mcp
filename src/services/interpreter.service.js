const logger = require("../utils/logger");
const { interpretWithLLM } = require("./llm.service");
const { validatePlan } = require("./validator.service");

// ─── Rule-based fallback (Phase 2 logic, preserved) ─────────────────

const FRAMEWORK_RULES = [
  { keywords: ["react"], framework: "react" },
  { keywords: ["fastapi", "fast api", "flask", "python api"], framework: "fastapi" },
  { keywords: ["node", "express", "javascript api"], framework: "node" },
];

const STOP_WORDS = [
  "a", "an", "the", "with", "and", "for", "in", "on", "to", "of",
  "my", "me", "it", "is", "do", "so", "or", "by", "at", "be",
  "create", "build", "scaffold", "make", "setup", "set", "up",
  "generate", "new", "project", "app", "application", "using",
  "use", "add", "start", "write", "develop", "code", "please",
  "want", "need", "like", "should", "would", "could", "simple",
  "basic", "full", "complete", "stack", "web", "website", "site",
  "frontend", "backend", "server", "client", "api",
];

function detectFramework(text) {
  const lower = text.toLowerCase();
  for (const rule of FRAMEWORK_RULES) {
    if (rule.keywords.some((kw) => lower.includes(kw))) {
      return rule.framework;
    }
  }
  return "node";
}

function deriveProjectName(text, framework) {
  const allFrameworkKeywords = FRAMEWORK_RULES.flatMap((r) => r.keywords);
  const ignore = new Set([...STOP_WORDS, ...allFrameworkKeywords]);

  const words = text
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, "")
    .split(/\s+/)
    .filter((w) => w.length > 1 && !ignore.has(w));

  const meaningful = words.slice(0, 3);

  if (meaningful.length > 0) {
    return meaningful.join("_");
  }
  return `${framework}_app`;
}

function parseWithRules(taskText) {
  const framework = detectFramework(taskText);
  const projectName = deriveProjectName(taskText, framework);

  const plan = {
    action: "scaffold_project",
    framework,
    project_name: projectName,
    features: [],
  };

  logger.info(`[rules] Parsed → action: ${plan.action}, framework: ${plan.framework}, name: ${plan.project_name}`);
  return plan;
}

// ─── Main interpreter (LLM-first, rule-based fallback) ──────────────

/**
 * Parse a task description into a structured execution plan.
 * Tries LLM interpretation first; falls back to rule-based parsing on any failure.
 *
 * @param {string} taskText — raw task title from Notion
 * @returns {Promise<{ action: string, framework: string, project_name: string, features: string[] }>}
 */
async function parseTask(taskText) {
  if (!taskText || typeof taskText !== "string" || taskText.trim().length === 0) {
    throw new Error("Cannot parse empty task text");
  }

  if (!process.env.OPENAI_API_KEY) {
    logger.warn("OPENAI_API_KEY not set — using rule-based parser");
    return parseWithRules(taskText);
  }

  try {
    const rawPlan = await interpretWithLLM(taskText);
    const plan = validatePlan(rawPlan);
    logger.info(`[llm] Parsed → action: ${plan.action}, framework: ${plan.framework}, name: ${plan.project_name}`);
    if (plan.features.length > 0) {
      logger.info(`[llm] Features: ${plan.features.join(", ")}`);
    }
    return plan;
  } catch (err) {
    logger.warn(`LLM interpretation failed: ${err.message}`);
    logger.info("Falling back to rule-based parser");
    return parseWithRules(taskText);
  }
}

module.exports = { parseTask, parseWithRules };
