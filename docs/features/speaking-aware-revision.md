# Speaking-aware revision engine

| Field | Value |
|-------|-------|
| Status | Planned |
| Roadmap | [Release 5](../constitution/roadmap_v1.md) (retention) |
| Priority | P1 |
| Migration | `007_skill_progress.sql` |

## Learner outcome

“Revision makes me speak, listen and recall — not just tap answers — and the phrases I stumble on when speaking come back sooner.”

## Principles

- **Retention by design** — keep SM-2; extend the signals, do not replace the scheduler.
- **Correctness** — scheduling stays deterministic and unit-tested.
- **Trust** — a recognizer failure is not a learner failure.
- **Local-first** — no cloud scheduling.

## Current state

- One progress row per phrase (`learner_item_progress`) with ease, interval, repetitions, mastery and next review.
- `src/domain/revision/sm2.ts` is pure and tested; `gradeFromAttempt` converts correctness/confidence into a grade.
- Practice mixes exercise types but has no per-skill history and no session composition rule.
- Release 1 adds `speaking_attempts` with `counts_as_failure`; Release 2 adds conversation turns; Release 4 adds listening attempts.

## Design

### 1. Skill dimensions

`skill_progress` (migration `007`) — one row per phrase × dimension:

```sql
CREATE TABLE skill_progress (
  learning_item_id TEXT NOT NULL REFERENCES learning_items(id),
  skill_dimension TEXT NOT NULL
    CHECK (skill_dimension IN ('recognition','recall','speaking','listening')),
  attempts INTEGER NOT NULL DEFAULT 0,
  correct_attempts INTEGER NOT NULL DEFAULT 0,
  unusable_attempts INTEGER NOT NULL DEFAULT 0,
  ease_factor REAL NOT NULL DEFAULT 2.5,
  interval_days INTEGER NOT NULL DEFAULT 0,
  repetitions INTEGER NOT NULL DEFAULT 0,
  next_review_at TEXT,
  mastery_status TEXT NOT NULL DEFAULT 'new',
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  PRIMARY KEY (learning_item_id, skill_dimension)
);
```

Backfill (must not reset schedules):

```sql
INSERT INTO skill_progress (learning_item_id, skill_dimension, attempts, correct_attempts,
  ease_factor, interval_days, repetitions, next_review_at, mastery_status, updated_at)
SELECT learning_item_id, 'recognition', attempts, correct_attempts,
  ease_factor, interval_days, repetitions, next_review_at, mastery_status, updated_at
FROM learner_item_progress
WHERE attempts > 0;
```

- Keep `learner_item_progress` as the compatibility view for existing Home/Progress/phrase-detail queries until they are migrated. A phrase can be mastered in recognition and still be `learning` in speaking.
- Dimension routing:

| Signal source | Dimension |
|---------------|-----------|
| `listen_identify`, `vocabulary_flashcard`, multiple-choice | recognition |
| typed `english_to_kannada` / recall drills | recall |
| speaking attempts (`speaking` source, usable or self-rated) | speaking |
| `listen_comprehension` dialogues | listening |

- One attempt updates one dimension; no cross-dimension penalty. A speaking `unusable` increments `unusable_attempts` only and leaves ease/interval untouched.

### 2. Deterministic session builder

`src/domain/revision/session.ts`:

```ts
export interface RevisionMix { speaking: number; listening: number; recognition: number; conversation: number }

export function buildRevisionSession(input: {
  dueItems: Array<{ itemId: string; dimension: SkillDimension; nextReviewAt: string; weakness: number }>;
  mix?: RevisionMix;      // default 40/25/20/15
  seededDate: string;     // YYYY-MM-DD, local
  size: number;           // default 10
}): RevisionPlanItem[];
```

- Default mix 40 % speaking, 25 % listening, 20 % recognition, 15 % conversation; configuration lives in `app_settings`, not hard-coded UI.
- Selection priority: due first, then weakest (lowest accuracy / most `needs_practice`), then newest; ties broken deterministically by seeded date + item id.
- No `Math.random`, no wall-clock reads inside the builder; the caller injects the local date (the existing local-time scheduling convention).
- Conversation slots deep-link to a scenario when one is available; if no scenarios/dialogues exist, redistribute deterministically to speaking/recognition rather than showing an empty slot.
- If a dimension has no reviewable items, redistribute its share and record that in the plan (UI can explain the mix).

### 3. Score & grade mapping

- Reuse `scheduleReview` and `gradeFromAttempt`.
- `unusable` → no `scheduleReview` call.
- Self-rated speaking (Release 0) → grade from confidence/difficulty as today.
- Objective spoken evaluation (Release 1) → `match` 4/5 (5 when unaided), `near` 3, `mismatch` 0/1. Preserve existing `wasDifficult` behaviour.
- XP stays as-is unless a separate decision changes it; dimension writes must not double-award XP.

### 4. UI

- Practice screen shows the planned mix and why a phrase appears (“weak when speaking” is enough; no pseudo-science labels).
- Home due count remains the union of due dimensions, deduplicated per phrase for display but not for scheduling.
- Per-phrase detail can show dimension chips (Recognition / Recall / Speaking / Listening) with mastery states.

## Out of scope

- Replacing SM-2, FSRS, or ML-tuned intervals.
- Cross-device review history.
- Anki import/export.
- Pronunciation-based scheduling.

## Acceptance criteria

- [ ] Migration backfills recognition rows without changing any existing `next_review_at`, ease or interval (Rust migration test).
- [ ] Practice after migration still shows the same due items for a pre-existing learner.
- [ ] Speaking, listening and recognition attempts write separate dimension rows.
- [ ] A speaking `unusable` attempt never lowers ease/interval or counts as incorrect.
- [ ] Session builder is deterministic for the same inputs; unit tests cover mix, redistribution, weakness priority and dedupe.
- [ ] A phrase mastered in recognition but weak in speaking is selected for speaking before another recognition item.
- [ ] Existing SM-2 unit tests remain green; new tests cover dimension routing and grade mapping.
- [ ] No network dependency.

## Dependencies

- [speaking-practice-mode.md](./speaking-practice-mode.md), [spoken-answer-evaluation.md](./spoken-answer-evaluation.md), [listening-comprehension.md](./listening-comprehension.md), [conversation-engine.md](./conversation-engine.md).
- Migration `007`; update `record_exercise_attempt` / `record_speaking_attempt` / conversation completion writes.
- [proficiency-dashboard.md](./proficiency-dashboard.md) reads these rows.

## Touchpoints

`src/domain/revision/session.ts` (new), `src/domain/revision/sm2.ts`, `src/features/practice/PracticeScreen.tsx`, `src/features/home/HomeScreen.tsx`, `src/features/phrases/PhraseDetailScreen.tsx`, `src-tauri/src/commands/progress.rs`, `src-tauri/src/commands/speaking.rs`, `src-tauri/migrations/007_skill_progress.sql`.

## Migration order note

Apply `004` → `005` → `006` → `007` in order. `007` is safe to ship only after Release 0–2 attempt writes exist, otherwise dimension rows will be empty but harmless.
