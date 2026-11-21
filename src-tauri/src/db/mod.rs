pub mod migrations;

use rusqlite::Connection;
use std::path::{Path, PathBuf};
use std::sync::Mutex;

pub struct DbState {
    pub conn: Mutex<Connection>,
    pub path: PathBuf,
}

impl DbState {
    pub fn open(path: &Path) -> Result<Self, String> {
        if let Some(parent) = path.parent() {
            std::fs::create_dir_all(parent).map_err(|e| e.to_string())?;
        }
        let conn = Self::connect_and_migrate(path)?;
        Ok(Self {
            conn: Mutex::new(conn),
            path: path.to_path_buf(),
        })
    }

    fn connect_and_migrate(path: &Path) -> Result<Connection, String> {
        let conn = Connection::open(path).map_err(|e| e.to_string())?;
        conn.execute_batch("PRAGMA foreign_keys = ON;")
            .map_err(|e| e.to_string())?;
        migrations::run(&conn)?;
        Ok(conn)
    }

    /// Re-open the database file from disk (required after external restore over live path).
    pub fn reopen(&self) -> Result<(), String> {
        let conn = Self::connect_and_migrate(&self.path)?;
        let mut guard = self.conn.lock().map_err(|e| e.to_string())?;
        *guard = conn;
        Ok(())
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