import type {
  AIContentProvider,
  ExerciseCandidate,
  ExerciseGenerationInput,
  GrammarExplanation,
  GrammarExplanationInput,
  PhraseVariationInput,
  PhraseVariationResult,
} from "./types";

const GRAMMAR_NOTES: Record<string, GrammarExplanation> = {
  "pattern-sari": {
    title: "Using sari (ಸರಿ)",
    explanationEn:
      "ಸರಿ (sari) is a high-frequency affirmative in Kannada — similar to “okay”, “right”, or “that works”. " +
      "It often closes a short exchange when you accept what was said. Tone is friendly and neutral, not formal.",
  },
  default: {
    title: "Kannada phrase pattern",
    explanationEn:
      "Focus on the chunk as a whole first, then break it into syllables. " +
      "Kannada verb endings and postpositions change meaning subtly — reuse this phrase in the same situation until it feels automatic.",
  },
};

/** Local mock provider for dev/desktop builds — no network or API keys. */
export class MockAIContentProvider implements AIContentProvider {
  async generatePhraseVariations(
    _input: PhraseVariationInput,
  ): Promise<PhraseVariationResult> {
    const drafts: PhraseVariationResult["drafts"] = [
      {
        kannadaText: "ಹೌದು, ಸರಿ",
        transliteration: "haudu, sari",
        englishMeaning: "Yes, okay",
        validationStatus: "draft",
      },
      {
        kannadaText: "ಸರಿ, ಮುಂದುವರಿಸೋಣ",
        transliteration: "sari, munduvarisona",
        englishMeaning: "Okay, let's continue",
        validationStatus: "draft",
      },
    ];
    return { drafts };
  }

  async generateExercises(
    input: ExerciseGenerationInput,
  ): Promise<ExerciseCandidate[]> {
    return input.learningItemIds.slice(0, 2).map((id) => ({
      exerciseType: input.exerciseTypes[0] ?? "english_to_kannada",
      prompt: {
        learningItemId: id,
        hint: "Supplementary recall (mock AI)",
      },
    }));
  }

  async explainGrammar(input: GrammarExplanationInput): Promise<GrammarExplanation> {
    return GRAMMAR_NOTES[input.patternId] ?? GRAMMAR_NOTES.default;
  }
}