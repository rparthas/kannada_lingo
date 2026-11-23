# Human / studio phrase audio

| Field | Value |
|-------|-------|
| Status | Planned |
| Roadmap | Phase 7 |
| Priority | P1 |

## Learner outcome

“The voices sound like real Bengaluru Kannada, not robotic TTS, especially for greetings and high-traffic phrases.”

## Principles

- **Bengaluru Kannada** — natural prosody matters for trust.
- **Content as a product** — audio is versioned alongside phrases; validation in CI.

## Current state

- `npm run content:build` generates WAV via macOS TTS (Soumya) for bulk assets.
- `course.json` supports `extra_audio_assets` with `source: "ai"` / review metadata.
- Import path maps files into `audio_assets` on first launch.

## In scope

- Editorial priority list: Unit 1–4 + high-frequency items (greetings, travel, food).
- WAV format consistency (sample rate, duration_ms) enforced by `content:validate`.
- Replace or supplement TTS files while keeping stable `learning_item_id` / asset IDs.
- Document recording guidelines (pace, formal vs spoken note in content spec).

## Out of scope

- Per-learner custom voices.
- Dynamic TTS at runtime for all phrases.

## Acceptance criteria

- [ ] At least N approved human recordings (target TBD, suggest 30+) pass validation and ship in bundle.
- [ ] Phrase detail and exercises prefer human asset when `review_status: approved`.
- [ ] Fallback to existing TTS asset when human file missing (no broken playback).

## Dependencies

- Content version bump in `course.json`.
- Optional: extend validator to flag `source: human` vs `tts` for QA reports.