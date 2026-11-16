use rusqlite::Connection;

pub const LATEST_VERSION: i32 = 1;

const MIGRATION_001: &str = include_str!("../../migrations/001_initial.sql");

pub fn run(conn: &Connection) -> Result<(), String> {
    let current: i32 = conn
        .query_row(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_migrations'",
            [],
            |_| Ok(()),
        )
        .ok()
        .and_then(|_| {
            conn.query_row(
                "SELECT COALESCE(MAX(version), 0) FROM schema_migrations",
                [],
                |row| row.get(0),
            )
            .ok()
        })
        .unwrap_or(0);

    if current < 1 {
        conn.execute_batch(MIGRATION_001)
            .map_err(|e| format!("migration 001 failed: {e}"))?;
        conn.execute(
            "INSERT OR IGNORE INTO schema_migrations (version) VALUES (1)",
            [],
        )
        .map_err(|e| e.to_string())?;
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use rusqlite::Connection;

    #[test]
    fn migrations_apply_idempotently() {
        let conn = Connection::open_in_memory().unwrap();
        run(&conn).unwrap();
        run(&conn).unwrap();
        let count: i64 = conn
            .query_row("SELECT COUNT(*) FROM learning_items", [], |r| r.get(0))
            .unwrap();
        assert_eq!(count, 0);
    }
}