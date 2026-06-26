import config


class Baseline:
    """First CALIBRATION_S seconds establish baseline CPM; then classify vs tolerance band."""

    def __init__(self, calibration_s=config.CALIBRATION_S, tolerance=config.TOLERANCE_FRAC):
        self.calibration_s = calibration_s
        self.tolerance = tolerance
        self.baseline_cpm = None
        self._cal_samples = []

    @property
    def calibrated(self):
        return self.baseline_cpm is not None

    def update(self, cpm, now):
        if not self.calibrated:
            if cpm is not None and now > config.CPM_WINDOW_S:
                self._cal_samples.append(cpm)
            if now >= self.calibration_s and self._cal_samples:
                self.baseline_cpm = sum(self._cal_samples) / len(self._cal_samples)
            return "calibrating"
        if cpm is None:
            return "normal"
        if cpm > self.baseline_cpm * (1 + self.tolerance):
            return "fast"
        return "normal"
