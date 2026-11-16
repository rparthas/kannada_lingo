use crate::content::import::import_bundled;
use crate::db::DbState;
use serde::Serialize;
use tauri::State;

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
pub struct AppInitResult {
    pub schema_version: i32,
    pub content_items: usize,
    pub content_imported: bool,
    pub integrity_ok: bool,
}

#[tauri::command]
pub fn init_app(state: State<DbState>) -> Result<AppInitResult, String> {
    let imported = if state.content_is_empty()? {
        let count = crate::db::with_conn(&state, |conn| import_bundled(conn))?;
        Some(count)
    } else {
        None
    };

    let integrity = state.integrity_check()?;
    Ok(AppInitResult {
        schema_version: state.schema_version()?,
        content_items: imported.unwrap_or(0),
        content_imported: imported.is_some(),
        integrity_ok: integrity == "ok",
    })
}

#[tauri::command]
pub fn complete_onboarding(state: State<DbState>, display_name: Option<String>) -> Result<(), String> {
    crate::db::with_conn(&state, |conn| {
        conn.execute(
            "UPDATE learner_profile SET display_name = ?1, onboarding_complete = 1, updated_at = datetime('now') WHERE id = 'default'",
            [display_name.as_deref().unwrap_or("Learner")],
        )
        .map_err(|e| e.to_string())?;
        Ok(())
    })
}

#[tauri::command]
pub fn get_learner_profile(state: State<DbState>) -> Result<serde_json::Value, String> {
    crate::db::with_conn(&state, |conn| {
        conn.query_row(
            "SELECT display_name, daily_goal_xp, onboarding_complete FROM learner_profile WHERE id = 'default'",
            [],
            |row| {
                Ok(serde_json::json!({
                    "displayName": row.get::<_, Option<String>>(0)?,
                    "dailyGoalXp": row.get::<_, i32>(1)?,
                    "onboardingComplete": row.get::<_, i32>(2)? == 1,
                }))
            },
        )
        .map_err(|e| e.to_string())
    })
}