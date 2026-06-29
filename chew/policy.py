import random

import config

MODES = ("off", "real", "sham")


class Policy:
    """OFF: never cue. REAL: cue on 'fast' state with cooldown.
    SHAM: cue decoupled from cadence — REAL-triggered events are re-emitted after a
    random delay (matched count/cooldown), or a fixed metronome if metronome=True."""

    def __init__(self, mode, metronome=False, seed=None):
        assert mode in MODES
        self.mode = mode
        self.metronome = metronome
        self.cooldown_s = config.CUE_COOLDOWN_S
        self._last_cue_t = -1e9
        self._pending_sham = []
        self._rng = random.Random(seed)
        self._metronome_period = 60.0 / config.SHAM_METRONOME_CPM

    def _fire(self, now):
        self._last_cue_t = now
        return True

    def should_cue(self, state, now):
        if self.mode == "off":
            return False
        in_cooldown = now - self._last_cue_t < self.cooldown_s
        if self.mode == "real":
            return state == "fast" and not in_cooldown and self._fire(now)
        if self.metronome:
            return state != "calibrating" and not in_cooldown \
                and now - self._last_cue_t >= self._metronome_period and self._fire(now)
        if state == "fast":
            self._pending_sham.append(now + self._rng.uniform(15.0, 60.0))
        due = [t for t in self._pending_sham if t <= now]
        if due and not in_cooldown:
            self._pending_sham.remove(due[0])
            return self._fire(now)
        return False
