# Kannada Quest

Mobile-first Kannada learning app (Tauri 2 + React + SQLite). Teaches practical spoken **Bengaluru Kannada** with script, transliteration, and English explanations.

## Status

Foundation and learning loop work on desktop Tauri. **iOS Phase 0**: run `npm run ios:setup` then follow `docs/PHASE0_BLOCKERS.md` (Xcode.app + Apple Development cert).

### Included now

- Bottom navigation (Home, Learn, Practice, Progress)
- Beginner curriculum sample (10 phrases, 2 lessons, exercise types including scripted conversations)
- Lesson player with resume after interrupt, review mode, and immediate feedback
- Phrase detail screen with attempt history; practice tab recall drills
- SQLite schema + migrations + bundled content import
- SM-2-inspired review scheduling (unit tested)
- Answer evaluation with accepted alternatives
- Backup export/import (ZIP, manifest, SHA-256, integrity check)
- Bundled phrase audio (placeholder tones — swap for human recordings), slow/normal playback, learner recording playback
- Curriculum content validation (`npm run content:validate`)
- AI audio **interface** for Phase 5 (supplementary AI asset on `item-sari`)

## Quick start

```bash
npm install
npm run test
npm run tauri dev
```

## Documentation

- `docs/FISH_SETUP.md` — rustup PATH on fish
- `docs/PHASE0_BLOCKERS.md` — Xcode + signing
- `docs/ARCHITECTURE.md`
- `docs/DEVELOPER_SETUP.md`
- `docs/IMPLEMENTATION_PLAN.md`