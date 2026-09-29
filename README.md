# EEG Wheelchair

A wheelchair steered by brain activity (EEG), with muscle activity (EMG) as a fast, reliable stop channel. The full system is proven on a small RC car first.

**Status:** Phase 1 (Research and planning).

- **Proposed paradigm:** SSVEP for commands, EMG (e.g. a jaw clench) for stop. To be confirmed at the end of Phase 1.
- **Hardware:** OpenBCI Cyton (8 channels, 250 Hz), Raspberry Pi RC car, then a wheelchair.
- **Software (proposed):** BrainFlow, LSL, PsychoPy, MNE-Python, MOABB.

## Where to start

- [`docs/PROJECT_CHARTER.md`](docs/PROJECT_CHARTER.md): goals, scope, phases, safety rules, and repository layout.
- [`docs/DECISION_LOG.md`](docs/DECISION_LOG.md): dated record of decisions.
- [`docs/literature/`](docs/literature/): one note per paper (see `_TEMPLATE.md`).
- [`docs/experiments/`](docs/experiments/): one log per recording session.

This is a research prototype, not a medical device.
