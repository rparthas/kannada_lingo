# Kannada Quest — Product Vision

## Vision

Build a focused, mobile-first Kannada learning application that teaches **practical spoken Bengaluru Kannada** for everyday life—not textbook grammar in isolation.

The goal is to help learners hear, read, and use real phrases in context (greetings, travel, food, work, family, and daily errands), build durable recall through spaced repetition, and grow confidence speaking and understanding Kannada in Bengaluru.

## Product Principles

1. **Practical-first:** Prioritize phrases and situations learners actually encounter over abstract coverage metrics.
2. **Bengaluru Kannada:** Teach the spoken variety learners will hear locally, with clear notes where usage differs from formal or literary Kannada.
3. **Multimodal clarity:** Pair Kannada script, transliteration, and English meaning so learners can progress whether or not they already read Kannada.
4. **Local-first:** Learning progress, review schedules, and backups stay on the device under the learner's control.
5. **Offline-first:** Core lessons, practice, and revision should work without a network connection.
6. **Retention by design:** Use principled review scheduling and varied recall drills so knowledge sticks beyond the first session.
7. **Content as a product:** Treat curriculum as versioned, validated data that can grow independently of app releases.
8. **Optional intelligence:** AI may explain grammar or nuance when configured, but must never replace authoritative content or ship secrets in the client.

## Platform

- Mobile-first experience (iOS as the primary target; desktop Tauri for development and validation).
- Tauri 2 + React for the application shell and UI.
- SQLite for learner progress, schedules, and imported curriculum.
- Bundled JSON curriculum and audio assets, imported on first launch.

## Guiding Principle

Kannada Quest should be more than a phrasebook or a streak counter. It should be a dependable daily practice companion that turns fragmentary vocabulary into usable spoken Kannada—accurate enough to trust, light enough to open for five minutes, and respectful of the learner's time and privacy.

## Related docs

- [GitHub Issues](https://github.com/rparthas/kannada_lingo/issues) — feature backlog and acceptance criteria (source of truth)
- [`FEATURE_WORKFLOW.md`](FEATURE_WORKFLOW.md) — how issues, milestones, and labels are used
- [`constitution/mission.md`](constitution/mission.md) — audience, boundaries, expanded principles
- [`constitution/techstack.md`](constitution/techstack.md) — architecture, TDD, and engineering rules
- [`constitution/roadmap.md`](constitution/roadmap.md) — phase status and priorities