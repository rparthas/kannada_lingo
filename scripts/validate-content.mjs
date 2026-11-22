#!/usr/bin/env node
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

// Mirror rules in src/domain/content/validate.ts (kept lean for CI without Vitest)
function validateBundle(bundle) {
  const issues = [];
  const items = bundle.learning_items ?? [];
  const audio = bundle.audio_assets ?? [];
  const approved = items.filter((i) => (i.validation_status ?? "approved") === "approved");
  const humanNormal = new Set(
    audio
      .filter(
        (a) =>
          (a.source === "human" || a.source === "tts") &&
          (a.speaking_speed ?? "normal") === "normal",
      )
      .map((a) => a.learning_item_id),
  );
  for (const item of approved) {
    if (!humanNormal.has(item.id)) {
      issues.push(`missing_human_audio: ${item.id}`);
    }
  }
  const ids = items.map((i) => i.id);
  if (new Set(ids).size !== ids.length) issues.push("duplicate learning item ids");
  return issues;
}

const file = path.join(root, "content/curriculum/beginner-path.json");
const bundle = JSON.parse(readFileSync(file, "utf8"));
const issues = validateBundle(bundle);

if (issues.length) {
  console.error("Content validation failed:");
  for (const line of issues) console.error("  -", line);
  process.exit(1);
}
console.log(`Content OK (version ${bundle.content_version})`);