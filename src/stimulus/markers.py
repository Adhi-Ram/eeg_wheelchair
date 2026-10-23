"""Event marker code table for SSVEP sessions.

This module is the single source of truth for marker codes. Codes are
written into the BrainFlow marker channel with ``board.insert_marker()``
and into ``events.csv``. BrainFlow requires markers to be non-zero.

| Code    | Event                                   |
|---------|-----------------------------------------|
| 1       | Session start                           |
| 2       | Session end (normal or after abort)     |
| 10 / 11 | Baseline eyes-open start / end          |
| 20 / 21 | Baseline eyes-closed start / end        |
| 100 + k | Cue onset, target k                     |
| 200 + k | Flicker onset, target k                 |
| 300 + k | Flicker offset, target k                |
| 400     | Rest onset                              |
| 999     | Abort (Esc pressed)                     |

Targets k: 1 = up, 2 = down, 3 = left, 4 = right.
"""

SESSION_START = 1
SESSION_END = 2
EYES_OPEN_START = 10
EYES_OPEN_END = 11
EYES_CLOSED_START = 20
EYES_CLOSED_END = 21
CUE_BASE = 100
FLICKER_ON_BASE = 200
FLICKER_OFF_BASE = 300
REST_ONSET = 400
ABORT = 999

# Target index k -> name. Order matches FREQS_HZ in ssvep_session.py.
TARGETS = {1: "up", 2: "down", 3: "left", 4: "right"}


def cue(k):
    return CUE_BASE + k


def flicker_on(k):
    return FLICKER_ON_BASE + k


def flicker_off(k):
    return FLICKER_OFF_BASE + k


def describe(code):
    """Return a human-readable label for a marker code."""
    code = int(code)
    fixed = {
        SESSION_START: "session_start",
        SESSION_END: "session_end",
        EYES_OPEN_START: "eyes_open_start",
        EYES_OPEN_END: "eyes_open_end",
        EYES_CLOSED_START: "eyes_closed_start",
        EYES_CLOSED_END: "eyes_closed_end",
        REST_ONSET: "rest_onset",
        ABORT: "abort",
    }
    if code in fixed:
        return fixed[code]
    base, k = divmod(code, 100)
    if k in TARGETS:
        kind = {1: "cue", 2: "flicker_on", 3: "flicker_off"}.get(base)
        if kind:
            return f"{kind}_{TARGETS[k]}"
    return f"unknown_{code}"
