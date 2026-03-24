require("dotenv").config();

const logger = require("../src/utils/logger");
const { runAURA } = require("../src/core/orchestrator");

runAURA().catch((err) => {
  logger.error("Pipeline crashed:", err.message);
  process.exitCode = 1;
});
