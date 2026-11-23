# Kannada Quest — Technology Stack & Architecture

## 1. Platform

| Area | Decision |
|---|---|
| Target platform | iOS primary; macOS desktop via Tauri for dev and validation |
| Application type | Mobile-first app (Tauri 2 shell) |
| Primary user | Individual learner |
| Operating model | Local-first, offline-first |
| Primary persistence | SQLite |
| Curriculum delivery | Bundled JSON + assets, imported on first launch |

Do not introduce Android, web-only, or mandatory cloud backends for core learning unless product direction explicitly changes.

## 2. Repository Stack

| Layer | Technology | Responsibility |
|---|---|---|
| Desktop / mobile shell | Tauri 2 | App lifecycle, IPC, filesystem, backup |
| UI | React 19 + React Router | Screens, navigation, exercise presentation |
| UI build | Vite | Dev server and production bundles |
| Styling | Tailwind CSS 4 | Layout and visual design |
| Domain logic | TypeScript (`src/domain`) | SM-2 scheduling, answer evaluation (no Tauri imports) |
| Services | TypeScript (`src/services`) | Tauri IPC, audio and AI interfaces |
| Persistence | Rust + SQLite (`src-tauri`) | Migrations, commands, online backup |
| Content | `content/` JSON + WAV | Versioned curriculum validated in CI |
| Tests (TS) | Vitest + Testing Library | Domain and UI unit tests |
| Tests (Rust) | `cargo test` | Migrations and backup integrity |
| Content tooling | Python scripts, Node validators | `content:build`, `content:validate` |

## 3. Architectural Layers

### Presentation (`src/features`, `src/components`)

Responsibilities:

- iPhone and iPad layouts, bottom navigation, lesson and practice flows.
- Exercise rendering and immediate feedback UX.
- Loading, empty, and error states.

Rules:

- Do not embed SM-2 or answer-evaluation rules in components; call domain modules.
- Do not access SQLite from React; use Tauri commands via services.
- Keep pages focused on learner workflows.

### Domain (`src/domain`)

Responsibilities:

- Spaced-repetition updates (SM-2-inspired).
- Answer normalization and accepted alternatives.
- XP and scheduling rules independent of storage.

Rules:

- No imports from `@tauri-apps/*` or Rust types.
- Domain functions should be pure and unit-tested where behavior is non-obvious.

### Services (`src/services`)

Responsibilities:

- Wrap IPC calls to the Tauri backend.
- `WebAudioService` and pluggable `AIContentProvider` implementations.

Rules:

- Swappable providers (mock vs unconfigured vs future real backend) via env/build config.
- Never embed API secrets in the client bundle.

### Persistence (`src-tauri/src/db`, commands)

Responsibilities:

- Schema migrations and curriculum import when the DB is empty.
- Recording attempts, progress, review schedules, and settings.
- Backup: SQLite online backup → integrity check → ZIP with manifest and SHA-256.

Rules:

- Parameterized SQL; transactional multi-row updates.
- Migrations are versioned and covered by Rust tests where failure modes matter.

### Content (`content/`)

Responsibilities:

- Authoritative phrase, lesson, and exercise definitions.
- Audio asset references imported into `audio_assets`.
- **Source specs:** `content/curriculum/specs/` (`course.json` + `units/*.json`).
- **Built bundle:** `content/curriculum/beginner-path.json` from `scripts/build-beginner-path.py`.

Rules:

- Edit unit JSON specs, not `beginner-path.json`, for routine curriculum changes.
- Bump `content_version` in `course.json` when curriculum changes.
- Run `npm run content:validate` before shipping content changes.
- Prefer `npm run content:build` over hand-editing generated assets.

## 4. Data Flow

1. `init_app` runs migrations and imports bundled curriculum if the database is empty.
2. The lesson player loads lesson detail via IPC and renders `ExerciseRenderer`.
3. On submit, TypeScript evaluates the answer, updates SM-2 state, then `record_exercise_attempt` persists progress and schedules.
4. Backup exports a ZIP; restore validates manifest and checksum before replacing learner data.

## 5. Extension Points

| Area | Current | Direction |
|---|---|---|
| Audio | `WebAudioService` + bundled WAV; macOS TTS in `content:build` | Native iOS playback/recording adapters where web APIs are insufficient |
| AI | `MockAIContentProvider`; `VITE_AI_PROVIDER=unconfigured` in production | Secure backend or on-device boundary; keys never in the app bundle |
| Content updates | Reinstall / dev DB reset | Future import CLI for content-only updates |

## 6. Testing and TDD

**Default workflow:** test-driven development (red → green) in vertical slices. Agents and contributors should follow this unless the change is documentation-only or explicitly exploratory.

### Loop

1. **Red** — Add or extend a test at a public seam; run the suite and confirm it fails for the right reason.
2. **Green** — Change production code with the smallest diff that passes.
3. **Repeat** — One behavior per cycle; avoid drafting many tests before any implementation.

Refactor after green when needed; do not add new behavior without a failing test first.

### Seams (where tests belong)

| Concern | Seam | Tests |
|---------|------|--------|
| Scheduling, grading, XP | `src/domain/**` exports | `tests/unit/*.test.ts` (Vitest) |
| Curriculum integrity | `validateCurriculumBundle` | `tests/unit/content-validate.test.ts` |
| Shipped bundle | `content/curriculum/beginner-path.json` | `npm run content:validate` |
| SQLite, migrations, backup | Rust modules + commands | `src-tauri`: `cargo test` |
| UI | Components | Only when behavior is not visible from domain/API; prefer Testing Library smoke tests |

Domain logic stays in TypeScript **without** Tauri imports so it remains fast to test. Rust tests focus on data integrity and backup roundtrips.

### Commands (run before claiming done)

```bash
npm run test
cd src-tauri && cargo test
npm run content:validate   # when specs or beginner-path.json change
```

### Quality bar

- Assert **behavior** learners or callers care about, not internal structure.
- Use **independent** expected values (spec, fixture, worked example)—not a duplicate of the implementation.
- Do not merge scheduling, grading, or import rules only in UI without domain tests.

### Cursor / agent instruction

Project rule: [`.cursor/rules/tdd.mdc`](../../.cursor/rules/tdd.mdc) (`alwaysApply`).

## 7. Engineering Principles

1. Prefer simple, testable domain code over UI-duplicated rules.
2. Keep learner data local unless the user explicitly exports it.
3. Make content validation part of the delivery path.
4. Introduce new dependencies only for a concrete requirement.
5. Document significant architectural changes when they affect persistence or content contracts.

## 8. Non-Goals (unless explicitly approved)

- Mandatory user accounts or cloud sync for core learning.
- Shipping third-party API keys in the client.
- Duplicating curriculum truth in the database without a import/version story.

For a short layer diagram, see [`docs/ARCHITECTURE.md`](../ARCHITECTURE.md) (summary only).