from collections import deque

import numpy as np

import config
from chew.dsp import EnvelopeExtractor


class ChewDetector:
    """Envelope peak-picking with refractory interval and adaptive amplitude threshold.

    Feed audio blocks; returns chew timestamps (seconds since stream start).
    """

    def __init__(self, sample_rate=config.SAMPLE_RATE):
        self.sample_rate = sample_rate
        self.envelope = EnvelopeExtractor(sample_rate)
        self.refractory_s = config.REFRACTORY_MS / 1000.0
        self._samples_seen = 0
        self._last_chew_t = -1e9
        floor_n = int(config.NOISE_FLOOR_WINDOW_S * sample_rate)
        self._floor_buf = deque(maxlen=max(1, floor_n // 64))
        self._prev = 0.0
        self._prev_prev = 0.0

    def _noise_floor(self):
        if not self._floor_buf:
            return 0.0
        return float(np.median(self._floor_buf))

    def process(self, block):
        env = self.envelope.process(np.asarray(block, dtype=np.float64))
        t0 = self._samples_seen / self.sample_rate
        chews = []
        self._floor_buf.extend(env[::64])
        threshold = self._noise_floor() * config.PEAK_THRESHOLD_RATIO
        for i, v in enumerate(env):
            if (
                self._prev > threshold
                and self._prev >= self._prev_prev
                and self._prev > v
            ):
                t = t0 + (i - 1) / self.sample_rate
                if t - self._last_chew_t >= self.refractory_s:
                    chews.append(t)
                    self._last_chew_t = t
            self._prev_prev = self._prev
            self._prev = v
        self._samples_seen += len(block)
        return chews
