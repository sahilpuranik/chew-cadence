"""all my tunables. the TODO(tune) ones i still need to set from my own recordings (phase 0/1)."""

SAMPLE_RATE = 44100
BLOCK_SIZE = 1024

# TODO(tune): still need to look at spectrograms of my gum recordings and pick the band
# that actually isolates the chew thumps on my mic/room/food. just a placeholder for now.
BANDPASS_LOW_HZ = 100.0
BANDPASS_HIGH_HZ = 1000.0
BANDPASS_ORDER = 4

ENVELOPE_SMOOTH_MS = 75.0

# Peak picking
REFRACTORY_MS = 400.0
# TODO(tune): threshold as a multiple of the rolling noise floor - need to adjust once i have real recordings.
PEAK_THRESHOLD_RATIO = 3.0
NOISE_FLOOR_WINDOW_S = 2.0

# Cadence
CPM_WINDOW_S = 8.0
CPM_EMA_ALPHA = 0.3

# Baseline
CALIBRATION_S = 90.0
TOLERANCE_FRAC = 0.12

# Policy / cue
CUE_COOLDOWN_S = 10.0
CUE_FREQ_HZ = 880.0
CUE_DURATION_S = 0.05
CUE_GAIN = 0.2
SHAM_METRONOME_CPM = 60.0


def as_dict():
    return {k: v for k, v in globals().items() if k.isupper()}
