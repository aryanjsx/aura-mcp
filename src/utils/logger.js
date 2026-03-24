const PREFIX = "[AURA]";

function timestamp() {
  return new Date().toISOString();
}

function info(...args) {
  console.log(`${PREFIX} INFO  [${timestamp()}]`, ...args);
}

function error(...args) {
  console.error(`${PREFIX} ERROR [${timestamp()}]`, ...args);
}

function warn(...args) {
  console.warn(`${PREFIX} WARN  [${timestamp()}]`, ...args);
}

module.exports = { info, error, warn };
