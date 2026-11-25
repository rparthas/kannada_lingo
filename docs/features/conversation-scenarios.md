# Five everyday conversation scenarios

| Field | Value |
|-------|-------|
| Status | Planned |
| Roadmap | [Release 2](../constitution/roadmap_v1.md) (conversation simulator) |
| Priority | P0 |
| Slice | 3 — Speak in context |
| Depends on | [conversation-engine.md](./conversation-engine.md) |

## Learner outcome

“I have rehearsed the five conversations I actually have in Bengaluru — auto, food, delivery, shop and neighbour — before they happen.”

## Principles

- **Practical-first / Bengaluru Kannada** — situations and register from daily life, not textbook set pieces.
- **Content as a product** — authored, reviewed JSON; validated in CI; audio and transcripts versioned together.
- **Multimodal clarity** — spoken partner turns, English hints, transliteration only as scaffolding.
- **Offline-first** — all audio bundled.

## Scope

Five scenarios, using existing Level 1/2 phrases wherever possible:

| Scenario id | Situation | Decision points | Reuses |
|-------------|-----------|-----------------|--------|
| `auto-ride-fare` | Hail an auto, state destination, agree fare, ask to stop | destination, fare, stop here | travel, directions, money units |
| `restaurant-order` | Order food, say preference, ask for bill, pay | item, spice/preference, bill/pay | food, money, politeness |
| `apartment-security` | Visitor/delivery at the gate, give flat number, ask to hold | purpose, flat/name, allow entry | home, phone, directions |
| `kirana-shop` | Ask price, quantity, availability, pay | item, quantity, price, change/UPI | shopping, numbers, money |
| `neighbour-smalltalk` | Greet, answer how-are-you, accept/decline invitation | greeting, wellbeing, invitation | greetings, family, social |

Per scenario:

- 6–10 turns; 3+ valid learner responses at each meaningful decision (exact variants, not three arbitrary sentences).
- Partner turns are natural spoken Kannada with normal-speed audio; slow audio optional but preferred for the first two scenarios.
- Hints ladder: intent hint → suggested phrase → reveal + continue.
- “Why this works” feedback in English on accepted turns (register/formality, e.g. `-ri` forms with elders).
- A terminal step that records completion.

## Content shape

Use the schema in [conversation-engine.md](./conversation-engine.md). Files live at
`content/curriculum/conversations/<scenario-id>.json`.

Authoring rules:

1. Prefer an existing `learning_item_id` for every partner and accepted learner phrase.
2. If a phrase is genuinely missing, add it to the owning unit with `validation_status: "approved"` and audio; never inline an unvalidated phrase.
3. Accepted answers include common spoken reductions (e.g. `beku`, `beku illa`) and English-loan variants actually used in Bengaluru, marked for comparison only.
4. Keep partner audio and transcript paired; bump `content_version` for any change to either.
5. Do not copy the existing `scripted_conversation` multiple-choice prompt; this content is branch-based.

## Audio

- Reuse `content/audio/` naming (`item-<slug>-normal.wav`) for phrases; scenario-only partner lines go under `content/audio/conversations/<scenario>/`.
- Human recordings where quality matters; TTS acceptable for scaffolding, per [human-phrase-audio.md](./human-phrase-audio.md).
- `content:validate` must confirm every referenced audio file exists and every partner turn has one.

## Out of scope

- AI-driven variation of these scenarios.
- New units or a new level.
- Pronunciation scoring.
- Cultural notes longer than one sentence per scenario.

## Acceptance criteria

- [ ] Five scenario files pass `npm run content:validate` and import into `conversation_scenarios`.
- [ ] Each scenario completes offline with bundled audio and no AI configured.
- [ ] Every decision point has at least three accepted responses, at least one of which is a full Kannada phrase.
- [ ] Every partner turn has approved Kannada text, transliteration, English meaning, and normal-speed audio.
- [ ] Transcript is hidden until the learner asks for it.
- [ ] Wrong/unusable answers trigger hints and never dead-end the scenario.
- [ ] Completion produces a summary with unaided-turn count and phrases to revisit.
- [ ] `content_version` is bumped and backup/restore still passes.

## Dependencies

- Engine + schema + migration `006`.
- Content import path and audio build (`scripts/build-beginner-path.py`, `scripts/validate-content.mjs`).
- [human-phrase-audio.md](./human-phrase-audio.md) if human partner lines are recorded.

## Touchpoints

`content/curriculum/conversations/*.json`, `content/schemas/` (scenario schema), `content/audio/conversations/`, `scripts/validate-content.mjs`, `src-tauri/src/content/import.rs`.
