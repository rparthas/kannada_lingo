# Listening comprehension

| Field | Value |
|-------|-------|
| Status | Planned |
| Roadmap | [Release 4](../constitution/roadmap_v1.md) (listening) |
| Priority | P1 |
| Migration | None (reuses `exercise_attempts` + skill progress) |

## Learner outcome

“I understand two people talking at normal speed, without reading along, and I can tell what they meant.”

## Principles

- **Multimodal clarity** — audio is the exercise; text is a post-answer reveal.
- **Bengaluru Kannada** — natural speed and reductions, not slowed classroom speech only.
- **Retention by design** — results feed revision and the skill dimensions.
- **Offline-first** — dialogues and audio bundled.

## Current state

- Single-phrase playback and `listen_identify` / `listen_repeat` exist.
- No multi-turn dialogue content model, no audio-first comprehension question, no transcript reveal flow.
- Audio assets are WAV in `content/audio/`, versioned through `content_version`.

## In scope

### 1. Content model

New exercise type `listen_comprehension` (added to `ExerciseType` and validation whitelist) backed by a dialogue payload:

```jsonc
{
  "dialogue_id": "dlg-chai-stall-01",
  "level_id": "level-1-survival",
  "difficulty": 2,
  "audio_version": 1,
  "turns": [
    { "speaker": "partner", "kannada_text": "…", "transliteration": "…", "english_meaning": "…", "audio": "conversations/chai/q1-normal.wav" },
    { "speaker": "learner", "kannada_text": "…", "audio": "conversations/chai/a1-normal.wav" }
  ],
  "question": {
    "prompt_en": "What does the customer want?",
    "choices": [
      { "text": "Tea without sugar", "correct": true },
      { "text": "Coffee with milk", "correct": false },
      { "text": "Water", "correct": false }
    ]
  },
  "transcript_version": 1
}
```

- Audio and transcript share a version; validation fails if either changes without a version bump.
- Progression ladder: single phrase → short sentence → two-turn exchange → longer everyday dialogue → natural-speed conversation.
- 20 dialogues minimum across the five roadmap situations.

### 2. Learner flow

1. Audio autoplays (normal speed); transcript hidden.
2. Replay normal / slow as needed; no text shown before answering.
3. Answer the comprehension question (or choose the appropriate next response in later items).
4. See correct/incorrect + transcript reveal with transliteration/English.
5. Optional “practice this phrase” → speaking practice.
6. Result stored and routed to the listening skill dimension.

### 3. UI

`src/features/listening/ListeningPracticeScreen.tsx` + a dialogue player component:

- One large play control, replay counter (to discourage infinite replay), slow toggle.
- Transcript locked until answered; a visible “Show transcript” after answer only.
- No auto-reveal of the answer on replay.
- Accessible labels; works without AI.

### 4. Persistence & revision

- Persist via the existing `record_exercise_attempt` path (`exercise_type = 'listen_comprehension'`, `response_json` holds selected choice + replay count).
- When [speaking-aware-revision.md](./speaking-aware-revision.md) lands, write a `listening` row in `skill_progress`; before then, keep the attempt in `exercise_attempts` so no data is lost and backfill is possible.
- Comprehension result influences scheduling only through the listening dimension, never by penalizing speaking.

### 5. Validation

- Extend `src/domain/content/validate.ts` and `scripts/validate-content.mjs`:
  - every turn has approved Kannada text, transliteration, English meaning and an existing audio file;
  - exactly one correct choice;
  - transcript/audio version match the declared item version;
  - dialogue id uniqueness.

## Out of scope

- Free-text dictation or transcription scoring of what the learner heard.
- Shadowing/pronunciation scoring.
- AI-generated dialogues.
- Video or multi-speaker spatial audio.

## Acceptance criteria

- [ ] At least 20 dialogue exercises pass `content:validate` and import with audio.
- [ ] Transcript is not visible before an answer; reveal happens only after submission.
- [ ] Normal and slow playback both work offline; replay does not reveal text.
- [ ] Every dialogue has approved transcript text versioned with its audio.
- [ ] Results persist and survive restart; a Rust test reads a stored result.
- [ ] Listening results are available to the revision layer without schema changes to `exercise_attempts`.
- [ ] Dialogues load on a fresh install from bundled content (no network).
- [ ] Accessibility: controls are labelled and usable one-handed on iPhone.

## Dependencies

- Audio content pipeline / [human-phrase-audio.md](./human-phrase-audio.md) for dialogue recordings.
- [conversation-scenarios.md](./conversation-scenarios.md) for reusable partner lines and situations.
- [speaking-aware-revision.md](./speaking-aware-revision.md) for dimension routing (soft dependency; attempts persist regardless).

## Touchpoints

`content/curriculum/dialogues/` (new), `content/schemas/dialogue.schema.json`, `src/features/listening/`, `src/components/exercises/ExerciseRenderer.tsx` (or a dedicated player), `src/domain/content/validate.ts`, `scripts/validate-content.mjs`, `src-tauri/src/content/import.rs`.

## Test table

| Case | Expected |
|------|----------|
| Audio file missing | validation error |
| Transcript edited without version bump | validation error |
| Choice list with 0 or 2 correct | validation error |
| Replay before answer | no transcript in DOM |
| Offline start | dialogue plays from bundle |
