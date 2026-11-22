# Kannada Quest

Mobile-first Kannada learning app (Tauri 2 + React + SQLite). Teaches practical spoken **Bengaluru Kannada** with script, transliteration, and English explanations.

## Status

Foundation and learning loop work on desktop Tauri. **iOS Phase 0**: run `npm run ios:setup` then follow `docs/PHASE0_BLOCKERS.md` (Xcode.app + Apple Development cert).

### Included now

- Bottom navigation (Home, Learn, Practice, Progress)
- Level 1 Survival path: **54 phrases**, **12 lessons** (6 units), exercise types including scripted conversations (`python3 scripts/build-beginner-path.py` to regenerate JSON)
- Lesson player with resume after interrupt, review mode, and immediate feedback
- Phrase detail screen with attempt history; practice tab recall drills
- SQLite schema + migrations + bundled content import
- SM-2-inspired review scheduling (unit tested)
- Answer evaluation with accepted alternatives
- Backup export/import (ZIP, manifest, SHA-256, integrity check)
- Bundled phrase audio (placeholder tones — swap for human recordings), slow/normal playback, learner recording playback
- Curriculum content validation (`npm run content:validate`)
- Phase 5 mock AI grammar insight on phrase detail (`VITE_AI_PROVIDER=unconfigured` for production stub)

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