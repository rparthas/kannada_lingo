# Architecture

## Layers

| Layer | Location | Responsibility |
|-------|----------|------------------|
| UI | `src/features`, `src/components` | iPhone/iPad layouts, navigation, exercise presentation |
| Domain | `src/domain` | SM-2 scheduling, answer evaluation (no Tauri imports) |
| Services | `src/services` | Tauri IPC, audio/AI interfaces |
| Persistence | `src-tauri/src/db`, `commands` | SQLite, migrations, backup |
| Content | `content/` | Versioned JSON imported into SQLite on first launch |

## Data flow

1. `init_app` migrates SQLite and imports bundled curriculum if empty.
2. Lesson player loads `get_lesson_detail` and renders `ExerciseRenderer`.
3. On submit, TypeScript evaluates answers, runs SM-2, then `record_exercise_attempt` persists progress, XP, and review schedule.
4. Backup uses SQLite online backup → integrity check → ZIP with manifest + checksum.

## Extension points

- **Audio**: `WebAudioService` + Tauri commands (`list_audio_assets`, `resolve_resource_path`, `write_learner_recording`); native iOS adapters can replace the web recording/playback layer later.
- **AI**: implement `AIContentProvider` behind a secure backend; never ship API keys in the app bundle.
- **Content**: add JSON under `content/curriculum/`, bump `content_version`, re-import via tooling (future CLI).