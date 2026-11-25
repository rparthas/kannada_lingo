# Optional AI conversation coach

| Field | Value |
|-------|-------|
| Status | Planned |
| Roadmap | [Release 3](../constitution/roadmap_v1.md) (AI conversation coach) |
| Priority | P1 |
| Depends on | [conversation-engine.md](./conversation-engine.md) |

## Learner outcome

“The partner stops sounding scripted, stays at my level, and afterwards tells me how a Bengaluru speaker would have said it — only when I turn AI on.”

## Principles

- **Optional intelligence** — disabled by default; explicit opt-in; core lessons never depend on it.
- **Privacy** — recognized text only, never audio; no API secrets in the bundle.
- **Content as a product** — AI output is labelled, stored separately, and never becomes canonical curriculum.
- **Offline-first** — every scenario must still run deterministically without AI.

## Current state

- `AIContentProvider` (`src/services/ai/types.ts`) covers phrase variations, exercise generation and grammar explanation behind an `unconfigured` stub; no conversation interface, no backend proxy, no opt-in setting.
- Release 2 provides `ConversationState`, scenario content, and turn persistence with `mode = 'deterministic'`.
- `AI_GATEWAY`/`VITE_AI_PROVIDER` style env config exists for the mock provider; no secret handling.

## Design

### Separate boundary

`src/services/ai/conversation/types.ts` — do **not** widen `AIContentProvider`:

```ts
export interface ConversationPartnerProvider {
  nextTurn(input: PartnerContext): Promise<PartnerTurn>;
  feedback(input: SessionFeedbackInput): Promise<SessionFeedback>;
}
```

- `PartnerContext`: role/scenario, learner level, difficulty, mode (`guided|normal|challenge`), last N turns (text), allowed phrases/grammar ids, teaching language `en`, target language `kn`.
- `PartnerTurn`: Kannada text, transliteration, English gloss, optional audio plan (play an approved asset or TTS), and `source: "ai"`.
- `SessionFeedback`: successes, grammar notes, natural alternatives, new vocabulary, phrases to revisit — each with the learner’s utterance and a suggested one.
- Implementations: `DisabledConversationProvider` (default; throws a typed `ai_disabled`), `ProxyConversationProvider` (calls a backend you control).

### Backend boundary

- The app calls a proxy endpoint (Cloudflare Worker / small server / on-device model) that holds the provider key. No key in JS, `Info.plist`, or the Tauri bundle.
- Document the proxy contract and the prompt contract in this brief before implementation; version the prompt so feedback stays reproducible.
- Request body contains text context only — no audio, no recording paths.
- Timeout budget (e.g. 12 s) and one retry; on failure return control to the deterministic engine.

### Three modes

| Mode | Behaviour |
|------|-----------|
| Guided | Hint/suggested phrase visible before the learner answers |
| Normal | Natural reply; corrections only in the post-session summary |
| Challenge | Kannada only, no translations until the summary |

Mode is chosen per session and recorded on `conversation_sessions.mode = 'ai'`.

### Context builder

`src/domain/conversations/context.ts`:

- Learner level and recent accuracy (from skill progress, not XP).
- Scenario role, step intent, and the last 10 turns.
- Approved phrase ids and grammar patterns only; do not dump the whole curriculum.
- Hard cap: maintain context for at least 10 turns; trim oldest turns first.
- In Guided mode include the current step’s hints; in Challenge mode omit transliteration/English from the partner payload.

### Response validation

`src/domain/conversations/validate-ai-response.ts`:

- Schema/S length checks; non-empty Kannada text; transliteration present; English gloss present.
- Reject responses that claim to overwrite a canonical phrase or invent a new lesson.
- Reject/repair turns that are not Kannada when Kannada is expected (allow a short clarification in English only in Normal/Guided).
- Mark stored AI turns `source = 'ai'`; canonical `learning_items` are never written.
- On validation failure: retry once, then deterministic fallback with a visible “scripted reply” note.

### Post-session feedback

- English, ≤5 bullets per category.
- Every correction shows “you said / more natural / why”, validated against the intended meaning and reviewed patterns, not presented as a universal rule.
- Example: `nanu coffee beku` → `nanage coffee beku` with a one-line explanation.
- Suggestions may create *draft* phrases for future editorial review, never approved content.

### Settings & privacy

- Settings toggle “AI conversation coach (beta)” default **off**, per-session opt-in reminder.
- Show what will be sent (text transcript summary) and what will not (audio, recordings, progress).
- Disable provider config in production builds unless the proxy URL is present; `unconfigured` fallback is the default.
- Keep AI sessions locally; no automatic cloud sync.

## Out of scope

- Real-time voice-to-voice agent, streaming TTS/STT round-trip.
- Multiple providers, routing, cost dashboards.
- Autonomous curriculum generation.
- Sending recordings or raw audio anywhere.

## Acceptance criteria

- [ ] AI is off by default; with AI off, every conversation runs deterministically and offline.
- [ ] No secret or proxy token exists in the client bundle (review `dist/` and Tauri config).
- [ ] A session maintains context for at least 10 turns with level-appropriate replies (mocked provider contract test).
- [ ] Feedback is English, references the learner’s actual utterance, and separates “suggestion” from “rule”.
- [ ] AI turns persist with source `ai`; `learning_items` and curriculum files are unchanged.
- [ ] Only recognized text is sent; a code-path test/review confirms audio and file paths never enter the request.
- [ ] Network failure/timeout falls back to the deterministic next step within the session with a visible banner.
- [ ] Validation rejects malformed/non-Kannada responses and retries/falls back.
- [ ] Mode (guided/normal/challenge) changes hint visibility as specified.

## Dependencies

- [conversation-engine.md](./conversation-engine.md), [spoken-answer-evaluation.md](./spoken-answer-evaluation.md).
- A backend proxy you control (decision + deployment note required before coding).
- Settings surface from [settings-discoverability.md](./settings-discoverability.md); keep the toggle discoverable, not buried.
- [speaking-aware-revision.md](./speaking-aware-revision.md) for “phrases to revisit” deep links.

## Touchpoints

`src/services/ai/conversation/`, `src/domain/conversations/context.ts`, `src/domain/conversations/validate-ai-response.ts`, `src/features/conversations/`, `src/features/backup/SettingsScreen.tsx`, `src-tauri/src/commands/conversations.rs` (mode/summary writes).

## Open decisions

1. Proxy host (managed worker vs. self-hosted) — decide before UI work.
2. Whether AI turn audio uses bundled assets only (safer) or TTS (needs an on-device/approved voice path).
3. Text retention for AI sessions: default to local-only, opt-in export.
