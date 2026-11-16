# Developer setup

## Prerequisites

- Node 22+
- Rust via **rustup** (required for iOS). On **fish**: `source $HOME/.cargo/env.fish` (see `docs/FISH_SETUP.md`).
- **Xcode 15+** for iOS (full app, not only Command Line Tools)
- Apple Developer signing for physical devices (`APPLE_DEVELOPMENT_TEAM` or `bundle.iOS.developmentTeam` in `tauri.conf.json`)

## Commands

```bash
npm install
npm run ios:setup     # rustup targets, CocoaPods, tauri ios init (stops early if Xcode missing)
npm run test
npm run dev           # Vite UI only
npm run tauri dev     # Desktop shell + UI
# After Xcode + APPLE_DEVELOPMENT_TEAM (see docs/PHASE0_BLOCKERS.md):
npm run ios:dev
```

## Rust tests (backup + migrations)

```bash
cd src-tauri && cargo test
```

## Content import

Bundled curriculum is embedded at build time from `content/curriculum/beginner-path.json`. To refresh learner DB during development, delete the app data directory or remove `learner.sqlite` from the platform app data folder.

## Phase 0

See `docs/PHASE0_DEVICE_CHECKLIST.md` before treating iOS features as complete.