"""phase 5 - compare my OFF/SHAM/REAL session logs.

what i'm hoping to see: a REAL-vs-SHAM difference i can actually spot in the logs and
believe if i'm honest with myself. for each session i plot the CPM trajectory + cue
markers, and look at mean CPM in the window after each cue vs matched no-cue windows.

TODO: still need to run real sessions (phase4_live.py) across OFF/SHAM/REAL, then point
this at the sessions/ files.
"""
import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chew.logger import load_session

POST_CUE_WINDOW_S = 20.0


def cue_response(records):
    """Mean CPM change from pre-cue to post-cue window, per cue."""
    cpms = [(r["t"], r["cpm"]) for r in records if r["type"] == "cpm" and r["cpm"] is not None]
    cues = [r["t"] for r in records if r["type"] == "cue"]
    if not cpms:
        return []
    ts, vs = np.array([c[0] for c in cpms]), np.array([c[1] for c in cpms])
    deltas = []
    for c in cues:
        pre = vs[(ts >= c - POST_CUE_WINDOW_S) & (ts < c)]
        post = vs[(ts > c) & (ts <= c + POST_CUE_WINDOW_S)]
        if len(pre) and len(post):
            deltas.append(post.mean() - pre.mean())
    return deltas


def main():
    p = argparse.ArgumentParser()
    p.add_argument("sessions", nargs="+", help="JSONL session logs")
    args = p.parse_args()

    fig, axes = plt.subplots(len(args.sessions), 1, figsize=(12, 3 * len(args.sessions)),
                             squeeze=False, sharex=True)
    for ax, path in zip(axes[:, 0], args.sessions):
        recs = load_session(path)
        mode = next(r["mode"] for r in recs if r["type"] == "meta")
        cpms = [(r["t"], r["cpm"]) for r in recs if r["type"] == "cpm" and r["cpm"] is not None]
        cues = [r["t"] for r in recs if r["type"] == "cue"]
        if cpms:
            t0 = cpms[0][0]
            ax.plot([t - t0 for t, _ in cpms], [v for _, v in cpms])
            for c in cues:
                ax.axvline(c - t0, color="purple", alpha=0.5)
        deltas = cue_response(recs)
        d = f"mean ΔCPM post-cue: {np.mean(deltas):+.1f} (n={len(deltas)})" if deltas else "no cues"
        ax.set_title(f"{Path(path).name}  [{mode.upper()}]  {d}")
        ax.set_ylabel("CPM")
        print(f"{mode.upper():5s} {Path(path).name}: {d}")
    axes[-1, 0].set_xlabel("s")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
