# Skill-specific proficiency dashboard

| Field | Value |
|-------|-------|
| Status | Planned |
| Roadmap | [Release 5 / supporting](../constitution/roadmap_v1.md) (insights) |
| Priority | P2 |
| Depends on | [speaking-aware-revision.md](./speaking-aware-revision.md) |

## Learner outcome

“I can see whether I am actually getting better at speaking, listening and recall — not just how many XP I earned.”

## Principles

- **Practical-first** — measure usable communication, not gamification.
- **Correctness** — every number has a documented formula and a test.
- **Local-first** — computed on device from local tables; no analytics service.

## Current state

- Progress screen shows aggregate mastered/learning/accuracy/attempts, XP, streak, backup.
- Release 0 adds `speaking_attempts`; Release 2 adds conversation sessions/turns; Release 5 adds `skill_progress` per dimension.
- No unaided-speaking metric, no per-skill breakdown, no conversation completion rate.

## Metrics (definitions are the spec)

| Metric | Formula | Source |
|--------|---------|--------|
| Unaided speaking rate | usable unaided speaking attempts ÷ all speaking attempts | `speaking_attempts` (`revealed_text = 0`, `counts_as_failure = 0` excluded) |
| Speaking success rate | `match` + self-rated good/easy ÷ usable speaking attempts | `speaking_attempts` |
| First-attempt success | items whose first speaking attempt was `match`/good ÷ items attempted | `speaking_attempts` |
| Listening comprehension | correct `listen_comprehension` ÷ answered | `exercise_attempts` / `skill_progress('listening')` |
| Delayed recall | `recall`/`recognition` matches on items with interval ≥ 7 days | `skill_progress` |
| Conversation completion | completed sessions ÷ started sessions | `conversation_sessions` |
| **North Star** | distinct conversation turns completed unaided | `conversation_session_turns` |

- Do not convert these into an invented 0–100 “proficiency score”. Show counts, rates and sample sizes.
- Show “not enough data yet” instead of 0 % when the denominator is below a documented threshold (e.g. 5 attempts).
- XP and streak remain visible but secondary; do not label them as learning outcomes.

## In scope

- `src/features/proficiency/ProficiencyScreen.tsx` reachable from Progress (not a new bottom tab).
- `src/domain/proficiency/calculate.ts` — pure functions taking rows, returning metrics + sample sizes; fully unit-tested.
- Rust read command `proficiency_summary` in `src-tauri/src/commands/proficiency.rs` with a single query pass per window; no N+1 per item.
- Windows: last 7 days, 30 days, all time (local date boundaries).
- Per-dimension cards: mastery counts, accuracy, attempts, weakest phrases (deep-link to speaking practice).
- Empty states that explain what to do next (e.g. “Record 5 speaking attempts to see a rate”).
- Loading and error states; works offline.

## Out of scope

- Cloud analytics, charts requiring a charting dependency unless already present.
- Social comparison or leaderboards.
- Predictive proficiency or CEFR mapping.
- Pronunciation scores (still not measured).

## Acceptance criteria

- [ ] Every displayed metric has a formula in this brief and a unit test with fixed input rows.
- [ ] Rates hide below the minimum sample threshold and show the threshold instead.
- [ ] `unusable` speaking attempts are excluded from success/failure rates but counted in total attempts.
- [ ] North Star counts distinct unaided conversation turns, not messages or sessions.
- [ ] Screen loads offline with no AI configured.
- [ ] Existing Progress screen metrics remain unchanged or are explicitly superseded with matching values.
- [ ] Query performance is acceptable on a 190-phrase, multi-year dataset (single command, indexed reads).
- [ ] No new bottom-nav item; entry point is discoverable from Progress.

## Dependencies

- `skill_progress` and attempt/session tables from Releases 0–2/5.
- Existing Progress screen and `commands/progress.rs` aggregates.
- [personal-phrasebook.md](./personal-phrasebook.md) optional deep links.

## Touchpoints

`src/features/proficiency/`, `src/domain/proficiency/calculate.ts`, `tests/unit/proficiency.test.ts`, `src/features/progress/ProgressScreen.tsx`, `src/services/api/tauri.ts`, `src-tauri/src/commands/proficiency.rs`.

## Display rule

Lead with “Successful unaided responses” and speaking/listening rates. Place XP/streak in a collapsed “activity” section. A learner should be able to answer “can I speak more than last month?” in one screen.
