#!/usr/bin/env bash
# Phase 0: install everything that does NOT require Apple ID / sudo password.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="${HOME}/.cargo/bin:${HOME}/.local/bin:/opt/homebrew/bin:${PATH}"

echo "==> Rust (rustup + iOS targets)"
if ! command -v rustup >/dev/null 2>&1; then
  curl -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable
fi
# shellcheck source=/dev/null
source "${HOME}/.cargo/env"
rustup target add aarch64-apple-ios aarch64-apple-ios-sim x86_64-apple-ios >/dev/null 2>&1 || true

echo "==> Homebrew iOS helpers"
brew list xcodegen >/dev/null 2>&1 || brew install xcodegen
brew list libimobiledevice >/dev/null 2>&1 || brew install libimobiledevice
brew list cocoapods >/dev/null 2>&1 || brew install cocoapods

if ! command -v xcodes >/dev/null 2>&1; then
  echo "==> xcodes CLI (Xcode downloader)"
  mkdir -p "${HOME}/.local/bin"
  XCODES_TGZ="/tmp/xcodes-cli.tgz"
  curl -fsSL -o "${XCODES_TGZ}" \
    "https://github.com/XcodesOrg/xcodes/releases/download/2.2.0/xcodes-2.2.0.macos.arm64.bottle.tar.gz"
  rm -rf /tmp/xcodes-extract
  mkdir -p /tmp/xcodes-extract
  tar -xzf "${XCODES_TGZ}" -C /tmp/xcodes-extract
  install -m 755 /tmp/xcodes-extract/xcodes/2.2.0/bin/xcodes "${HOME}/.local/bin/xcodes"
fi

echo "==> Tauri iOS project"
cd "${ROOT}"
npm install
npm run ios:init
# XcodeGen expands ${VAR} from the generating shell; npm/Cursor set FORCE_COLOR=0,
# which was baked into the "Build Rust Code" script as a bogus arch. Regenerate without it.
if [[ -f "${ROOT}/src-tauri/gen/apple/project.yml" ]]; then
  echo "==> Regenerate Xcode project (project.yml → .xcodeproj)"
  (cd "${ROOT}/src-tauri/gen/apple" && env -u FORCE_COLOR xcodegen generate)
fi

if [[ ! -d "/Applications/Xcode.app" ]]; then
  echo ""
  echo "⚠️  Full Xcode is not installed yet (only Command Line Tools)."
  echo "    Install Xcode (one of these):"
  echo "      1) App Store:  open \"macappstore://apps.apple.com/app/xcode/id497799835\""
  echo "      2) CLI:        xcodes signin   # then:  xcodes install 27.2"
  echo "    After install: sudo xcode-select -s /Applications/Xcode.app/Contents/Developer"
  echo "    Accept license: sudo xcodebuild -license accept"
  exit 2
fi

if [[ "$(xcode-select -p)" != "/Applications/Xcode.app/Contents/Developer" ]]; then
  echo "==> Pointing xcode-select at Xcode.app (may prompt for password)"
  sudo xcode-select -s /Applications/Xcode.app/Contents/Developer
fi

if ! security find-identity -v -p codesigning 2>/dev/null | grep -q "Apple Development"; then
  echo ""
  echo "⚠️  No Apple Development certificate yet."
  echo "    Open Xcode → Settings → Accounts → add Apple ID → Download Manual Profiles."
  echo "    Then set APPLE_DEVELOPMENT_TEAM in .env (see .env.example)."
  exit 2
fi

echo "==> Toolchain ready."
echo "    fish: source \$HOME/.cargo/env.fish && set -x APPLE_DEVELOPMENT_TEAM <team> && npm run ios:dev"
echo "    (see docs/FISH_SETUP.md)"