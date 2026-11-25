//! Import bundled curriculum into a learner SQLite file (power-user / editorial loop).
use std::env;
use std::fs;
use std::path::PathBuf;
use std::process::ExitCode;

use tauri_app_lib::content::import::{
    bundle_content_version, import_bundle, import_if_newer, installed_content_version,
    ContentImportOutcome,
};
use tauri_app_lib::db::DbState;

const USAGE: &str = "Usage: content_import [--db PATH] [--bundle PATH] [--force]\n\
Default bundle: content/curriculum/beginner-path.json (relative to repo root).\n\
Default db: $KANNADA_LEARNER_DB or ./learner.sqlite";

fn main() -> ExitCode {
    let args: Vec<String> = env::args().collect();
    let mut db_path: Option<PathBuf> = env::var("KANNADA_LEARNER_DB").ok().map(PathBuf::from);
    let mut bundle_path: Option<PathBuf> = None;
    let mut force = false;

    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "--db" => {
                i += 1;
                db_path = Some(PathBuf::from(args.get(i).unwrap_or(&String::new())));
            }
            "--bundle" => {
                i += 1;
                bundle_path = Some(PathBuf::from(args.get(i).unwrap_or(&String::new())));
            }
            "--force" => force = true,
            "-h" | "--help" => {
                eprintln!("{USAGE}");
                return ExitCode::SUCCESS;
            }
            other => {
                eprintln!("Unknown argument: {other}\n{USAGE}");
                return ExitCode::from(2);
            }
        }
        i += 1;
    }

    let db_path = db_path.unwrap_or_else(|| PathBuf::from("learner.sqlite"));
    let bundle_path = bundle_path.unwrap_or_else(|| {
        PathBuf::from(env!("CARGO_MANIFEST_DIR"))
            .join("../content/curriculum/beginner-path.json")
    });

    let json = match fs::read_to_string(&bundle_path) {
        Ok(s) => s,
        Err(e) => {
            eprintln!("Could not read bundle {}: {e}", bundle_path.display());
            return ExitCode::from(1);
        }
    };

    let incoming = bundle_content_version(&json);
    let state = match DbState::open(&db_path) {
        Ok(s) => s,
        Err(e) => {
            eprintln!("Could not open database {}: {e}", db_path.display());
            return ExitCode::from(1);
        }
    };

    let conn = state.conn.lock().expect("db lock");
    let stored = installed_content_version(&conn);

    if force && incoming <= stored {
        match import_bundle(&conn, &json) {
            Ok(items) => {
                println!(
                    "Forced import v{incoming} into {} ({items} items; was v{stored}).",
                    db_path.display()
                );
                return ExitCode::SUCCESS;
            }
            Err(e) => {
                eprintln!("Import failed: {e}");
                return ExitCode::from(1);
            }
        }
    }

    match import_if_newer(&conn, &json) {
        Ok(ContentImportOutcome::Imported { items, content_version }) => {
            println!(
                "Imported content v{content_version} into {} ({items} learning items).",
                db_path.display()
            );
            ExitCode::SUCCESS
        }
        Ok(ContentImportOutcome::NoChange {
            stored_version,
            incoming_version,
        }) => {
            println!(
                "No import: installed v{stored_version}, bundle v{incoming_version} (use --force to re-apply)."
            );
            ExitCode::SUCCESS
        }
        Err(e) => {
            eprintln!("Import failed: {e}");
            ExitCode::from(1)
        }
    }
}