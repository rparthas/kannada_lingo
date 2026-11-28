# Personal release cadence (~7 days)

| Field | Value |
|-------|-------|
| Status | Active |
| Audience | Solo developer (personal use only) |
| Priority | P0 (governs all other priorities) |

This is an operational runbook. Feature scope, status, and acceptance criteria
live in [GitHub Issues](https://github.com/rparthas/kannada_lingo/issues); see
[FEATURE_WORKFLOW.md](FEATURE_WORKFLOW.md).

## Intent

Kannada Quest is built and run **for one learner: you**. There is no App Store or public distribution goal. You refresh the app on a **roughly weekly** cycle from this repo—new curriculum, fixes, or UI—while keeping progress on device whenever possible.

## What “publish” means here

| Channel | Use |
|---------|-----|
| **Desktop** | `npm run tauri dev` for daily study; `npm run test` before merge |
| **iOS (your devices)** | `npm run ios:dev` / device build with your signing team |
| **Not in scope** | TestFlight, App Store, store assets, external testers |

App Store work is **deferred** and out of scope for this personal build.

## Recommended weekly loop

1. **Content** — edit specs under `content/`, run `npm run content:validate` (and `content:build` on macOS if audio changed).
2. **Quality** — `npm run test` and `cd src-tauri && cargo test`.
3. **Version** — bump app version in Tauri config if binary changed; bump `content_version` in `course.json` if curriculum changed.
4. **Install** — build/install to the device you actually practice on.
5. **Data** — export backup before risky schema or content experiments (`Progress` → Export backup).

## Progress across weekly installs

Fresh installs import bundled curriculum when the database is empty. Existing databases can receive a newer validated bundle through `npm run content:import` without wiping learner attempts, XP, streaks, or schedules. Reinstalling or wiping the app's data can still lose learner state unless you restore a backup.

For a 7-day rhythm, prioritize:

| Approach | When |
|----------|------|
| **Backup → update app → restore** | Safe default before any risky schema or content experiment |
| **Same DB file** (dev: don’t wipe `learner.sqlite`) | Desktop practice between iOS rebuilds |
| **Content update without reinstall** | Run `npm run content:import` for a newer validated bundle; see [DEVELOPER_SETUP.md](DEVELOPER_SETUP.md) |

## Priority stack (personal use)

1. **Trust your data** — backup/restore, SM-2, evaluation tests stay green.
2. **Weekly content velocity** — validators, content version, import story (CLI or pack).
3. **Device practice quality** — audio/recording on *your* phone ([DEVICE_AUDIO_VERIFICATION.md](DEVICE_AUDIO_VERIFICATION.md)).
4. **Learning UX** — search, unit map, onboarding tweaks as *you* feel friction.
5. **AI grammar** — only if you wire a backend you control; mock is enough for solo use.

## Cadence work

Track cadence work in GitHub Issues, not in this document:

- [#143 — Documented minimum commands for Tuesday/Friday workflow](https://github.com/rparthas/kannada_lingo/issues/143)
- [#145 — Backup recovery from a bad week](https://github.com/rparthas/kannada_lingo/issues/145)
- [#147 — Optional weekly release script](https://github.com/rparthas/kannada_lingo/issues/147)
