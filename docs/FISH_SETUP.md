# Fish shell setup (Kannada Quest / iOS)

Tauri iOS commands need **rustup’s** `cargo`/`rustc`, not Homebrew Rust alone. On fish, wire this once in your config.

## One-time: `~/.config/fish/config.fish`

```fish
# Rust (rustup) — required for `tauri ios` / iOS targets
if test -f $HOME/.cargo/env.fish
    source $HOME/.cargo/env.fish
end

# Optional: xcodes CLI (Phase 0 Xcode install) if not on PATH elsewhere
fish_add_path -m $HOME/.local/bin
```

`fish_add_path -m` prepends so `$HOME/.cargo/bin` wins over `/opt/homebrew/bin/rustc`.

Verify in a **new** terminal:

```fish
which rustup rustc cargo
# expect: ~/.cargo/bin/...
rustup show
```

## Per-session (if you skip config.fish)

```fish
source $HOME/.cargo/env.fish
fish_add_path $HOME/.local/bin
```

## iOS build env

Copy team ID:

```fish
cp .env.example .env
# edit .env — set APPLE_DEVELOPMENT_TEAM
```

For one command:

```fish
set -x APPLE_DEVELOPMENT_TEAM XXXXXXXXXX
npm run ios:dev
```

Fish has no `.env` auto-load; use [direnv](https://direnv.net/) or export manually.

## Phase 0

```fish
cd /Users/rparthas/git/kannada_lingo
npm run ios:setup
```

Then follow `docs/PHASE0_BLOCKERS.md` (Xcode.app + Apple Development certificate).