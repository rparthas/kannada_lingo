# Native iOS audio & recording

| Field | Value |
|-------|-------|
| Status | Implemented (device verification required) |
| Roadmap | Phase 7 (cross-cutting) |
| Priority | P0 prerequisite |

## Learner outcome

“I hear phrase audio clearly on my phone, and listen-and-repeat lets me record and replay my voice reliably.”

## Principles

- **Multimodal clarity** — audio is primary for spoken Kannada.
- **Offline-first** — playback from bundled/imported assets, not streaming.

## Current state

- **`WebAudioService`** — desktop macOS / Windows playback and recording (HTML media APIs).
- **`NativeIosAudioService`** — physical iOS via `tauri-plugin-native-audio` (AVAudioPlayer / AVAudioRecorder).
- **`configureAudioService()`** — selects the adapter at boot using `get_app_platform`.
- **`LearnerRecordingPanel`** — listen-and-repeat recording UI; permission errors surface from native layer.

## Screen lock / background

Phrase playback uses `AVAudioSession` **playback** (not background audio). **Playback stops when the screen locks** — the recording panel notes this for learners.

## In scope (done)


## Out of scope

- Speech-to-text scoring or sending recordings to a server.
- Replacing all WAV assets (see [human-phrase-audio.md](./human-phrase-audio.md)).

## Acceptance criteria

- [ ] Normal and slow playback work on physical iPhone with screen locked policy documented (if background not supported, UX explains it). — **UX copy added**; verify on device.
- [ ] Mic permission prompt is clear on your device build (store review not required).
- [ ] Record → playback → retry flow works on device for at least one `listen_repeat` exercise.

## Manual device test

1. `npm run ios:dev` on a physical iPhone.
2. Open a `listen_repeat` lesson → Play (normal + slow).
3. Record → Stop → Play my recording → Record again.
4. Deny mic once → confirm Settings guidance message → enable in Settings → retry.

## Dependencies

- [personal-release-cadence.md](./personal-release-cadence.md) for sideloaded iOS installs.
- Rust/Tauri plugin: `tauri-plugin-native-audio/` (Swift + IPC).

## Follow-on work

- [recording-reliability.md](./recording-reliability.md) — permission recovery, interruptions, navigation-safe takes.
- [speaking-practice-mode.md](./speaking-practice-mode.md) — first learner-facing mode built on this pipeline.
