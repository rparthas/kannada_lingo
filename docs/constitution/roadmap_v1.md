# Kannada Quest — Speaking-First Roadmap

## Product direction

Build a personal Kannada speaking coach for everyday conversations in Bengaluru.

The primary learning loop is: **listen → understand → speak → get feedback → retain**.

This roadmap sequences the next product work. It does not replace the mission, platform boundaries, or engineering rules in the rest of the [constitution](./mission.md).

## Constraints

- Personal, single-learner use; iPhone first, with iPad support.
- English is the teaching language; spoken Bengaluru Kannada is the subject.
- Core lessons, practice, and revision work offline.
- Human recordings are used where quality matters; generated audio can supplement them.
- AI may assist with context and feedback, but never becomes the source of canonical curriculum.
- No mandatory account, cloud sync, client-side API key, or server-side speech-to-text for the core loop.

## Priority order

| Capability | Priority | Learner outcome |
|---|---:|---|
| Reliable recording and speaking practice | P0 | I can repeat a phrase, replay myself, and keep the attempt. |
| On-device recognition and answer feedback | P0 | I know whether my response matched the intended phrase. |
| Deterministic conversation practice | P0 | I can respond in familiar everyday situations. |
| Speaking-aware revision and listening | P1 | Practice returns the skills I still need. |
| Optional AI conversation coach | P1 | I can extend a bounded scenario when I choose to be online. |
| Dashboard, phrasebook, and navigation polish | P2 | I can see progress and find what matters to me. |

Recognition, recall, and pronunciation are different signals. Speech-to-text can establish recognition and support recall feedback; it must not be presented as pronunciation scoring.

## Delivery sequence

### 0. Verify the device foundation

Before new speech features, complete the physical-device checks in the [Phase 0 milestone](https://github.com/rparthas/kannada_lingo/milestone/1): playback, microphone permission recovery, repeated recording/playback, interruptions, and navigation-safe takes. The runbook is [DEVICE_AUDIO_VERIFICATION.md](../DEVICE_AUDIO_VERIFICATION.md).

### 1. Speak and record

Deliver [recording reliability and speaking practice](https://github.com/rparthas/kannada_lingo/milestone/2).

- Play a phrase, hide the answer, record, replay, retry, and self-rate.
- Persist local attempt history and speaking counters.
- Keep recordings local and make their retention clear.

**Exit:** speaking practice is useful offline even without recognition.

### 2. Speak and evaluate

Deliver the [on-device speech recognition adapter and spoken-answer evaluation](https://github.com/rparthas/kannada_lingo/milestone/3).

- Detect availability for `kn-IN`; provide typed fallback.
- Normalize Kannada script and supported transliteration variants.
- Compare the transcript with accepted answers, explain missing or substituted words, and allow another attempt.
- Do not penalize an unavailable or failed recognition service as a learner mistake.

**Exit:** a learner receives reliable, privacy-preserving feedback on a spoken response.

### 3. Speak in context

Deliver the [deterministic conversation engine and five everyday scenarios](https://github.com/rparthas/kannada_lingo/milestone/4).

- Start with content-defined branching, accepted responses, hints, and local completion history.
- Cover auto rides, restaurants, apartment security, shops, and neighbours.
- Reuse curriculum phrases where appropriate without forcing every interaction into multiple choice.

**Exit:** learners can complete offline conversations with more than one valid response path.

### 4. Retain and understand

Deliver [listening comprehension and speaking-aware revision](https://github.com/rparthas/kannada_lingo/milestone/5).

- Track recognition, recall, speaking, and listening separately.
- Prioritize weak speaking and listening skills without discarding existing schedules.
- Keep scheduling deterministic and domain-tested.

### 5. Extend intentionally

Add the [optional AI conversation coach, proficiency dashboard, and personal phrasebook](https://github.com/rparthas/kannada_lingo/milestone/6).

AI is opt-in, disabled by default, and receives recognized text rather than recordings by default. Its suggestions remain distinct from canonical content.

## Dependency and migration ledger

This roadmap owns the planned migration numbers. Reserve them in this order to avoid collisions:

| Migration | Purpose |
|---|---|
| `004_speaking_attempts` | Local speaking attempts |
| `005_speaking_evaluation` | Transcript and answer-evaluation result |
| `006_conversation_sessions` | Conversation sessions and turns |
| `007_skill_progress` | Per-skill progress and revision inputs |
| `008_saved_phrases` | Personal phrasebook |

These are planned names, not migrations that already exist. Add each only with the feature that needs it, migration tests, and backup/restore coverage.

## Supporting work

- [Human phrase audio](https://github.com/rparthas/kannada_lingo/milestone/7) for high-frequency phrases.
- Content updates and ongoing Level 2 curriculum work.
- [UX enhancements](https://github.com/rparthas/kannada_lingo/milestone/9) — search, learning-path UX, and settings — when daily use exposes friction.
- [RELEASE.md](../RELEASE.md) for weekly installs and data safety.

## Measures of success

Use learning signals rather than XP as the primary product measures:

- unaided spoken responses;
- first-attempt success and delayed recall;
- listening-comprehension success;
- completed conversation turns without a displayed answer.

Establish a personal baseline before setting targets. Do not infer proficiency from XP alone.

## Explicit deferrals

- Phoneme-level pronunciation scoring.
- Real-time voice-to-voice AI.
- Multiple AI providers or complex model routing.
- Cloud sync, social features, Android, and dynamic curriculum generation.

## Source of truth

This roadmap sets sequencing. [GitHub Issues](https://github.com/rparthas/kannada_lingo/issues) are the delivery board and define scope and acceptance criteria; [FEATURE_WORKFLOW.md](../FEATURE_WORKFLOW.md) explains how to use them. [baseline.md](../baseline.md) records what has shipped.
