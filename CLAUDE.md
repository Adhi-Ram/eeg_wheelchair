# CLAUDE.md

Before starting any task in this repository:

1. Read `docs/PROJECT_CHARTER.md`. It is the single source of truth for goals, scope, phases, and working rules.
2. Check the current phase (charter Section 5 and the Status field at the top). Only do work that belongs to the current phase. Work for a later phase is noted, not built, unless the project lead explicitly asks for it.
3. Follow the working principles in charter Section 8.
4. Treat the open questions in charter Section 10 as undecided. Do not assume an answer; ask or flag it.
5. When a decision is made, add an entry to `docs/DECISION_LOG.md` and update the charter to match.

Current phase: **Phase 1 (Research and planning).**

Approved exception (see `docs/DECISION_LOG.md`, 2026-10-22): Phase 3 SSVEP data-collection tooling may be built now. That covers `src/acquisition/` (BrainFlow wrapper with a synthetic-board mode), `src/stimulus/` (PsychoPy frame-locked SSVEP stimulus with event markers), saving raw data and metadata to `data/raw/`, and an offline quick-look notebook in `notebooks/`. Online decoding, EMG, and vehicle control are still out of scope. Test against the BrainFlow synthetic board before using the Cyton.
