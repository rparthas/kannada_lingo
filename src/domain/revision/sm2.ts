export type ReviewGrade = 0 | 1 | 2 | 3 | 4 | 5;

export interface Sm2State {
  easeFactor: number;
  intervalDays: number;
  repetitions: number;
}

export interface Sm2ScheduleResult extends Sm2State {
  nextIntervalDays: number;
  masteryStatus: "new" | "learning" | "reviewing" | "mastered";
}

const MIN_EASE = 1.3;

/** SM-2-inspired scheduler (deterministic, UI-agnostic). */
export function scheduleReview(
  state: Sm2State,
  grade: ReviewGrade,
): Sm2ScheduleResult {
  let { easeFactor, intervalDays, repetitions } = state;

  if (grade < 3) {
    repetitions = 0;
    intervalDays = grade === 0 ? 0 : 1;
    easeFactor = Math.max(MIN_EASE, easeFactor - 0.2);
    return {
      easeFactor,
      intervalDays,
      repetitions,
      nextIntervalDays: intervalDays,
      masteryStatus: "learning",
    };
  }

  easeFactor = Math.max(
    MIN_EASE,
    easeFactor + (0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02)),
  );

  if (repetitions === 0) {
    intervalDays = 1;
  } else if (repetitions === 1) {
    intervalDays = 3;
  } else {
    intervalDays = Math.max(1, Math.round(intervalDays * easeFactor));
  }
  repetitions += 1;

  const masteryStatus =
    repetitions >= 5 && intervalDays >= 14 ? "mastered" : "reviewing";

  return {
    easeFactor,
    intervalDays,
    repetitions,
    nextIntervalDays: intervalDays,
    masteryStatus,
  };
}

export function gradeFromAttempt(options: {
  isCorrect: boolean;
  selfAssessedConfident?: boolean;
  wasDifficult?: boolean;
}): ReviewGrade {
  if (!options.isCorrect) return options.wasDifficult ? 1 : 0;
  if (options.selfAssessedConfident) return 5;
  if (options.wasDifficult) return 3;
  return 4;
}