# Content updates without full reinstall

| Field | Value |
|-------|-------|
| Status | Shipped |
| Roadmap | Phase 8 |
| Priority | P2 |

## Learner outcome

“I got new lessons and phrases in an update pack without losing my streak, review schedule, or backups.”

## Principles

- **Content as a product**, **local-first** — learner state stays on device; content is replaceable/mergeable with care.
- **Data integrity** — checksums and version gates like backup restore.

## Current state

- Curriculum imported only when DB is empty (`init_app` import path in Rust).
- Dev workflow: delete `learner.sqlite` to re-import.
- The local CLI is the supported personal-release path; no in-app download flow exists.

## Delivered approach

`npm run content:import -- --db PATH` imports a newer validated bundled curriculum into an existing database. It is the editor/developer workflow for personal releases; it is not an in-app download mechanism. `--force` re-applies a bundle whose version matches the installed version.

## In scope

- Idempotent import: add new levels/lessons/items; do not wipe `exercise_attempts` or SM-2 rows for existing `learning_item_id`s.
- Version gate: if incoming `content_version` is not newer, the command no-ops with a message unless `--force` is used.
- Migration story when exercise definitions change for an existing item (version pin or soft “relearn” flag).

## Out of scope

- Cloud CDN or automatic background downloads.
- Merging divergent forks of user-edited content.

## Acceptance criteria

- [x] Documented command or settings action imports content pack and preserves learner profile (`npm run content:import`).
- [x] Rust tests: import on non-empty DB adds new lesson without deleting attempts.
- [x] Restore backup after content import still works (unchanged backup path; import uses `INSERT OR REPLACE` on content tables only).
- [x] `content:validate` runs on pack before import is offered.

## Dependencies

- Schema stability for `content_version` in manifest (align with backup manifest).
- Future in-app content packs should use the same validation and version-gating contract.
