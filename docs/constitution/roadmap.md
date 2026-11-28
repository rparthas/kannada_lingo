# Kannada Quest — Product Roadmap

> **Current direction:** [Speaking-first roadmap](roadmap_v1.md). It owns the next build sequence. This document records the shipped foundation and continuing delivery constraints.

## Roadmap Objective

Keep a trustworthy, offline-first practical Kannada experience on iOS while expanding the spoken-learning loop—without sacrificing content accuracy or local control of progress.

Capabilities are grouped by phase, not fixed release dates.

## Current Baseline

The repository already includes:

- Bottom navigation (Home, Learn, Practice, Progress).
- Two-level path: **21 units**, **42 lessons**, **190 phrases**.
- Lesson player (resume, review mode, scripted conversations, all exercise types).
- Practice drills, phrase detail with attempt history, SM-2-inspired scheduling.
- Bundled audio (slow/normal), learner recording hooks, `content:validate`.
- Backup export/import with manifest and SHA-256 integrity checks.
- Mock AI grammar insight (`VITE_AI_PROVIDER=unconfigured` for production stub).

Treat "complete" in the table below as **implemented in repo**; device-only checks and store submission remain open.

---

## Phase Status

| Phase | Status | Notes |
|-------|--------|-------|
| 0 — Technical feasibility | **Verified (Simulator)** | Toolchain and sim build; device smoke test in `docs/DEVELOPER_SETUP.md` |
| 1 — Application foundation | Complete | Scaffold, navigation, SQLite, migrations, content import |
| 2 — Learning engine | Complete | Lesson player, exercises, XP, phrase history, practice drills |
| 3 — Audio and content | Complete | WAV import, `WebAudioService`, validation tooling |
| 4 — Revision and retention | Complete | Streaks, daily goal, review UI, local-time scheduling |
| 5 — AI personalization | Complete (mock) | Swap provider via env; no client secrets |
| 6 — Backup / personal delivery | Complete (app) | Restore UX and tests; weekly personal installs govern delivery |

---

## Phase 0 — Close Mobile Feasibility (optional)

**Objective:** Confirm on **physical** iPhone/iPad when mic, Files, and device audio matter.

Use the device smoke table in `docs/DEVELOPER_SETUP.md`. Simulator feasibility is already verified.

---

## Phase 7 — Device Readiness

**Objective:** Make Kannada Quest dependable on the personal iPhone/iPad used for practice.

### Priorities

- Privacy strings and microphone usage descriptions aligned with exercises.
- Crash-free smoke path on device.
- Replace or supplement TTS placeholder audio with human recordings where quality matters.
- Harden native audio/recording if `WebAudioService` limits appear on device.

### Exit Criteria

- Device smoke checks pass for playback, recording, and backup/restore.
- Backup/restore verified on device via Files/iCloud Drive.
- Personal release steps and versioning process documented.

Public App Store work is deferred; see [RELEASE.md](../RELEASE.md).

---

## Phase 8 — Curriculum Expansion

**Objective:** Grow beyond Survival Kannada with the same content discipline.

### Priorities

- Level 2 units with validated JSON and audio pipeline are shipped.
- Content import without a full reinstall is available through the local CLI.
- Expanded accepted-answer variants and regional notes where needed.

### Exit Criteria

- New or changed units ship through `content:validate` and version bumps.
- A newer bundle imports without losing local progress.

---

## Phase 9 — Optional Intelligence

**Objective:** Add grammar or usage help without compromising privacy or curriculum authority.

### Priorities

- Real `AIContentProvider` behind a user-controlled backend or on-device boundary.
- Clear labeling of AI-generated vs canonical phrase content.
- Graceful degradation when AI is disabled or offline.

### Product Rules

- Canonical phrases and exercises remain source-of-truth in `content/`.
- No autonomous curriculum generation without editorial review.
- No sending learner recordings off-device without explicit consent.

### Exit Criteria

- Production build operates with AI disabled by default.
- When enabled, insights trace to phrase context the user already sees.

---

## Cross-Cutting Priorities

- **Data integrity:** Migrations, backup checksums, restore confirmation UX.
- **Privacy:** Local progress; optional AI; export only on user action.
- **Quality:** Domain and backup tests on every change to scheduling or persistence.
- **Content:** Validation script in the path for curriculum edits.
- **UX:** Mobile layouts, Kannada script rendering, accessible audio controls.

## Prioritization Rules

1. Protect learner data and restore safety.
2. Correctness of evaluation and scheduling.
3. Physical iOS verification and speaking-loop blockers.
4. Curriculum accuracy and audio quality.
5. Optional AI and supporting polish.

Changes to mission or platform should align with `docs/constitution/mission.md` and `docs/vision.md`.

Feature-level scope, status, and acceptance criteria live in [GitHub Issues](https://github.com/rparthas/kannada_lingo/issues); see [FEATURE_WORKFLOW.md](../FEATURE_WORKFLOW.md).

**Personal-use note:** Solo use with roughly weekly installs from the repo; no App Store release is planned. The current sequence is in [the speaking-first roadmap](roadmap_v1.md), and the delivery routine is in [RELEASE.md](../RELEASE.md).
