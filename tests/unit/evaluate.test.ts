import { describe, expect, it } from "vitest";
import {
  evaluateEnglishMeaning,
  evaluateKannadaRecall,
  evaluateWordOrder,
  normalizeFreeText,
} from "../../src/domain/exercises/evaluate";

describe("evaluate", () => {
  it("normalizes whitespace", () => {
    expect(normalizeFreeText("  Hello   there ")).toBe("hello there");
  });

  it("accepts colloquial alternatives", () => {
    const ok = evaluateEnglishMeaning("okay", {
      kannadaText: "ಸರಿ",
      transliteration: "sari",
      englishMeaning: "Okay / all right",
      acceptedAnswers: ["okay", "ok"],
    });
    expect(ok).toBe(true);
  });

  it("matches Kannada recall by transliteration or script", () => {
    const item = {
      kannadaText: "ಧನ್ಯವಾದ",
      transliteration: "dhanyavāda",
      englishMeaning: "Thank you",
    };
    expect(evaluateKannadaRecall("dhanyavada", item)).toBe(true);
    expect(evaluateKannadaRecall("ಧನ್ಯವಾದ", item)).toBe(true);
  });

  it("validates word order", () => {
    expect(evaluateWordOrder(["āṭō", "biḍi"], ["āṭō", "biḍi"])).toBe(true);
    expect(evaluateWordOrder(["biḍi", "āṭō"], ["āṭō", "biḍi"])).toBe(false);
  });
});