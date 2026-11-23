# Kannada Quest

Mobile-first Kannada learning app (Tauri 2 + React + SQLite). Teaches practical spoken **Bengaluru Kannada** with script, transliteration, and English explanations.

Product vision: [`docs/vision.md`](docs/vision.md)

## Status

Core learning loop works on desktop Tauri. iOS toolchain and simulator build are in place; see [`docs/DEVELOPER_SETUP.md`](docs/DEVELOPER_SETUP.md) to run the app.

### Included now

- Bottom navigation (Home, Learn, Practice, Progress)
- Level 1 Survival path: **13 units**, **26 lessons**, **110 phrases** — macOS Kannada TTS (`npm run content:build`)
- Lesson player with resume after interrupt, review mode, and immediate feedback
- Phrase detail screen with attempt history; practice tab recall drills
- SQLite schema + migrations + bundled content import
- SM-2-inspired review scheduling (unit tested)
- Answer evaluation with accepted alternatives
- Backup export/import (ZIP, manifest, SHA-256, integrity check)
- Bundled phrase audio (macOS **Soumya** Kannada TTS on `content:build`; tone fallback on Linux CI), slow/normal playback, learner recording
- Curriculum content validation (`npm run content:validate`)
- Phase 5 mock AI grammar insight on phrase detail (`VITE_AI_PROVIDER=unconfigured` for production stub)

## Quick start

```bash
npm install
npm run test
npm run tauri dev
```

iOS and content tooling: [`docs/DEVELOPER_SETUP.md`](docs/DEVELOPER_SETUP.md).

## Documentation

| Document | Description |
|----------|-------------|
| [`docs/DEVELOPER_SETUP.md`](docs/DEVELOPER_SETUP.md) | Run commands (desktop + iOS) |
| [`docs/vision.md`](docs/vision.md) | Vision and principles |
| [`docs/constitution/mission.md`](docs/constitution/mission.md) | Mission and boundaries |
| [`docs/constitution/techstack.md`](docs/constitution/techstack.md) | Stack and architecture |
| [`docs/constitution/roadmap.md`](docs/constitution/roadmap.md) | Phases and priorities |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Short layer summary |

[`docs/IMPLEMENTATION_PLAN.md`](docs/IMPLEMENTATION_PLAN.md) points at the roadmap.