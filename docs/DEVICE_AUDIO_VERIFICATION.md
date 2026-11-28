# Device audio verification runbook

Closes the Phase 0 checks tracked in issues **#1**, **#2**, and **#3**.

These checks must run on a **physical iPhone or iPad**. The simulator can show the
screens, but it cannot verify speaker routing, the system microphone prompt, or
screen-lock behaviour.

## Before you start

- iPhone/iPad with Developer Mode enabled.
- Xcode signed in with the Apple ID that owns `APPLE_DEVELOPMENT_TEAM`.
- The phone unlocked and either plugged in or paired on the same Wi-Fi network.
- App built from the current `main` branch.

```bash
npm install
npm run build
npm run ios:dev          # installs and launches on the connected device
```

If signing fails, open `src-tauri/gen/apple/kannada-quest.xcodeproj`, select the
`kannada-quest_iOS` target, and enable automatic signing.

Check that the device is visible before building:

```bash
xcrun devicectl list devices
```

`Connection: available` means the phone is ready.

## Check 1 — Normal and slow playback

1. Open any lesson that contains a `listen_repeat` exercise.
2. Tap **Play**. The phrase should play once at a natural pace.
3. Tap **slow**. Tap **Play** again. The phrase should play slower and stay
   intelligible.
4. Tap **Replay**. It should restart from the beginning.
5. Lock the phone while a phrase is playing.

Expected:

- Normal playback is clear and starts within about one second.
- Slow playback is slower than normal, not distorted or half speed.
- Replay restarts the phrase.
- Playback stops when the screen locks. The app does not keep playing in the
  background. The recording panel explains this before the learner records.

Screen-lock policy: the app uses `AVAudioSession` category `playback` without
the `audio` background mode. iOS therefore suspends playback when the screen
locks. This is intentional; the app is for active practice, not background
listening.

## Check 2 — Microphone permission prompt

1. If the app already has microphone permission, remove it first:
   **Settings → Kannada Quest → Microphone → Off** (or delete and reinstall).
2. Return to the `listen_repeat` exercise and tap **Record**.

Expected:

- iOS shows the system prompt with this text:
  > Kannada Quest uses the microphone only while you record your pronunciation
  > for listen-and-repeat practice. Recordings stay on your device.
- **Allow** starts the recording.
- **Don't Allow** shows this in-app guidance:
  > Microphone access is off. Open Settings → Kannada Quest and turn on
  > Microphone, then try again.
- After enabling Microphone in Settings and returning to the app, tapping
  **Record** works without restarting the app.

## Check 3 — Record, play back, retry

1. In a `listen_repeat` exercise, tap **Record**.
2. Say the phrase. Tap **Stop**.
3. Tap **Play my recording**. You should hear your own take.
4. Tap **Record again**. Record a second take and stop.
5. Tap **Play my recording** again.

Expected:

- The first take is saved locally and can be replayed.
- The second take does not overwrite the first file. Each take gets a new
  `learner_recordings/<uuid>.m4a` file.
- While the microphone is recording, **Play my recording** is disabled, so a
  playback cannot interrupt the take.
- Starting a recording stops any phrase audio that is still playing.
- No audio leaves the device.

## Sign-off

Record the result here or in the GitHub issue.

| Check | Device | iOS | Result | Date |
|-------|--------|-----|--------|------|
| 1 — normal/slow playback, screen lock | | | | |
| 2 — mic prompt and Settings recovery | | | | |
| 3 — record, play, retry | | | | |

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `Connection: unavailable` in `devicectl` | Unlock the phone, accept **Trust**, or connect the cable. |
| No audio at all | Check the silent switch, volume, and whether Bluetooth headphones are connected. |
| Recording is silent | Confirm Microphone is on in Settings and no other app is using the mic. |
| `Audio file is missing` | Run `npm run content:build` and reinstall the app. |
| Permission prompt never appears | Delete the app, reinstall, and tap **Record** again. |

## Automated coverage

The JavaScript side of this flow is covered by:

- `tests/unit/native-audio-service.test.ts` — path resolution, normal/slow rate
  selection, recording result mapping, replay, and permission errors.
- `tests/unit/learner-recording-panel.test.tsx` — record → play → retry, replay
  disabled while recording, and permission/stop error messages.

The Swift plugin is compiled by `npm run ios:build -- --ci --target aarch64-sim`.
Physical audio routing and the system prompt still need the manual checks above.
