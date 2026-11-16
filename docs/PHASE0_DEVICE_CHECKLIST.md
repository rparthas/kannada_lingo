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

## Agent verification (2026-11-16)

Simulator only: iOS sim **build + launch** passed on iPhone 17 (iOS 27.2). Toolchain details in `docs/PHASE0_VERIFICATION.md`.

## Device signing note

If `tauri ios build` (device SDK) fails with missing team/profile, open `src-tauri/gen/apple/kannada-quest.xcodeproj` in Xcode, sign in under **Accounts**, enable **Automatically manage signing** for `kannada-quest_iOS`.