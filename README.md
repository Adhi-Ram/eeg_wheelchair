# Brain-Controlled RC Car (EEG Wheelchair project)

A shared-control RC car: **SSVEP** (looking at flickering boxes) picks the direction, an **EMG** clench on the right forearm is the stop, and an onboard **obstacle sensor** keeps the car from hitting things. A wheelchair version comes later.

**Current milestone:** M1, SSVEP data-collection app. See the milestone checklist in [`docs/PROJECT_CHARTER.md`](docs/PROJECT_CHARTER.md).

- **Hardware:** OpenBCI Cyton (8 channels, 250 Hz), Raspberry Pi robot car.
- **Software:** Python 3.11, BrainFlow, PsychoPy, NumPy/SciPy/MNE.
- [`docs/DECISION_LOG.md`](docs/DECISION_LOG.md): dated record of decisions.
- [`docs/experiments/`](docs/experiments/): one log per recording session.

This is a research prototype, not a medical device.

## SSVEP data collection (M1)

Environment: Python 3.11 (`/opt/homebrew/bin/python3.11 -m venv .venv && .venv/bin/pip install -r requirements.txt`).

```bash
# Check the stream on its own (synthetic first, then the Cyton)
.venv/bin/python -m src.acquisition.cyton_stream --synthetic --seconds 10
.venv/bin/python -m src.acquisition.cyton_stream --serial-port /dev/cu.usbserial-XXXX

# Smoke test the session (5 s baselines, 2 trials/target, windowed, no Space wait)
.venv/bin/python -m src.stimulus.ssvep_session --synthetic --quick --windowed

# Real session: fullscreen, Space to start, Esc aborts (data is still saved)
.venv/bin/python -m src.stimulus.ssvep_session --serial-port /dev/cu.usbserial-XXXX --session s01
```

- The session checks the display refresh rate at startup and refuses to run if it is not `--refresh-hz` (default 60). On a ProMotion Mac, set a fixed refresh rate in System Settings > Displays, or pass `--refresh-hz 120` (all four frequencies are whole frame counts at both 60 and 120 Hz).
- Output goes to `data/raw/<date>_<session>/`: `raw.csv` (BrainFlow format, read with `DataFilter.read_file`), `events.csv`, `metadata.json`.
- Marker codes are documented in `src/stimulus/markers.py`.
- Analyse with `notebooks/ssvep_quicklook.ipynb`, and log each session in `docs/experiments/` (see `_TEMPLATE.md`).
