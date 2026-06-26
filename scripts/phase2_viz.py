"""phase 2: cadence over time + detected peaks. done when the plot tracks me deliberately chewing fast vs slow."""
import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chew.dsp import EnvelopeExtractor
from chew.offline import load_wav, run_wav


def main():
    p = argparse.ArgumentParser()
    p.add_argument("wav")
    args = p.parse_args()

    audio, sr = load_wav(args.wav)
    chews, cpm_series = run_wav(args.wav)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
    t = np.arange(len(audio)) / sr
    env = EnvelopeExtractor(sr).process(audio)
    ax1.plot(t, env, lw=0.5)
    ax1.plot(chews, np.interp(chews, t, env), "rv", ms=6)
    ax1.set_ylabel("envelope")
    ts, cpms = zip(*cpm_series)
    ax2.plot(ts, cpms)
    ax2.set_ylabel("CPM (EMA)")
    ax2.set_xlabel("s")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
