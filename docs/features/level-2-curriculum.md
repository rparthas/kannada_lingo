# Level 2+ curriculum

| Field | Value |
|-------|-------|
| Status | Planned |
| Roadmap | [Phase 8](../constitution/roadmap.md#phase-8--curriculum-expansion) |
| Priority | P2 |

## Learner outcome

“After Survival Kannada, I have a clear next level for work meetings, neighbors, and longer conversations—without restarting my progress.”

## Principles

- **Practical-first**, **Bengaluru Kannada**.
- **Content as a product** — JSON specs, validators, versioned release independent of app binary when possible.

## Current state

- Single level: `level-1-survival` in `content/curriculum/specs/course.json`.
- `LearnScreen` already lists levels from DB via `listLevels` — UI ready for multiple levels.
- 13 units cover survival domains (greetings → social).

## Proposed Level 2 themes (draft)

Pick 2–3 for MVP Level 2; validate with content author:

| Unit theme | Example situations |
|------------|-------------------|
| Deeper work | standups, deadlines, polite disagreement |
| Neighborhood | society gate, deliveries, festivals with neighbors |
| Services | plumber, electrician, cab small talk |
| Kids & school | parent–teacher, pickup lines (extends unit 12) |
| Culture & etiquette | honorifics, `neenu`/`nimma`, soft refusals |

## In scope

- New level record in `course.json` with `ordinal: 2`.
- New unit JSON files under `content/curriculum/specs/units/`.
- Lessons reuse existing exercise types; new phrases get `accepted_answers` and optional `context_note`.
- Audio via `content:build` pipeline until human recordings land per phrase.

## Out of scope

- Literary Kannada, poetry, or certification exam syllabus.
- AI-generated phrase lists without editorial sign-off.

## Acceptance criteria

- [ ] `npm run content:validate` passes with level 2 content.
- [ ] `content_version` incremented; import adds rows without migration breakage.
- [ ] Learner completing Level 1 sees Level 2 in Learn tab; prior XP/schedules unchanged.
- [ ] Regional/formal notes present where spoken Bengaluru differs.

## Dependencies

- [content-updates.md](./content-updates.md) if learners need content without full app update.
- Phrase count target TBD (suggest ≥80 new items for a credible “Level 2”).