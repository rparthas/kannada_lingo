# Unit map & learning path UX

| Field | Value |
|-------|-------|
| Status | Shipped |
| Roadmap | Cross-cutting (curriculum scale) |
| Priority | P4 |

## Learner outcome

“I see how units fit together—greetings before shopping—and which lesson to do next in the path.”

## Principles

- **Practical-first** — situations grouped visibly, not a flat lesson grid only.

## Current state

- `LearnScreen`: level chips + flat lesson list with completion and duration.
- Unit metadata exists in content specs (`unit-1-greetings.json`, etc.) but UI does not group by unit.

## In scope

- Group lessons under unit titles with short unit descriptions from specs.
- Visual “recommended next” lesson (first incomplete in ordinal order).
- Optional lock icon **off** by default (mission: no punitive gating); optional soft suggestion only.

## Out of scope

- Skill tree gamification, leagues, hearts/lives.

## Acceptance criteria

- [ ] 13 units visible for Level 1 with correct lesson ordering.
- [ ] Tapping lesson still opens existing `LessonPlayerScreen`.
- [ ] iPad: two-column unit cards if space allows.

## Dependencies

- IPC: ensure `listLessonsForLevel` returns `unit_id` / `unit_title` or fetch unit list command.
- Content specs already carry unit structure — prefer import-time denormalization into DB for simple queries.