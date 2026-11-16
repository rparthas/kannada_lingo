import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import path from "node:path";
import {
  validateCurriculumBundle,
  type CurriculumBundleLike,
} from "../../src/domain/content/validate";

const bundlePath = path.resolve(
  import.meta.dirname,
  "../../content/curriculum/beginner-path.json",
);

describe("validateCurriculumBundle", () => {
  it("accepts bundled beginner path", () => {
    const bundle = JSON.parse(readFileSync(bundlePath, "utf8")) as CurriculumBundleLike;
    const issues = validateCurriculumBundle(bundle);
    expect(issues).toEqual([]);
  });

  it("flags missing human audio on approved items", () => {
    const issues = validateCurriculumBundle({
      learning_items: [
        {
          id: "item-a",
          kannada_text: "ಅ",
          transliteration: "a",
          english_meaning: "A",
          validation_status: "approved",
        },
      ],
      audio_assets: [],
    });
    expect(issues.some((i) => i.code === "missing_human_audio")).toBe(true);
  });
});