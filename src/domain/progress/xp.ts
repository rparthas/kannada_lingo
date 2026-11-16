import type { ExerciseType } from "../exercises/evaluate";

/** XP earned per exercise completion (distinct from mastery). */
export function xpForExercise(
  exerciseType: ExerciseType | string,
  isCorrect: boolean,
): number {
  if (exerciseType === "vocabulary_flashcard") return 6;
  if (exerciseType === "listen_repeat") return isCorrect ? 8 : 5;
  if (exerciseType === "scripted_conversation") return isCorrect ? 12 : 6;
  return isCorrect ? 10 : 4;
}

export function sumXpFromAttempts(
  attempts: { exerciseType: string; isCorrect: boolean }[],
): number {
  return attempts.reduce(
    (total, a) => total + xpForExercise(a.exerciseType, a.isCorrect),
    0,
  );
}