# Kannada Quest

Mobile-first Kannada learning app (Tauri 2 + React + SQLite). Teaches practical spoken **Bengaluru Kannada** with script, transliteration, and English explanations.

## Status

Foundation and learning loop work on desktop Tauri. **iOS Phase 0**: run `npm run ios:setup` then follow `docs/PHASE0_BLOCKERS.md` (Xcode.app + Apple Development cert).

### Included now

- Bottom navigation (Home, Learn, Practice, Progress)
- Beginner curriculum sample (10 phrases, 2 lessons, multiple exercise types)
- SQLite schema + migrations + bundled content import
- SM-2-inspired review scheduling (unit tested)
- Answer evaluation with accepted alternatives
- Backup export/import (ZIP, manifest, SHA-256, integrity check)
- AI and audio **interfaces** (stubs until device spike)

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