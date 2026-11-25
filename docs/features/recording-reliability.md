# Recording reliability & audio sessions

| Field | Value |
|-------|-------|
| Status | Planned |
| Roadmap | [Release 0B](../constitution/roadmap_v1.md) (speaking foundation) |
| Priority | P0 |
| Slice | 1 — Speak and record |

## Learner outcome

“Recording never loses my take, and when the microphone is blocked I know exactly what to fix instead of guessing.”

## Principles

- **Sustainable engineering** — one explicit recording state machine instead of component-local booleans.
- **Local-first** — takes stay in the app’s data directory; nothing is uploaded.
- **Trust** — interruptions and permission failures degrade predictably, never with a silent loss.

## Current state

- `LearnerRecordingPanel` owns `recording`, `lastPath` and `message` in local state; unmounting loses the path.
- `tauri-plugin-native-audio` (Swift, AVFoundation) exposes `play_phrase`, `pause_playback`, `start_recording`, `stop_recording`, `play_learner_recording`.
- `activateRecordingSession()` sets `.playAndRecord` / `.spokenAudio`; `activatePlaybackSession()` sets `.playback`.
- Microphone denial surfaces as text in the panel; there is no permission query, no Settings recovery step, and no interruption handling.
- `NSMicrophoneUsageDescription` exists in `src-tauri/Info.ios.plist`.

## In scope

### 1. Recording state outside the component

- A session-scoped store (React context or small service module, e.g. `src/services/recording/session.ts`) keyed by exercise/phrase id holds:
  `{ phase, filePath, durationMs, startedAt, error }`.
- Phase machine: `idle → requesting → ready → recording → finalizing → recorded → playing`.
- `LearnerRecordingPanel` becomes a consumer; navigation within an exercise or to the summary and back must not clear `recorded`.
- Retry appends a take; it does not delete the previous file or attempt.

### 2. Permission handling

- Native commands `check_microphone_permission` and `request_microphone_permission` (or a single `ensure_microphone_permission`) returning a typed status: `granted | denied | restricted | undetermined | unavailable`.
- UI states:
  - first use → explain why, then request;
  - `denied` → explain and offer “Open Settings” via `tauri-plugin-opener`;
  - `restricted` / no input device → block recording with a specific message;
  - grant in Settings → retry works without reinstalling.
- Never auto-record on screen mount.

### 3. Interruptions and route changes

- Observe `AVAudioSession.interruptionNotification` and `routeChangeNotification` in the plugin.
- On interruption begin: stop the recorder safely, finalize the file, emit an event so JS marks the take `interrupted`; on end: do not auto-resume recording.
- On route change (headphones unplugged, Bluetooth disconnect): pause playback and warn rather than blasting speaker audio.
- Release the audio session when leaving the speaking screen so other apps recover.
- Backgrounding/screen lock: finalize an in-progress recording instead of leaving a half-written file; document the playback policy from [native-ios-audio.md](./native-ios-audio.md).

### 4. Visual and safety feedback

- Elapsed timer and pulsing indicator while recording.
- Hard maximum (60 s) with automatic stop and a clear reason.
- Guard against double-tap start/stop; disable controls during `finalizing`.
- Show a non-blocking “Saved on this phone — not uploaded” confirmation after stop.

### 5. Retention

- Store takes under the app data directory with `speaking-attempts/<item-id>/<uuid>.m4a`.
- Delete orphaned or superseded takes after the attempt is persisted; keep the latest per attempt only.
- A retention rule (e.g. prune takes older than 30 days, always keep the newest attempt per phrase) is documented and tested at the file-path helper level.
- Recordings never leave the device and are excluded from backup unless explicitly added later.

## Out of scope

- Speech recognition or transcription (Release 1).
- Waveform display, trimming, or audio editing.
- Background recording.

## Acceptance criteria

- [ ] Deny mic → guidance appears → grant in Settings → retry records successfully in the same app install.
- [ ] An incoming call/Siri interruption stops recording without a crash and leaves a playable take when audio was already captured.
- [ ] Navigating away from the speaking screen and back preserves the last take and its replay control.
- [ ] Starting a second recording never overwrites or loses the first file.
- [ ] Double-tapping stop is a no-op; no zero-duration files are created.
- [ ] Unplugging headphones during playback pauses rather than switching to full speaker volume.
- [ ] Orphaned takes are cleaned up; a unit test covers the retention/path helper.
- [ ] Manual device checklist below passes on the physical iPhone.

## Dependencies

- `tauri-plugin-native-audio` Swift source and permission defaults (`permissions/default.toml`).
- [native-ios-audio.md](./native-ios-audio.md) for device verification of the base pipeline.
- `tauri-plugin-opener` (already registered) for the Settings deep link.

## Touchpoints

`tauri-plugin-native-audio/ios/Sources/NativeAudioPlugin.swift`, `tauri-plugin-native-audio/permissions/`, `src/services/audio/*`, `src/services/recording/session.ts` (new), `src/components/audio/LearnerRecordingPanel.tsx`, `src/features/speaking/`.

## Manual device test

1. Fresh install → start recording → deny → confirm Settings guidance → enable → retry.
2. Record, press home, return → take is still replayable.
3. Start recording, trigger Siri or an incoming call → confirm clean stop.
4. Record with wired/BT headphones, unplug mid-replay → playback pauses.
5. Start then immediately stop repeatedly → no crash, no unplayable file.
