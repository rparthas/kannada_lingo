use rusqlite::Connection;
use serde::Deserialize;

const BUNDLED_CURRICULUM: &str = include_str!("../../../content/curriculum/beginner-path.json");

#[derive(Debug, Deserialize)]
struct CurriculumBundle {
    content_version: i32,
    course: CourseJson,
    levels: Vec<LevelJson>,
    units: Vec<UnitJson>,
    lessons: Vec<LessonJson>,
    learning_items: Vec<LearningItemJson>,
    lesson_items: Vec<LessonItemJson>,
    exercises: Vec<ExerciseJson>,
}

#[derive(Debug, Deserialize)]
struct CourseJson {
    id: String,
    title: String,
    description: Option<String>,
}

#[derive(Debug, Deserialize)]
struct LevelJson {
    id: String,
    course_id: String,
    ordinal: i32,
    title: String,
    description: Option<String>,
}

#[derive(Debug, Deserialize)]
struct UnitJson {
    id: String,
    level_id: String,
    ordinal: i32,
    title: String,
    description: Option<String>,
}

#[derive(Debug, Deserialize)]
struct LessonJson {
    id: String,
    unit_id: String,
    ordinal: i32,
    title: String,
    description: Option<String>,
    estimated_minutes: Option<i32>,
}

#[derive(Debug, Deserialize)]
struct LearningItemJson {
    id: String,
    kannada_text: String,
    transliteration: String,
    english_meaning: String,
    literal_translation: Option<String>,
    context_note: Option<String>,
    register: Option<String>,
    dialect: Option<String>,
    tags: Option<Vec<String>>,
    difficulty: Option<i32>,
    accepted_answers: Option<Vec<String>>,
    validation_status: Option<String>,
}

#[derive(Debug, Deserialize)]
struct LessonItemJson {
    lesson_id: String,
    learning_item_id: String,
    sort_order: i32,
}

#[derive(Debug, Deserialize)]
struct ExerciseJson {
    id: String,
    lesson_id: String,
    learning_item_id: Option<String>,
    exercise_type: String,
    prompt: serde_json::Value,
    sort_order: i32,
}

pub fn import_bundled(conn: &Connection) -> Result<usize, String> {
    let bundle: CurriculumBundle =
        serde_json::from_str(BUNDLED_CURRICULUM).map_err(|e| format!("invalid bundled JSON: {e}"))?;

    let tx = conn.unchecked_transaction().map_err(|e| e.to_string())?;

    tx.execute(
        "INSERT OR REPLACE INTO courses (id, title, description, content_version) VALUES (?1, ?2, ?3, ?4)",
        (
            &bundle.course.id,
            &bundle.course.title,
            &bundle.course.description,
            bundle.content_version,
        ),
    )
    .map_err(|e| e.to_string())?;

    for level in &bundle.levels {
        tx.execute(
            "INSERT OR REPLACE INTO levels (id, course_id, ordinal, title, description) VALUES (?1, ?2, ?3, ?4, ?5)",
            (
                &level.id,
                &level.course_id,
                level.ordinal,
                &level.title,
                &level.description,
            ),
        )
        .map_err(|e| e.to_string())?;
    }

    for unit in &bundle.units {
        tx.execute(
            "INSERT OR REPLACE INTO units (id, level_id, ordinal, title, description) VALUES (?1, ?2, ?3, ?4, ?5)",
            (
                &unit.id,
                &unit.level_id,
                unit.ordinal,
                &unit.title,
                &unit.description,
            ),
        )
        .map_err(|e| e.to_string())?;
    }

    for lesson in &bundle.lessons {
        tx.execute(
            "INSERT OR REPLACE INTO lessons (id, unit_id, ordinal, title, description, estimated_minutes) VALUES (?1, ?2, ?3, ?4, ?5, ?6)",
            (
                &lesson.id,
                &lesson.unit_id,
                lesson.ordinal,
                &lesson.title,
                &lesson.description,
                lesson.estimated_minutes.unwrap_or(15),
            ),
        )
        .map_err(|e| e.to_string())?;
    }

    let mut item_count = 0usize;
    for item in &bundle.learning_items {
        let tags = item
            .tags
            .as_ref()
            .map(|t| serde_json::to_string(t).unwrap_or_default());
        let accepted = item
            .accepted_answers
            .as_ref()
            .map(|a| serde_json::to_string(a).unwrap_or_default());
        tx.execute(
            "INSERT OR REPLACE INTO learning_items (id, kannada_text, transliteration, english_meaning, literal_translation, context_note, register, dialect, tags, difficulty, accepted_answers, validation_status, content_version) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11, ?12, ?13)",
            (
                &item.id,
                &item.kannada_text,
                &item.transliteration,
                &item.english_meaning,
                &item.literal_translation,
                &item.context_note,
                item.register.as_deref().unwrap_or("informal"),
                item.dialect.as_deref().unwrap_or("bengaluru"),
                &tags,
                item.difficulty.unwrap_or(1),
                &accepted,
                item.validation_status.as_deref().unwrap_or("approved"),
                bundle.content_version,
            ),
        )
        .map_err(|e| e.to_string())?;
        item_count += 1;
    }

    for li in &bundle.lesson_items {
        tx.execute(
            "INSERT OR REPLACE INTO lesson_items (lesson_id, learning_item_id, sort_order) VALUES (?1, ?2, ?3)",
            (&li.lesson_id, &li.learning_item_id, li.sort_order),
        )
        .map_err(|e| e.to_string())?;
    }

    for ex in &bundle.exercises {
        let prompt_json = serde_json::to_string(&ex.prompt).map_err(|e| e.to_string())?;
        tx.execute(
            "INSERT OR REPLACE INTO exercise_definitions (id, lesson_id, learning_item_id, exercise_type, prompt_json, sort_order) VALUES (?1, ?2, ?3, ?4, ?5, ?6)",
            (
                &ex.id,
                &ex.lesson_id,
                &ex.learning_item_id,
                &ex.exercise_type,
                &prompt_json,
                ex.sort_order,
            ),
        )
        .map_err(|e| e.to_string())?;
    }

    let version_id = format!("v{}", bundle.content_version);
    tx.execute(
        "INSERT OR REPLACE INTO content_versions (id, label, item_count) VALUES (?1, ?2, ?3)",
        (&version_id, "beginner-path", item_count as i32),
    )
    .map_err(|e| e.to_string())?;

    tx.commit().map_err(|e| e.to_string())?;
    Ok(item_count)
}