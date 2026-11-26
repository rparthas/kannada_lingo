# Settings discoverability

| Field | Value |
|-------|-------|
| Status | Shipped |
| Roadmap | Cross-cutting UX |
| Priority | P3 |

## Learner outcome

“I can change my daily goal and restore a backup without hunting through the Progress screen.”

## Problem

- `SettingsScreen` exists at `/settings` but is **not** in `BottomNav`.
- Only link: Progress → “Settings” text link.
- Daily goal affects Home streak UX — learners may not find it.

## Principles

- **Local-first** — backup/restore and goals are core trust features, not hidden admin.

## In scope

- One of (pick during implementation):
  - Fifth tab “More” or gear on Home header linking to Settings, **or**
  - Settings entry on Home below daily goal card.
- Safe area and iPad layout check.
- Deep link `/settings` unchanged for bookmarks.

## Out of scope

- Account settings, notifications push, theme marketplace.

## Acceptance criteria

- [ ] New user can reach Settings within 2 taps from Home.
- [ ] Bottom nav remains thumb-friendly on iPhone SE size.
- [ ] No regression to lesson routes (settings not shown during lesson player).

## Dependencies

- None technical; pure UI routing.