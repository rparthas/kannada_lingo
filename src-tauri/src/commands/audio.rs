use crate::db::DbState;
use serde::Serialize;
use tauri::{AppHandle, Manager, State};
use tauri::path::BaseDirectory;

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
pub struct AudioAssetDto {
    pub id: String,
    pub learning_item_id: String,
    pub source: String,
    pub speaking_speed: String,
    pub relative_path: Option<String>,
    pub duration_ms: Option<i32>,
}

#[tauri::command]
pub fn list_audio_assets(
    state: State<DbState>,
    learning_item_id: String,
) -> Result<Vec<AudioAssetDto>, String> {
    crate::db::with_conn(&state, |conn| {
        let mut stmt = conn
            .prepare(
                "SELECT id, learning_item_id, source, speaking_speed, relative_path, duration_ms
                 FROM audio_assets
                 WHERE learning_item_id = ?1 AND review_status = 'approved'
                 ORDER BY CASE speaking_speed WHEN 'normal' THEN 0 ELSE 1 END, source",
            )
            .map_err(|e| e.to_string())?;

        let rows = stmt
            .query_map([&learning_item_id], |row| {
                Ok(AudioAssetDto {
                    id: row.get(0)?,
                    learning_item_id: row.get(1)?,
                    source: row.get(2)?,
                    speaking_speed: row.get(3)?,
                    relative_path: row.get(4)?,
                    duration_ms: row.get(5)?,
                })
            })
            .map_err(|e| e.to_string())?
            .collect::<Result<Vec<_>, _>>()
            .map_err(|e| e.to_string())?;

        Ok(rows)
    })
}

#[tauri::command]
pub fn resolve_resource_path(app: AppHandle, relative_path: String) -> Result<String, String> {
    app.path()
        .resolve(relative_path, BaseDirectory::Resource)
        .map(|p| p.to_string_lossy().into_owned())
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub fn write_learner_recording(
    app: AppHandle,
    bytes: Vec<u8>,
) -> Result<LearnerRecordingMeta, String> {
    let dir = app
        .path()
        .app_data_dir()
        .map_err(|e| e.to_string())?
        .join("learner_recordings");
    std::fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
    let id = uuid::Uuid::new_v4().to_string();
    let file_name = format!("{id}.webm");
    let path = dir.join(&file_name);
    std::fs::write(&path, &bytes).map_err(|e| e.to_string())?;
    let duration_ms = rough_webm_duration_ms(&bytes);
    Ok(LearnerRecordingMeta {
        file_path: path.to_string_lossy().into_owned(),
        duration_ms,
    })
}

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
pub struct LearnerRecordingMeta {
    pub file_path: String,
    pub duration_ms: i64,
}

fn rough_webm_duration_ms(bytes: &[u8]) -> i64 {
    // MVP: estimate from size — replaced when native recording reports duration.
    let kb = bytes.len() as f64 / 1024.0;
    ((kb / 16.0) * 1000.0).clamp(200.0, 120_000.0) as i64
}