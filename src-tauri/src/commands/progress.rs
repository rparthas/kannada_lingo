use crate::db::DbState;
use serde::{Deserialize, Serialize};
use tauri::State;
use uuid::Uuid;

#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct RecordAttemptInput {
    pub exercise_id: String,
    pub learning_item_id: Option<String>,
    pub is_correct: bool,
    pub response_json: serde_json::Value,
    pub self_assessed: Option<bool>,
    pub xp_amount: i32,
    pub lesson_id: Option<String>,
    pub ease_factor: f64,
    pub interval_days: i32,
    pub repetitions: i32,
    pub mastery_status: String,
}

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
pub struct LessonAttemptSnapshot {
    pub exercise_id: String,
    pub exercise_type: String,
    pub is_correct: bool,
}

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
pub struct LessonResumeState {
    pub resume_index: i32,
    pub lesson_completed: bool,
    pub attempts: Vec<LessonAttemptSnapshot>,
}

#[derive(Clone, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct ItemScheduleState {
    pub ease_factor: f64,
    pub interval_days: i32,
    pub repetitions: i32,
    pub mastery_status: String,
}

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
pub struct AttemptHistoryRow {
    pub exercise_type: String,
    pub is_correct: bool,
    pub attempted_at: String,
}

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
pub struct LearningItemDetail {
    pub id: String,
    pub kannada_text: String,
    pub transliteration: String,
    pub english_meaning: String,
    pub literal_translation: Option<String>,
    pub context_note: Option<String>,
    pub accepted_answers: Vec<String>,
    pub progress: Option<ItemScheduleState>,
    pub next_review_at: Option<String>,
    pub attempt_count: i32,
    pub correct_count: i32,
    pub recent_attempts: Vec<AttemptHistoryRow>,
}

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
pub struct ReviewQueueItem {
    pub learning_item_id: String,
    pub kannada_text: String,
    pub transliteration: String,
    pub english_meaning: String,
    pub next_review_at: String,
    pub exercise_id: Option<String>,
    pub exercise_type: Option<String>,
    pub exercise_prompt: Option<serde_json::Value>,
    pub accepted_answers: Vec<String>,
}

#[tauri::command]
pub fn record_exercise_attempt(
    state: State<DbState>,
    input: RecordAttemptInput,
) -> Result<(), String> {
    crate::db::with_conn(&state, |conn| {
        let attempt_id = Uuid::new_v4().to_string();
        let response_json = serde_json::to_string(&input.response_json).map_err(|e| e.to_string())?;

        conn.execute(
            "INSERT INTO exercise_attempts (id, exercise_id, learning_item_id, is_correct, response_json, self_assessed)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6)",
            (
                &attempt_id,
                &input.exercise_id,
                &input.learning_item_id,
                if input.is_correct { 1 } else { 0 },
                &response_json,
                input.self_assessed.map(|v| if v { 1 } else { 0 }),
            ),
        )
        .map_err(|e| e.to_string())?;

        if input.xp_amount != 0 {
            let xp_id = Uuid::new_v4().to_string();
            conn.execute(
                "INSERT INTO xp_transactions (id, amount, reason) VALUES (?1, ?2, 'exercise')",
                (&xp_id, input.xp_amount),
            )
            .map_err(|e| e.to_string())?;

            conn.execute(
                "INSERT INTO daily_activity (activity_date, xp_earned, exercises_completed, goal_met)
                 VALUES (date('now', 'localtime'), ?1, 1,
                   CASE WHEN ?1 >= (SELECT daily_goal_xp FROM learner_profile WHERE id = 'default') THEN 1 ELSE 0 END)
                 ON CONFLICT(activity_date) DO UPDATE SET
                   xp_earned = xp_earned + excluded.xp_earned,
                   exercises_completed = exercises_completed + 1,
                   goal_met = CASE WHEN xp_earned + excluded.xp_earned >= (SELECT daily_goal_xp FROM learner_profile WHERE id = 'default') THEN 1 ELSE goal_met END",
                [input.xp_amount],
            )
            .map_err(|e| e.to_string())?;
        }

        if let Some(item_id) = &input.learning_item_id {
            conn.execute(
                "INSERT INTO learner_item_progress (learning_item_id, attempts, correct_attempts, incorrect_attempts, last_attempt_at, last_correct_at, ease_factor, interval_days, repetitions, mastery_status, next_review_at, updated_at)
                 VALUES (?1, 1, ?2, ?3, datetime('now'), CASE WHEN ?2 = 1 THEN datetime('now') ELSE NULL END, ?4, ?5, ?6, ?7, datetime('now', 'localtime', '+' || ?5 || ' days'), datetime('now'))
                 ON CONFLICT(learning_item_id) DO UPDATE SET
                   attempts = learner_item_progress.attempts + 1,
                   correct_attempts = learner_item_progress.correct_attempts + excluded.correct_attempts,
                   incorrect_attempts = learner_item_progress.incorrect_attempts + excluded.incorrect_attempts,
                   last_attempt_at = datetime('now'),
                   last_correct_at = CASE WHEN excluded.correct_attempts = 1 THEN datetime('now') ELSE last_correct_at END,
                   ease_factor = excluded.ease_factor,
                   interval_days = excluded.interval_days,
                   repetitions = excluded.repetitions,
                   mastery_status = excluded.mastery_status,
                   next_review_at = datetime('now', 'localtime', '+' || excluded.interval_days || ' days'),
                   updated_at = datetime('now')",
                (
                    item_id,
                    if input.is_correct { 1 } else { 0 },
                    if input.is_correct { 0 } else { 1 },
                    input.ease_factor,
                    input.interval_days,
                    input.repetitions,
                    &input.mastery_status,
                ),
            )
            .map_err(|e| e.to_string())?;

            let next_review: String = conn
                .query_row(
                    "SELECT datetime('now', 'localtime', '+' || ?1 || ' days')",
                    [input.interval_days],
                    |row| row.get(0),
                )
                .map_err(|e| e.to_string())?;
            conn.execute(
                "INSERT INTO review_schedule (learning_item_id, next_review_at, priority_score)
                 VALUES (?1, ?2, CASE WHEN ?3 = 0 THEN 2.0 ELSE 1.0 END)
                 ON CONFLICT(learning_item_id) DO UPDATE SET next_review_at = excluded.next_review_at, priority_score = excluded.priority_score",
                (item_id, &next_review, input.interval_days),
            )
            .map_err(|e| e.to_string())?;
        }

        Ok(())
    })
}

#[tauri::command]
pub fn complete_lesson(
    state: State<DbState>,
    lesson_id: String,
    xp_earned: i32,
) -> Result<(), String> {
    crate::db::with_conn(&state, |conn| {
        let exists: i32 = conn
            .query_row(
                "SELECT COUNT(*) FROM lesson_attempts WHERE lesson_id = ?1 AND completed_at IS NOT NULL",
                [&lesson_id],
                |row| row.get(0),
            )
            .unwrap_or(0);
        if exists > 0 {
            return Ok(());
        }
        let updated = conn
            .execute(
                "UPDATE lesson_attempts SET completed_at = datetime('now'), xp_earned = ?2
                 WHERE lesson_id = ?1 AND completed_at IS NULL",
                (&lesson_id, xp_earned),
            )
            .map_err(|e| e.to_string())?;
        if updated == 0 {
            let la_id = Uuid::new_v4().to_string();
            conn.execute(
                "INSERT INTO lesson_attempts (id, lesson_id, started_at, completed_at, xp_earned)
                 VALUES (?1, ?2, datetime('now'), datetime('now'), ?3)",
                (&la_id, &lesson_id, xp_earned),
            )
            .map_err(|e| e.to_string())?;
        }
        Ok(())
    })
}

#[tauri::command]
pub fn prepare_lesson(state: State<DbState>, lesson_id: String) -> Result<LessonResumeState, String> {
    crate::db::with_conn(&state, |conn| {
        let lesson_completed: i32 = conn
            .query_row(
                "SELECT COUNT(*) FROM lesson_attempts WHERE lesson_id = ?1 AND completed_at IS NOT NULL",
                [&lesson_id],
                |row| row.get(0),
            )
            .unwrap_or(0);

        if lesson_completed == 0 {
            let open: i32 = conn
                .query_row(
                    "SELECT COUNT(*) FROM lesson_attempts WHERE lesson_id = ?1 AND completed_at IS NULL",
                    [&lesson_id],
                    |row| row.get(0),
                )
                .unwrap_or(0);
            if open == 0 {
                let la_id = Uuid::new_v4().to_string();
                conn.execute(
                    "INSERT INTO lesson_attempts (id, lesson_id, started_at, xp_earned)
                     VALUES (?1, ?2, datetime('now'), 0)",
                    (&la_id, &lesson_id),
                )
                .map_err(|e| e.to_string())?;
            }
        }

        let mut exercise_stmt = conn
            .prepare(
                "SELECT e.id, e.exercise_type, e.sort_order
                 FROM exercise_definitions e
                 WHERE e.lesson_id = ?1
                 ORDER BY e.sort_order",
            )
            .map_err(|e| e.to_string())?;

        let exercises: Vec<(String, String, i32)> = exercise_stmt
            .query_map([&lesson_id], |row| {
                Ok((row.get(0)?, row.get(1)?, row.get(2)?))
            })
            .map_err(|e| e.to_string())?
            .collect::<Result<Vec<_>, _>>()
            .map_err(|e| e.to_string())?;

        let mut resume_index = exercises.len() as i32;
        for (idx, (ex_id, _, _)) in exercises.iter().enumerate() {
            let attempted: i32 = conn
                .query_row(
                    "SELECT COUNT(*) FROM exercise_attempts WHERE exercise_id = ?1",
                    [ex_id],
                    |row| row.get(0),
                )
                .unwrap_or(0);
            if attempted == 0 {
                resume_index = idx as i32;
                break;
            }
        }

        let mut attempt_stmt = conn
            .prepare(
                "SELECT ea.exercise_id, ed.exercise_type, ea.is_correct
                 FROM exercise_attempts ea
                 JOIN exercise_definitions ed ON ed.id = ea.exercise_id
                 WHERE ed.lesson_id = ?1
                 ORDER BY ea.attempted_at",
            )
            .map_err(|e| e.to_string())?;

        let attempts = attempt_stmt
            .query_map([&lesson_id], |row| {
                Ok(LessonAttemptSnapshot {
                    exercise_id: row.get(0)?,
                    exercise_type: row.get(1)?,
                    is_correct: row.get::<_, i32>(2)? == 1,
                })
            })
            .map_err(|e| e.to_string())?
            .collect::<Result<Vec<_>, _>>()
            .map_err(|e| e.to_string())?;

        Ok(LessonResumeState {
            resume_index,
            lesson_completed: lesson_completed > 0,
            attempts,
        })
    })
}

#[tauri::command]
pub fn get_item_schedule_state(
    state: State<DbState>,
    learning_item_id: String,
) -> Result<ItemScheduleState, String> {
    crate::db::with_conn(&state, |conn| {
        Ok(
            conn.query_row(
                "SELECT ease_factor, interval_days, repetitions, mastery_status
                 FROM learner_item_progress WHERE learning_item_id = ?1",
                [&learning_item_id],
                |row| {
                    Ok(ItemScheduleState {
                        ease_factor: row.get(0)?,
                        interval_days: row.get(1)?,
                        repetitions: row.get(2)?,
                        mastery_status: row.get(3)?,
                    })
                },
            )
            .unwrap_or(ItemScheduleState {
                ease_factor: 2.5,
                interval_days: 0,
                repetitions: 0,
                mastery_status: "new".to_string(),
            }),
        )
    })
}

fn parse_accepted_answers(raw: Option<String>) -> Vec<String> {
    raw.and_then(|s| serde_json::from_str(&s).ok())
        .unwrap_or_default()
}

#[tauri::command]
pub fn get_learning_item_detail(
    state: State<DbState>,
    learning_item_id: String,
) -> Result<LearningItemDetail, String> {
    crate::db::with_conn(&state, |conn| {
        let item = conn.query_row(
            "SELECT id, kannada_text, transliteration, english_meaning, literal_translation, context_note, accepted_answers
             FROM learning_items WHERE id = ?1",
            [&learning_item_id],
            |row| {
                Ok((
                    row.get::<_, String>(0)?,
                    row.get::<_, String>(1)?,
                    row.get::<_, String>(2)?,
                    row.get::<_, String>(3)?,
                    row.get::<_, Option<String>>(4)?,
                    row.get::<_, Option<String>>(5)?,
                    parse_accepted_answers(row.get(6)?),
                ))
            },
        ).map_err(|e| e.to_string())?;

        let progress = conn
            .query_row(
                "SELECT ease_factor, interval_days, repetitions, mastery_status, attempts, correct_attempts
                 FROM learner_item_progress WHERE learning_item_id = ?1",
                [&learning_item_id],
                |row| {
                    Ok((
                        ItemScheduleState {
                            ease_factor: row.get(0)?,
                            interval_days: row.get(1)?,
                            repetitions: row.get(2)?,
                            mastery_status: row.get(3)?,
                        },
                        row.get::<_, i32>(4)?,
                        row.get::<_, i32>(5)?,
                    ))
                },
            )
            .ok();

        let next_review_at: Option<String> = conn
            .query_row(
                "SELECT next_review_at FROM review_schedule WHERE learning_item_id = ?1",
                [&learning_item_id],
                |row| row.get(0),
            )
            .ok();

        let mut hist_stmt = conn
            .prepare(
                "SELECT ed.exercise_type, ea.is_correct, ea.attempted_at
                 FROM exercise_attempts ea
                 JOIN exercise_definitions ed ON ed.id = ea.exercise_id
                 WHERE ea.learning_item_id = ?1
                 ORDER BY ea.attempted_at DESC
                 LIMIT 12",
            )
            .map_err(|e| e.to_string())?;

        let recent_attempts = hist_stmt
            .query_map([&learning_item_id], |row| {
                Ok(AttemptHistoryRow {
                    exercise_type: row.get(0)?,
                    is_correct: row.get::<_, i32>(1)? == 1,
                    attempted_at: row.get(2)?,
                })
            })
            .map_err(|e| e.to_string())?
            .collect::<Result<Vec<_>, _>>()
            .map_err(|e| e.to_string())?;

        Ok(LearningItemDetail {
            id: item.0,
            kannada_text: item.1,
            transliteration: item.2,
            english_meaning: item.3,
            literal_translation: item.4,
            context_note: item.5,
            accepted_answers: item.6,
            progress: progress.as_ref().map(|p| p.0.clone()),
            next_review_at,
            attempt_count: progress.as_ref().map(|p| p.1).unwrap_or(0),
            correct_count: progress.as_ref().map(|p| p.2).unwrap_or(0),
            recent_attempts,
        })
    })
}

#[tauri::command]
pub fn get_review_queue(state: State<DbState>) -> Result<Vec<ReviewQueueItem>, String> {
    crate::db::with_conn(&state, |conn| {
        let mut stmt = conn
            .prepare(
                "SELECT rs.learning_item_id, li.kannada_text, li.transliteration, li.english_meaning, rs.next_review_at,
                        (SELECT e.id FROM exercise_definitions e
                           WHERE e.learning_item_id = rs.learning_item_id
                           ORDER BY e.sort_order LIMIT 1),
                        (SELECT e.exercise_type FROM exercise_definitions e
                           WHERE e.learning_item_id = rs.learning_item_id
                           ORDER BY e.sort_order LIMIT 1),
                        (SELECT e.prompt_json FROM exercise_definitions e
                           WHERE e.learning_item_id = rs.learning_item_id
                           ORDER BY e.sort_order LIMIT 1),
                        li.accepted_answers
                 FROM review_schedule rs
                 JOIN learning_items li ON li.id = rs.learning_item_id
                 WHERE rs.next_review_at <= datetime('now', 'localtime')
                 ORDER BY rs.priority_score DESC, rs.next_review_at ASC
                 LIMIT 50",
            )
            .map_err(|e| e.to_string())?;

        let rows = stmt
            .query_map([], |row| {
                Ok(ReviewQueueItem {
                    learning_item_id: row.get(0)?,
                    kannada_text: row.get(1)?,
                    transliteration: row.get(2)?,
                    english_meaning: row.get(3)?,
                    next_review_at: row.get(4)?,
                    exercise_id: row.get(5)?,
                    exercise_type: row.get(6)?,
                    exercise_prompt: row
                        .get::<_, Option<String>>(7)?
                        .and_then(|s| serde_json::from_str(&s).ok()),
                    accepted_answers: parse_accepted_answers(row.get(8)?),
                })
            })
            .map_err(|e| e.to_string())?;

        rows.collect::<Result<Vec<_>, _>>().map_err(|e| e.to_string())
    })
}

#[tauri::command]
pub fn get_progress_stats(state: State<DbState>) -> Result<serde_json::Value, String> {
    crate::db::with_conn(&state, |conn| {
        let mastered: i32 = conn
            .query_row(
                "SELECT COUNT(*) FROM learner_item_progress WHERE mastery_status = 'mastered'",
                [],
                |row| row.get(0),
            )
            .unwrap_or(0);

        let learning: i32 = conn
            .query_row(
                "SELECT COUNT(*) FROM learner_item_progress WHERE mastery_status IN ('learning', 'reviewing')",
                [],
                |row| row.get(0),
            )
            .unwrap_or(0);

        let total_correct: i32 = conn
            .query_row(
                "SELECT COALESCE(SUM(correct_attempts), 0) FROM learner_item_progress",
                [],
                |row| row.get(0),
            )
            .unwrap_or(0);

        let total_attempts: i32 = conn
            .query_row(
                "SELECT COALESCE(SUM(attempts), 0) FROM learner_item_progress",
                [],
                |row| row.get(0),
            )
            .unwrap_or(0);

        let accuracy = if total_attempts > 0 {
            (total_correct as f64 / total_attempts as f64) * 100.0
        } else {
            0.0
        };

        Ok(serde_json::json!({
            "masteredCount": mastered,
            "learningCount": learning,
            "recallAccuracyPercent": accuracy,
            "totalAttempts": total_attempts,
        }))
    })
}