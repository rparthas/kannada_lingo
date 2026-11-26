# Feature planning

This folder turns [product vision](../vision.md), [mission](../constitution/mission.md), and [roadmap](../constitution/roadmap.md) into **buildable feature briefs**. Each brief states learner value, scope, alignment with constitution principles, and acceptance criteria.

## Operating mode (solo, personal)

- **No App Store** — you ship to yourself from this repo about **every 7 days**.
- **Governance doc:** [personal-release-cadence.md](./personal-release-cadence.md)
- App Store brief is [deferred](./ios-app-store-release.md).

## How to use

1. Pick work from the **speaking-first wave** below, then the supporting backlog.
2. Open the linked brief before implementation.
3. When a feature ships, move its summary into [baseline.md](./baseline.md) and mark the brief **Shipped**.

## Current direction: speaking-first

[Roadmap v1](../constitution/roadmap_v1.md) replaces the "more units first" sequencing with a **speaking-first** product: listen → understand → speak → get feedback → retain. The legacy backlog below still applies to content, backup and release mechanics; the wave below is the **next build order**.

## Speaking-first wave (roadmap v1)

| Slice | Feature | Priority | Brief | Depends on | Migration |
|-------|---------|----------|-------|------------|-----------|
| 0 — Foundation | Device audio verification | P0 | [native-ios-audio.md](./native-ios-audio.md) | physical iPhone/iPad | — |
| 1 — Speak and record | Recording reliability & audio sessions | P0 | [recording-reliability.md](./recording-reliability.md) | device audio verification | — |
| 1 — Speak and record | Dedicated speaking practice + progress | P0 | [speaking-practice-mode.md](./speaking-practice-mode.md) | recording-reliability | `004_speaking_attempts` |
| 2 — Speak and evaluate | On-device speech recognition adapter | P0 | [speech-recognition-adapter.md](./speech-recognition-adapter.md) | device check of on-device `kn-IN` | — |
| 2 — Speak and evaluate | Spoken answer evaluation & feedback | P0 | [spoken-answer-evaluation.md](./spoken-answer-evaluation.md) | speech adapter, speaking mode | `005_speaking_evaluation` |
| 3 — Speak in context | Deterministic conversation engine | P0 | [conversation-engine.md](./conversation-engine.md) | spoken evaluation | `006_conversation_sessions` |
| 3 — Speak in context | Five everyday conversation scenarios | P0 | [conversation-scenarios.md](./conversation-scenarios.md) | conversation engine | — |
| 4 — Retention | Speaking-aware revision engine | P1 | [speaking-aware-revision.md](./speaking-aware-revision.md) | slices 1–3, listening | `007_skill_progress` |
| 4 — Listening | Audio-first comprehension exercises | P1 | [listening-comprehension.md](./listening-comprehension.md) | audio pipeline | — |
| 5 — Intelligence | Optional AI conversation coach | P1 | [ai-conversation-coach.md](./ai-conversation-coach.md) | slices 1–3, proxy | — |
| 5 — Insights | Skill-specific proficiency dashboard | P2 | [proficiency-dashboard.md](./proficiency-dashboard.md) | revisions, sessions | — |
| 5 — Support | Personal phrasebook | P2 | [personal-phrasebook.md](./personal-phrasebook.md) | search, speaking mode | `008_saved_phrases` |

**Prerequisite:** [native-ios-audio.md](./native-ios-audio.md) device verification closes the open Release 0 checks (playback, permission, record/replay). Do not start slice 2 until recording is stable on the physical iPhone.

### Build order

1. **Slice 1 — speak and record:** recording reliability + speaking mode + local attempts. This alone is a useful speaking app.
2. **Slice 2 — speak and evaluate:** on-device recognition, normalization, accepted-answer comparison, feedback. Privacy rule: no server STT.
3. **Slice 3 — speak in context:** deterministic engine + five scenarios.
4. Then listening, speaking-aware revision, optional AI, dashboard/phrasebook.

Migration numbers are claimed here to avoid collisions: `004` speaking attempts, `005` evaluation, `006` conversation sessions, `007` skill progress, `008` saved phrases.

## Supporting backlog

| P | Feature | Phase | Brief | Code touchpoints |
|---|---------|-------|-------|------------------|
| P0 | Weekly personal publish loop | — | [personal-release-cadence.md](./personal-release-cadence.md) | backup, versions, build commands |
| P1 | Human / studio phrase audio | — | [human-phrase-audio.md](./human-phrase-audio.md) | `content/audio/`, `content:validate`, import |
| P2 | Real AI grammar insights (opt-in) | — | [ai-grammar-insights.md](./ai-grammar-insights.md) | `src/services/ai/`, phrase detail |
| P2 | Settings in primary navigation | — | [settings-discoverability.md](./settings-discoverability.md) | `BottomNav`, `HomeScreen` |
| P2 | Phrase search & browse | — | [phrase-search-browse.md](./phrase-search-browse.md) | new feature + IPC list/search |
| P2 | Guided onboarding & goals | — | [guided-onboarding.md](./guided-onboarding.md) | `OnboardingScreen`, learner profile |
| P2 | Unit map & learning path UX | — | [learn-path-ux.md](./learn-path-ux.md) | `LearnScreen`, curriculum metadata |

Priorities use the same product meaning as [roadmap v1](../constitution/roadmap_v1.md): P0 protects the speaking loop, P1 is supporting capability, and P2 is polish or optional expansion. The personal release cadence governs safe weekly installs across all priorities.

Completed delivery work is intentionally excluded from the backlogs: [content updates](./content-updates.md) and [Level 2 curriculum](./level-2-curriculum.md) are recorded in the shipped baseline.

## Shipped baseline

What already exists in the repo is catalogued in [baseline.md](./baseline.md). Treat it as the feature inventory, not duplicate specs.

## Spec template

New briefs should include:

- **Learner outcome** — one sentence a user would say after using it.
- **Principles** — which items from [mission](../constitution/mission.md) apply.
- **In scope / out of scope** — especially boundaries (no cloud accounts, no invented curriculum).
- **Acceptance criteria** — testable, including offline where relevant.
- **Dependencies** — content version, schema migration, platform.

## Related docs

- [Vision](../vision.md) · [Mission](../constitution/mission.md) · [Roadmap](../constitution/roadmap.md) · [Speaking-first roadmap v1](../constitution/roadmap_v1.md) · [Tech stack](../constitution/techstack.md) · [Architecture](../ARCHITECTURE.md)
