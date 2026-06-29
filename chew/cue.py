import numpy as np

import config


class Cue:
    """Short soft tone, non-blocking playback."""

    def __init__(self, sample_rate=config.SAMPLE_RATE):
        self.sample_rate = sample_rate
        n = int(config.CUE_DURATION_S * sample_rate)
        t = np.arange(n) / sample_rate
        tone = np.sin(2 * np.pi * config.CUE_FREQ_HZ * t)
        fade = np.minimum(1.0, np.minimum(t, t[::-1]) / 0.005)
        self.samples = (config.CUE_GAIN * tone * fade).astype(np.float32)

    def play(self):
        import sounddevice as sd

        sd.play(self.samples, self.sample_rate, blocking=False)
