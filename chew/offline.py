import numpy as np
import soundfile as sf

import config
from chew.cadence import CadenceTracker
from chew.detector import ChewDetector


def load_wav(path):
    audio, sr = sf.read(path, always_2d=False)
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    return audio.astype(np.float64), sr


def run_wav(path):
    """Replay a WAV through the block-wise pipeline.

    Returns (chew_times, cpm_series) where cpm_series is a list of (t, cpm)."""
    audio, sr = load_wav(path)
    detector = ChewDetector(sample_rate=sr)
    tracker = CadenceTracker()
    chew_times, cpm_series = [], []
    for start in range(0, len(audio), config.BLOCK_SIZE):
        block = audio[start:start + config.BLOCK_SIZE]
        chews = detector.process(block)
        chew_times.extend(chews)
        now = (start + len(block)) / sr
        cpm = tracker.update(chews, now)
        cpm_series.append((now, cpm))
    return chew_times, cpm_series
