# Spoken answer evaluation & feedback

| Field | Value |
|-------|-------|
| Status | Planned |
| Roadmap | [Release 1](../constitution/roadmap_v1.md) (speaking feedback) |
| Priority | P0 |
| Slice | 2 — Speak and evaluate |
| Migration | `005_speaking_evaluation.sql` |

## Learner outcome

“After I speak, I see whether I was understood, which word was missing, and what to try next — and a recognizer hiccup never counts against me.”

## Principles

- **Correctness of evaluation** — deterministic comparison, no claims beyond recognition + recall.
- **Trust** — unusable audio is a system failure, not a learner failure.
- **Multimodal clarity** — feedback in English, target phrase in Kannada with transliteration as scaffolding.
- **Test-driven delivery** — normalization and comparison are pure domain functions with unit tests.

## Current state

- `src/domain/exercises/evaluate.ts` has `normalizeFreeText`, `normalizeTransliteration` (NFD + strip combining marks), `evaluateExactOrAlternatives`, `evaluateKannadaRecall`.
- `accepted_answers` exists on `learning_items` and is surfaced in DTOs.
- No transcript path, no word-level diff, no notion of an unusable attempt.
- SM-2 grade mapping exists in `gradeFromAttempt`, but every attempt currently counts.

## Three evaluation levels (do not conflate)

| Level | Question | This release |
|-------|----------|--------------|
| Recognition | Did the system hear Kannada text? | Speech-to-text transcript |
| Recall | Did the learner produce the expected phrase? | Normalized answer comparison |
| Pronunciation | Was it natural/accurate? | **Not implemented; never inferred from STT** |

Copy for feedback must say “I heard …” / “that matched …”, never “your pronunciation is 80%”.

## In scope

### 1. Normalization — `src/domain/speech/normalize.ts`

- Unicode NFC/NFD consistency for Kannada script; strip zero-width joiners/non-joiners and punctuation (`।`, `.`, `?`, `!`, quotes, danda).
- Collapse whitespace; case-fold Latin input.
- Transliteration variants for comparison only (never rewrite displayed content): long/short vowels (`ā/a`, `ī/i`, `ū/u`, `ē/e`, `ō/o`), retroflex/dental sibilants (`ś/ṣ/s`, `c/ch`), `ṇ/n`, `ḷ/l`, aspiration variants (`bh/b`, `dh/d`, …) as an explicit, tested map.
- Kannada script alternatives where they are genuinely equivalent in spoken content (e.g. anusvara vs homorganic nasal) only when covered by tests and approved examples; no fuzzy “sounds like” heuristics.
- Reuse `normalizeTransliteration` where possible; keep one canonical normalizer exported for both script and roman input.

### 2. Comparison — `src/domain/speech/evaluate.ts`

```ts
export type SpokenEvaluationStatus = "match" | "near" | "mismatch" | "unusable";

export interface SpokenEvaluation {
  status: SpokenEvaluationStatus;
  matchedVariant?: string;
  wordDiff: { missing: string[]; extra: string[]; substituted: Array<{ expected: string; heard: string }> };
  countsAsFailure: boolean;
}
```

- `match` — normalized transcript equals the canonical transliteration, Kannada text, or an accepted answer.
- `near` — token multiset/sequence comparison finds a small edit (missing, extra, or substituted token); surfaced as “almost — you missed X”.
- `mismatch` — usable speech that does not match; counts as a failure.
- `unusable` — empty transcript, confidence below a documented threshold, or recognizer error. `countsAsFailure = false`; do not change SM-2.
- Word order: compare as a sequence first, then as a multiset for short phrases so normal Kannada reordering is not punished. Document which applies at each phrase length.
- Typed answers use the same evaluator with `source: "typed"`; typed input is not penalized for the recognizer.

### 3. Feedback — `src/domain/speech/feedback.ts`

- Pure function from evaluation + phrase to a short English message and next action:
  - `match` → confirm, offer natural-speed replay, suggest repeating without transliteration.
  - `near` → name the missing/substituted token, offer slow replay, allow retry.
  - `mismatch` → offer listen again, reveal after attempt, allow retry or type.
  - `unusable` → “I couldn’t catch that — try again or type it”; no failure recorded.
- Feedback must state what was recognized and must not diagnose pronunciation.

### 4. Persistence — `005_speaking_evaluation.sql`

Extend the table created by [speaking-practice-mode.md](./speaking-practice-mode.md):

```sql
ALTER TABLE speaking_attempts ADD COLUMN transcript TEXT;
ALTER TABLE speaking_attempts ADD COLUMN transcript_confidence REAL;
ALTER TABLE speaking_attempts ADD COLUMN evaluation_status TEXT
  CHECK (evaluation_status IN ('match','near','mismatch','unusable'));
ALTER TABLE speaking_attempts ADD COLUMN evaluation_json TEXT;
```

- `source` already distinguishes `self | typed | speech`.
- Command `record_speaking_attempt` accepts the optional transcript/evaluation; for `unusable`, persist the attempt row but skip SM-2 and XP.
- Phrase detail gains a compact “Speaking attempts” list (heard text, status, date) next to existing recent attempts; keep recordings separate and never render a recording without a clear local-only note.

### 5. Learner flow

1. Play partner/phrase audio.
2. Record + recognize (or type).
3. Evaluate → feedback card.
4. Retry (new attempt row) or reveal + continue.
5. Only usable attempts feed the schedule.

## Out of scope

- Pronunciation scoring, fluency/intonation metrics, phoneme alignment.
- LLM-based semantic grading (Release 3 may *suggest*, but not replace this evaluator).
- Storing or uploading audio for evaluation.

## Acceptance criteria

- [ ] `normalize` unit tests cover Kannada punctuation, ZWJ/ZWNJ, whitespace, Latin case, and every documented transliteration variant.
- [ ] Accepted answers and canonical variants all evaluate as `match`.
- [ ] A single missing word evaluates as `near` with that word in `wordDiff.missing`.
- [ ] Word-order variation for short phrases does not produce `mismatch`.
- [ ] Empty or low-confidence transcripts evaluate as `unusable` and do **not** change SM-2 or XP.
- [ ] Typed fallback reaches the same evaluation and persistence path.
- [ ] Attempts persist transcript, confidence, status and JSON; a Rust test reads them back.
- [ ] Feedback copy never claims pronunciation accuracy.
- [ ] Works offline; no transcript or recording is transmitted.

## Dependencies

- [speech-recognition-adapter.md](./speech-recognition-adapter.md) for transcripts.
- [speaking-practice-mode.md](./speaking-practice-mode.md) for the attempt table, screen and SM-2 integration.
- Migration `005` registered in `src-tauri/src/db/migrations.rs`.

## Touchpoints

`src/domain/speech/`, `tests/unit/speech-evaluate.test.ts` (new), `src/features/speaking/`, `src/features/phrases/PhraseDetailScreen.tsx`, `src/services/api/tauri.ts`, `src-tauri/src/commands/speaking.rs`, `src-tauri/migrations/005_speaking_evaluation.sql`.

## Test table

| Case | Expected |
|------|----------|
| `namaskara` vs `namaskāra` | match |
| `namaskar` (missing final vowel) | match only if a tested variant exists, else near |
| `namaskara` vs `dhanyavada` | mismatch |
| `""` / confidence 0.05 | unusable, no schedule change |
| Kannada script with danda/punctuation | match after normalization |
| Accepted English meaning submitted when recall expected | mismatch (wrong level) |
