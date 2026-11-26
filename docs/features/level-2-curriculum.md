# Level 2+ curriculum

| Field | Value |
|-------|-------|
| Status | Shipped |
| Roadmap | [Phase 8](../constitution/roadmap.md#phase-8--curriculum-expansion) |
| Priority | P2 |

## Learner outcome

“After Survival Kannada, I have a clear next level for work meetings, neighbors, and longer conversations—without restarting my progress.”

## Principles

- **Practical-first**, **Bengaluru Kannada**.
- **Content as a product** — JSON specs, validators, versioned release independent of app binary when possible.

## Delivered scope

`level-2-everyday` is present in `content/curriculum/specs/course.json` and `LearnScreen` lists it from the database. The shipped units cover the following themes:

| Unit theme | Example situations |
|------------|-------------------|
| Deeper work | standups, deadlines, polite disagreement |
| Neighborhood | society gate, deliveries, festivals with neighbors |
| Services | plumber, electrician, cab small talk |
| Kids & school | parent–teacher, pickup lines (extends unit 12) |
| Culture & etiquette | honorifics, `neenu`/`nimma`, soft refusals |

## Ongoing scope

- Maintain and extend Level 2 through unit specs under `content/curriculum/specs/units/`.
- Reuse exercise types; give new phrases `accepted_answers` and optional `context_note`.
- Generate audio through `content:build` until human recordings land per phrase.

## Out of scope

- Literary Kannada, poetry, or certification exam syllabus.
- AI-generated phrase lists without editorial sign-off.

## Acceptance criteria

- [x] `npm run content:validate` passes with level 2 content.
- [x] `content_version` incremented; import adds rows without migration breakage.
- [x] Learner completing Level 1 sees Level 2 in Learn tab; prior XP/schedules unchanged.
- [x] Regional/formal notes present where spoken Bengaluru differs.

## Dependencies

- [content-updates.md](./content-updates.md) if learners need content without full app update.
- Phrase count target TBD (suggest ≥80 new items for a credible “Level 2”).
