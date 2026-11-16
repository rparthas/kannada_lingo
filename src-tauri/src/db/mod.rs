pub mod migrations;

use rusqlite::{Connection, OptionalExtension};
use std::path::Path;
use std::sync::Mutex;

pub struct DbState {
    pub conn: Mutex<Connection>,
}

impl DbState {
    pub fn open(path: &Path) -> Result<Self, String> {
        if let Some(parent) = path.parent() {
            std::fs::create_dir_all(parent).map_err(|e| e.to_string())?;
        }
        let conn = Connection::open(path).map_err(|e| e.to_string())?;
        conn.execute_batch("PRAGMA foreign_keys = ON;")
            .map_err(|e| e.to_string())?;
        migrations::run(&conn)?;
        Ok(Self {
            conn: Mutex::new(conn),
        })
    }

    pub fn schema_version(&self) -> Result<i32, String> {
        let conn = self.conn.lock().map_err(|e| e.to_string())?;
        let version: i32 = conn
            .query_row(
                "SELECT COALESCE(MAX(version), 0) FROM schema_migrations",
                [],
                |row| row.get(0),
            )
            .unwrap_or(0);
        Ok(version.max(migrations::LATEST_VERSION))
    }

    pub fn content_is_empty(&self) -> Result<bool, String> {
        let conn = self.conn.lock().map_err(|e| e.to_string())?;
        let count: i64 = conn
            .query_row("SELECT COUNT(*) FROM learning_items", [], |row| row.get(0))
            .map_err(|e| e.to_string())?;
        Ok(count == 0)
    }

    pub fn integrity_check(&self) -> Result<String, String> {
        let conn = self.conn.lock().map_err(|e| e.to_string())?;
        conn.query_row("PRAGMA integrity_check", [], |row| row.get(0))
            .map_err(|e| e.to_string())
    }
}

pub fn with_conn<T, F>(state: &DbState, f: F) -> Result<T, String>
where
    F: FnOnce(&Connection) -> Result<T, String>,
{
    let conn = state.conn.lock().map_err(|e| e.to_string())?;
    f(&conn)
}

pub fn query_optional_string(
    conn: &Connection,
    sql: &str,
    params: &[&dyn rusqlite::ToSql],
) -> Result<Option<String>, rusqlite::Error> {
    conn.query_row(sql, params, |row| row.get(0))
        .optional()
}