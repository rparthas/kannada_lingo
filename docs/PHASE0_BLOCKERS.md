# Phase 0 blockers — status

## Resolved on this machine

| Blocker | Resolution |
|---------|------------|
| `rustup` missing | Installed rustup stable 1.100; use `~/.cargo/bin` before Homebrew `rustc` |
| iOS Rust targets | `aarch64-apple-ios`, `aarch64-apple-ios-sim`, `x86_64-apple-ios` added |
| `tauri ios init` failed on `rustup target add` | Fixed by rustup + PATH |
| CocoaPods missing | `brew install cocoapods` |
| XcodeGen / libimobiledevice | Installed via `tauri ios init` / Homebrew |
| iOS Xcode project | Generated at `src-tauri/gen/apple/kannada-quest.xcodeproj` |

Run automated checks anytime:

```bash
npm run ios:setup
```

**Fish** (recommended on this machine) — add to `~/.config/fish/config.fish`:

```fish
if test -f $HOME/.cargo/env.fish
    source $HOME/.cargo/env.fish
end
fish_add_path -m $HOME/.local/bin
```

Details: `docs/FISH_SETUP.md`.

**bash/zsh:**

```bash
. "$HOME/.cargo/env"
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
```

## Still requires you (cannot automate without Apple ID / password)

### 1. Full Xcode.app

Command Line Tools alone cause `xcrun simctl` exit **72**.

**Option A — App Store**

```bash
open "macappstore://apps.apple.com/app/xcode/id497799835"
```

Install, then:

```bash
sudo xcode-select -s /Applications/Xcode.app/Contents/Developer
sudo xcodebuild -license accept
```

**Option B — xcodes CLI** (already at `~/.local/bin/xcodes`)

```bash
xcodes signin YOUR_APPLE_ID@email.com
xcodes install 27.2    # matches macOS 27.x on this Mac; use `xcodes list` to pick another
sudo xcode-select -s /Applications/Xcode.app/Contents/Developer
```

`mas install 497799835` failed here because `sudo` was required for the App Store helper — use App Store UI or `xcodes signin` instead.

### 2. Code signing

`security find-identity` reported **0 valid identities**.

1. Open **Xcode** → **Settings** → **Accounts** → sign in with Apple ID.
2. Select your team → **Manage Certificates** → **+** → **Apple Development**.
3. Copy your **Team ID** into `.env` as `APPLE_DEVELOPMENT_TEAM` (see `.env.example`).

### 3. First device / simulator run

```fish
source $HOME/.cargo/env.fish
set -x APPLE_DEVELOPMENT_TEAM XXXXXXXXXX   # from .env
npm run ios:dev
```

Complete the checklist in `docs/PHASE0_DEVICE_CHECKLIST.md`.