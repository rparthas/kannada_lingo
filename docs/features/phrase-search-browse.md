# Phrase search & browse

| Field | Value |
|-------|-------|
| Status | Shipped |
| Roadmap | Cross-cutting (supports Phase 8 scale) |
| Priority | P4 |

## Learner outcome

“Before a cab ride I can search ‘airport’ or ‘how much’ and practice the phrases I need.”

## Principles

- **Practical-first** — situation lookup beats scrolling 110+ items across units.
- **Offline-first** — search index local after import.

## Current state

- Phrase detail at `/phrase/:itemId` exists.
- Progress shows counts only; no global phrase list in UI.
- IPC likely needs `search_learning_items` or filter on existing list command (verify in `src-tauri/src/commands/curriculum.rs`).

## In scope

- Search by English, transliteration, and Kannada substring (normalized).
- Filter chips: unit, mastery status (`new` / `learning` / `mastered`).
- Result row → existing `PhraseDetailScreen`.
- Empty state when no matches.

## Out of scope

- Full-text search across lesson narrative JSON.
- Semantic / embedding search (unless on-device and offline).

## Acceptance criteria

- [ ] Search works in airplane mode after first launch.
- [ ] Performance acceptable for 500+ items (target for Level 1+2).
- [ ] Kannada script rendering in results matches lesson player.

## Dependencies

- Optional DB index migration for `english_meaning`, `transliteration`, `kannada_text`.
- More valuable after [level-2-curriculum.md](./level-2-curriculum.md).