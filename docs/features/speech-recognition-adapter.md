# Speech recognition adapter (on-device)

| Field | Value |
|-------|-------|
| Status | Planned |
| Roadmap | [Release 1](../constitution/roadmap_v1.md) (speech recognition) |
| Priority | P0 |
| Slice | 2 — Speak and evaluate |

## Learner outcome

“I say the phrase in Kannada and the app shows what it heard — and I know my voice never left my phone.”

## Principles

- **Privacy** — recognition runs on device only; recordings are never uploaded or transmitted.
- **Offline-first** — availability is detected, not assumed; core practice degrades to typing.
- **Sustainable engineering** — recognition is a separate service from audio playback/recording, behind a testable interface.

## Current state

- Audio is abstracted in `src/services/audio/` with `NativeIosAudioService` + `WebAudioService` + `StubAudioService`, selected by `resolveAudioServiceKind`.
- The native audio plugin already uses AVFoundation and has a Swift/Tauri command pattern to copy.
- No speech framework, no `NSSpeechRecognitionUsageDescription`, no recognition interface.

## Design

### TypeScript boundary

`src/services/speech/types.ts`:

```ts
export type SpeechAvailability =
  | "available"
  | "permission_denied"
  | "unsupported_locale"
  | "on_device_unavailable"
  | "unavailable";

export interface SpeechRecognitionResult {
  transcript: string;
  confidence?: number;
  durationMs?: number;
}

export interface SpeechRecognitionService {
  isAvailable(): Promise<SpeechAvailability>;
  requestPermission(): Promise<SpeechAvailability>;
  startRecognition(): Promise<void>;
  stopRecognition(): Promise<SpeechRecognitionResult>;
  cancelRecognition(): Promise<void>;
}
```

- Implementations: `StubSpeechService` (desktop/dev, always `unavailable`), `NativeIosSpeechService`.
- `configureSpeechService()` runs at boot next to `configureAudioService()`; `resolveSpeechServiceKind({ isTauri, platform })` is unit-tested exactly like `resolveAudioServiceKind`.
- The service may expose an optional partial-transcript subscription, but the first release may ignore partials.

### Native iOS plugin

Add `tauri-plugin-native-speech/` mirroring the native-audio plugin layout (Rust shim + Swift `Plugin` subclass + permission files), rather than adding recognition into the audio plugin. Commands:

- `speech_availability` — recognizer exists for `kn-IN`, authorization status, on-device support.
- `request_speech_permission`.
- `start_recognition` — configures `SFSpeechRecognizer(locale: kn-IN)` and a fresh `SFSpeechAudioBufferRecognitionRequest` with **`requiresOnDeviceRecognition = true`**.
- `stop_recognition` — finalizes and returns `{ transcript, confidence, durationMs }`.
- `cancel_recognition` — tears down tap/request without producing a result.

Implementation notes:

- Reuse the audio session from the recording service but do not run recognition and phrase playback simultaneously; one owner at a time.
- Install the input tap on an `AVAudioEngine`; remove it and stop the engine on every exit path.
- **Do not** fall back to server-side recognition when on-device `kn-IN` is unsupported. Return `on_device_unavailable` and let the UI offer typing. This is the concrete guarantee behind “no recordings are transmitted.”
- Add `NSSpeechRecognitionUsageDescription` to `src-tauri/Info.ios.plist`, worded like the microphone string: recognition happens on device; audio is not uploaded.
- If Apple’s recognizer reports the locale as unavailable on the target OS, `isAvailable()` must surface that rather than throwing at start.

### Fallback contract

- The UI always offers a typed answer when availability is anything other than `available`.
- A permission denial is recoverable (`requestPermission` again) and points to Settings.
- `isAvailable()` must not require a network probe; network state is irrelevant because the design forbids server recognition.

## Out of scope

- Pronunciation/phoneme scoring — transcription is not pronunciation quality.
- Continuous dictation, wake words, or voice-to-voice AI.
- Third-party or cloud STT providers.
- Recognition for languages other than `kn-IN` (English teaching text is typed).

## Acceptance criteria

- [ ] Adapter can be swapped by platform in unit tests; desktop returns a stub without throwing at import time.
- [ ] On a physical iPhone with on-device Kannada support, saying a supported phrase returns a Kannada transcript plus optional confidence.
- [ ] Turning on airplane mode does not change recognition behaviour (on-device path).
- [ ] On a device/OS where on-device `kn-IN` is unavailable, `isAvailable()` returns `on_device_unavailable` and the UI offers typing.
- [ ] Denying speech permission yields `permission_denied`; granting later recovers without app restart where iOS allows.
- [ ] Repeated start/stop cycles do not leak the audio engine or crash.
- [ ] Code review confirms `requiresOnDeviceRecognition = true` and no network upload path.
- [ ] Info.plist strings and app capabilities include the speech permission.
- [ ] Typed fallback is available in every failure mode.

## Dependencies

- iOS 15+ (already the plugin platform floor) and an OS/device where Kannada on-device recognition exists; verify on the actual phone before committing to the UX.
- [spoken-answer-evaluation.md](./spoken-answer-evaluation.md) consumes `SpeechRecognitionResult`.
- [recording-reliability.md](./recording-reliability.md) for shared audio-session ownership and permission UX patterns.

## Touchpoints

`src/services/speech/` (new), `tauri-plugin-native-speech/` (new), `src-tauri/Cargo.toml`, `src-tauri/capabilities/default.json`, `src-tauri/Info.ios.plist`, `src/app/AppShell.tsx`.

## Open decision (resolve before build)

If the physical iPhone cannot run on-device `kn-IN` recognition, choose explicitly between:

1. Ship speech as unavailable on that device and rely on typed recall (privacy preserved), or
2. Revisit the privacy rule for transcription with an explicit, documented opt-in.

Do not silently switch to server recognition.
