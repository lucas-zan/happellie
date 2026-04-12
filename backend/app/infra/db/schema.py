from pathlib import Path

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS lesson_cache (
    cache_key TEXT PRIMARY KEY,
    lesson_json TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    lesson_id TEXT NOT NULL,
    duration_seconds INTEGER NOT NULL,
    total_score INTEGER NOT NULL,
    earned_food INTEGER NOT NULL DEFAULT 0,
    earned_coins INTEGER NOT NULL DEFAULT 0,
    wrong_count INTEGER NOT NULL DEFAULT 0,
    preferred_block_types_json TEXT NOT NULL DEFAULT '[]',
    block_results_json TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS profiles (
    student_id TEXT PRIMARY KEY,
    profile_json TEXT NOT NULL,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pets (
    student_id TEXT PRIMARY KEY,
    pet_json TEXT NOT NULL,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cost_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    count INTEGER NOT NULL DEFAULT 1,
    cost_cents INTEGER NOT NULL DEFAULT 0,
    metadata_json TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sessions_student_created ON sessions(student_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_cost_events_category_created ON cost_events(category, created_at DESC);
"""


def ensure_schema(db_path: str) -> None:
    import sqlite3

    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
        _ensure_column(conn, "sessions", "wrong_count", "INTEGER NOT NULL DEFAULT 0")
        _ensure_column(conn, "sessions", "preferred_block_types_json", "TEXT NOT NULL DEFAULT '[]'")
        conn.commit()
    finally:
        conn.close()


def _ensure_column(conn, table: str, column: str, definition: str) -> None:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    existing = {row[1] for row in rows}
    if column not in existing:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
