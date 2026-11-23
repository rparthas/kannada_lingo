# Feature planning

This folder turns [product vision](../vision.md), [mission](../constitution/mission.md), and [roadmap](../constitution/roadmap.md) into **buildable feature briefs**. Each brief states learner value, scope, alignment with constitution principles, and acceptance criteria.

## Operating mode (solo, personal)

- **No App Store** — you ship to yourself from this repo about **every 7 days**.
- **Governance doc:** [personal-release-cadence.md](./personal-release-cadence.md)
- App Store brief is [deferred](./ios-app-store-release.md).

## How to use

1. Pick work from the **priority backlog** below (same order as [roadmap prioritization](../constitution/roadmap.md)).
2. Open the linked brief before implementation.
3. When a feature ships, move its summary into [baseline.md](./baseline.md) and mark the brief **Shipped**.

## Priority backlog

| P | Feature | Phase | Brief | Code touchpoints |
|---|---------|-------|-------|------------------|
| 0 | Weekly personal publish loop | — | [personal-release-cadence.md](./personal-release-cadence.md) | backup, versions, build commands |
| 1 | Content update without reinstall | 8 | [content-updates.md](./content-updates.md) | `src-tauri/src/content/`, CLI TBD |
| 1 | Level 2+ / weekly curriculum edits | 8 | [level-2-curriculum.md](./level-2-curriculum.md) | `content/curriculum/specs/`, validators |
| 2 | Native audio & recording on device | 7 | [native-ios-audio.md](./native-ios-audio.md) | `src/services/audio/`, `LearnerRecordingPanel` |
| 2 | Human / studio phrase audio | 7 | [human-phrase-audio.md](./human-phrase-audio.md) | `content/audio/`, `content:validate`, import |
| 3 | Real AI grammar insights (opt-in) | 9 | [ai-grammar-insights.md](./ai-grammar-insights.md) | `src/services/ai/`, phrase detail |
| 3 | Settings in primary navigation | — | [settings-discoverability.md](./settings-discoverability.md) | `BottomNav`, `HomeScreen` |
| 4 | Phrase search & browse | — | [phrase-search-browse.md](./phrase-search-browse.md) | new feature + IPC list/search |
| 4 | Guided onboarding & goals | — | [guided-onboarding.md](./guided-onboarding.md) | `OnboardingScreen`, learner profile |
| 4 | Unit map & learning path UX | — | [learn-path-ux.md](./learn-path-ux.md) | `LearnScreen`, curriculum metadata |

**P0** = how you install weekly without losing progress. **P1** = content velocity + safe imports. **P2** = practice quality on your phone. **P3–4** = polish when daily use exposes friction.

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

- [Vision](../vision.md) · [Mission](../constitution/mission.md) · [Roadmap](../constitution/roadmap.md) · [Tech stack](../constitution/techstack.md) · [Architecture](../ARCHITECTURE.md)