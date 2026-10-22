# Decision Log

Dated record of significant project decisions. Newest entries at the top. When a decision changes something in `PROJECT_CHARTER.md`, update the charter to match.

---

## Entry template

Copy this block for each new decision.

```markdown
## YYYY-MM-DD: <Short title>

- **Phase:** <current phase>
- **Context:** <What prompted the decision?>
- **Options considered:**
  1. <Option A>: <pros / cons>
  2. <Option B>: <pros / cons>
- **Decision:** <What was chosen>
- **Reasoning:** <Why, with references to docs/literature/ notes where relevant>
- **Consequences:** <What changes as a result; charter sections updated>
- **Status:** Accepted | Superseded by <date/title> | Revisited
```

---

## Decisions

<!-- Add entries below, newest first. -->

## 2026-10-22: Fast-track SSVEP data-collection tooling (Phase 3 work) during Phase 1

- **Phase:** 1 (Research and planning)
- **Context:** The project lead wants real Cyton SSVEP data soon, both as a quick demo and to test the signal early, instead of waiting for the full Phase 1 literature review and Phase 2 validation on public data.
- **Options considered:**
  1. Follow the phases strictly: finish Phase 1, validate on public data in Phase 2, then build recording tools in Phase 3. Lowest risk, but slow, and no real data for weeks.
  2. Fast-track only the Phase 3 data-collection tools (stimulus, acquisition, offline quick-look) while Phase 1 continues in parallel. Real data comes quickly and tests the signal before any decoding is built on it.
  3. Build an online decoding demo (Phase 4) now. Rejected: it builds on a signal and pipeline that have not been validated, which is the failure mode from earlier attempts.
- **Decision:** Option 2. Build a minimal SSVEP data-collection app now: a BrainFlow acquisition wrapper (with a synthetic-board mode), a PsychoPy frame-locked stimulus with event markers, raw data and metadata saving, and an offline quick-look notebook (PSD per target and plain CCA). Online decoding, EMG, and vehicle control stay out of scope.
- **Reasoning:** Consistent with working principle 1 ("prove the signal before building on it"). Data collection is a Phase 3 deliverable, so this moves tooling earlier without skipping a gate. The Phase 3 gate checks (alpha peak, SSVEP spectral peaks, above-chance offline classification, measured timing) can be run as soon as data exists.
- **Consequences:**
  - Code is now allowed in `src/acquisition/`, `src/stimulus/`, and `notebooks/`, limited to the scope above.
  - Phase 1 is still the official phase. The paradigm decision and the open questions in charter Section 10 are still open.
  - Risk: without Phase 2, a poor CCA result cannot separate a pipeline bug from a weak signal. Mitigation: look at raw PSD peaks first, since they do not depend on the decoder, and still complete Phase 2 before Phase 4.
  - Stimulus frequencies 7.5, 8.57, 10, and 12 Hz (60 Hz display, fixed refresh) are provisional for this tooling only. Open question 5 stays open until frame timing is measured.
  - Every recording session gets a log in `docs/experiments/`. The laptop runs on battery while the Cyton is worn (charter Section 7).
  - Charter updated: Status field, Phase 1 note in Section 5, revision history (v0.2).
- **Status:** Accepted

