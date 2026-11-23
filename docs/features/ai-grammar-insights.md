# Real AI grammar insights (opt-in)

| Field | Value |
|-------|-------|
| Status | Planned |
| Roadmap | [Phase 9](../constitution/roadmap.md#phase-9--optional-intelligence) |
| Priority | P3 |

## Learner outcome

“When I tap ‘Explain grammar,’ I get a short, accurate note about *sari* or word order—clearly labeled as AI help, not the official phrase meaning.”

## Principles

- **Optional intelligence** — never replaces canonical phrase text in `content/`.
- **Privacy** — no learner recordings off-device; grammar request uses phrase context already on screen.

## Current state

- `AIContentProvider` in `src/services/ai/types.ts` with `explainGrammar`, variations, exercise generation.
- `MockAIContentProvider` in dev; `UnconfiguredAIProvider` when `VITE_AI_PROVIDER=unconfigured`.
- Phrase detail: `loadGrammarExplanation()` with brittle `grammarPatternForItem` id heuristic.

## In scope

- User-visible toggle: “Grammar insights” off by default in production builds.
- Real provider behind env-selected backend URL or on-device boundary (**no API keys in client** per techstack).
- UI labels: “AI explanation” vs canonical fields (Kannada, transliteration, English).
- Grounding: send only `patternId`, `exampleItemIds`, and canonical strings from DB—not free-form user text.
- Offline: show cached explanation per pattern if previously fetched (optional v1); otherwise friendly disabled state.

## Out of scope

- `generatePhraseVariations` / `generateExercises` in production without editorial workflow.
- Autonomous curriculum generation.

## Acceptance criteria

- [ ] Production build with AI off: button hidden or shows “Not available in this build.”
- [ ] With AI on: explanation loads for at least 3 patterns wired in content metadata (replace id heuristic).
- [ ] Network failure does not block phrase detail or audio.
- [ ] Security review: no secrets in bundle; request payload documented.

## Dependencies

- Content: add explicit `grammar_pattern_id` on items or patterns table in JSON spec.
- Optional small backend repo or serverless function (out of band).

## Future (not v1)

- Exercise generation for authors only (internal tooling).
- Phrase variation drafts with `validationStatus: draft` never shown to learners until approved.