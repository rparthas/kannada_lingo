# Content updates without full reinstall

| Field | Value |
|-------|-------|
| Status | Planned |
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
- Roadmap lists “CLI or in-app, TBD”.

## Options (decide before build)

| Approach | Pros | Cons |
|----------|------|------|
| **A. Content-only ZIP** (manifest + JSON + audio) | Matches backup mental model; user-initiated | Large downloads; UX for “import content” |
| **B. CLI `content:import`** for power users | Simple; good for editors | Not learner-facing |
| **C. App update only** | Simplest | Requires store release for every curriculum fix |

**Recommendation:** Implement **B** first for editorial loop; design **A** manifest compatible with backup manifest fields (`content_version`, checksum).

## In scope

- Idempotent import: add new levels/lessons/items; do not wipe `exercise_attempts` or SM-2 rows for existing `learning_item_id`s.
- Bump detection: if incoming `content_version` ≤ installed, no-op with message.
- Migration story when exercise definitions change for an existing item (version pin or soft “relearn” flag).

## Out of scope

- Cloud CDN or automatic background downloads.
- Merging divergent forks of user-edited content.

## Acceptance criteria

- [ ] Documented command or settings action imports content pack and preserves learner profile.
- [ ] Rust tests: import on non-empty DB adds new lesson without deleting attempts.
- [ ] Restore backup after content import still works.
- [ ] `content:validate` runs on pack before import is offered.

## Dependencies

- Schema stability for `content_version` in manifest (align with backup manifest).
- Level 2 content package as first real-world test ([level-2-curriculum.md](./level-2-curriculum.md)).