import { describe, expect, it } from "vitest";
import { filterPhrases } from "../../src/domain/phrase-search/filter";

function phrase(i: number) {
  return {
    id: `item-${i}`,
    kannada_text: i === 7 ? "ವಿಮಾನ ನಿಲ್ದಾಣ" : `ಪದ${i}`,
    transliteration: i === 7 ? "vimana nildana" : `pada${i}`,
    english_meaning: i === 7 ? "airport" : `word ${i}`,
  };
}

const phrases = Array.from({ length: 600 }, (_, i) => phrase(i));

describe("filterPhrases", () => {
  it("returns every phrase for an empty search", () => {
    expect(filterPhrases(phrases, "")).toHaveLength(600);
    expect(filterPhrases(phrases, "   ")).toHaveLength(600);
  });

  it("matches English meanings", () => {
    const results = filterPhrases(phrases, "airport");
    expect(results.map((p) => p.id)).toEqual(["item-7"]);
  });

  it("matches transliteration", () => {
    const results = filterPhrases(phrases, "vimana");
    expect(results.map((p) => p.id)).toEqual(["item-7"]);
  });

  it("matches Kannada script", () => {
    const results = filterPhrases(phrases, "ವಿಮಾನ");
    expect(results.map((p) => p.id)).toEqual(["item-7"]);
  });

  it("stays fast across 500+ bundled items", () => {
    const started = performance.now();
    const results = filterPhrases(phrases, "word 5");
    const elapsed = performance.now() - started;
    expect(results.length).toBeGreaterThan(0);
    // Generous bound: the synchronous scan should be far under a frame.
    expect(elapsed).toBeLessThan(50);
  });
});
