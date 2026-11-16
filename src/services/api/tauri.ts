import { invoke } from "@tauri-apps/api/core";

export interface HomeSummary {
  streakDays: number;
  todayXp: number;
  dailyGoalXp: number;
  dueReviews: number;
  continueLessonId?: string;
  continueLessonTitle?: string;
}

export interface LevelSummary {
  id: string;
  ordinal: number;
  title: string;
  description?: string;
  unitCount: number;
  completedLessons: number;
  totalLessons: number;
}

export interface LessonSummary {
  id: string;
  ordinal: number;
  title: string;
  description?: string;
  estimatedMinutes: number;
  completed: boolean;
}

export interface LearningItemDto {
  id: string;
  kannadaText: string;
  transliteration: string;
  englishMeaning: string;
  literalTranslation?: string;
  contextNote?: string;
  acceptedAnswers: string[];
}

export interface ExerciseDto {
  id: string;
  exerciseType: string;
  learningItemId?: string;
  prompt: Record<string, unknown>;
  learningItem?: LearningItemDto;
}

export interface LessonDetail {
  id: string;
  title: string;
  description?: string;
  exercises: ExerciseDto[];
}

export const tauriApi = {
  initApp: () => invoke<{ contentImported: boolean }>("init_app"),
  getLearnerProfile: () =>
    invoke<{
      displayName?: string;
      dailyGoalXp: number;
      onboardingComplete: boolean;
    }>("get_learner_profile"),
  completeOnboarding: (displayName?: string) =>
    invoke("complete_onboarding", { displayName }),
  getHomeSummary: () => invoke<HomeSummary>("get_home_summary"),
  listLevels: () => invoke<LevelSummary[]>("list_levels"),
  listLessonsForLevel: (levelId: string) =>
    invoke<LessonSummary[]>("list_lessons_for_level", { levelId }),
  getLessonDetail: (lessonId: string) =>
    invoke<LessonDetail>("get_lesson_detail", { lessonId }),
  recordExerciseAttempt: (input: Record<string, unknown>) =>
    invoke("record_exercise_attempt", { input }),
  completeLesson: (lessonId: string, xpEarned: number) =>
    invoke("complete_lesson", { lessonId, xpEarned }),
  getReviewQueue: () => invoke<unknown[]>("get_review_queue"),
  getProgressStats: () => invoke<Record<string, number>>("get_progress_stats"),
  exportLearningBackup: (destPath: string) =>
    invoke("export_learning_backup", { destPath }),
  validateLearningBackup: (path: string) =>
    invoke("validate_learning_backup", { path }),
  restoreLearningBackup: (path: string) =>
    invoke("restore_learning_backup", { path }),
};