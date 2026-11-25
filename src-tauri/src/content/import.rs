use rusqlite::Connection;
use serde::Deserialize;

const BUNDLED_CURRICULUM: &str = include_str!("../../../content/curriculum/beginner-path.json");

pub fn bundled_curriculum_json() -> &'static str {
    BUNDLED_CURRICULUM
}

pub fn bundled_content_version() -> i32 {
    bundle_content_version(BUNDLED_CURRICULUM)
}

pub fn bundle_content_version(json: &str) -> i32 {
    serde_json::from_str::<serde_json::Value>(json)
        .ok()
        .and_then(|v| v.get("content_version").and_then(|c| c.as_i64()))
        .unwrap_or(1) as i32
}

pub fn installed_content_version(conn: &Connection) -> i32 {
    conn.query_row(
        "SELECT COALESCE(MAX(content_version), 0) FROM courses",
        [],
        |row| row.get(0),
    )
    .unwrap_or(0)
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ContentImportOutcome {
    NoChange {
        stored_version: i32,
        incoming_version: i32,
    },
    Imported {
        items: usize,
        content_version: i32,
    },
}

pub fn import_if_newer(conn: &Connection, json: &str) -> Result<ContentImportOutcome, String> {
    let incoming = bundle_content_version(json);
    let stored = installed_content_version(conn);
    let empty = conn
        .query_row("SELECT COUNT(*) FROM learning_items", [], |row| row.get::<_, i64>(0))
        .unwrap_or(0)
        == 0;
    if !empty && incoming <= stored {
        return Ok(ContentImportOutcome::NoChange {
            stored_version: stored,
            incoming_version: incoming,
        });
    }
    let items = import_bundle(conn, json)?;
    Ok(ContentImportOutcome::Imported {
        items,
        content_version: incoming,
    })
}

#[derive(Debug, Deserialize)]
struct CurriculumBundle {
    content_version: i32,
    course: CourseJson,
    levels: Vec<LevelJson>,
    units: Vec<UnitJson>,
    lessons: Vec<LessonJson>,
    learning_items: Vec<LearningItemJson>,
    audio_assets: Option<Vec<AudioAssetJson>>,
    lesson_items: Vec<LessonItemJson>,
    exercises: Vec<ExerciseJson>,
}

#[derive(Debug, Deserialize)]
struct AudioAssetJson {
    id: String,
    learning_item_id: String,
    source: String,
    speaking_speed: Option<String>,
    review_status: Option<String>,
    duration_ms: Option<i32>,
    file_format: Option<String>,
    relative_path: Option<String>,
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
    import_bundle(conn, BUNDLED_CURRICULUM)
}

pub fn import_bundle(conn: &Connection, json: &str) -> Result<usize, String> {
    let bundle: CurriculumBundle =
        serde_json::from_str(json).map_err(|e| format!("invalid curriculum JSON: {e}"))?;

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

    if let Some(assets) = &bundle.audio_assets {
        for asset in assets {
            tx.execute(
                "INSERT OR REPLACE INTO audio_assets (id, learning_item_id, locale, source, speaking_speed, review_status, duration_ms, file_format, relative_path, content_version)
                 VALUES (?1, ?2, 'kn-IN', ?3, ?4, ?5, ?6, ?7, ?8, ?9)",
                (
                    &asset.id,
                    &asset.learning_item_id,
                    &asset.source,
                    asset.speaking_speed.as_deref().unwrap_or("normal"),
                    asset.review_status.as_deref().unwrap_or("approved"),
                    asset.duration_ms,
                    &asset.file_format,
                    &asset.relative_path,
                    bundle.content_version,
                ),
            )
            .map_err(|e| e.to_string())?;
        }
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

#[cfg(test)]
mod tests {
    use super::*;
    use crate::db::migrations;
    use rusqlite::Connection;

    const FIXTURE_V1: &str = r#"{
      "content_version": 1,
      "course": { "id": "course-test", "title": "Test", "description": null },
      "levels": [{ "id": "level-test", "course_id": "course-test", "ordinal": 1, "title": "L1", "description": null }],
      "units": [{ "id": "unit-test", "level_id": "level-test", "ordinal": 1, "title": "U1", "description": null }],
      "lessons": [{
        "id": "lesson-test-1", "unit_id": "unit-test", "ordinal": 1,
        "title": "Lesson 1", "description": null, "estimated_minutes": 10
      }],
      "learning_items": [{
        "id": "item-alpha", "kannada_text": "ಆ", "transliteration": "aa",
        "english_meaning": "Alpha"
      }],
      "audio_assets": [],
      "lesson_items": [{ "lesson_id": "lesson-test-1", "learning_item_id": "item-alpha", "sort_order": 1 }],
      "exercises": [{
        "id": "ex-alpha", "lesson_id": "lesson-test-1", "learning_item_id": "item-alpha",
        "exercise_type": "vocabulary_flashcard", "prompt": {}, "sort_order": 1
      }]
    }"#;

    const FIXTURE_V2: &str = r#"{
      "content_version": 2,
      "course": { "id": "course-test", "title": "Test", "description": null },
      "levels": [{ "id": "level-test", "course_id": "course-test", "ordinal": 1, "title": "L1", "description": null }],
      "units": [{ "id": "unit-test", "level_id": "level-test", "ordinal": 1, "title": "U1", "description": null }],
      "lessons": [
        {
          "id": "lesson-test-1", "unit_id": "unit-test", "ordinal": 1,
          "title": "Lesson 1", "description": null, "estimated_minutes": 10
        },
        {
          "id": "lesson-test-2", "unit_id": "unit-test", "ordinal": 2,
          "title": "Lesson 2", "description": null, "estimated_minutes": 10
        }
      ],
      "learning_items": [
        {
          "id": "item-alpha", "kannada_text": "ಆ", "transliteration": "aa",
          "english_meaning": "Alpha"
        },
        {
          "id": "item-beta", "kannada_text": "ಬ", "transliteration": "ba",
          "english_meaning": "Beta"
        }
      ],
      "audio_assets": [],
      "lesson_items": [
        { "lesson_id": "lesson-test-1", "learning_item_id": "item-alpha", "sort_order": 1 },
        { "lesson_id": "lesson-test-2", "learning_item_id": "item-beta", "sort_order": 1 }
      ],
      "exercises": [
        {
          "id": "ex-alpha", "lesson_id": "lesson-test-1", "learning_item_id": "item-alpha",
          "exercise_type": "vocabulary_flashcard", "prompt": {}, "sort_order": 1
        },
        {
          "id": "ex-beta", "lesson_id": "lesson-test-2", "learning_item_id": "item-beta",
          "exercise_type": "vocabulary_flashcard", "prompt": {}, "sort_order": 1
        }
      ]
    }"#;

    fn fresh_db() -> Connection {
        let conn = Connection::open_in_memory().unwrap();
        conn.execute_batch("PRAGMA foreign_keys = ON;").unwrap();
        migrations::run(&conn).unwrap();
        conn
    }

    #[test]
    fn import_on_nonempty_db_adds_lesson_without_deleting_attempts() {
        let conn = fresh_db();
        import_bundle(&conn, FIXTURE_V1).expect("v1 import");
        conn.execute(
            "INSERT INTO exercise_attempts (id, exercise_id, learning_item_id, is_correct, response_json)
             VALUES ('att-1', 'ex-alpha', 'item-alpha', 1, '{}')",
            [],
        )
        .unwrap();

        let outcome = import_if_newer(&conn, FIXTURE_V2).expect("v2 import");
        assert_eq!(
            outcome,
            ContentImportOutcome::Imported {
                items: 2,
                content_version: 2,
            }
        );

        let attempts: i64 = conn
            .query_row("SELECT COUNT(*) FROM exercise_attempts", [], |r| r.get(0))
            .unwrap();
        assert_eq!(attempts, 1);

        let lessons: i64 = conn
            .query_row("SELECT COUNT(*) FROM lessons", [], |r| r.get(0))
            .unwrap();
        assert_eq!(lessons, 2);
    }

    #[test]
    fn import_if_newer_noops_when_incoming_not_newer() {
        let conn = fresh_db();
        import_bundle(&conn, FIXTURE_V1).unwrap();
        let outcome = import_if_newer(&conn, FIXTURE_V1).unwrap();
        assert_eq!(
            outcome,
            ContentImportOutcome::NoChange {
                stored_version: 1,
                incoming_version: 1,
            }
        );
    }

    #[test]
    fn bundled_import_includes_audio_assets() {
        let conn = Connection::open_in_memory().unwrap();
        conn.execute_batch("PRAGMA foreign_keys = ON;")
            .unwrap();
        migrations::run(&conn).unwrap();
        import_bundled(&conn).expect("import");
        let audio_count: i64 = conn
            .query_row("SELECT COUNT(*) FROM audio_assets", [], |r| r.get(0))
            .unwrap();
        let item_count: i64 = conn
            .query_row("SELECT COUNT(*) FROM learning_items", [], |r| r.get(0))
            .unwrap();
        assert!(audio_count >= item_count * 2);
        let voiced_normal: i64 = conn
            .query_row(
                "SELECT COUNT(DISTINCT learning_item_id) FROM audio_assets
                 WHERE source IN ('human', 'tts') AND speaking_speed = 'normal'",
                [],
                |r| r.get(0),
            )
            .unwrap();
        assert_eq!(voiced_normal, item_count);
    }
}