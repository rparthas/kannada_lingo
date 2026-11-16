PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS courses (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    content_version INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS levels (
    id TEXT PRIMARY KEY,
    course_id TEXT NOT NULL REFERENCES courses(id),
    ordinal INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    UNIQUE(course_id, ordinal)
);

CREATE TABLE IF NOT EXISTS units (
    id TEXT PRIMARY KEY,
    level_id TEXT NOT NULL REFERENCES levels(id),
    ordinal INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    UNIQUE(level_id, ordinal)
);

CREATE TABLE IF NOT EXISTS lessons (
    id TEXT PRIMARY KEY,
    unit_id TEXT NOT NULL REFERENCES units(id),
    ordinal INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    estimated_minutes INTEGER DEFAULT 15,
    UNIQUE(unit_id, ordinal)
);

CREATE TABLE IF NOT EXISTS learning_items (
    id TEXT PRIMARY KEY,
    kannada_text TEXT NOT NULL,
    transliteration TEXT NOT NULL,
    english_meaning TEXT NOT NULL,
    literal_translation TEXT,
    context_note TEXT,
    register TEXT DEFAULT 'informal',
    dialect TEXT DEFAULT 'bengaluru',
    tags TEXT,
    difficulty INTEGER DEFAULT 1,
    grammar_pattern_id TEXT,
    accepted_answers TEXT,
    validation_status TEXT NOT NULL DEFAULT 'approved',
    content_version INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS lesson_items (
    lesson_id TEXT NOT NULL REFERENCES lessons(id),
    learning_item_id TEXT NOT NULL REFERENCES learning_items(id),
    sort_order INTEGER NOT NULL,
    PRIMARY KEY (lesson_id, learning_item_id)
);

CREATE TABLE IF NOT EXISTS exercise_definitions (
    id TEXT PRIMARY KEY,
    lesson_id TEXT NOT NULL REFERENCES lessons(id),
    learning_item_id TEXT REFERENCES learning_items(id),
    exercise_type TEXT NOT NULL,
    prompt_json TEXT NOT NULL,
    sort_order INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS grammar_patterns (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    explanation_en TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    lesson_id TEXT REFERENCES lessons(id),
    title TEXT NOT NULL,
    scenario_tag TEXT
);

CREATE TABLE IF NOT EXISTS conversation_turns (
    id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL REFERENCES conversations(id),
    turn_order INTEGER NOT NULL,
    speaker TEXT NOT NULL,
    learning_item_id TEXT REFERENCES learning_items(id),
    response_options_json TEXT
);

CREATE TABLE IF NOT EXISTS audio_assets (
    id TEXT PRIMARY KEY,
    learning_item_id TEXT NOT NULL REFERENCES learning_items(id),
    locale TEXT NOT NULL DEFAULT 'kn-IN',
    speaker_id TEXT,
    source TEXT NOT NULL CHECK (source IN ('human', 'ai')),
    speaking_speed TEXT DEFAULT 'normal',
    review_status TEXT DEFAULT 'approved',
    duration_ms INTEGER,
    file_format TEXT,
    relative_path TEXT,
    content_version INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS content_versions (
    id TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    imported_at TEXT NOT NULL DEFAULT (datetime('now')),
    item_count INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS learner_profile (
    id TEXT PRIMARY KEY DEFAULT 'default',
    display_name TEXT,
    daily_goal_xp INTEGER NOT NULL DEFAULT 50,
    onboarding_complete INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS learner_item_progress (
    learning_item_id TEXT PRIMARY KEY REFERENCES learning_items(id),
    attempts INTEGER NOT NULL DEFAULT 0,
    correct_attempts INTEGER NOT NULL DEFAULT 0,
    incorrect_attempts INTEGER NOT NULL DEFAULT 0,
    last_attempt_at TEXT,
    last_correct_at TEXT,
    ease_factor REAL NOT NULL DEFAULT 2.5,
    interval_days INTEGER NOT NULL DEFAULT 0,
    next_review_at TEXT,
    mastery_status TEXT NOT NULL DEFAULT 'new',
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS review_schedule (
    learning_item_id TEXT PRIMARY KEY REFERENCES learning_items(id),
    next_review_at TEXT NOT NULL,
    priority_score REAL NOT NULL DEFAULT 1.0
);

CREATE TABLE IF NOT EXISTS lesson_attempts (
    id TEXT PRIMARY KEY,
    lesson_id TEXT NOT NULL REFERENCES lessons(id),
    started_at TEXT NOT NULL,
    completed_at TEXT,
    xp_earned INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS exercise_attempts (
    id TEXT PRIMARY KEY,
    exercise_id TEXT NOT NULL REFERENCES exercise_definitions(id),
    learning_item_id TEXT REFERENCES learning_items(id),
    is_correct INTEGER NOT NULL,
    response_json TEXT,
    self_assessed INTEGER,
    attempted_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS learning_sessions (
    id TEXT PRIMARY KEY,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    xp_earned INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS xp_transactions (
    id TEXT PRIMARY KEY,
    amount INTEGER NOT NULL,
    reason TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS daily_activity (
    activity_date TEXT PRIMARY KEY,
    xp_earned INTEGER NOT NULL DEFAULT 0,
    exercises_completed INTEGER NOT NULL DEFAULT 0,
    goal_met INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS achievements (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS learner_achievements (
    achievement_id TEXT NOT NULL REFERENCES achievements(id),
    earned_at TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (achievement_id)
);

CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS backup_history (
    id TEXT PRIMARY KEY,
    export_path TEXT,
    checksum TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    success INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_levels_course ON levels(course_id);
CREATE INDEX IF NOT EXISTS idx_units_level ON units(level_id);
CREATE INDEX IF NOT EXISTS idx_lessons_unit ON lessons(unit_id);
CREATE INDEX IF NOT EXISTS idx_exercises_lesson ON exercise_definitions(lesson_id);
CREATE INDEX IF NOT EXISTS idx_review_next ON review_schedule(next_review_at);

INSERT OR IGNORE INTO learner_profile (id) VALUES ('default');