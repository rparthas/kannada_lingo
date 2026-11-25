# Deterministic conversation engine

| Field | Value |
|-------|-------|
| Status | Planned |
| Roadmap | [Release 2](../constitution/roadmap_v1.md) (conversation simulator) |
| Priority | P0 |
| Slice | 3 — Speak in context |
| Migration | `006_conversation_sessions.sql` |

## Learner outcome

“I can get through a chai order or an auto ride by answering out loud, and the conversation reacts like a real one — even offline.”

## Principles

- **Practical-first** — scenarios are Bengaluru situations, not abstract dialogues.
- **Content as a product** — every branch and accepted answer is authored, versioned and validated; no generated canonical content.
- **Correctness** — the engine is a pure deterministic reducer; the same inputs always produce the same turn.
- **Offline-first** — bundled scenarios and audio; AI is a later, optional layer.

## Current state

- `scripted_conversation` exists as an exercise type (`ExerciseRenderer`) with narration, partner phrase, and multiple-choice `choices` from `prompt_json`.
- Tables `conversations` / `conversation_turns` exist but are lesson-scoped with `response_options_json` — a multiple-choice model.
- `src/domain/exercises/evaluate.ts` and the Release 1 speech evaluator can compare free text; there is no conversation engine or session persistence.

## Design

### Content model (owned by [conversation-scenarios.md](./conversation-scenarios.md))

`content/curriculum/conversations/<scenario-id>.json`:

```jsonc
{
  "id": "auto-ride-fare",
  "title": "Auto ride",
  "situation": "Hailing an auto near your apartment",
  "difficulty": 2,
  "level_id": "level-1-survival",
  "steps": [{
    "id": "ask-destination",
    "partnerPhraseId": "item-ellige-hogbeku",   // existing learning item
    "partnerAudio": { "normal": "auto/ask-dest-normal.wav", "slow": "…" },
    "expectedIntents": ["state_destination"],
    "acceptedPhraseIds": ["item-majestic-hogbeku"],
    "acceptedAnswers": ["majestic", "majestic ge hogi"],
    "hints": ["Say where you want to go.", "Try: Majestic ge hogbeku."],
    "branches": { "understood": "confirm-fare", "unclear": "repeat-destination" },
    "feedback": { "why": "Naming the destination first is enough here." }
  }]
}
```

Keep the existing `scripted_conversation` exercise untouched. Do not force new scenarios into its multiple-choice shape.

### Engine — `src/domain/conversations/engine.ts`

```ts
export interface ConversationState {
  scenarioId: string;
  stepId: string;
  hintLevel: number;
  turns: ConversationTurnRecord[];
  done: boolean;
}

export function startConversation(scenario: ConversationScenario): ConversationState;
export function advanceConversation(
  scenario: ConversationScenario,
  state: ConversationState,
  response: { text: string; source: "speech" | "typed"; confidence?: number },
): { state: ConversationState; evaluation: SpokenEvaluation; nextStepId?: string; feedback?: string };
```

Rules:

- A response is accepted if normalized text matches an accepted answer, or resolves to an `acceptedPhraseId` whose canonical/accepted answers match (reuse Release 1 normalization; do not fork it).
- `unusable` (empty/low confidence) → repeat the same step, no hint escalation penalty, no failure recorded.
- Hint escalation: first miss → step hint; second miss → reveal a suggested phrase and allow “continue anyway”; third → `unclear` branch.
- Branch selection is declarative (`branches` on the step); unknown branch ids fail content validation.
- Completion when a step has no `branches`/next or declares `terminal: true`.
- No randomness. Optional per-scenario shuffle of *hint choice order* is out of scope.
- The engine never calls AI and never mutates bundled content.

### Persistence — `006_conversation_sessions.sql`

```sql
CREATE TABLE conversation_scenarios (          -- imported content mirror, like lessons
  id TEXT PRIMARY KEY, title TEXT NOT NULL, situation TEXT,
  difficulty INTEGER NOT NULL, level_id TEXT REFERENCES levels(id),
  content_version INTEGER NOT NULL, definition_json TEXT NOT NULL
);

CREATE TABLE conversation_sessions (
  id TEXT PRIMARY KEY,
  scenario_id TEXT NOT NULL REFERENCES conversation_scenarios(id),
  mode TEXT NOT NULL DEFAULT 'deterministic' CHECK (mode IN ('deterministic','ai')),
  started_at TEXT NOT NULL,
  ended_at TEXT,
  completed INTEGER NOT NULL DEFAULT 0,
  summary_json TEXT
);

CREATE TABLE conversation_session_turns (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES conversation_sessions(id),
  turn_index INTEGER NOT NULL,
  speaker TEXT NOT NULL CHECK (speaker IN ('partner','learner')),
  step_id TEXT,
  phrase_id TEXT REFERENCES learning_items(id),
  transcript TEXT,
  evaluation_status TEXT,
  evaluation_json TEXT,
  hint_used INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
```

- Content import mirrors scenario JSON into `conversation_scenarios`; sessions/turns are learner data and must survive content updates.
- Commands in `src-tauri/src/commands/conversations.rs`: `list_conversation_scenarios`, `start_conversation_session`, `record_conversation_turn`, `complete_conversation_session`, `conversation_summary`.
- Turn rows store recognized text only, never audio.

### UI — `src/features/conversations/`

- `ConversationListScreen` — situation cards (auto, restaurant, security, shop, neighbour) with difficulty and completion.
- `ConversationPlayerScreen` — partner audio autoplay, transcript hidden by default with an explicit reveal, record/type answer, inline hint ladder, “why this works” after an accepted turn.
- `ConversationSummary` — turns taken, unaided turns, accepted alternatives the learner did not use, phrases to revisit (deep-link to speaking practice), completion stored.
- Exit mid-scenario prompts “Leave and keep this session?”; resume is not required in this release, but the session must be closed cleanly.

### Validation

Extend `src/domain/content/validate.ts` / `scripts/validate-content.mjs`:

- unique scenario/step ids; every `partnerPhraseId` and `acceptedPhraseId` resolves to an approved item;
- every branch target exists; every decision step has ≥3 accepted responses (where the scenario calls for it);
- partner audio file exists for normal speed; transcript text is present for every partner turn;
- no scenario duplicates canonical phrases into new unvalidated items.

## Out of scope

- AI-generated dialogue ([ai-conversation-coach.md](./ai-conversation-coach.md)).
- Voice-to-voice streaming, interruptions/overlap, free-form semantic understanding.
- Pronunciation scoring.
- Adapting existing `scripted_conversation` content automatically.

## Acceptance criteria

- [ ] Reducer tests cover accepted answer, accepted phrase id, near miss → hint, second miss → reveal, unusable → same step, branch selection, and completion.
- [ ] Same state + response always yields the same next step (deterministic; no time/random input).
- [ ] Spoken and typed responses both drive the engine through the Release 1 evaluator.
- [ ] A completed session and every turn persist; summary reads back after app restart.
- [ ] Content validation rejects unknown phrase/branch references and missing audio.
- [ ] Five scenarios load and complete offline (content brief).
- [ ] `conversation_scenarios` content updates do not delete learner sessions.
- [ ] No AI or network dependency in this path.

## Dependencies

- [spoken-answer-evaluation.md](./spoken-answer-evaluation.md) and [speech-recognition-adapter.md](./speech-recognition-adapter.md).
- [conversation-scenarios.md](./conversation-scenarios.md) for authored content.
- Migration `006`; content mirror import in `src-tauri/src/content/import.rs`.
- [speaking-aware-revision.md](./speaking-aware-revision.md) later consumes close-the-loop results.

## Touchpoints

`src/domain/conversations/`, `src/features/conversations/`, `src/services/api/tauri.ts`, `src-tauri/src/commands/conversations.rs`, `src-tauri/src/content/import.rs`, `src-tauri/migrations/006_conversation_sessions.sql`, `content/curriculum/conversations/`.

## Open decision

Whether conversation scenarios import as part of the existing curriculum pack or a separate `conversations/` manifest. Recommendation: same pack and `content_version`, separate top-level table so sessions survive item edits.
