export interface ValidationIssue {
  code: string;
  message: string;
  path?: string;
}

export interface CurriculumBundleLike {
  content_version?: number;
  learning_items?: {
    id: string;
    kannada_text?: string;
    transliteration?: string;
    english_meaning?: string;
    validation_status?: string;
  }[];
  lessons?: { id: string }[];
  exercises?: {
    id: string;
    lesson_id: string;
    learning_item_id?: string;
    exercise_type: string;
  }[];
  lesson_items?: { lesson_id: string; learning_item_id: string }[];
  audio_assets?: {
    id: string;
    learning_item_id: string;
    source: string;
    speaking_speed?: string;
    relative_path?: string;
    review_status?: string;
  }[];
}

function duplicateIds(ids: string[], label: string): ValidationIssue[] {
  const seen = new Set<string>();
  const issues: ValidationIssue[] = [];
  for (const id of ids) {
    if (seen.has(id)) {
      issues.push({
        code: "duplicate_id",
        message: `Duplicate ${label} id: ${id}`,
        path: id,
      });
    }
    seen.add(id);
  }
  return issues;
}

export function validateCurriculumBundle(
  bundle: CurriculumBundleLike,
): ValidationIssue[] {
  const issues: ValidationIssue[] = [];
  const items = bundle.learning_items ?? [];
  const exercises = bundle.exercises ?? [];
  const lessons = bundle.lessons ?? [];
  const lessonItems = bundle.lesson_items ?? [];
  const audio = bundle.audio_assets ?? [];

  issues.push(...duplicateIds(items.map((i) => i.id), "learning_item"));
  issues.push(...duplicateIds(exercises.map((e) => e.id), "exercise"));
  issues.push(...duplicateIds(lessons.map((l) => l.id), "lesson"));
  issues.push(...duplicateIds(audio.map((a) => a.id), "audio_asset"));

  const itemIds = new Set(items.map((i) => i.id));
  const lessonIds = new Set(lessons.map((l) => l.id));

  for (const item of items) {
    if (!item.kannada_text?.trim()) {
      issues.push({
        code: "missing_kannada",
        message: `Missing kannada_text for ${item.id}`,
        path: item.id,
      });
    }
    if (!item.transliteration?.trim()) {
      issues.push({
        code: "missing_transliteration",
        message: `Missing transliteration for ${item.id}`,
        path: item.id,
      });
    }
    if (!item.english_meaning?.trim()) {
      issues.push({
        code: "missing_english",
        message: `Missing english_meaning for ${item.id}`,
        path: item.id,
      });
    }
  }

  const approvedIds = items
    .filter((i) => (i.validation_status ?? "approved") === "approved")
    .map((i) => i.id);

  const humanNormal = new Set(
    audio
      .filter(
        (a) =>
          (a.source === "human" || a.source === "tts") &&
          (a.speaking_speed ?? "normal") === "normal" &&
          (a.review_status ?? "approved") === "approved",
      )
      .map((a) => a.learning_item_id),
  );

  for (const id of approvedIds) {
    if (!humanNormal.has(id)) {
      issues.push({
        code: "missing_human_audio",
        message: `Approved item ${id} has no human normal-speed audio`,
        path: id,
      });
    }
  }

  for (const asset of audio) {
    if (!itemIds.has(asset.learning_item_id)) {
      issues.push({
        code: "orphan_audio",
        message: `Audio ${asset.id} references unknown learning item`,
        path: asset.id,
      });
    }
    if (!asset.relative_path?.trim()) {
      issues.push({
        code: "missing_audio_path",
        message: `Audio ${asset.id} has no relative_path`,
        path: asset.id,
      });
    }
  }

  for (const ex of exercises) {
    if (!lessonIds.has(ex.lesson_id)) {
      issues.push({
        code: "orphan_exercise",
        message: `Exercise ${ex.id} references unknown lesson ${ex.lesson_id}`,
        path: ex.id,
      });
    }
    if (
      ex.learning_item_id &&
      !itemIds.has(ex.learning_item_id) &&
      ex.exercise_type !== "scripted_conversation"
    ) {
      issues.push({
        code: "orphan_exercise_item",
        message: `Exercise ${ex.id} references unknown learning item`,
        path: ex.id,
      });
    }
  }

  for (const li of lessonItems) {
    if (!lessonIds.has(li.lesson_id)) {
      issues.push({
        code: "orphan_lesson_item",
        message: `Lesson link references unknown lesson ${li.lesson_id}`,
      });
    }
    if (!itemIds.has(li.learning_item_id)) {
      issues.push({
        code: "orphan_lesson_item",
        message: `Lesson link references unknown item ${li.learning_item_id}`,
      });
    }
  }

  return issues;
}