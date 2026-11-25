# Speaking practice mode

| Field | Value |
|-------|-------|
| Status | Planned |
| Roadmap | [Release 0A/0C](../constitution/roadmap_v1.md) (speaking foundation) |
| Priority | P0 |
| Slice | 1 — Speak and record |
| Migration | `004_speaking_attempts.sql` |

## Learner outcome

“I hear a phrase, say it out loud without reading, hear my own take, and rate how it felt — then the phrase comes back when I need it.”

## Principles

- **Practical-first** — speaking is the exercise, not an optional extra after a quiz.
- **Multimodal clarity** — audio first; script, transliteration and English are *scaffolding that can be hidden*.
- **Retention by design** — every spoken attempt feeds the existing SM-2 scheduler.
- **Local-first / offline-first** — attempts and recordings stay on device; the mode works with no network.

## Current state

- `listen_repeat` in `ExerciseRenderer` already combines `PhraseAudioControls` with `LearnerRecordingPanel` and a three-way self-rating (**Needs practice / Good / Easy**).
- `gradeFromAttempt` in `src/domain/revision/sm2.ts` maps correctness + confidence to a review grade.
- `record_exercise_attempt` (`src-tauri/src/commands/progress.rs`) persists attempts, XP and `learner_item_progress`.
- Gaps: the flow always shows the phrase text; there is no answer-hidden recall step; the recording path lives only in component state; no dedicated speaking entry point; progress counters do not separate speaking.

## In scope

### 1. Dedicated mode

- New route `/practice/speaking` and screen `src/features/speaking/SpeakingPracticeScreen.tsx`, launched from Practice and Home (“Speak today”).
- Item pool: learned/review-due items from `learner_item_progress` + `review_schedule`; no curriculum file changes required. Optional later: `speaking_recall` exercise type for lesson embedding.
- Session of 5–10 phrases, then a short summary.

### 2. Exercise phases (per phrase)

1. **Listen** — normal-speed audio autoplays; a slow replay is available.
2. **Conceal** — Kannada script, transliteration and English stay hidden.
3. **Speak** — record (reuse the recording state machine from [recording-reliability.md](./recording-reliability.md)); a typed “I said it” path is *not* part of this release.
4. **Replay** — play the learner take; retry without losing the previous attempt.
5. **Reveal + self-rate** — show script/transliteration/meaning, then Needs practice / Good / Easy.
6. **Schedule** — write a speaking attempt and apply SM-2 with `gradeFromAttempt({ isCorrect, selfAssessedConfident })`.
7. **Next** — no forced reveal on the next phrase.

### 3. Attempt persistence

`004_speaking_attempts.sql` (forward-compatible with Release 1):

```sql
CREATE TABLE speaking_attempts (
  id TEXT PRIMARY KEY,
  learning_item_id TEXT NOT NULL REFERENCES learning_items(id),
  exercise_id TEXT REFERENCES exercise_definitions(id),
  source TEXT NOT NULL DEFAULT 'self' CHECK (source IN ('self','typed','speech')),
  self_rating TEXT CHECK (self_rating IN ('needs_practice','good','easy')),
  revealed_text INTEGER NOT NULL DEFAULT 1,
  recording_path TEXT,
  duration_ms INTEGER,
  is_correct INTEGER,
  counts_as_failure INTEGER NOT NULL DEFAULT 1,
  attempted_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX idx_speaking_attempts_item ON speaking_attempts(learning_item_id);
```

- New command `record_speaking_attempt` in `src-tauri/src/commands/speaking.rs` (registered in `commands/mod.rs`), or an added input variant in `progress.rs` — prefer a separate module to keep Release 1 evaluation isolated.
- Audio files remain separate from attempts; `recording_path` is nullable and pruned per the retention rule in recording-reliability.

### 4. Speaking progress counters

- Distinct phrases spoken, attempts, self-rated difficulty, and “needs more practice” (latest rating `needs_practice` or ≥2 attempts without `good`/`easy`).
- Read via a command; surfaced on the speaking summary and later in [proficiency-dashboard.md](./proficiency-dashboard.md).
- No XP overhaul: keep existing `listen_repeat` XP weights unless a deliberate change is specified.

### 5. UX details

- Answer-hidden state must survive re-render, retry and app backgrounding within the session.
- Large, thumb-reachable record/stop/replay controls; visible recording indicator and elapsed time.
- Screen-lock policy copy is shown once per session (playback stops when locked; documented in [native-ios-audio.md](./native-ios-audio.md)).
- If audio playback is unavailable, the phrase cannot silently become a reading exercise — show a clear blocked state.

## Out of scope

- Speech recognition, transcripts, pronunciation scoring (Release 1 → [speech-recognition-adapter.md](./speech-recognition-adapter.md), [spoken-answer-evaluation.md](./spoken-answer-evaluation.md)).
- AI-generated phrases or feedback.
- New curriculum content or new units.

## Acceptance criteria

- [ ] A learner can complete a 5-phrase speaking session end-to-end on a physical iPhone.
- [ ] Script, transliteration and meaning are hidden until after the recording step.
- [ ] Record → stop → replay → retry works; a second take does not delete the first attempt row.
- [ ] Each rated take persists to `speaking_attempts` with `learning_item_id`, `self_rating`, `revealed_text` and timestamp.
- [ ] SM-2 state for the phrase changes using the existing scheduler; no new scheduling algorithm.
- [ ] Leaving the screen and returning within the session preserves the current take and phase.
- [ ] Session works with airplane mode on and no AI/network configured.
- [ ] Unit tests cover phase transitions and grade mapping; a Rust test covers attempt insert + schedule read-back.
- [ ] Denying then granting the microphone does not lose the current phrase (see recording-reliability).

## Dependencies

- Device verification from [native-ios-audio.md](./native-ios-audio.md) (playback + recording on the physical phone).
- [recording-reliability.md](./recording-reliability.md) for navigation-safe recording state.
- Migration `004` applied through `src-tauri/src/db/migrations.rs`.

## Touchpoints

`src/features/speaking/`, `src/features/practice/PracticeScreen.tsx`, `src/components/audio/LearnerRecordingPanel.tsx`, `src/domain/revision/sm2.ts`, `src/services/api/tauri.ts`, `src-tauri/src/commands/speaking.rs`, `src-tauri/migrations/004_speaking_attempts.sql`.

## Manual device test

1. `npm run ios:dev` on the iPhone → Practice → Speaking.
2. Confirm no text before the attempt; record two takes; replay both; rate one.
3. Background the app mid-session and return; confirm the phrase and take survive.
4. Enable airplane mode; repeat once; confirm the attempt still saves.
5. Compare today’s speaking count and due date against the Progress / phrase detail views.
