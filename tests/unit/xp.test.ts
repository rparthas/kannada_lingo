import { describe, expect, it } from "vitest";
import { sumXpFromAttempts, xpForExercise } from "../../src/domain/progress/xp";

describe("xpForExercise", () => {
  it("rewards flashcards lightly and conversations more", () => {
    expect(xpForExercise("vocabulary_flashcard", true)).toBe(6);
    expect(xpForExercise("scripted_conversation", true)).toBe(12);
    expect(xpForExercise("english_to_kannada", false)).toBe(4);
  });

  it("sums lesson attempts", () => {
    expect(
      sumXpFromAttempts([
        { exerciseType: "vocabulary_flashcard", isCorrect: true },
        { exerciseType: "english_to_kannada", isCorrect: false },
      ]),
    ).toBe(10);
  });
});