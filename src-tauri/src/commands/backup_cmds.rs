use crate::backup::{export_backup_package, restore_backup_package, safety_backup_path, validate_backup_package, BackupManifest};
use crate::db::DbState;
use std::path::PathBuf;
use tauri::{Manager, State};

#[derive(serde::Serialize)]
#[serde(rename_all = "camelCase")]
pub struct BackupPathResult {
    pub path: String,
    pub manifest: BackupManifest,
}

fn db_path(app: &tauri::AppHandle) -> Result<PathBuf, String> {
    let dir = app
        .path()
        .app_data_dir()
        .map_err(|e| e.to_string())?;
    Ok(dir.join("learner.sqlite"))
}

#[tauri::command]
pub fn export_learning_backup(
    app: tauri::AppHandle,
    state: State<DbState>,
    dest_path: String,
) -> Result<BackupPathResult, String> {
    let db_path = db_path(&app)?;
    let dest = PathBuf::from(&dest_path);
    let schema_version = state.schema_version()?;
    let content_version: i32 = crate::db::with_conn(&state, |conn| {
        conn.query_row(
            "SELECT COALESCE(MAX(content_version), 1) FROM learning_items",
            [],
            |row| row.get(0),
        )
        .map_err(|e| e.to_string())
    })?;

    let manifest = export_backup_package(
        &db_path,
        &dest,
        schema_version,
        env!("CARGO_PKG_VERSION"),
        content_version,
    )?;

    crate::db::with_conn(&state, |conn| {
        conn.execute(
            "INSERT INTO backup_history (id, export_path, checksum, success) VALUES (?1, ?2, ?3, 1)",
            (
                &manifest.backup_id,
                &dest_path,
                &manifest.database_checksum_sha256,
            ),
        )
        .map_err(|e| e.to_string())?;
        Ok(())
    })?;

    Ok(BackupPathResult {
        path: dest_path,
        manifest,
    })
}

#[tauri::command]
pub fn validate_learning_backup(path: String) -> Result<BackupManifest, String> {
    let manifest = validate_backup_package(&PathBuf::from(path))?;
    crate::backup::assert_restore_compatible(
        &manifest,
        crate::db::migrations::LATEST_VERSION,
    )?;
    Ok(manifest)
}

#[tauri::command]
pub fn restore_learning_backup(
    app: tauri::AppHandle,
    state: State<DbState>,
    path: String,
) -> Result<BackupManifest, String> {
    let live = db_path(&app)?;
    let safety = safety_backup_path(&live);
    let schema_version = crate::db::migrations::LATEST_VERSION;
    let manifest =
        restore_backup_package(&PathBuf::from(path), &live, &safety, schema_version)?;
    state.reopen()?;
    Ok(manifest)
}