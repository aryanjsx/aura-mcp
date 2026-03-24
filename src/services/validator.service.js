const ALLOWED_ACTIONS = ["scaffold_project"];
const ALLOWED_FRAMEWORKS = ["react", "node", "fastapi"];
const PROJECT_NAME_PATTERN = /^[a-z0-9][a-z0-9_-]{0,63}$/;

/**
 * Validate that an LLM-generated plan is safe and usable by the executor.
 * Throws a descriptive error if any check fails.
 *
 * @param {object} plan — the parsed plan object
 * @returns {object} The validated (and lightly sanitized) plan
 */
function validatePlan(plan) {
  if (!plan || typeof plan !== "object") {
    throw new Error("Plan must be a non-null object");
  }

  if (!ALLOWED_ACTIONS.includes(plan.action)) {
    throw new Error(
      `Invalid action "${plan.action}". Allowed: ${ALLOWED_ACTIONS.join(", ")}`
    );
  }

  if (!ALLOWED_FRAMEWORKS.includes(plan.framework)) {
    throw new Error(
      `Invalid framework "${plan.framework}". Allowed: ${ALLOWED_FRAMEWORKS.join(", ")}`
    );
  }

  if (!plan.project_name || typeof plan.project_name !== "string") {
    throw new Error("Plan must include a non-empty project_name string");
  }

  const sanitized = plan.project_name
    .toLowerCase()
    .replace(/[^a-z0-9_-]/g, "_")
    .replace(/_{2,}/g, "_")
    .replace(/^[-_]+|[-_]+$/g, "")
    .slice(0, 64);

  if (!PROJECT_NAME_PATTERN.test(sanitized)) {
    throw new Error(`Could not produce a valid project name from "${plan.project_name}"`);
  }

  return {
    action: plan.action,
    framework: plan.framework,
    project_name: sanitized,
    features: Array.isArray(plan.features) ? plan.features : [],
  };
}

module.exports = { validatePlan };
