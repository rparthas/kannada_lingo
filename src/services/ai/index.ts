import { MockAIContentProvider } from "./mockProvider";
import type { AIContentProvider } from "./types";
import { UnconfiguredAIProvider } from "./types";

export type AIProviderMode = "mock" | "unconfigured";

const configuredMode: AIProviderMode =
  import.meta.env.VITE_AI_PROVIDER === "unconfigured" ? "unconfigured" : "mock";

let cached: AIContentProvider | null = null;

/** Returns the configured AI boundary for this build (mock by default). */
export function getAIContentProvider(): AIContentProvider {
  if (cached) return cached;
  cached =
    configuredMode === "mock"
      ? new MockAIContentProvider()
      : new UnconfiguredAIProvider();
  return cached;
}

export * from "./types";