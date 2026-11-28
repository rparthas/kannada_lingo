# Feature workflow

**GitHub Issues are the source of truth** for feature scope, status, acceptance
criteria, and verification evidence.

Feature briefs under `docs/features/` were retired in November 2026. Do not add
new briefs or keep a parallel backlog in Markdown. If you need the old design
notes, read them from git history before the retirement commit:

```bash
git log --all -- docs/features
git show <commit>^:docs/features/speaking-practice-mode.md
```

## What lives where

| Question | Where |
|----------|-------|
| What are we building next? | [Open issues](https://github.com/rparthas/kannada_lingo/issues) |
| What does “done” mean? | Acceptance criteria in the issue |
| Which slice is this in? | [Milestones](#milestones) |
| What area does it touch? | [Labels](#labels) |
| What already shipped? | [baseline.md](baseline.md) |
| How do I install a weekly build? | [RELEASE.md](RELEASE.md) |
| How do I verify device audio? | [DEVICE_AUDIO_VERIFICATION.md](DEVICE_AUDIO_VERIFICATION.md) |
| Why does the product exist? | [vision.md](vision.md) and [constitution](constitution/mission.md) |

## Milestones

Milestones are delivery slices, not dates.

| Milestone | Scope |
|-----------|-------|
| [Phase 0 — Device audio verification](https://github.com/rparthas/kannada_lingo/milestone/1) | Physical-device playback, mic permission, record/replay |
| [Slice 1 — Speak and record](https://github.com/rparthas/kannada_lingo/milestone/2) | Recording reliability, speaking practice, attempts |
| [Slice 2 — Speak and evaluate](https://github.com/rparthas/kannada_lingo/milestone/3) | On-device recognition, spoken answer evaluation |
| [Slice 3 — Speak in context](https://github.com/rparthas/kannada_lingo/milestone/4) | Conversation engine and scenarios |
| [Slice 4 — Retention and listening](https://github.com/rparthas/kannada_lingo/milestone/5) | Speaking-aware revision, listening comprehension |
| [Slice 5 — Intelligence and polish](https://github.com/rparthas/kannada_lingo/milestone/6) | AI coach, proficiency dashboard, phrasebook |
| [Supporting — Human phrase audio](https://github.com/rparthas/kannada_lingo/milestone/7) | Human recordings and fallback |
| [Supporting — AI features](https://github.com/rparthas/kannada_lingo/milestone/8) | Optional AI grammar and conversation help |
| [Supporting — UX enhancements](https://github.com/rparthas/kannada_lingo/milestone/9) | Search, learn path, settings, release cadence |

The sequencing rationale is in [roadmap_v1.md](constitution/roadmap_v1.md).

## Labels

| Label | Use |
|-------|-----|
| `phase-0-device-audio` | Physical iPhone/iPad checks |
| `slice-1-speak-record` … `slice-5-intelligence` | Delivery slice |
| `support-human-audio`, `support-ai-features`, `support-ux` | Supporting work |
| `bug`, `enhancement`, `documentation`, `accessibility` | Change type |
| `duplicate`, `invalid`, `wontfix` | Closed without delivery |

## Issue structure

Every feature issue states:

- the learner outcome;
- the principles it must respect;
- testable acceptance criteria with checkboxes;
- dependencies and code touchpoints;
- the manual or device test, when one is needed.

The repository template is
[`.github/ISSUE_TEMPLATE/feature.yml`](../.github/ISSUE_TEMPLATE/feature.yml).

## Lifecycle

1. **Create** the issue from the feature template. Put it in a milestone and add
   area labels.
2. **Refine** scope in issue comments. Design notes, decisions, and trade-offs
   belong on the issue, not in a new Markdown brief.
3. **Implement** the change and add or update automated tests.
4. **Verify** each acceptance criterion. Post the evidence as a comment: test
   output, build result, screenshot, or device sign-off.
5. **Close** only when every acceptance criterion is checked. If a criterion
   needs a physical device, leave the issue open until that check is recorded.

## Commands

```bash
gh issue list --state open
gh issue view 123
gh issue create --template feature
gh issue comment 123 --body "Verified on iPhone 17, iOS 27.2: ..."
gh issue close 123
```

Useful filters:

```bash
gh issue list --milestone "Slice 1: Speak and Record"
gh issue list --label phase-0-device-audio
gh issue list --search "is:open label:bug"
```

## Guardrails

- Do not duplicate issue status in docs. Link to the issue instead.
- Do not create a second backlog. If an idea is not in the tracker, it is not
  planned.
- Do not check an acceptance box without evidence. Manual device checks stay
  open until someone runs them.
- Keep [baseline.md](baseline.md) for shipped capabilities only; it is an
  inventory, not a backlog.
