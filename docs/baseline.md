# Shipped baseline (feature inventory)

Capabilities **implemented in the repository** as of the current Level 1 Survival release. Status labels match [roadmap](constitution/roadmap.md): *complete* in repo; device-only or store steps may still be open.

## Navigation & shell

| Feature | Routes / UI | Backend |
|---------|-------------|---------|
| Bottom tab nav | `BottomNav` — Home, Learn, Practice, Progress | — |
| App bootstrap | `AppShell` — `init_app`, onboarding gate | `commands/app.rs` |
| Settings (secondary) | `/settings` (linked from Home gear and Progress) | learner profile commands |

## Onboarding

| Feature | Notes |
|---------|--------|
| First-run welcome | Optional display name → `completeOnboarding` |
| Guided onboarding & goals | Sets daily XP goal + optional Kannada script preference |
| Content import on empty DB | Bundled JSON + WAV on first launch |

## Home (Today)

| Feature | Notes |
|---------|--------|
| Daily XP goal progress | Bar + percent vs `dailyGoalXp` |
| Streak | Days with goal met |
| Continue lesson | Resume `continueLessonId` |
| Due revision count | Link to Practice |
| Settings link | Gear/“Settings” link in Home header to `/settings` |

## Learn

| Feature | Notes |
|---------|--------|
| Level selector | **Level 1 Survival** + **Level 2 Everyday Conversations** |
| Lesson list | Completion markers, estimated minutes |
| Unit map & learning path UX | Grouped lessons by unit title, “Recommended next” highlight |
| Lesson player | Resume, review mode, all exercise types |

### Exercise types (domain)

Defined in `src/domain/exercises/evaluate.ts` and rendered in `ExerciseRenderer`:

- `listen_identify`, `vocabulary_flashcard`, `kannada_to_english`, `english_to_kannada`
- `sentence_construction`, `fill_blank`, `listen_repeat`, `scripted_conversation`

## Practice & retention

| Feature | Notes |
|---------|--------|
| Review queue | SM-2-inspired scheduling (`src/domain/revision/sm2.ts`) |
| Mixed recall drills | Exercise renderer + typed recall fallback |
| XP on attempts | `domain/progress/xp.ts` |

## Progress & phrases

| Feature | Notes |
|---------|--------|
| Aggregate stats | Mastered / learning / accuracy / attempts |
| Backup export | ZIP + manifest + SHA-256 from Progress |
| Phrase detail | Script, transliteration, meaning, audio, attempt history |
| Mock AI grammar | Phrase detail; production uses `unconfigured` stub |
| Phrase search & browse | `/phrase-search` — search by English, transliteration, Kannada; links to phrase detail |

## Audio

| Feature | Notes |
|---------|--------|
| Bundled WAV (slow/normal) | Imported to `audio_assets` |
| Phrase playback | `WebAudioService`, `PhraseAudioControls` |
| Learner recording hooks | `LearnerRecordingPanel` (verify on device) |

## Settings & data safety

| Feature | Notes |
|---------|--------|
| Daily goal editor | 10–500 XP |
| Backup restore | Validate manifest → confirm → replace DB |
| Integrity | Checksum rejection tested (Rust + TS paths) |

## Content

| Metric | Value |
|--------|-------|
| Levels | 2 (Survival + Everyday Conversations) |
| Units | 21 (`content/curriculum/specs/units/`) |
| Lessons | 42 |
| Phrases | 190 |
| Content version | See `content/curriculum/specs/course.json` |
| Validation | `npm run content:validate` |
| Content import (no wipe) | `npm run content:import` |

## Explicit non-features (by design)

Per [mission](constitution/mission.md) boundaries:

- User accounts, cloud sync, social leaderboards
- Autonomous AI-generated lesson content in production
- Formal certification or literary Kannada track
- Android / web-only deployment for core learning

Future work for these areas requires an explicit product direction change.