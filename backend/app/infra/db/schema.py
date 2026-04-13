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

CREATE TABLE IF NOT EXISTS session_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    lesson_id TEXT NOT NULL,
    step_id TEXT NOT NULL,
    template_id TEXT NOT NULL,
    correct INTEGER,
    score INTEGER NOT NULL DEFAULT 0,
    duration_ms INTEGER NOT NULL DEFAULT 0,
    details_json TEXT NOT NULL DEFAULT '{}',
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

CREATE TABLE IF NOT EXISTS learning_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    student_id TEXT NOT NULL,
    lesson_id TEXT NOT NULL DEFAULT '',
    step_id TEXT NOT NULL DEFAULT '',
    template_id TEXT NOT NULL DEFAULT '',
    event_type TEXT NOT NULL,
    payload_json TEXT NOT NULL DEFAULT '{}',
    event_at TEXT DEFAULT CURRENT_TIMESTAMP,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vocab_mastery (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    vocab_key TEXT NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    correct_count INTEGER NOT NULL DEFAULT 0,
    wrong_count INTEGER NOT NULL DEFAULT 0,
    last_result_correct INTEGER NOT NULL DEFAULT 0,
    last_score INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, vocab_key)
);

CREATE TABLE IF NOT EXISTS story_state (
    student_id TEXT PRIMARY KEY,
    arc_key TEXT NOT NULL DEFAULT 'snack_scouts',
    chapter_key TEXT NOT NULL DEFAULT 'chapter_1',
    episode_index INTEGER NOT NULL DEFAULT 1,
    last_choice_key TEXT NOT NULL DEFAULT '',
    last_choice_tag TEXT NOT NULL DEFAULT '',
    unresolved_hooks_json TEXT NOT NULL DEFAULT '[]',
    state_json TEXT NOT NULL DEFAULT '{}',
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS story_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    lesson_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    event_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sessions_student_created ON sessions(student_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_session_steps_student_created ON session_steps(student_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_session_steps_lesson ON session_steps(lesson_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_story_state_updated ON story_state(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_story_events_student_created ON story_events(student_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_cost_events_category_created ON cost_events(category, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_learning_events_student_created ON learning_events(student_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_learning_events_session_created ON learning_events(session_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_vocab_mastery_student_wrong ON vocab_mastery(student_id, wrong_count DESC, updated_at DESC);
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
