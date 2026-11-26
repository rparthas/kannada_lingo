use crate::db::DbState;
use serde::Serialize;
use tauri::State;

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
pub struct HomeSummary {
    pub streak_days: i32,
    pub today_xp: i32,
    pub daily_goal_xp: i32,
    pub due_reviews: i32,
    pub continue_lesson_id: Option<String>,
    pub continue_lesson_title: Option<String>,
}

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
pub struct LevelSummary {
    pub id: String,
    pub ordinal: i32,
    pub title: String,
    pub description: Option<String>,
    pub unit_count: i32,
    pub completed_lessons: i32,
    pub total_lessons: i32,
}

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
pub struct LessonSummary {
    pub id: String,
    pub ordinal: i32,
    pub title: String,
    pub description: Option<String>,
    pub estimated_minutes: i32,
    pub completed: bool,
    pub unit_id: String,
    pub unit_title: String,
}

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
pub struct LearningItemDto {
    pub id: String,
    pub kannada_text: String,
    pub transliteration: String,
    pub english_meaning: String,
    pub literal_translation: Option<String>,
    pub context_note: Option<String>,
    pub accepted_answers: Vec<String>,
}

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
pub struct ExerciseDto {
    pub id: String,
    pub exercise_type: String,
    pub learning_item_id: Option<String>,
    pub prompt: serde_json::Value,
    pub learning_item: Option<LearningItemDto>,
}

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
pub struct LessonDetail {
    pub id: String,
    pub title: String,
    pub description: Option<String>,
    pub exercises: Vec<ExerciseDto>,
}

/// Consecutive calendar days with daily XP goal met, ending today if met or yesterday otherwise.
fn consecutive_goal_streak(conn: &rusqlite::Connection) -> Result<i32, String> {
    let today_met: i32 = conn
        .query_row(
            "SELECT COALESCE(goal_met, 0) FROM daily_activity WHERE activity_date = date('now', 'localtime')",
            [],
            |row| row.get(0),
        )
        .unwrap_or(0);
    let mut offset = if today_met == 1 { 0 } else { 1 };
    let mut streak = 0i32;
    loop {
        let met: i32 = conn
            .query_row(
                "SELECT COALESCE(goal_met, 0) FROM daily_activity
                 WHERE activity_date = date('now', '-' || ?1 || ' days', 'localtime')",
                [offset],
                |row| row.get(0),
            )
            .unwrap_or(0);
        if met == 0 {
            break;
        }
        streak += 1;
        offset += 1;
        if offset > 400 {
            break;
        }
    }
    Ok(streak)
}

fn parse_accepted_answers(raw: Option<String>) -> Vec<String> {
    raw.and_then(|s| serde_json::from_str(&s).ok()).unwrap_or_default()
}

fn learning_item_from_row(
    row: &rusqlite::Row<'_>,
    offset: usize,
) -> Result<LearningItemDto, rusqlite::Error> {
    Ok(LearningItemDto {
        id: row.get(offset)?,
        kannada_text: row.get(offset + 1)?,
        transliteration: row.get(offset + 2)?,
        english_meaning: row.get(offset + 3)?,
        literal_translation: row.get(offset + 4)?,
        context_note: row.get(offset + 5)?,
        accepted_answers: parse_accepted_answers(row.get(offset + 6)?),
    })
}

#[tauri::command]
pub fn get_home_summary(state: State<DbState>) -> Result<HomeSummary, String> {
    crate::db::with_conn(&state, |conn| {
        let daily_goal: i32 = conn
            .query_row(
                "SELECT daily_goal_xp FROM learner_profile WHERE id = 'default'",
                [],
                |row| row.get(0),
            )
            .unwrap_or(50);

        let today_xp: i32 = conn
            .query_row(
                "SELECT COALESCE(xp_earned, 0) FROM daily_activity WHERE activity_date = date('now', 'localtime')",
                [],
                |row| row.get(0),
            )
            .unwrap_or(0);

        let due_reviews: i32 = conn
            .query_row(
                "SELECT COUNT(*) FROM review_schedule WHERE next_review_at <= datetime('now', 'localtime')",
                [],
                |row| row.get(0),
            )
            .unwrap_or(0);

        let streak_days = consecutive_goal_streak(conn)?;

        let in_progress = conn
            .query_row(
                "SELECT l.id, l.title FROM lesson_attempts la
                 JOIN lessons l ON l.id = la.lesson_id
                 WHERE la.completed_at IS NULL
                 ORDER BY la.started_at DESC LIMIT 1",
                [],
                |row| Ok((row.get::<_, String>(0)?, row.get::<_, String>(1)?)),
            )
            .ok();

        let next_lesson = in_progress.or_else(|| {
            conn.query_row(
                "SELECT l.id, l.title FROM lessons l
                 LEFT JOIN lesson_attempts la ON la.lesson_id = l.id AND la.completed_at IS NOT NULL
                 WHERE la.id IS NULL
                 ORDER BY l.ordinal LIMIT 1",
                [],
                |row| Ok((row.get::<_, String>(0)?, row.get::<_, String>(1)?)),
            )
            .ok()
        });

        Ok(HomeSummary {
            streak_days,
            today_xp,
            daily_goal_xp: daily_goal,
            due_reviews,
            continue_lesson_id: next_lesson.as_ref().map(|(id, _)| id.clone()),
            continue_lesson_title: next_lesson.map(|(_, t)| t),
        })
    })
}

#[tauri::command]
pub fn list_levels(state: State<DbState>) -> Result<Vec<LevelSummary>, String> {
    crate::db::with_conn(&state, |conn| {
        let mut stmt = conn
            .prepare(
                "SELECT lv.id, lv.ordinal, lv.title, lv.description,
                        (SELECT COUNT(*) FROM units u WHERE u.level_id = lv.id) AS unit_count,
                        (SELECT COUNT(*) FROM lessons l
                           JOIN units u ON u.id = l.unit_id
                           WHERE u.level_id = lv.id) AS total_lessons,
                        (SELECT COUNT(*) FROM lesson_attempts la
                           JOIN lessons l ON l.id = la.lesson_id
                           JOIN units u ON u.id = l.unit_id
                           WHERE u.level_id = lv.id AND la.completed_at IS NOT NULL) AS completed_lessons
                 FROM levels lv ORDER BY lv.ordinal",
            )
            .map_err(|e| e.to_string())?;

        let rows = stmt
            .query_map([], |row| {
                Ok(LevelSummary {
                    id: row.get(0)?,
                    ordinal: row.get(1)?,
                    title: row.get(2)?,
                    description: row.get(3)?,
                    unit_count: row.get(4)?,
                    completed_lessons: row.get(6)?,
                    total_lessons: row.get(5)?,
                })
            })
            .map_err(|e| e.to_string())?;

        rows.collect::<Result<Vec<_>, _>>().map_err(|e| e.to_string())
    })
}

#[tauri::command]
pub fn list_lessons_for_level(
    state: State<DbState>,
    level_id: String,
) -> Result<Vec<LessonSummary>, String> {
    crate::db::with_conn(&state, |conn| {
        let mut stmt = conn
            .prepare(
                "SELECT l.id, l.ordinal, l.title, l.description, l.estimated_minutes,
                        CASE WHEN EXISTS (
                          SELECT 1 FROM lesson_attempts la WHERE la.lesson_id = l.id AND la.completed_at IS NOT NULL
                        ) THEN 1 ELSE 0 END AS completed,
                        u.id AS unit_id,
                        u.title AS unit_title
                 FROM lessons l
                 JOIN units u ON u.id = l.unit_id
                 WHERE u.level_id = ?1
                 ORDER BY u.ordinal, l.ordinal",
            )
            .map_err(|e| e.to_string())?;

        let rows = stmt
            .query_map([&level_id], |row| {
                Ok(LessonSummary {
                    id: row.get(0)?,
                    ordinal: row.get(1)?,
                    title: row.get(2)?,
                    description: row.get(3)?,
                    estimated_minutes: row.get(4)?,
                    completed: row.get::<_, i32>(5)? == 1,
                    unit_id: row.get(6)?,
                    unit_title: row.get(7)?,
                })
            })
            .map_err(|e| e.to_string())?;

        rows.collect::<Result<Vec<_>, _>>().map_err(|e| e.to_string())
    })
}

#[tauri::command]
pub fn get_lesson_detail(state: State<DbState>, lesson_id: String) -> Result<LessonDetail, String> {
    crate::db::with_conn(&state, |conn| {
        let (title, description): (String, Option<String>) = conn
            .query_row(
                "SELECT title, description FROM lessons WHERE id = ?1",
                [&lesson_id],
                |row| Ok((row.get(0)?, row.get(1)?)),
            )
            .map_err(|e| e.to_string())?;

        let mut stmt = conn
            .prepare(
                "SELECT e.id, e.exercise_type, e.learning_item_id, e.prompt_json,
                        li.id, li.kannada_text, li.transliteration, li.english_meaning,
                        li.literal_translation, li.context_note, li.accepted_answers
                 FROM exercise_definitions e
                 LEFT JOIN learning_items li ON li.id = e.learning_item_id
                 WHERE e.lesson_id = ?1
                 ORDER BY e.sort_order",
            )
            .map_err(|e| e.to_string())?;

        let exercises = stmt
            .query_map([&lesson_id], |row| {
                let prompt: serde_json::Value =
                    serde_json::from_str(row.get::<_, String>(3)?.as_str()).unwrap_or_default();
                let learning_item = if row.get::<_, Option<String>>(4)?.is_some() {
                    Some(learning_item_from_row(row, 4)?)
                } else {
                    None
                };
                Ok(ExerciseDto {
                    id: row.get(0)?,
                    exercise_type: row.get(1)?,
                    learning_item_id: row.get(2)?,
                    prompt,
                    learning_item,
                })
            })
            .map_err(|e| e.to_string())?
            .collect::<Result<Vec<_>, _>>()
            .map_err(|e| e.to_string())?;

        Ok(LessonDetail {
            id: lesson_id,
            title,
            description,
            exercises,
        })
    })
}