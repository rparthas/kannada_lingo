# Kannada Quest — Implementation Plan

## Current status

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 0 — Technical feasibility | **Verified (Simulator)** | Xcode 27.2, rustup iOS targets, sim build + launch; see `docs/PHASE0_VERIFICATION.md`. Physical device + audio/mic/iCloud checks remain on checklist |
| Phase 1 — Application foundation | Complete | Project scaffold, navigation, SQLite, migrations, content import (verified: 7/7 JS tests, tsc clean, 2/2 Rust tests) |
| Phase 2 — Learning engine | **Complete** | Lesson player with resume + review mode, all exercise types incl. scripted conversations, XP domain, phrase history, practice drills, SM-2 state from DB (`repetitions` migration 002) |
| Phase 3 — Audio and content | **Complete** | Bundled WAV assets + `audio_assets` import (v3), `WebAudioService` (play/pause/replay, normal/slow, recording), phrase + exercise UI, `npm run content:validate` |
| Phase 4 — Revision and retention | **Complete** | Local-time scheduling, consecutive streak, multi-type practice w/ self-grades, phrase review schedule UI, daily goal settings |
| Phase 5 — AI personalization | **Complete (mock)** | `MockAIContentProvider` + phrase grammar insight UI; swap via `VITE_AI_PROVIDER=unconfigured` for production boundary |
| Phase 6 — Backup / release | **Complete (app)** | Schema-safe restore, confirm UX, export feedback, restore roundtrip tests; device signing / store submission remain manual |

## Toolchain (recorded)

- Node: v22.x
- Rust: 1.99.x (Homebrew)
- Tauri: 2.x (create-tauri-app template)
- Xcode: **Not installed** — `xcodebuild` points at Command Line Tools only

## Next steps (manual)

1. Install Xcode from the App Store and run `sudo xcode-select -s /Applications/Xcode.app/Contents/Developer`
2. `npm run tauri ios init` then `npm run tauri ios dev` on a physical device
3. Complete Phase 0 checklist in `docs/PHASE0_DEVICE_CHECKLIST.md`
4. Record human audio for Level 1 items and wire `audio_assets` paths

## Architecture

Domain logic lives in `src/domain` (framework-agnostic TypeScript). Persistence and backup live in `src-tauri` (SQLite + migrations). Content is versioned JSON under `content/` imported into SQLite on first launch.