const fs = require("fs");
const path = require("path");

/**
 * Create a directory recursively. No-op if it already exists.
 */
function createFolder(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
}

/**
 * Create a file with content. Creates parent directories if needed.
 */
function createFile(filePath, content) {
  const dir = path.dirname(filePath);
  createFolder(dir);
  fs.writeFileSync(filePath, content, "utf-8");
}

module.exports = { createFolder, createFile };
