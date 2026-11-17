import { describe, expect, it, vi } from "vitest";

describe("getAIContentProvider", () => {
  it("returns mock provider by default", async () => {
    vi.stubEnv("VITE_AI_PROVIDER", undefined);
    const { getAIContentProvider } = await import("../../src/services/ai/index");
    const p = getAIContentProvider();
    const explanation = await p.explainGrammar({ patternId: "default", exampleItemIds: [] });
    expect(explanation.title.length).toBeGreaterThan(0);
  });
});