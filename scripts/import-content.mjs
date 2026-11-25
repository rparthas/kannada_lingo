#!/usr/bin/env node
/**
 * Validate bundled curriculum and import into a learner SQLite database.
 * Run `npm run content:build` first if specs changed.
 */
import { spawnSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const tauriDir = path.join(root, "src-tauri");

const validate = spawnSync("npm", ["run", "content:validate"], {
  cwd: root,
  stdio: "inherit",
  shell: true,
});
if (validate.status !== 0) {
  process.exit(validate.status ?? 1);
}

const extra = process.argv.slice(2);
const cargo = spawnSync(
  "cargo",
  ["run", "--quiet", "--bin", "content_import", "--", ...extra],
  { cwd: tauriDir, stdio: "inherit", env: process.env },
);
process.exit(cargo.status ?? 1);