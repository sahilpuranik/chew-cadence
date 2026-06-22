"""make a synthetic chew recording at a known CPM so i can check the pipeline myself."""
import argparse
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config


def generate(duration_s=60.0, cpm=60.0, sr=config.SAMPLE_RATE, noise=0.01, seed=0,
             cpm_schedule=None):
    """cpm_schedule: optional list of (start_s, cpm) segments overriding cpm."""
    rng = np.random.default_rng(seed)
    audio = rng.normal(0, noise, int(duration_s * sr))
    segments = cpm_schedule or [(0.0, cpm)]
    chew_times = []
    for i, (start, seg_cpm) in enumerate(segments):
        end = segments[i + 1][0] if i + 1 < len(segments) else duration_s
        t = start
        while t < end:
            chew_times.append(t)
            t += 60.0 / seg_cpm
    burst_n = int(0.06 * sr)
    tb = np.arange(burst_n) / sr
    burst = np.sin(2 * np.pi * 400 * tb) * np.exp(-tb / 0.015)
    for ct in chew_times:
        i0 = int(ct * sr)
        seg = min(burst_n, len(audio) - i0)
        if seg > 0:
            audio[i0:i0 + seg] += 0.5 * burst[:seg]
    return audio.astype(np.float32), chew_times


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="recordings/synthetic.wav")
    p.add_argument("--duration", type=float, default=60.0)
    p.add_argument("--cpm", type=float, default=60.0)
    p.add_argument("--accelerate", action="store_true",
                   help="normal cpm for first 2/3, then cpm*1.35")
    args = p.parse_args()
    schedule = None
    if args.accelerate:
        schedule = [(0.0, args.cpm), (args.duration * 2 / 3, args.cpm * 1.35)]
    audio, chews = generate(args.duration, args.cpm, cpm_schedule=schedule)
    Path(args.out).parent.mkdir(exist_ok=True)
    sf.write(args.out, audio, config.SAMPLE_RATE)
    print(f"wrote {args.out}: {len(chews)} chews over {args.duration}s")


if __name__ == "__main__":
    main()
