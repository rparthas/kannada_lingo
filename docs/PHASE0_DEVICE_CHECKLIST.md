# Phase 0 — device checklist

Record results on a **physical** iPhone and iPad. Simulator is useful but not sufficient for audio/mic/File Provider behavior.

| Check | iPhone | iPad | Notes |
|-------|--------|------|-------|
| App launches | ☐ | ☐ | |
| SQLite init + curriculum import | ☐ | ☐ | First launch imports bundled JSON |
| Lesson completes offline | ☐ | ☐ | Airplane mode |
| Progress survives force quit | ☐ | ☐ | |
| Kannada script renders | ☐ | ☐ | Noto Sans Kannada / system fallback |
| Audio playback (human) | ☐ | ☐ | After assets added |
| Microphone permission flow | ☐ | ☐ | listen_repeat exercise |
| Export backup to iCloud Drive | ☐ | ☐ | ZIP + manifest |
| Import backup from Files | ☐ | ☐ | Invalid ZIP rejected |
| Portrait / landscape layout | ☐ | ☐ | iPad two-column where applicable |

## Known environment gap

This workspace had **Command Line Tools only** (no `xcodebuild`). Install Xcode and select it with `xcode-select` before `tauri ios dev`.