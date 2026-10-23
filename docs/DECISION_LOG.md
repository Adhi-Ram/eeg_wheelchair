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

## 2026-10-22: Simplify the project to a shared-control RC car with milestones

- **Context:** The six-phase wheelchair charter, plus fast-tracking Phase 3 work, made it hard to track where the project stands. After reading some of the research, the project lead settled on a concrete design.
- **Options considered:**
  1. Keep the six phases and keep adding exceptions: thorough, but confusing to follow.
  2. Rewrite the charter around one concrete goal with a simple milestone checklist and build as you go.
- **Decision:** Option 2. The goal is a shared-control RC car: SSVEP picks the direction, EMG on the right forearm is the stop, and an onboard obstacle system stops or steers around obstacles. The literature phase and the public-data validation phase are dropped as required steps. The wheelchair is deferred.
- **Reasoning:** A single goal and a short checklist are easier to follow. The core safeguard is kept as a working rule: check the raw signal before trusting a decoder, and use a public dataset only if results on real data are unclear.
- **Consequences:** Charter rewritten (v1.0) with milestones M1 to M7; CLAUDE.md and README updated. The SSVEP data-collection code already built counts as M1. Earlier entries below are kept as history; their phase references are superseded.
- **Status:** Accepted


## 2026-10-22: Use Python 3.11 for the project environment

- **Phase:** 1 (Research and planning)
- **Context:** The SSVEP stimulus needs PsychoPy. The existing `.venv` was Python 3.14.2. On 3.14, pip only finds PsychoPy 2023.1.3 (newer releases do not support 3.14), and that version fails to install because its pinned numpy does not build (`pkgutil.ImpImporter` removed). A dry run on Homebrew Python 3.11 resolved PsychoPy 2026.2.4 and BrainFlow 5.23.0 cleanly.
- **Options considered:**
  1. Rebuild `.venv` on Python 3.11: one environment for acquisition, stimulus, and analysis. Cost: numpy and scipy drop to the versions PsychoPy accepts (numpy 2.5.3 -> 2.3.5, scipy 1.18.1 -> 1.17.1).
  2. Keep 3.14 for analysis and add a separate 3.11 environment for the stimulus: newest analysis libraries, but two environments and two requirements files to keep in sync.
- **Decision:** Option 1.
- **Reasoning:** The stimulus and acquisition run in one process (markers are inserted from the PsychoPy flip), so they must share an environment anyway. One environment is simpler, and nothing in the current scope needs numpy 2.5 or scipy 1.18. mne 1.13.2 imports on the new versions (not otherwise exercised yet; the quick-look notebook uses numpy/scipy).
- **Consequences:** `.venv` rebuilt with Homebrew `python3.11`; `requirements.txt` regenerated with `pip freeze` (now includes PsychoPy and its dependencies, plus ipykernel/nbconvert for the notebook). Charter Section 3.3 updated (v0.3).
- **Status:** Accepted

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

