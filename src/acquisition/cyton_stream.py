"""BrainFlow wrapper for the OpenBCI Cyton, with a synthetic-board mode.

Standalone use (hardware check, no stimulus):

    python -m src.acquisition.cyton_stream --synthetic --seconds 10
    python -m src.acquisition.cyton_stream --serial-port /dev/cu.usbserial-XXXX

Timing note: insert_marker() tags the sample that is next written into the
host-side buffer, so Bluetooth/dongle latency and jitter between true
acquisition and host arrival are NOT removed. Measuring that (e.g. a
photodiode on a Cyton analog pin) is required for Phase 3 gate 4.
TODO: photodiode latency measurement.
"""

import argparse
import json
import time
from datetime import date
from pathlib import Path

import numpy as np
from brainflow.board_shim import BoardIds, BoardShim, BrainFlowInputParams
from brainflow.data_filter import DataFilter

# Cyton channels 1-8 in wiring order (charter Section 3.2).
MONTAGE = ["O1", "Oz", "O2", "PO3", "POz", "PO4", "PO7", "PO8"]

REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = REPO_ROOT / "data" / "raw"


class CytonStream:
    """Owns one BrainFlow session. Use as a context manager so the stream is
    always stopped and the session released, even on errors."""

    def __init__(self, serial_port=None, synthetic=False, buffer_seconds=900):
        if not synthetic and not serial_port:
            raise ValueError("Pass serial_port, or synthetic=True")
        self.synthetic = synthetic
        self.board_id = BoardIds.SYNTHETIC_BOARD.value if synthetic else BoardIds.CYTON_BOARD.value
        params = BrainFlowInputParams()
        if not synthetic:
            params.serial_port = serial_port
        self.serial_port = serial_port
        self.board = BoardShim(self.board_id, params)
        self.sampling_rate = BoardShim.get_sampling_rate(self.board_id)
        self.eeg_channels = BoardShim.get_eeg_channels(self.board_id)[: len(MONTAGE)]
        self.marker_channel = BoardShim.get_marker_channel(self.board_id)
        self.timestamp_channel = BoardShim.get_timestamp_channel(self.board_id)
        # Ring buffer holds the whole session; data is pulled once at the end
        # so nothing reads the board while the stimulus is flickering.
        self.buffer_size = int(buffer_seconds * self.sampling_rate)
        self._streaming = False

    def start(self):
        self.board.prepare_session()
        self.board.start_stream(self.buffer_size)
        self._streaming = True

    def insert_marker(self, code):
        self.board.insert_marker(float(code))

    def get_all_data(self, tail_seconds=0.5):
        """Return and clear everything in the ring buffer (rows x samples).

        A marker is attached to the next sample that arrives, so we wait
        briefly first; otherwise a marker inserted just before this call
        (e.g. session end) would be lost.
        """
        time.sleep(tail_seconds)
        return self.board.get_board_data()

    def stop(self):
        if self._streaming:
            self.board.stop_stream()
            self._streaming = False
        if self.board.is_prepared():
            self.board.release_session()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *exc):
        self.stop()

    def describe(self):
        """Board info for metadata.json."""
        return {
            "board_id": self.board_id,
            "board_name": "synthetic" if self.synthetic else "cyton",
            "serial_port": self.serial_port,
            "sampling_rate_hz": self.sampling_rate,
            "eeg_channel_rows": self.eeg_channels,
            "marker_channel_row": self.marker_channel,
            "timestamp_channel_row": self.timestamp_channel,
            "montage": dict(zip(MONTAGE, self.eeg_channels)),
            "brainflow_version": BoardShim.get_version(),
        }


def make_session_dir(session_name):
    out = RAW_DIR / f"{date.today().isoformat()}_{session_name}"
    out.mkdir(parents=True, exist_ok=False)
    return out


def save_raw(out_dir, data):
    """Write the full board array (all rows, incl. timestamps and markers)."""
    DataFilter.write_file(data, str(out_dir / "raw.csv"), "w")


def add_board_args(parser):
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--serial-port", help="Cyton dongle port, e.g. /dev/cu.usbserial-XXXX")
    src.add_argument("--synthetic", action="store_true", help="Use BrainFlow's synthetic board")


def main():
    parser = argparse.ArgumentParser(description="Stream from the Cyton (or synthetic board) and save raw data.")
    add_board_args(parser)
    parser.add_argument("--seconds", type=float, default=10.0)
    parser.add_argument("--session", default="stream_check")
    args = parser.parse_args()

    with CytonStream(args.serial_port, args.synthetic) as stream:
        info = stream.describe()
        print(json.dumps(info, indent=2))
        stream.insert_marker(1)
        time.sleep(args.seconds)
        stream.insert_marker(2)
        data = stream.get_all_data()

    n = data.shape[1]
    ts = data[stream.timestamp_channel]
    print(f"{n} samples in {ts[-1] - ts[0]:.2f} s "
          f"(effective {n / (ts[-1] - ts[0]):.1f} Hz, nominal {stream.sampling_rate} Hz)")
    print("markers found:", data[stream.marker_channel][data[stream.marker_channel] != 0])
    eeg = data[stream.eeg_channels]
    for name, row in zip(MONTAGE, eeg):
        print(f"  {name:4s} mean {np.mean(row):10.2f}  std {np.std(row):8.2f} uV")

    out = make_session_dir(args.session)
    save_raw(out, data)
    (out / "metadata.json").write_text(json.dumps({"board": info, "duration_s": args.seconds}, indent=2))
    print("saved to", out)


if __name__ == "__main__":
    main()
