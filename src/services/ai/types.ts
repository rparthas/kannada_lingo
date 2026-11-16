export interface PhraseVariationInput {
  learningItemId: string;
  scenarioTag: string;
  approvedVocabularyIds: string[];
}

export interface PhraseVariationResult {
  drafts: Array<{
    kannadaText: string;
    transliteration: string;
    englishMeaning: string;
    validationStatus: "draft";
  }>;
}

export interface ExerciseGenerationInput {
  learningItemIds: string[];
  exerciseTypes: string[];
}

export interface ExerciseCandidate {
  exerciseType: string;
  prompt: Record<string, unknown>;
}

export interface GrammarExplanationInput {
  patternId: string;
  exampleItemIds: string[];
}

export interface GrammarExplanation {
  title: string;
  explanationEn: string;
}

/** Provider-independent AI boundary (no secrets in the client bundle). */
export interface AIContentProvider {
  generatePhraseVariations(
    input: PhraseVariationInput,
  ): Promise<PhraseVariationResult>;
  generateExercises(input: ExerciseGenerationInput): Promise<ExerciseCandidate[]>;
  explainGrammar(input: GrammarExplanationInput): Promise<GrammarExplanation>;
}

export class UnconfiguredAIProvider implements AIContentProvider {
  async generatePhraseVariations(): Promise<PhraseVariationResult> {
    throw new Error("AI provider is not configured for this build.");
  }
  async generateExercises(): Promise<ExerciseCandidate[]> {
    throw new Error("AI provider is not configured for this build.");
  }
  async explainGrammar(): Promise<GrammarExplanation> {
    throw new Error("AI provider is not configured for this build.");
  }
}