"""phase 1: wav -> detector -> CPM. done when i'm within ±10-15% of my manual count."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chew.offline import load_wav, run_wav


def main():
    p = argparse.ArgumentParser()
    p.add_argument("wav")
    p.add_argument("--manual-count", type=int)
    args = p.parse_args()

    audio, sr = load_wav(args.wav)
    chews, cpm_series = run_wav(args.wav)
    duration = len(audio) / sr
    auto_cpm = len(chews) * 60.0 / duration
    print(f"{len(chews)} chews / {duration:.1f}s -> {auto_cpm:.1f} CPM")
    final_cpm = cpm_series[-1][1] if cpm_series else None
    print(f"final smoothed CPM: {final_cpm:.1f}" if final_cpm else "no CPM")
    if args.manual_count:
        err = abs(len(chews) - args.manual_count) / args.manual_count
        print(f"vs manual {args.manual_count}: error {err:.1%}  "
              f"exit(±15%): {'PASS' if err <= 0.15 else 'FAIL'}")


if __name__ == "__main__":
    main()
