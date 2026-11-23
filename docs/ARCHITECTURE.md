# Architecture (summary)

Full stack, layer rules, data flow, and extension points: **[`docs/constitution/techstack.md`](constitution/techstack.md)**.

## Layers

| Layer | Location | Responsibility |
|-------|----------|------------------|
| UI | `src/features`, `src/components` | Layouts, navigation, exercises |
| Domain | `src/domain` | SM-2 scheduling, answer evaluation |
| Services | `src/services` | Tauri IPC, audio/AI interfaces |
| Persistence | `src-tauri/src/db`, commands | SQLite, migrations, backup |
| Content | `content/` | Versioned JSON + audio imported on first launch |

## Data flow (short)

1. `init_app` → migrate + import curriculum if empty.
2. Lesson player → IPC → `ExerciseRenderer`.
3. Submit → domain evaluation + SM-2 → `record_exercise_attempt`.
4. Backup → online SQLite backup → ZIP + manifest + checksum.