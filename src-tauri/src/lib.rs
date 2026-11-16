mod backup;
mod commands;
mod content;
mod db;

use db::DbState;
use tauri::Manager;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .setup(|app| {
            let data_dir = app
                .path()
                .app_data_dir()
                .expect("failed to resolve app data directory");
            let db_path = data_dir.join("learner.sqlite");
            let db_state = DbState::open(&db_path).expect("failed to open SQLite database");
            app.manage(db_state);
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            commands::init_app,
            commands::complete_onboarding,
            commands::get_learner_profile,
            commands::get_home_summary,
            commands::list_levels,
            commands::list_lessons_for_level,
            commands::get_lesson_detail,
            commands::record_exercise_attempt,
            commands::complete_lesson,
            commands::get_review_queue,
            commands::get_progress_stats,
            commands::export_learning_backup,
            commands::validate_learning_backup,
            commands::restore_learning_backup,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}