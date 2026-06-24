"""phase 0 gate helper - inspect a recording and compare auto CPM against my hand count.

gate i set for myself: across 3 separate 60s gum recordings, auto CPM within ±15% of the hand count.
TODO: still need to record 3x60s gum wavs into recordings/ and run this on each with --manual-count.
"""
import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy import signal as sig

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from chew.offline import load_wav, run_wav


def main():
    p = argparse.ArgumentParser()
    p.add_argument("wav")
    p.add_argument("--manual-count", type=int, help="chews you hand-counted")
    args = p.parse_args()

    audio, sr = load_wav(args.wav)
    chews, cpm_series = run_wav(args.wav)
    duration = len(audio) / sr
    auto_cpm = len(chews) * 60.0 / duration
    print(f"duration {duration:.1f}s  detected {len(chews)} chews  auto CPM {auto_cpm:.1f}")
    if args.manual_count:
        manual_cpm = args.manual_count * 60.0 / duration
        err = abs(auto_cpm - manual_cpm) / manual_cpm
        print(f"manual CPM {manual_cpm:.1f}  error {err:.1%}  "
              f"gate(±15%): {'PASS' if err <= 0.15 else 'FAIL'}")

    t = np.arange(len(audio)) / sr
    fig, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=True)
    axes[0].plot(t, audio, lw=0.3)
    axes[0].set_ylabel("waveform")
    from chew.dsp import EnvelopeExtractor
    env = EnvelopeExtractor(sr).process(audio)
    axes[1].plot(t, env, lw=0.5)
    for ct in chews:
        axes[1].axvline(ct, color="r", alpha=0.4, lw=0.5)
    axes[1].set_ylabel("envelope + chews")
    f, tt, S = sig.spectrogram(audio, sr, nperseg=1024)
    axes[2].pcolormesh(tt, f, 10 * np.log10(S + 1e-12), shading="auto")
    axes[2].set_ylim(0, 3000)
    axes[2].set_ylabel("Hz")
    axes[2].set_xlabel("s")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
