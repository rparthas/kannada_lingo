-- Allow system TTS clips alongside human and AI audio.
PRAGMA foreign_keys = OFF;

CREATE TABLE audio_assets_new (
    id TEXT PRIMARY KEY,
    learning_item_id TEXT NOT NULL REFERENCES learning_items(id),
    locale TEXT NOT NULL DEFAULT 'kn-IN',
    speaker_id TEXT,
    source TEXT NOT NULL CHECK (source IN ('human', 'ai', 'tts')),
    speaking_speed TEXT DEFAULT 'normal',
    review_status TEXT DEFAULT 'approved',
    duration_ms INTEGER,
    file_format TEXT,
    relative_path TEXT,
    content_version INTEGER NOT NULL DEFAULT 1
);

INSERT INTO audio_assets_new
SELECT * FROM audio_assets;

DROP TABLE audio_assets;

ALTER TABLE audio_assets_new RENAME TO audio_assets;

PRAGMA foreign_keys = ON;