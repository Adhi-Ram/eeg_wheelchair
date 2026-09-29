# EEG Wheelchair: Project Charter

| Field | Value |
|---|---|
| Project lead | Adhitya (UCLA Bioengineering) |
| Status | Phase 1: Research |
| Charter version | 0.1 (draft) |
| Last updated | 2026-09-29 |

---

## 0. How to use this document

This charter is the single source of truth for the project's goal, scope, phases, and working rules. It is written for two audiences: the project lead, and AI assistants (Claude Code, Claude Cowork) that work in this repository.

**For AI assistants:**
- Read this file before starting any task in this repository.
- Check Section 5 to learn the current phase. Do not build components that belong to a later phase unless explicitly asked.
- Follow the working principles in Section 8. They exist because earlier versions of this project failed by skipping them.
- Treat items in Section 10 (Open Questions) as undecided. Do not assume an answer; ask or flag it.
- When a decision is made, it is recorded in `docs/DECISION_LOG.md`, and this charter is updated to match.

---

## 1. Vision

Build a wheelchair that a user can steer using brain activity (EEG), with muscle activity (EMG) providing a fast and reliable safety channel. Before working with a wheelchair, the full system is proven on a small RC car.

The long-term goal is a system that is genuinely usable, not just a lab demo: reliable command decoding, a dependable stop mechanism, and enough onboard intelligence (shared control) that the user provides high-level intent while the vehicle handles low-level safety.

---

## 2. Background and lessons learned

Two previous attempts did not succeed. Their failure modes shape this charter.

### Attempt 1: "Think the direction" decoding
- **Approach:** The user imagined the desired direction, and the system tried to decode it from EEG.
- **Outcome:** Recordings appeared to contain no usable signal.
- **Likely cause:** Abstract directional intention has no reliable scalp EEG signature. Decodable imagined-movement signals (motor imagery) require specific body-part imagery, specific electrode sites (C3, Cz, C4), and substantial user training.

### Attempt 2: P300 with flashing arrows
- **Approach:** Four arrows (forward, back, left, right) flashed; the target was identified from the P300 response.
- **Outcome:** Did not work reliably.
- **Likely causes (to be verified):**
  - Stimulus and EEG timestamps were not tightly synchronized; Bluetooth streaming jitter smears the P300.
  - With only four targets, each flash is a 25% event, which weakens the oddball response.
  - Too few repetitions averaged before classification.
  - Electrode montage may not have covered centro-parietal sites (Cz, Pz, P3, P4, PO7, PO8).

### Process lessons
1. Too little time was spent reviewing prior work before building.
2. Project direction was not fixed, so effort was scattered.
3. The full system was built before confirming that the signal existed.

---

## 3. Technical approach

> **Status:** Proposed. The paradigm choice is confirmed or revised at the end of Phase 1 (see Section 10).

### 3.1 Control paradigm (proposed)
- **Primary: SSVEP.** Each command is a visual stimulus flickering at a distinct frequency. Looking at a stimulus produces a measurable response at that frequency (and its harmonics) over the visual cortex. SSVEP offers high signal-to-noise ratio with 8 channels, requires little or no user training, and can be decoded without calibration using CCA-based methods.
- **Safety channel: EMG.** A deliberate muscle action (for example, a jaw clench) acts as an immediate stop and, optionally, a command confirmation. The stop must never depend on the slower EEG channel.
- **Shared control (Phase 6).** The BCI supplies high-level intent; the vehicle handles obstacle detection and low-level motion.

**Known limitation:** SSVEP requires the user to look at the stimuli rather than the environment. This is acceptable for the RC car stage and must be addressed before the wheelchair stage (for example, stimuli placed in the user's field of view, or a hybrid design).

### 3.2 Hardware
| Component | Details | Notes |
|---|---|---|
| EEG | OpenBCI Cyton, 8 channels, 250 Hz | Streams via Bluetooth dongle; timing jitter must be handled |
| EMG | To be confirmed | See Section 10 |
| Stimulus display | Laptop or monitor | Refresh rate constrains usable SSVEP frequencies |
| Proof-of-concept vehicle | RC car with Raspberry Pi | Pi robot car kit preferred over modifying a stock RC car |
| Final vehicle | Wheelchair | Source to be confirmed |

**Proposed SSVEP montage:** O1, Oz, O2, PO3, POz, PO4, PO7, PO8 (reference and ground per OpenBCI guidance).

### 3.3 Software stack (proposed)
| Purpose | Tool |
|---|---|
| Cyton acquisition | BrainFlow |
| Time synchronization of streams | Lab Streaming Layer (LSL) |
| Stimulus presentation | PsychoPy (frame-locked timing) |
| Offline analysis | MNE-Python, NumPy, SciPy |
| Benchmarking on public data | MOABB |
| Decoding | CCA / filter-bank CCA to start; TRCA as a later option |
| Vehicle communication | UDP over Wi-Fi, laptop to Raspberry Pi |

**Architecture rule:** All signal processing and decoding runs on the laptop. The Raspberry Pi only receives simple commands and drives motors.

---

## 4. Scope

### In scope
- Non-invasive EEG and surface EMG only.
- A small command set (target: 4 motion commands plus stop).
- Testing on the project lead as the primary user.
- RC car proof of concept, followed by a wheelchair prototype.

### Out of scope (for now)
- Invasive recording of any kind.
- Continuous (proportional) control; the system issues discrete commands.
- Use by people with disabilities or testing on other participants without appropriate review (see Section 7).
- Custom EEG hardware.

---

## 5. Phases and go/no-go criteria

Each phase ends with a gate. The next phase does not begin until the gate criteria are met or a documented decision is made to change them.

| Phase | Name | Est. duration |
|---|---|---|
| 1 | Research and planning | 2-3 weeks |
| 2 | Pipeline validation on public data | 1-2 weeks |
| 3 | Signal sanity check with Cyton | 1-2 weeks |
| 4 | Online decoding on screen | 3-4 weeks |
| 5 | RC car integration | 3-4 weeks |
| 6 | Wheelchair prototype | TBD |

Durations are estimates and will be revised.

### Phase 1: Research and planning (CURRENT)
- **Goal:** Understand prior work and commit to a paradigm.
- **Deliverables:** Literature notes in `docs/literature/`; confirmed paradigm; updated charter; initialized repository.
- **Gate:** Paradigm decision recorded in the decision log with supporting references. Open questions in Section 10 answered or explicitly deferred.

### Phase 2: Pipeline validation on public data
- **Goal:** Confirm the decoding code works on data known to contain the signal.
- **Deliverables:** Notebook that loads a public SSVEP dataset and reports classification accuracy.
- **Gate:** Accuracy comparable to published results for the same method and dataset. If not, the bug is in the pipeline, not the hardware.

### Phase 3: Signal sanity check with Cyton
- **Goal:** Confirm the recording setup captures real brain signals.
- **Deliverables:** Offline recordings and analysis notebooks.
- **Gate:**
  1. Eyes-closed recordings show a clear alpha peak (around 10 Hz) over occipital channels compared with eyes-open.
  2. SSVEP recordings show clear spectral peaks at each stimulus frequency.
  3. Offline classification of recorded SSVEP trials is clearly above chance.
  4. Stimulus and EEG timestamps are synchronized, with measured latency and jitter documented.

### Phase 4: Online decoding on screen
- **Goal:** Real-time classification of which stimulus the user is attending to.
- **Deliverables:** Real-time application showing decoded commands; EMG stop detection.
- **Gate (targets, to be refined in Phase 1):**
  - Online accuracy of at least 85% across the command set.
  - Decision time of a few seconds or less per command.
  - Low false-command rate when the user is not attending to any stimulus (idle state).
  - EMG stop detected reliably with minimal latency.

### Phase 5: RC car integration
- **Goal:** Drive the RC car with the Phase 4 system.
- **Deliverables:** Pi-based car receiving commands over Wi-Fi; end-to-end demo.
- **Gate:** The user completes a simple course (for example, a short route with turns) using only BCI and EMG commands, with the EMG stop working every time.

### Phase 6: Wheelchair prototype
- **Goal:** Port the system to a wheelchair with shared control.
- **Deliverables:** Defined at the end of Phase 5.
- **Gate:** Defined at the end of Phase 5. Safety requirements in Section 7 apply in full.

---

## 6. Success metrics

| Metric | Definition | Tracked from |
|---|---|---|
| Classification accuracy | Correct commands / total commands | Phase 2 |
| Decision time | Seconds from stimulus onset to issued command | Phase 4 |
| Information transfer rate (ITR) | Standard BCI bits-per-minute measure | Phase 4 |
| Idle false-positive rate | Unintended commands per minute while idle | Phase 4 |
| Stop latency | Time from EMG action to vehicle stop | Phase 4 |
| Task completion | Course completed without manual intervention | Phase 5 |

---

## 7. Safety and ethics

- **Independent kill switch:** Every vehicle has a physical or remote stop that does not depend on the BCI or EMG pipeline.
- **EMG stop priority:** The EMG stop overrides all EEG commands.
- **Fail-safe default:** If the signal stream drops or decoding confidence is low, the vehicle stops.
- **Speed limits:** Conservative speed caps on all vehicles, especially the wheelchair.
- **Spotter required:** Wheelchair testing always has a second person present.
- **Electrical safety:** The Cyton runs on battery power. It is not connected to mains-powered equipment while worn.
- **Human subjects:** Testing on anyone other than the project lead requires checking UCLA IRB requirements first.
- **Not a medical device:** This is a research prototype and is not intended for clinical use.

---

## 8. Working principles

These apply to all contributors, including AI assistants.

1. **Prove the signal before building on it.** Every new paradigm or setup is validated offline before any real-time or hardware work.
2. **Validate code on known-good data first.** New analysis or decoding code is tested on public datasets before being applied to new recordings.
3. **Stay in the current phase.** Work that belongs to a later phase is noted, not built.
4. **Start simple.** Use the simplest method that meets the gate (for example, CCA before deep learning).
5. **Log decisions.** Significant choices go in `docs/DECISION_LOG.md` with date, options considered, and reasoning.
6. **Log experiments.** Every recording session gets an entry in `docs/experiments/` with date, setup, montage, conditions, and outcome, including failures.
7. **Measure timing.** Any component that timestamps events has its latency and jitter measured, not assumed.
8. **Safety is not deferred.** Safety requirements in Section 7 are built in at the phase where they first apply.

---

## 9. Repository structure

```
eeg-wheelchair/
├── CLAUDE.md                  # Short orientation for Claude Code; points here
├── README.md                  # Human-facing overview
├── docs/
│   ├── PROJECT_CHARTER.md     # This file
│   ├── DECISION_LOG.md        # Dated record of decisions
│   ├── literature/            # One note per paper
│   └── experiments/           # One log per recording session
├── data/
│   ├── raw/                   # Unmodified recordings (not committed to Git)
│   └── processed/
├── notebooks/                 # Exploratory and offline analysis
├── src/
│   ├── acquisition/           # BrainFlow / LSL streaming
│   ├── stimulus/              # PsychoPy stimulus code
│   ├── processing/            # Filtering, epoching, feature extraction
│   ├── decoding/              # Classifiers
│   └── control/               # Command logic and vehicle communication
├── hardware/                  # Wiring diagrams, parts lists, Pi code
└── tests/
```

### Literature note template
Each file in `docs/literature/` follows this format:
- Citation
- Paradigm
- Hardware and channel count
- Number of subjects
- Decoding method
- Reported performance (accuracy, ITR, decision time)
- Relevance to this project
- Key takeaways

---

## 10. Open questions

To be resolved during Phase 1 unless noted.

1. Is SSVEP confirmed as the primary paradigm, or does the literature review favor another approach or a hybrid?
2. How will the gaze limitation of SSVEP be handled at the wheelchair stage?
3. What EMG hardware is available, and can it be recorded through the Cyton or does it need a separate device?
4. Which public SSVEP dataset will be used for Phase 2?
5. What stimulus frequencies are usable given the display's refresh rate?
6. What exact numeric targets should the Phase 4 gate use (accuracy, decision time, idle false-positive rate)?
7. Which RC car or robot kit and motor driver will be used?
8. What wheelchair will be available for Phase 6, and how will it be interfaced?
9. What are UCLA's IRB requirements if other participants are ever tested?

---

## 11. Starting references

- Wolpaw et al. (2002). Brain-computer interfaces for communication and control.
- Fernández-Rodríguez et al. (2016). Review of real brain-controlled wheelchairs.
- Lin et al. (2006). CCA-based frequency recognition for SSVEP-based BCIs.
- Chen et al. (2015, PNAS). High-speed spelling with a noninvasive brain-computer interface.
- Rebsamen et al. (2010). A brain-controlled wheelchair to navigate in familiar environments.
- Iturrate et al. (2009). A noninvasive brain-actuated wheelchair based on a P300 neurophysiological protocol and automated navigation.
- Tonin et al. (2022, iScience). Learning to control a BMI-driven wheelchair for people with severe tetraplegia.

Full notes for each reference live in `docs/literature/`.

---

## 12. Revision history

| Version | Date | Changes |
|---|---|---|
| 0.1 | 2026-09-29 | Initial draft |
