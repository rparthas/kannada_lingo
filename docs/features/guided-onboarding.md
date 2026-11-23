# Guided onboarding & goals

| Field | Value |
|-------|-------|
| Status | Planned |
| Roadmap | Cross-cutting |
| Priority | P4 |

## Learner outcome

“On day one I picked a realistic daily goal and knew whether I already read Kannada script or need transliteration emphasis.”

## Principles

- **Multimodal clarity** — meet learners where they are (script literacy).
- **Retention by design** — goal setting ties to streaks already on Home.

## Current state

- `OnboardingScreen`: welcome copy + optional name → `completeOnboarding`.
- Daily goal defaults in DB; editable only in Settings (hard to discover).

## In scope

- 2–3 step onboarding (single screen or stepped):
  1. Welcome + name (keep optional).
  2. Daily goal preset chips (e.g. 15 / 30 / 50 XP) with plain-language time estimate.
  3. Optional: “I can read Kannada script” toggle → persisted preference for UI emphasis (transliteration prominence in exercises) — **only if** exercise renderer can honor flag without large refactor.
- Write goal via same API as Settings (`updateLearnerProfile`).

## Out of scope

- Placement test that skips units (risks holes in survival path).
- Social sign-in.

## Acceptance criteria

- [ ] First launch sets daily goal before Home; streak logic uses chosen value.
- [ ] Skip path still works (defaults to current 50 XP).
- [ ] Onboarding completion flag unchanged for returning users.

## Dependencies

- [settings-discoverability.md](./settings-discoverability.md) if goal editing stays in Settings for changes later.
- Schema: may only need `learner_profile` fields already present; script preference may need migration if added.