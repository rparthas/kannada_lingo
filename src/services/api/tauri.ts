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

export interface LessonResumeState {
  resumeIndex: number;
  lessonCompleted: boolean;
  attempts: { exerciseId: string; exerciseType: string; isCorrect: boolean }[];
}

export interface ItemScheduleState {
  easeFactor: number;
  intervalDays: number;
  repetitions: number;
  masteryStatus: string;
}

export interface ReviewQueueItem {
  learningItemId: string;
  kannadaText: string;
  transliteration: string;
  englishMeaning: string;
  nextReviewAt: string;
  exerciseId?: string;
  exerciseType?: string;
  exercisePrompt?: Record<string, unknown>;
  acceptedAnswers: string[];
}

export interface BackupManifest {
  backupFormatVersion: string;
  databaseSchemaVersion: number;
  applicationVersion: string;
  exportTimestamp: string;
  backupId: string;
  contentVersion: number;
  databaseChecksumSha256: string;
}

export interface BackupExportResult {
  path: string;
  manifest: BackupManifest;
}

export interface AudioAssetDto {
  id: string;
  learningItemId: string;
  source: string;
  speakingSpeed: string;
  relativePath?: string;
  durationMs?: number;
}

export interface LearningItemDetail {
  id: string;
  kannadaText: string;
  transliteration: string;
  englishMeaning: string;
  literalTranslation?: string;
  contextNote?: string;
  acceptedAnswers: string[];
  progress?: ItemScheduleState;
  nextReviewAt?: string;
  attemptCount: number;
  correctCount: number;
  recentAttempts: {
    exerciseType: string;
    isCorrect: boolean;
    attemptedAt: string;
  }[];
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
  updateLearnerProfile: (dailyGoalXp?: number) =>
    invoke("update_learner_profile", { dailyGoalXp }),
  getHomeSummary: () => invoke<HomeSummary>("get_home_summary"),
  listLevels: () => invoke<LevelSummary[]>("list_levels"),
  listLessonsForLevel: (levelId: string) =>
    invoke<LessonSummary[]>("list_lessons_for_level", { levelId }),
  getLessonDetail: (lessonId: string) =>
    invoke<LessonDetail>("get_lesson_detail", { lessonId }),
  prepareLesson: (lessonId: string) =>
    invoke<LessonResumeState>("prepare_lesson", { lessonId }),
  getItemScheduleState: (learningItemId: string) =>
    invoke<ItemScheduleState>("get_item_schedule_state", { learningItemId }),
  getLearningItemDetail: (learningItemId: string) =>
    invoke<LearningItemDetail>("get_learning_item_detail", { learningItemId }),
  listAudioAssets: (learningItemId: string) =>
    invoke<AudioAssetDto[]>("list_audio_assets", { learningItemId }),
  recordExerciseAttempt: (input: Record<string, unknown>) =>
    invoke("record_exercise_attempt", { input }),
  completeLesson: (lessonId: string, xpEarned: number) =>
    invoke("complete_lesson", { lessonId, xpEarned }),
  getReviewQueue: () => invoke<ReviewQueueItem[]>("get_review_queue"),
  getProgressStats: () => invoke<Record<string, number>>("get_progress_stats"),
  exportLearningBackup: (destPath: string) =>
    invoke<BackupExportResult>("export_learning_backup", { destPath }),
  validateLearningBackup: (path: string) =>
    invoke<BackupManifest>("validate_learning_backup", { path }),
  restoreLearningBackup: (path: string) =>
    invoke<BackupManifest>("restore_learning_backup", { path }),
};