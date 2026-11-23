# Kannada Quest — Mission

## Vision

Build a focused, mobile-first Kannada learning application that teaches **practical spoken Bengaluru Kannada** for everyday life—not textbook grammar in isolation.

Kannada Quest should help a learner hear, read, and use real phrases in context, retain them through spaced repetition, and grow confidence speaking and understanding Kannada in Bengaluru.

See also: [`docs/vision.md`](../vision.md).

## Mission

Provide a dependable daily practice companion through accurate curriculum, clear multimodal presentation, and locally stored progress—without requiring accounts, subscriptions, or always-on connectivity for core learning.

## Who We Build For

Kannada Quest is a **learner-first** app aimed primarily at people who need **usable spoken Kannada in Bengaluru**, including:

- Professionals and families newly living or working in Bengaluru.
- Heritage learners reconnecting with Kannada in daily life.
- Visitors who want practical phrases beyond tourist pamphlets.

The initial product optimizes for **individual study on a phone or tablet**, not classroom administration or multi-learner institutional workflows.

## Product Principles

### 1. Practical-first

Prioritize situations and phrases learners actually encounter over abstract coverage metrics or gamification for its own sake.

### 2. Bengaluru Kannada

Teach the spoken variety learners will hear locally. Note clearly where usage differs from formal or literary Kannada.

### 3. Multimodal clarity

Pair Kannada script, transliteration, and English meaning so learners can progress whether or not they already read Kannada.

### 4. Local-first

Learning progress, review schedules, streaks, and backups stay on the device under the learner's control.

### 5. Offline-first

Lessons, practice, and revision must work without a network connection once content is installed.

### 6. Retention by design

Use principled review scheduling and varied recall drills so knowledge sticks beyond the first session.

### 7. Content as a product

Treat curriculum as versioned, validated data that can grow independently of app releases.

### 8. Optional intelligence

AI may explain grammar or nuance when configured through a secure boundary. It must never replace authoritative phrase content or ship API keys in the client.

### 9. Sustainable engineering

Keep domain logic framework-agnostic, persistence explicit, and content import reproducible so the app can evolve without entangling learning rules with UI or platform APIs.

### 10. Test-driven delivery

Exercise new behavior through automated tests at domain and persistence seams before treating work as done. See [`techstack.md`](techstack.md) § Testing and TDD and [`.cursor/rules/tdd.mdc`](../../.cursor/rules/tdd.mdc).

## Platform

- Mobile-first (iOS primary; desktop Tauri for development and regression).
- Tauri 2 + React UI.
- SQLite for learner state and imported curriculum.
- Bundled JSON curriculum and audio, imported on first launch.

## Product Boundaries

Kannada Quest is:

- A phrase- and situation-based Kannada course.
- A spaced-repetition practice tool with lessons, drills, and progress tracking.
- A local backup and restore workflow for learner data.

Kannada Quest is not:

- A substitute for human conversation or professional interpretation.
- A formal Kannada literature or certification program.
- A cloud-synced social or leaderboard platform in its initial scope.
- An always-on AI tutor that invents lesson content without grounding in the curriculum.

## Guiding Principle

Kannada Quest should be more than a phrasebook or a streak counter. It should turn fragmentary vocabulary into usable spoken Kannada—accurate enough to trust, light enough for five minutes a day, and respectful of the learner's time and privacy.