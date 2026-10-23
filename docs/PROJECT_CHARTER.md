# Brain-Controlled RC Car: Project Charter

| Field | Value |
|---|---|
| Project lead | Adhitya (UCLA Bioengineering) |
| Current milestone | M1: SSVEP data-collection app (built, fixing frame drops) |
| Charter version | 1.0 |
| Last updated | 2026-10-22 |

This is the single source of truth for the project. It is short on purpose. Build as you go, one milestone at a time.

---

## 1. Goal

A **shared-control RC car**:

- **SSVEP picks the direction.** Four flickering boxes on the laptop screen. Looking at one sends that direction to the car.
- **EMG on the right forearm is the stop.** A deliberate muscle clench stops the car immediately and overrides everything else.
- **The car handles obstacles itself.** An onboard sensor detects obstacles. First the car stops before hitting them; later it steers around them.

The user gives high-level intent; the car handles low-level safety. A wheelchair version comes later and is out of scope for now.

---

## 2. How it fits together

```
 Laptop screen (4 flickering boxes)
          |  user looks at one
          v
 OpenBCI Cyton  --- EEG (occipital) ---+
 (8 ch, 250 Hz)  --- EMG (R forearm) --+--> Laptop: SSVEP decoder + EMG stop detector
                                                     |
                                                     |  UDP over Wi-Fi: direction / STOP
                                                     v
                                     Raspberry Pi car: motors + obstacle sensor
                                     (obstacle logic can veto or adjust a command)
```

**Rule:** all signal processing runs on the laptop. The Pi receives simple commands, drives the motors, and runs the obstacle logic.

---

## 3. Hardware and software

| Part | Choice | Notes |
|---|---|---|
| EEG / EMG amplifier | OpenBCI Cyton, 8 ch, 250 Hz | Bluetooth dongle; timing jitter is not yet measured |
| EEG montage | O1, Oz, O2, PO3, POz, PO4, PO7, PO8 | See open question 1 about freeing a channel for EMG |
| Stimulus display | MacBook screen at a **fixed 60 Hz** | Frequencies 7.5, 8.57, 10, 12 Hz (whole frame counts) |
| Car | Raspberry Pi robot car kit | Model to be chosen |
| Obstacle sensor | To be chosen | e.g. ultrasonic for a first version |
| Python | 3.11 in `.venv` | PsychoPy does not install on 3.14 (decision log 2026-10-22) |
| Acquisition | BrainFlow | |
| Stimulus | PsychoPy (frame-locked flicker) | |
| Analysis | NumPy, SciPy, MNE-Python | |
| Decoding | CCA to start; filter-bank CCA or TRCA if needed | |
| Car link | UDP over Wi-Fi | |

---

## 4. Milestones

Work through these roughly in order. Each has a "done when" check. Milestones 5 and 6 (the car) do not depend on EEG and can be built in parallel whenever convenient.

| # | Milestone | Done when | Status |
|---|---|---|---|
| M1 | SSVEP data-collection app | A fullscreen session at fixed 60 Hz runs with close to zero dropped frames, and saves raw data, events and metadata | Built; fixing frame drops |
| M2 | SSVEP signal check (offline) | Eyes-closed alpha peak visible; spectral peaks at each stimulus frequency; offline CCA clearly above 25% chance | Not started |
| M3 | Real-time SSVEP on screen | Live app shows the decoded direction; target about 85% accuracy and a decision within about 3 s | Not started |
| M4 | EMG stop | Right-forearm clench detected live, fast and every time, with no false stops during normal SSVEP use | Not started |
| M5 | Car driven from the laptop | Pi car drives from keyboard commands over UDP, and stops on its own if commands stop arriving | Not started |
| M6 | Obstacle detection | Car stops before hitting an obstacle. Stretch: steers around it | Not started |
| M7 | Full shared-control demo | Drive a short course with SSVEP directions and EMG stop, with the obstacle system preventing collisions | Not started |

---

## 5. Safety rules (always apply)

- **Physical kill switch** on the car that does not depend on any software.
- **EMG stop overrides** every EEG command.
- **Fail-safe:** if the data stream drops, decoding confidence is low, or the Pi stops receiving commands, the car stops.
- **Slow speed caps** on the car.
- **Battery only:** the laptop runs on battery (charger unplugged) while the Cyton is worn.
- **Only the project lead is tested.** Check UCLA IRB requirements before testing anyone else.
- Research prototype, not a medical device.

---

## 6. Working rules

1. **Check the signal before building on it.** Look at the raw spectra before trusting a decoder. If CCA fails on real data, run the notebook on a public SSVEP dataset to tell a code bug from a weak signal.
2. **Build as you go, one milestone at a time.** Do not build later milestones early unless the project lead asks.
3. **Log decisions** in `docs/DECISION_LOG.md` (date, options, choice, why).
4. **Log every recording session** in `docs/experiments/` (copy `_TEMPLATE.md`), including failed ones.

---

## 7. Open questions

Not yet decided. Ask the project lead rather than assuming.

1. **EMG hardware:** record EMG on one Cyton channel (leaving 7 EEG channels), add a Daisy board, or use a separate device?
2. **Command set:** what do the four boxes mean? (Proposed: forward, reverse, left, right, matching the current up/down/left/right layout.)
3. **Idle behavior:** when the user is not looking at any box, does the car keep doing the last command, or stop?
4. **Obstacle behavior:** what does "avoid" mean at first: stop only, or stop and turn?
5. **Car kit and obstacle sensor:** which ones?

---

## 8. Repository layout

```
docs/        Charter, decision log, experiment logs (literature/ is optional notes)
data/raw/    Recordings, never edited, not committed to Git
notebooks/   Offline analysis (ssvep_quicklook.ipynb)
src/         acquisition -> processing -> decoding -> control, plus stimulus
hardware/    Car wiring, parts list, Pi code
tests/       Tests
```

---

## 9. Revision history

| Version | Date | Changes |
|---|---|---|
| 0.1 to 0.3 | 2026-09-29 to 2026-10-22 | Original six-phase wheelchair charter (see Git history) |
| 1.0 | 2026-10-22 | Rewritten around a shared-control RC car: milestones replace phases, literature phase dropped, wheelchair deferred |
