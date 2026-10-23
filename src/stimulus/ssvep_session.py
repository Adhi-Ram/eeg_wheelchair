"""Frame-locked SSVEP data-collection session (PsychoPy + BrainFlow).

    python -m src.stimulus.ssvep_session --synthetic --quick --windowed
    python -m src.stimulus.ssvep_session --serial-port /dev/cu.usbserial-XXXX --session s01

Flow: Space to start -> 60 s eyes open -> 60 s eyes closed (beep at end)
-> trials (cue 1 s, flicker 4 s, rest 2 s; 10 per target, shuffled).
Esc aborts at any point; data recorded so far is still saved and the
stream is stopped.

Flicker is driven only by frame counts: box k is "on" when
(frame % period_k) < on_frames_k. Durations are also in frames. Nothing
here uses sleep or clock time to time the stimulus.

On macOS ProMotion displays, set a fixed 60 Hz refresh before running;
the startup check aborts if the measured rate does not match.
"""

import argparse
import csv
import json
import math
import platform
import random
import sys
import time
from datetime import datetime

import numpy as np
import psychopy
from psychopy import core, event, logging, visual

from src.acquisition.cyton_stream import CytonStream, add_board_args, make_session_dir, save_raw
from src.stimulus import markers as M

# Target k -> flicker frequency. Provisional (decision log 2026-10-22).
FREQS_HZ = {1: 7.5, 2: 8.57, 3: 10.0, 4: 12.0}
# Box centres in "height" units (screen height = 1).
POSITIONS = {1: (0, 0.33), 2: (0, -0.33), 3: (-0.45, 0), 4: (0.45, 0)}
BOX_SIZE = 0.2

CUE_S, FLICKER_S, REST_S = 1.0, 4.0, 2.0
BASELINE_S = 60.0
TRIALS_PER_TARGET = 10
REFRESH_TOLERANCE_HZ = 1.0
DROP_MARGIN_S = 0.004  # frame counted as dropped if interval > period + 4 ms


class Aborted(Exception):
    pass


def flicker_schedule(refresh_hz):
    """Frames per cycle and on-frames per target (square wave).

    Odd periods get an uneven duty cycle, e.g. 7 frames -> 4 on / 3 off.
    """
    sched = {}
    for k, f in FREQS_HZ.items():
        period = round(refresh_hz / f)
        on = math.ceil(period / 2)
        sched[k] = {
            "freq_hz_nominal": f,
            "frames_per_cycle": period,
            "on_frames": on,
            "off_frames": period - on,
            "freq_hz_at_nominal_refresh": refresh_hz / period,
        }
    return sched


class Session:
    def __init__(self, win, stream, sched, frame_s):
        self.win = win
        self.stream = stream
        self.sched = sched
        self.frame_s = frame_s
        self.events = []
        self.frame = 0  # global frame counter, drives the flicker phase

        self.boxes = {
            k: visual.Rect(win, width=BOX_SIZE, height=BOX_SIZE, pos=pos, units="height",
                           fillColor="white", lineColor=None)
            for k, pos in POSITIONS.items()
        }
        self.cue_frame = visual.Rect(win, width=BOX_SIZE * 1.3, height=BOX_SIZE * 1.3, units="height",
                                     fillColor=None, lineColor="red", lineWidth=8)
        self.fixation = visual.TextStim(win, "+", height=0.08, color="white", units="height")
        self.text = visual.TextStim(win, "", height=0.04, color="white", units="height", wrapWidth=1.2)

    # -- frame primitives -------------------------------------------------

    def flip(self, code=None, **info):
        """Flip once. If code is given, the marker is inserted on this flip."""
        if code is not None:
            self.win.callOnFlip(self.stream.insert_marker, code)
        t = self.win.flip()
        self.frame += 1
        if code is not None:
            self.log(code, t, **info)
        if event.getKeys(["escape"]):
            raise Aborted
        return t

    def log(self, code, flip_t, **info):
        self.events.append({
            "code": code,
            "label": M.describe(code),
            "psychopy_flip_s": flip_t,
            "unix_time_s": time.time(),
            **info,
        })

    def frames(self, seconds):
        return int(round(seconds / self.frame_s))

    def hold(self, n_frames, draw, code=None, **info):
        """Show `draw` for n_frames. Marker (if any) goes on the first flip."""
        for i in range(n_frames):
            draw()
            self.flip(code if i == 0 else None, **(info if i == 0 else {}))

    def dropped_since(self, start_idx):
        iv = np.asarray(self.win.frameIntervals[start_idx:])
        return int(np.sum(iv > self.frame_s + DROP_MARGIN_S))

    # -- drawing ----------------------------------------------------------

    def draw_static(self, cue_k=None):
        for b in self.boxes.values():
            b.fillColor = "gray"
            b.draw()
        if cue_k is not None:
            self.cue_frame.pos = POSITIONS[cue_k]
            self.cue_frame.draw()
        self.fixation.draw()

    def draw_flicker(self, flicker_frame):
        for k, b in self.boxes.items():
            s = self.sched[k]
            on = (flicker_frame % s["frames_per_cycle"]) < s["on_frames"]
            b.fillColor = "white" if on else "black"
            b.draw()
        self.fixation.draw()

    def show_text(self, msg):
        self.text.text = msg
        self.text.draw()

    # -- blocks -----------------------------------------------------------

    def wait_for_space(self, msg):
        event.clearEvents()
        while True:
            self.show_text(msg)
            self.flip()
            keys = event.getKeys(["space", "escape"])
            if "escape" in keys:
                raise Aborted
            if "space" in keys:
                return

    def baseline(self, seconds, beep):
        n = self.frames(seconds)
        self.hold(self.frames(3), lambda: self.show_text("Eyes OPEN. Look at the +"))
        self.hold(n, self.fixation.draw, M.EYES_OPEN_START)
        self.flip(M.EYES_OPEN_END)

        self.hold(self.frames(3), lambda: self.show_text("Close your eyes now.\nOpen them at the beep."))
        self.hold(n, lambda: None, M.EYES_CLOSED_START)
        self.flip(M.EYES_CLOSED_END)
        beep()
        self.hold(self.frames(3), lambda: self.show_text("Open your eyes.\nTrials start shortly."))

    def trial(self, idx, k):
        info = {"trial": idx, "target": M.TARGETS[k], "freq_hz": FREQS_HZ[k]}
        self.hold(self.frames(CUE_S), lambda: self.draw_static(cue_k=k), M.cue(k), **info)

        start = len(self.win.frameIntervals)
        n = self.frames(FLICKER_S)
        for i in range(n):
            self.draw_flicker(i)  # phase restarts at 0 each trial
            self.flip(M.flicker_on(k) if i == 0 else None, **(info if i == 0 else {}))
        self.draw_static()
        self.flip(M.flicker_off(k), **info, dropped_frames=self.dropped_since(start + 1))

        self.hold(self.frames(REST_S) - 1, self.draw_static, M.REST_ONSET, trial=idx)


def make_beep():
    try:
        from psychopy import sound
        snd = sound.Sound("A", secs=0.4)
        return snd.play
    except Exception as e:  # sound backend can be flaky on macOS
        logging.warning(f"sound unavailable ({e}); using terminal bell")
        return lambda: print("\a", end="", flush=True)


def frame_stats(win, frame_s):
    iv = np.asarray(win.frameIntervals) * 1000
    if iv.size == 0:
        return {}
    return {
        "n_intervals": int(iv.size),
        "mean_ms": float(iv.mean()),
        "sd_ms": float(iv.std()),
        "min_ms": float(iv.min()),
        "max_ms": float(iv.max()),
        "drop_threshold_ms": (frame_s + DROP_MARGIN_S) * 1000,
        "n_dropped": int(np.sum(iv > (frame_s + DROP_MARGIN_S) * 1000)),
        "psychopy_nDroppedFrames": int(win.nDroppedFrames),
    }


def _jsonable(o):
    return o.item() if hasattr(o, "item") else str(o)


def write_events(path, events):
    cols = ["code", "label", "trial", "target", "freq_hz", "psychopy_flip_s", "unix_time_s", "dropped_frames"]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for e in events:
            w.writerow({c: e.get(c, "") for c in cols})


def main():
    p = argparse.ArgumentParser(description="SSVEP data-collection session.")
    add_board_args(p)
    p.add_argument("--session", default="ssvep", help="Session name; folder is data/raw/<date>_<session>")
    p.add_argument("--refresh-hz", type=float, default=60.0, help="Expected display refresh rate")
    p.add_argument("--trials-per-target", type=int, default=TRIALS_PER_TARGET)
    p.add_argument("--baseline-s", type=float, default=BASELINE_S)
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--screen", type=int, default=0)
    p.add_argument("--windowed", action="store_true", help="Window instead of fullscreen (testing only)")
    p.add_argument("--quick", action="store_true",
                   help="Smoke test: 5 s baselines, 2 trials/target, no Space wait")
    p.add_argument("--notes", default="", help="Free-text notes stored in metadata.json")
    args = p.parse_args()

    if args.quick:
        args.baseline_s, args.trials_per_target = 5.0, 2
    seed = args.seed if args.seed is not None else int(time.time())
    order = [k for k in FREQS_HZ for _ in range(args.trials_per_target)]
    random.Random(seed).shuffle(order)

    logging.console.setLevel(logging.WARNING)
    win = visual.Window(size=(1280, 800), fullscr=not args.windowed, screen=args.screen, color="black",
                        units="height", allowGUI=args.windowed, waitBlanking=True, checkTiming=False)
    win.mouseVisible = False

    # Verify refresh rate before anything is recorded.
    measured = win.getActualFrameRate(nIdentical=30, nMaxFrames=300, nWarmUpFrames=30, threshold=1)
    print(f"measured refresh: {measured} Hz (expected {args.refresh_hz})")
    if measured is None or abs(measured - args.refresh_hz) > REFRESH_TOLERANCE_HZ:
        win.close()
        sys.exit(f"Refresh rate check failed: measured {measured}, expected {args.refresh_hz} "
                 f"+/- {REFRESH_TOLERANCE_HZ} Hz. Fix display settings (fixed refresh, no ProMotion).")
    frame_s = 1.0 / args.refresh_hz
    sched = flicker_schedule(args.refresh_hz)
    for k, s in sched.items():
        s["freq_hz_at_measured_refresh"] = measured / s["frames_per_cycle"]

    win.recordFrameIntervals = True
    win.refreshThreshold = frame_s + DROP_MARGIN_S

    out = make_session_dir(args.session)
    stream = CytonStream(args.serial_port, args.synthetic)
    started = datetime.now().isoformat(timespec="seconds")
    aborted = False
    error = None
    data = None
    sess = None
    n_done = 0
    beep = make_beep()  # sound backend init can stall ~0.7 s; do it before recording
    try:
        stream.start()
        sess = Session(win, stream, sched, frame_s)
        if not args.quick:
            sess.wait_for_space("SSVEP session\n\nKeep your gaze on the cued box when it flickers.\n\n"
                                "Press SPACE to start. Esc aborts.")
        stream.flush()  # drop wait-screen data so a long wait can't overflow the buffer
        event.clearEvents()  # a stale keypress must not abort the first frame
        win.frameIntervals = []  # stats exclude the wait screen
        sess.flip(M.SESSION_START)
        sess.baseline(args.baseline_s, beep)
        for i, k in enumerate(order):
            sess.trial(i, k)
            n_done = i + 1
    except Aborted:
        aborted = True
        print("Esc pressed: aborting, saving data recorded so far.")
        stream.insert_marker(M.ABORT)
        sess.log(M.ABORT, core.getTime())
    except (Exception, KeyboardInterrupt) as e:  # Ctrl+C must still save
        aborted = True
        error = repr(e)
        print("ERROR:", error, "- saving data recorded so far.")
    finally:
        try:
            if stream._streaming:
                stream.insert_marker(M.SESSION_END)
                if sess is not None:
                    sess.log(M.SESSION_END, core.getTime())
                data = stream.get_all_data()
        finally:
            stream.stop()
            stats = frame_stats(win, frame_s)
            win.close()

    if data is not None:
        save_raw(out, data)
    if sess is not None:
        write_events(out / "events.csv", sess.events)
    meta = {
        "session": args.session,
        "started": started,
        "aborted": aborted,
        "error": error,
        "notes": args.notes,
        "quick_mode": args.quick,
        "board": stream.describe(),
        "n_samples": int(data.shape[1]) if data is not None else 0,
        "display": {
            "expected_refresh_hz": args.refresh_hz,
            "measured_refresh_hz": measured,
            "window_size_px": [int(x) for x in win.size],
            "fullscreen": not args.windowed,
        },
        "frame_timing": stats,
        "stimulus": {
            "waveform": "square",
            "targets": {M.TARGETS[k]: {"marker_k": k, "pos_height_units": POSITIONS[k], **sched[k]}
                        for k in FREQS_HZ},
            "box_size_height_units": BOX_SIZE,
            "cue_s": CUE_S, "flicker_s": FLICKER_S, "rest_s": REST_S,
            "baseline_s": args.baseline_s,
            "trials_per_target": args.trials_per_target,
            "trial_order": [M.TARGETS[k] for k in order],
            "trials_completed": n_done,
            "seed": seed,
        },
        "marker_codes": M.__doc__,
        "timing_caveat": "Markers are inserted host-side on the flip; Bluetooth latency/jitter is not "
                         "measured or corrected (Phase 3 gate 4, TODO photodiode).",
        "versions": {"python": platform.python_version(), "psychopy": psychopy.__version__,
                     "numpy": np.__version__, "platform": platform.platform()},
    }
    # default= keeps a stray numpy scalar from losing the metadata of a real recording.
    (out / "metadata.json").write_text(json.dumps(meta, indent=2, default=_jsonable))
    print(f"saved to {out}  (trials {n_done}/{len(order)}, dropped frames {stats.get('n_dropped')})")
    core.quit()


if __name__ == "__main__":
    main()
