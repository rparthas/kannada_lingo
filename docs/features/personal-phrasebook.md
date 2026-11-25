# Personal phrasebook

| Field | Value |
|-------|-------|
| Status | Planned |
| Roadmap | Supporting feature ([roadmap v1 §3](../constitution/roadmap_v1.md)) |
| Priority | P2 |
| Migration | `008_saved_phrases.sql` |

## Learner outcome

“Before a cab ride or a delivery call I save the phrases I need and rehearse just those.”

## Principles

- **Practical-first** — organise around upcoming real situations, not course order.
- **Local-first** — saved list on device; no accounts or sharing.
- **Content as a product** — the phrasebook references canonical items; it never edits them.

## Current state

- Phrase detail exists (`src/features/phrases/PhraseDetailScreen.tsx`) with audio, attempt history, mock AI.
- [phrase-search-browse.md](./phrase-search-browse.md) is planned for discovery.
- No saved/bookmark concept and no custom practice list.

## In scope

### Data

```sql
CREATE TABLE saved_phrases (
  learning_item_id TEXT PRIMARY KEY REFERENCES learning_items(id),
  saved_at TEXT NOT NULL DEFAULT (datetime('now')),
  note TEXT,
  situation_tag TEXT
);
```

- No user-authored phrase text. A "phrase" is always a `learning_items` row; notes are free text ≤ 280 chars and stay local.
- Commands: `save_phrase`, `unsave_phrase`, `list_saved_phrases` (joined with item text, audio availability and dimension mastery).

### UI

- Save/bookmark control on phrase detail and search results; immediate optimistic toggle with error rollback.
- `src/features/phrasebook/PhrasebookScreen.tsx`, reachable from Progress or the Practice section (decide one entry point; do not duplicate).
- Group by `situation_tag` / existing phrase tags (travel, food, home…), with a text filter over Kannada, transliteration and English.
- Each row: play audio, open detail, remove.
- “Practice these” launches [speaking-practice-mode.md](./speaking-practice-mode.md) filtered to saved items (fall back to a normal list if the speaking mode is unavailable).
- Empty state suggests three high-frequency phrases to save.

### Backup & retention

- Include `saved_phrases` in backup/restore and checksum manifest.
- Restore must not fail when a saved item was removed from newer content; drop orphaned saves with a warning count.
- Unsave is immediate; no undo required.

## Out of scope

- Custom learner-entered Kannada phrases or translation.
- Sharing, export to other apps, cloud sync.
- Auto-save of every phrase encountered.

## Acceptance criteria

- [ ] Save/unsave persists across restart and appears in the list.
- [ ] List works offline and filters by Kannada, transliteration and English.
- [ ] “Practice these” opens speaking practice restricted to saved items; unsaved items are not included.
- [ ] Backup export/restore preserves saves; restore reports and drops orphans instead of failing.
- [ ] Saving does not change SM-2 state, XP or attempt history.
- [ ] Entry point is discoverable from one place without adding a fifth bottom tab.
- [ ] Note text is length-limited and rendered as plain text.

## Dependencies

- [phrase-search-browse.md](./phrase-search-browse.md) for discovery (soft).
- [speaking-practice-mode.md](./speaking-practice-mode.md) for filtered practice (soft; list still works without it).
- Migration `008`; backup module `src-tauri/src/backup/mod.rs`.

## Touchpoints

`src/features/phrasebook/`, `src/features/phrases/PhraseDetailScreen.tsx`, `src/services/api/tauri.ts`, `src-tauri/src/commands/phrasebook.rs`, `src-tauri/migrations/008_saved_phrases.sql`, backup manifest code.
