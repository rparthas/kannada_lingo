use chrono::Utc;
use rusqlite::Connection;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::fs::{self, File};
use std::io::{Read, Write};
use std::path::{Path, PathBuf};
use uuid::Uuid;
use zip::write::SimpleFileOptions;
use zip::ZipWriter;

pub const BACKUP_FORMAT_VERSION: &str = "1.0.0";

#[derive(Debug, Serialize, Deserialize, Clone)]
#[serde(rename_all = "camelCase")]
pub struct BackupManifest {
    pub backup_format_version: String,
    pub database_schema_version: i32,
    pub application_version: String,
    pub export_timestamp: String,
    pub backup_id: String,
    pub content_version: i32,
    pub database_checksum_sha256: String,
}

pub fn checksum_file(path: &Path) -> Result<String, String> {
    let mut file = File::open(path).map_err(|e| e.to_string())?;
    let mut hasher = Sha256::new();
    let mut buffer = [0u8; 8192];
    loop {
        let n = file.read(&mut buffer).map_err(|e| e.to_string())?;
        if n == 0 {
            break;
        }
        hasher.update(&buffer[..n]);
    }
    Ok(hasher
        .finalize()
        .iter()
        .map(|b| format!("{b:02x}"))
        .collect())
}

pub fn export_backup_package(
    db_path: &Path,
    dest_zip: &Path,
    schema_version: i32,
    app_version: &str,
    content_version: i32,
) -> Result<BackupManifest, String> {
    let temp_dir = std::env::temp_dir().join(format!("kq-backup-{}", Uuid::new_v4()));
    fs::create_dir_all(&temp_dir).map_err(|e| e.to_string())?;
    let snapshot_path = temp_dir.join("learner.sqlite");

    snapshot_database(db_path, &snapshot_path)?;
    let integrity: String = {
        let conn = Connection::open(&snapshot_path).map_err(|e| e.to_string())?;
        conn.query_row("PRAGMA integrity_check", [], |row| row.get(0))
            .map_err(|e| e.to_string())?
    };
    if integrity != "ok" {
        return Err(format!("snapshot integrity check failed: {integrity}"));
    }

    let checksum = checksum_file(&snapshot_path)?;
    let manifest = BackupManifest {
        backup_format_version: BACKUP_FORMAT_VERSION.to_string(),
        database_schema_version: schema_version,
        application_version: app_version.to_string(),
        export_timestamp: Utc::now().to_rfc3339(),
        backup_id: Uuid::new_v4().to_string(),
        content_version,
        database_checksum_sha256: checksum,
    };

    let manifest_path = temp_dir.join("manifest.json");
    let manifest_json = serde_json::to_string_pretty(&manifest).map_err(|e| e.to_string())?;
    fs::write(&manifest_path, manifest_json).map_err(|e| e.to_string())?;

    write_zip_package(dest_zip, &manifest_path, &snapshot_path)?;

    let _ = fs::remove_dir_all(&temp_dir);
    Ok(manifest)
}

fn write_zip_package(
    dest_zip: &Path,
    manifest_path: &Path,
    db_snapshot: &Path,
) -> Result<(), String> {
    let file = File::create(dest_zip).map_err(|e| e.to_string())?;
    let mut zip = ZipWriter::new(file);
    let options = SimpleFileOptions::default()
        .compression_method(zip::CompressionMethod::Deflated);

    zip.start_file("backup/manifest.json", options)
        .map_err(|e| e.to_string())?;
    let manifest_bytes = fs::read(manifest_path).map_err(|e| e.to_string())?;
    zip.write_all(&manifest_bytes).map_err(|e| e.to_string())?;

    zip.start_file("backup/learner.sqlite", options)
        .map_err(|e| e.to_string())?;
    let db_bytes = fs::read(db_snapshot).map_err(|e| e.to_string())?;
    zip.write_all(&db_bytes).map_err(|e| e.to_string())?;

    zip.finish().map_err(|e| e.to_string())?;
    Ok(())
}

pub fn validate_backup_package(zip_path: &Path) -> Result<BackupManifest, String> {
    let file = File::open(zip_path).map_err(|e| e.to_string())?;
    let mut archive = zip::ZipArchive::new(file).map_err(|e| e.to_string())?;

    let mut manifest_json = String::new();
    {
        let mut manifest_file = archive
            .by_name("backup/manifest.json")
            .map_err(|_| "missing backup/manifest.json".to_string())?;
        manifest_file
            .read_to_string(&mut manifest_json)
            .map_err(|e| e.to_string())?;
    }

    let manifest: BackupManifest =
        serde_json::from_str(&manifest_json).map_err(|e| format!("invalid manifest: {e}"))?;

    if manifest.backup_format_version != BACKUP_FORMAT_VERSION {
        return Err(format!(
            "unsupported backup format {}",
            manifest.backup_format_version
        ));
    }

    let temp_dir = std::env::temp_dir().join(format!("kq-validate-{}", Uuid::new_v4()));
    fs::create_dir_all(&temp_dir).map_err(|e| e.to_string())?;
    let db_path = temp_dir.join("learner.sqlite");

  let file = File::open(zip_path).map_err(|e| e.to_string())?;
    let mut archive = zip::ZipArchive::new(file).map_err(|e| e.to_string())?;
    let mut db_file = archive
        .by_name("backup/learner.sqlite")
        .map_err(|_| "missing backup/learner.sqlite".to_string())?;
    let mut out = File::create(&db_path).map_err(|e| e.to_string())?;
    std::io::copy(&mut db_file, &mut out).map_err(|e| e.to_string())?;

    let checksum = checksum_file(&db_path)?;
    if checksum != manifest.database_checksum_sha256 {
        let _ = fs::remove_dir_all(&temp_dir);
        return Err("database checksum mismatch".to_string());
    }

    let integrity: String = {
        let conn = Connection::open(&db_path).map_err(|e| e.to_string())?;
        conn.query_row("PRAGMA integrity_check", [], |row| row.get(0))
            .map_err(|e| e.to_string())?
    };
    let _ = fs::remove_dir_all(&temp_dir);
    if integrity != "ok" {
        return Err(format!("sqlite integrity check failed: {integrity}"));
    }

    Ok(manifest)
}

pub fn restore_backup_package(
    zip_path: &Path,
    live_db_path: &Path,
    safety_backup: &Path,
) -> Result<BackupManifest, String> {
    let manifest = validate_backup_package(zip_path)?;

    if live_db_path.exists() {
        snapshot_database(live_db_path, safety_backup)?;
    }

    let temp_dir = std::env::temp_dir().join(format!("kq-restore-{}", Uuid::new_v4()));
    fs::create_dir_all(&temp_dir).map_err(|e| e.to_string())?;
    let extracted = temp_dir.join("learner.sqlite");

    let file = File::open(zip_path).map_err(|e| e.to_string())?;
    let mut archive = zip::ZipArchive::new(file).map_err(|e| e.to_string())?;
    let mut db_file = archive
        .by_name("backup/learner.sqlite")
        .map_err(|e| e.to_string())?;
    let mut out = File::create(&extracted).map_err(|e| e.to_string())?;
    std::io::copy(&mut db_file, &mut out).map_err(|e| e.to_string())?;

    if let Some(parent) = live_db_path.parent() {
        fs::create_dir_all(parent).map_err(|e| e.to_string())?;
    }
    fs::copy(&extracted, live_db_path).map_err(|e| e.to_string())?;
    let _ = fs::remove_dir_all(&temp_dir);
    Ok(manifest)
}

fn snapshot_database(source: &Path, dest: &Path) -> Result<(), String> {
    let source_conn = Connection::open(source).map_err(|e| e.to_string())?;
    let mut dest_conn = Connection::open(dest).map_err(|e| e.to_string())?;
    let backup = rusqlite::backup::Backup::new(&source_conn, &mut dest_conn)
        .map_err(|e| e.to_string())?;
    backup
        .run_to_completion(200, std::time::Duration::from_millis(10), None)
        .map_err(|e| e.to_string())?;
    Ok(())
}

pub fn safety_backup_path(db_path: &Path) -> PathBuf {
    db_path.with_extension("pre-restore.sqlite.bak")
}

#[cfg(test)]
mod tests {
    use super::*;
    use rusqlite::Connection;

    #[test]
    fn export_and_validate_roundtrip() {
        let dir = std::env::temp_dir().join(format!("kq-test-{}", Uuid::new_v4()));
        fs::create_dir_all(&dir).unwrap();
        let db_path = dir.join("learner.sqlite");
        let zip_path = dir.join("backup.zip");

        {
            let conn = Connection::open(&db_path).unwrap();
            crate::db::migrations::run(&conn).unwrap();
        }

        let manifest = export_backup_package(&db_path, &zip_path, 1, "0.1.0", 1).unwrap();
        let validated = validate_backup_package(&zip_path).unwrap();
        assert_eq!(manifest.backup_id, validated.backup_id);
        let _ = fs::remove_dir_all(dir);
    }
}