# Native iOS audio & recording

| Field | Value |
|-------|-------|
| Status | Planned |
| Roadmap | Phase 7 (cross-cutting) |
| Priority | P1 |

## Learner outcome

“I hear phrase audio clearly on my phone, and listen-and-repeat lets me record and replay my voice reliably.”

## Principles

- **Multimodal clarity** — audio is primary for spoken Kannada.
- **Offline-first** — playback from bundled/imported assets, not streaming.

## Current state

- `WebAudioService` drives playback in `src/services/audio/webAudioService.ts`.
- `LearnerRecordingPanel` and `listen_repeat` exercises depend on web audio APIs inside the Tauri webview.
- Device smoke explicitly calls out audio and mic checks.

## In scope

- Adapter interface already implied by `src/services/audio/types.ts`: iOS-native playback when web APIs are insufficient (latency, background, session category).
- Recording pipeline for `listen_repeat` with clear permission UX and error states.
- Regression tests on desktop; manual device matrix for sim vs device.

## Out of scope

- Speech-to-text scoring or sending recordings to a server.
- Replacing all WAV assets (see [human-phrase-audio.md](./human-phrase-audio.md)).

## Acceptance criteria

- [ ] Normal and slow playback work on physical iPhone with screen locked policy documented (if background not supported, UX explains it).
- [ ] Mic permission prompt is clear on your device build (store review not required).
- [ ] Record → playback → retry flow works on device for at least one `listen_repeat` exercise.
- [ ] Desktop `tauri dev` behavior unchanged or gracefully degraded with visible message.

## Dependencies

- [personal-release-cadence.md](./personal-release-cadence.md) for sideloaded iOS installs.
- May require Rust/Tauri plugin or WKWebView bridge — follow [techstack](../constitution/techstack.md) service-layer rules (no audio logic in React beyond UI).