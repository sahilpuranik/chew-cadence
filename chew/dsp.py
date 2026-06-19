import numpy as np
from scipy import signal

import config


class EnvelopeExtractor:
    """Band-pass -> rectify -> moving-average envelope. Stateful for block-wise use."""

    def __init__(self, sample_rate=config.SAMPLE_RATE):
        self.sample_rate = sample_rate
        nyq = sample_rate / 2.0
        self.sos = signal.butter(
            config.BANDPASS_ORDER,
            [config.BANDPASS_LOW_HZ / nyq, config.BANDPASS_HIGH_HZ / nyq],
            btype="band",
            output="sos",
        )
        self.zi = signal.sosfilt_zi(self.sos)
        smooth_n = max(1, int(config.ENVELOPE_SMOOTH_MS / 1000.0 * sample_rate))
        self.smooth_kernel = np.ones(smooth_n) / smooth_n
        self._smooth_tail = np.zeros(smooth_n - 1)

    def process(self, block):
        filtered, self.zi = signal.sosfilt(self.sos, block, zi=self.zi)
        rectified = np.abs(filtered)
        padded = np.concatenate([self._smooth_tail, rectified])
        env = np.convolve(padded, self.smooth_kernel, mode="valid")
        tail_n = len(self.smooth_kernel) - 1
        if tail_n:
            self._smooth_tail = padded[-tail_n:]
        return env
