export type ExerciseType =
  | "listen_identify"
  | "vocabulary_flashcard"
  | "kannada_to_english"
  | "english_to_kannada"
  | "sentence_construction"
  | "fill_blank"
  | "listen_repeat"
  | "scripted_conversation";

export interface LearningItemRef {
  kannadaText: string;
  transliteration: string;
  englishMeaning: string;
  acceptedAnswers?: string[];
}

export function normalizeFreeText(value: string): string {
  return value.trim().replace(/\s+/g, " ").toLowerCase();
}

/** Learner-friendly transliteration compare (strip combining marks). */
export function normalizeTransliteration(value: string): string {
  return normalizeFreeText(value)
    .normalize("NFD")
    .replace(/\p{M}+/gu, "");
}

export function evaluateExactOrAlternatives(
  answer: string,
  canonical: string,
  alternatives: string[] = [],
): boolean {
  const normalized = normalizeTransliteration(answer);
  const accepted = new Set(
    [canonical, ...alternatives].map((s) => normalizeTransliteration(s)),
  );
  return accepted.has(normalized);
}

export function evaluateWordOrder(
  submitted: string[],
  solution: string[],
): boolean {
  if (submitted.length !== solution.length) return false;
  return submitted.every(
    (word, i) => normalizeFreeText(word) === normalizeFreeText(solution[i] ?? ""),
  );
}

export function evaluateMultipleChoice(
  selectedIndex: number,
  correctIndex: number,
): boolean {
  return selectedIndex === correctIndex;
}

export function evaluateKannadaRecall(
  answer: string,
  item: LearningItemRef,
): boolean {
  return evaluateExactOrAlternatives(answer, item.transliteration, [
    item.kannadaText,
    ...(item.acceptedAnswers ?? []),
  ]);
}

export function evaluateEnglishMeaning(
  answer: string,
  item: LearningItemRef,
): boolean {
  return evaluateExactOrAlternatives(answer, item.englishMeaning, [
    ...(item.acceptedAnswers ?? []),
  ]);
}