"""phase 4: the real-time loop. mic stream -> pipeline -> policy -> cue, with logging.

done when the cue fires correctly and detect->cue latency is under ~500 ms.
hard gate for myself: only run this after phases 0-3 pass on my own recordings.
"""
import argparse
import queue
import sys
import time
from pathlib import Path

import sounddevice as sd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from chew.baseline import Baseline
from chew.cadence import CadenceTracker
from chew.cue import Cue
from chew.detector import ChewDetector
from chew.logger import SessionLogger
from chew.policy import Policy


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["off", "real", "sham"], required=True)
    p.add_argument("--metronome", action="store_true", help="sham uses fixed metronome")
    p.add_argument("--device", type=int, help="input device index (see sd.query_devices())")
    args = p.parse_args()

    detector = ChewDetector()
    tracker = CadenceTracker()
    baseline = Baseline()
    policy = Policy(args.mode, metronome=args.metronome)
    cue = Cue()
    log = SessionLogger(args.mode)
    blocks = queue.Queue()

    def callback(indata, frames, t, status):
        if status:
            print(status, file=sys.stderr)
        blocks.put(indata[:, 0].copy())

    start = time.time()
    print(f"mode={args.mode}  log={log.path}  Ctrl-C to stop")
    try:
        with sd.InputStream(samplerate=config.SAMPLE_RATE, channels=1,
                            blocksize=config.BLOCK_SIZE, device=args.device,
                            callback=callback):
            while True:
                block = blocks.get()
                now = time.time() - start
                chews = detector.process(block)
                for ct in chews:
                    log.chew(ct)
                cpm = tracker.update(chews, now)
                log.cpm(now, cpm)
                state = baseline.update(cpm, now)
                log.state(now, state)
                if policy.should_cue(state, now):
                    cue.play()
                    log.cue(now)
                if baseline.calibrated:
                    print(f"\r{now:6.1f}s  CPM {cpm:5.1f}  base {baseline.baseline_cpm:5.1f}  "
                          f"{state:6s}", end="", flush=True)
                else:
                    print(f"\r{now:6.1f}s  calibrating... CPM {cpm:5.1f}", end="", flush=True)
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        log.close()


if __name__ == "__main__":
    main()
