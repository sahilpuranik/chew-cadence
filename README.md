# chew-cadence

estimate my chewing rhythm (CPM) from a mic, notice when i speed up past my own
baseline, and nudge me with a quiet little cue — with OFF/REAL/SHAM modes so i can
tell real entrainment apart from me just reacting to being watched. solo project to
teach myself some DSP + closed-loop control.

## setup

```sh
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest            # checks the pipeline on synthetic audio
```

## sanity-check the pipeline without any recordings

```sh
python scripts/make_synthetic.py --cpm 60 --accelerate
python scripts/phase1_offline.py recordings/synthetic.wav
python scripts/phase2_viz.py recordings/synthetic.wav
python scripts/phase3_baseline.py recordings/synthetic.wav --calibration 30
```

## my plan, roughly in order (stuff i still need to do is marked TODO)

- **phase 0 — the gate.** TODO: record 3×60s gum recordings into `recordings/`,
  hand-count the chews, then per file:
  `python scripts/phase0_inspect.py recordings/gum1.wav --manual-count N`
  gate i'm holding myself to: auto CPM within ±15% of the hand count on all 3, peaks
  clearly above the noise floor. if it passes i don't buy any hardware. if it fails i
  grab a sensor (throat mic first).
- **phase 1.** TODO: tune `config.py` — set `BANDPASS_*` from the phase0
  spectrogram, then `PEAK_THRESHOLD_RATIO` / `REFRACTORY_MS` until
  `phase1_offline.py` is within ±10–15% of my manual counts.
- **phase 2.** run `phase2_viz.py` on a recording where i deliberately chew fast
  then slow. done when the plot visibly tracks it.
- **phase 3.** `phase3_baseline.py` on the same one. done when fast segments get
  flagged and normal ones don't.
- **hard gate.** phases 0–3 are a complete little standalone DSP project on their
  own. only keep going if my more important commitments are actually on track.
- **phase 4.** `python scripts/phase4_live.py --mode off|real|sham`
  done when the cue fires correctly and detect→cue latency is under ~500 ms.
- **phase 5.** TODO: run sessions across OFF/SHAM/REAL, then
  `python scripts/phase5_analyze.py sessions/*.jsonl`
  done when there's a REAL-vs-SHAM difference i can see and actually believe if i'm
  honest with myself. a clean null is a real result too.

## limits (being honest with myself)

n=1, unblinded, single sensor, crunchy food in a quiet room. this thing doesn't
understand eating — it estimates a rhythm and pokes at it, with an honest control.
