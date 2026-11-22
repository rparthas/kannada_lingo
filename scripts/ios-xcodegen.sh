#!/usr/bin/env bash
# Regenerate src-tauri/gen/apple/*.xcodeproj from project.yml with Tauri-safe tweaks.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
YML="${ROOT}/src-tauri/gen/apple/project.yml"

if [[ ! -f "${YML}" ]]; then
  echo "Missing ${YML}; run: npm run ios:init" >&2
  exit 1
fi

# XcodeGen expands ${VAR} from the generating shell. npm/Cursor set FORCE_COLOR=0, which
# gets baked into the "Build Rust Code" script and is parsed as an invalid arch.
perl -pi -e 's/\$\{FORCE_COLOR\}\s+//g' "${YML}"

# Ensure rustup's cargo/rustc win over Homebrew when Xcode runs the build phase.
if ! grep -q '.cargo/bin' "${YML}"; then
  perl -pi -e 's/^(\s*)(npm run -- tauri ios)/$1export PATH="\$HOME\/.cargo\/bin:\$PATH"\n$1$2/' "${YML}"
fi

(cd "${ROOT}/src-tauri/gen/apple" && env -u FORCE_COLOR xcodegen generate)
echo "Regenerated ${ROOT}/src-tauri/gen/apple/kannada-quest.xcodeproj"