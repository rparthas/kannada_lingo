import { describe, expect, it } from "vitest";
import { MockAIContentProvider } from "../../src/services/ai/mockProvider";

describe("MockAIContentProvider", () => {
  const provider = new MockAIContentProvider();

  it("explains known grammar patterns", async () => {
    const result = await provider.explainGrammar({
      patternId: "pattern-sari",
      exampleItemIds: ["item-sari"],
    });
    expect(result.title).toContain("sari");
    expect(result.explanationEn.length).toBeGreaterThan(20);
  });

  it("returns phrase variation drafts", async () => {
    const result = await provider.generatePhraseVariations({
      learningItemId: "item-sari",
      scenarioTag: "greeting",
      approvedVocabularyIds: ["item-sari"],
    });
    expect(result.drafts.length).toBeGreaterThan(0);
    expect(result.drafts[0]?.validationStatus).toBe("draft");
  });
});