from collections import deque

import config


class CadenceTracker:
    """Sliding-window chews-per-minute, EMA-smoothed."""

    def __init__(self, window_s=config.CPM_WINDOW_S, alpha=config.CPM_EMA_ALPHA):
        self.window_s = window_s
        self.alpha = alpha
        self._chews = deque()
        self._ema = None

    def update(self, chew_times, now):
        self._chews.extend(chew_times)
        while self._chews and self._chews[0] < now - self.window_s:
            self._chews.popleft()
        window = min(self.window_s, now) or self.window_s
        raw = len(self._chews) * 60.0 / window
        if self._ema is None:
            self._ema = raw
        else:
            self._ema = self.alpha * raw + (1 - self.alpha) * self._ema
        return self._ema

    @property
    def cpm(self):
        return self._ema
