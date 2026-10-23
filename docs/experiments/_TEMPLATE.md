# <YYYY-MM-DD>_<session>: <short description>

One log per recording session (charter Section 8, principle 6), including failed or aborted sessions.

## Setup
- **Data folder:** `data/raw/<YYYY-MM-DD>_<session>/`
- **Board:** Cyton / synthetic; serial port:
- **Montage:** O1, Oz, O2, PO3, POz, PO4, PO7, PO8 (Cyton ch 1-8); reference: ; ground:
- **Electrode impedance / signal quality notes:**
- **Display:** model, refresh rate (measured value from `metadata.json`), viewing distance, room lighting
- **Power:** laptop on battery while the Cyton is worn (charter Section 7): yes / no
- **Command:** `python -m src.stimulus.ssvep_session ...`

## Conditions
- Baseline: eyes open / eyes closed duration
- Targets and frequencies:
- Trials per target, seed:

## Outcome
- Completed / aborted (why):
- Frame timing: dropped frames total, flicker blocks with drops
- Alpha check (eyes closed vs open):
- SSVEP PSD peaks:
- CCA accuracy (chance 25%), binomial p:

## Notes and follow-ups
