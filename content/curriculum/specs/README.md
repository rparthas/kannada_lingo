# Curriculum specs

Author units here; the app ships **`beginner-path.json`** built from these files.

## Layout

| Path | Purpose |
|------|---------|
| `course.json` | `content_version`, course + level metadata, optional `extra_audio_assets` |
| `units/unit-*.json` | One file per unit: phrases, lessons, exercise config |

## Add or extend a unit

1. Edit or add `units/unit-N-slug.json` (copy an existing unit as a template).
2. Add phrases under `phrases` (each needs `id`, `kannada_text`, `transliteration`, `english_meaning`; optional `context_note`, `tags`, `accepted_answers`, `register`, `difficulty`).
3. Add lessons with `phrase_ids` in teaching order.
4. Set `exercise_mode`:
   - **`generated`** — builder creates flashcard / MCQ / convo drills; optional `convo`, `fill`, `tiles` on the lesson.
   - **`hand`** — supply full `exercises` array (see `unit-1-greetings.json` lesson 1).
5. Bump `content_version` in `course.json`.
6. Run:

```bash
npm run content:build
npm run content:validate
npm run test
```

7. Re-import in the app: delete learner DB or install a fresh build so `init_app` sees the higher version.

## Generated exercise shorthand

For `exercise_mode: "generated"`, a lesson typically includes `convo` (scripted conversation steps). Optional:

- `fill` — `{ "item_id", "instruction", "blank", "accepted" }`
- `tiles` — `{ "item_id", "tiles", "solution", "instruction"? }`

Logic lives in `scripts/curriculum/assemble.py`.