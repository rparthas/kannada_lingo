# Developer setup

Node 22+, **rustup** (not Homebrew Rust alone), **Xcode.app** for iOS, `APPLE_DEVELOPMENT_TEAM` in `.env` for device builds.

## Desktop

```bash
npm install
npm run test         # Vitest (TDD default — see constitution/techstack §6)
npm run dev          # UI only
npm run tauri dev    # desktop shell
```

```bash
cd src-tauri && cargo test
npm run content:validate
npm run content:build   # specs → beginner-path.json + macOS TTS audio
```

Curriculum authoring: [`content/curriculum/specs/README.md`](../content/curriculum/specs/README.md).

To re-import bundled curriculum in dev, delete the app’s `learner.sqlite` (or wipe app data).

## iOS

**Fish** — add once to `~/.config/fish/config.fish` so Tauri sees rustup:

```fish
source $HOME/.cargo/env.fish 2>/dev/null; or true
fish_add_path -m $HOME/.local/bin
```

**bash/zsh:** `source "$HOME/.cargo/env"` and ensure `$HOME/.cargo/bin` is on `PATH`.

```bash
npm run ios:setup
cp .env.example .env    # set APPLE_DEVELOPMENT_TEAM
npm run test
npm run ios:dev         # simulator or connected device
```

Simulator-only CI build:

```bash
npm run ios:build -- --ci --target aarch64-sim
```

If **simctl** exits 72: install Xcode.app, then `sudo xcode-select -s /Applications/Xcode.app/Contents/Developer`.

If **device signing** fails: Xcode → Settings → Accounts → sign in; open `src-tauri/gen/apple/kannada-quest.xcodeproj` → automatically manage signing for `kannada-quest_iOS`.

## Device smoke test (optional)

On a physical iPhone/iPad when you care about mic, Files, and speakers—not simulator alone.

| Check | ☐ |
|-------|---|
| Launch, first-run import, lesson offline (airplane mode) | |
| Progress after force quit; Kannada script | |
| Audio normal/slow; mic on listen-repeat | |
| Backup export/import via Files | |
| iPad portrait + landscape | |

## Docs

| Doc | Purpose |
|-----|---------|
| [`vision.md`](vision.md) | Product vision |
| [`constitution/mission.md`](constitution/mission.md) | Mission and boundaries |
| [`constitution/techstack.md`](constitution/techstack.md) | Architecture, **TDD** (§6) |
| [`constitution/roadmap.md`](constitution/roadmap.md) | Phases and priorities |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Layer summary |