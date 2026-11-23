# Kannada Quest — Product Roadmap

## Roadmap Objective

Ship a trustworthy **Level 1 Survival** experience on iOS, then expand curriculum and polish native mobile affordances—without sacrificing offline learning, content accuracy, or local control of progress.

Capabilities are grouped by phase, not fixed release dates.

## Current Baseline

The repository already includes:

- Bottom navigation (Home, Learn, Practice, Progress).
- Level 1 Survival path: **13 units**, **26 lessons**, **110 phrases**.
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
| 6 — Backup / release | Complete (app) | Restore UX and tests; App Store submission manual |

---

## Phase 0 — Close Mobile Feasibility (optional)

**Objective:** Confirm on **physical** iPhone/iPad when mic, Files, and device audio matter.

Use the device smoke table in `docs/DEVELOPER_SETUP.md`. Simulator feasibility is already verified.

---

## Phase 7 — iOS Release Readiness

**Objective:** Make Kannada Quest shippable on the App Store.

### Priorities

- App icons, privacy strings, and microphone usage descriptions aligned with exercises.
- TestFlight build pipeline and crash-free smoke path on device.
- Replace or supplement TTS placeholder audio with human recordings where quality matters.
- Harden native audio/recording if `WebAudioService` limits appear on device.

### Exit Criteria

- TestFlight build accepted by at least one external tester path.
- Backup/restore verified on device via Files/iCloud Drive.
- Store listing assets and versioning process documented.

---

## Phase 8 — Curriculum Expansion

**Objective:** Grow beyond Survival Kannada with the same content discipline.

### Priorities

- Level 2+ units with validated JSON and audio pipeline.
- Content import or update path without full app reinstall (CLI or in-app, TBD).
- Expanded accepted-answer variants and regional notes where needed.

### Exit Criteria

- New levels ship through `content:validate` and version bumps.
- Learners can upgrade content without losing local progress.

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
3. Physical iOS verification and release blockers.
4. Curriculum accuracy and audio quality.
5. New levels and optional AI.

Changes to mission or platform should align with `docs/constitution/mission.md` and `docs/vision.md`.