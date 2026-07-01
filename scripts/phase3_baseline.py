"""phase 3: replay a wav through baseline+policy and label fast/normal segments.

done when it correctly labels my deliberate fast vs normal segments on replay.
"""
import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from chew.baseline import Baseline
from chew.cadence import CadenceTracker
from chew.detector import ChewDetector
from chew.offline import load_wav
from chew.policy import Policy


def main():
    p = argparse.ArgumentParser()
    p.add_argument("wav")
    p.add_argument("--mode", choices=["off", "real", "sham"], default="real")
    p.add_argument("--calibration", type=float, default=config.CALIBRATION_S)
    args = p.parse_args()

    audio, sr = load_wav(args.wav)
    detector = ChewDetector(sample_rate=sr)
    tracker = CadenceTracker()
    baseline = Baseline(calibration_s=args.calibration)
    policy = Policy(args.mode)

    times, cpms, states, cues = [], [], [], []
    for start in range(0, len(audio), config.BLOCK_SIZE):
        block = audio[start:start + config.BLOCK_SIZE]
        chews = detector.process(block)
        now = (start + len(block)) / sr
        cpm = tracker.update(chews, now)
        state = baseline.update(cpm, now)
        if policy.should_cue(state, now):
            cues.append(now)
        times.append(now)
        cpms.append(cpm)
        states.append(state)

    print(f"baseline CPM: {baseline.baseline_cpm and round(baseline.baseline_cpm, 1)}")
    print(f"fast: {sum(s == 'fast' for s in states)} blocks, cues: {len(cues)}")

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(times, cpms, label="CPM")
    if baseline.calibrated:
        band = baseline.baseline_cpm * (1 + baseline.tolerance)
        ax.axhline(baseline.baseline_cpm, color="g", ls="--", label="baseline")
        ax.axhline(band, color="orange", ls="--", label="threshold")
    for i, s in enumerate(states):
        if s == "fast":
            ax.axvspan(times[i - 1] if i else 0, times[i], color="red", alpha=0.1)
    for c in cues:
        ax.axvline(c, color="purple", alpha=0.6)
    ax.set_xlabel("s")
    ax.set_ylabel("CPM")
    ax.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
