import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import config
from chew.baseline import Baseline
from chew.cadence import CadenceTracker
from chew.detector import ChewDetector
from chew.policy import Policy
from make_synthetic import generate


def run_audio(audio, sr=config.SAMPLE_RATE):
    detector = ChewDetector(sample_rate=sr)
    tracker = CadenceTracker()
    chews = []
    cpm = None
    for start in range(0, len(audio), config.BLOCK_SIZE):
        block = audio[start:start + config.BLOCK_SIZE]
        new = detector.process(block)
        chews.extend(new)
        cpm = tracker.update(new, (start + len(block)) / sr)
    return chews, cpm


def test_detector_recovers_known_cpm():
    audio, true_chews = generate(duration_s=60.0, cpm=60.0)
    chews, cpm = run_audio(audio)
    assert abs(len(chews) - len(true_chews)) / len(true_chews) <= 0.15
    assert abs(cpm - 60.0) / 60.0 <= 0.15


def test_refractory_prevents_double_counting():
    audio, true_chews = generate(duration_s=30.0, cpm=90.0)
    chews, _ = run_audio(audio)
    diffs = np.diff(chews)
    assert (diffs >= config.REFRACTORY_MS / 1000.0 - 1e-6).all()


def test_baseline_flags_acceleration():
    schedule = [(0.0, 60.0), (60.0, 85.0)]
    audio, _ = generate(duration_s=90.0, cpm_schedule=schedule)
    detector = ChewDetector()
    tracker = CadenceTracker()
    baseline = Baseline(calibration_s=40.0)
    states = []
    for start in range(0, len(audio), config.BLOCK_SIZE):
        block = audio[start:start + config.BLOCK_SIZE]
        now = (start + len(block)) / config.SAMPLE_RATE
        cpm = tracker.update(detector.process(block), now)
        states.append((now, baseline.update(cpm, now)))
    assert baseline.calibrated
    assert abs(baseline.baseline_cpm - 60.0) / 60.0 <= 0.2
    late = [s for t, s in states if t > 75.0]
    assert "fast" in late
    early = [s for t, s in states if 45.0 < t < 58.0]
    assert "fast" not in early


def test_policy_real_cues_with_cooldown():
    policy = Policy("real")
    assert policy.should_cue("fast", 10.0)
    assert not policy.should_cue("fast", 12.0)
    assert policy.should_cue("fast", 10.0 + config.CUE_COOLDOWN_S)
    assert not policy.should_cue("normal", 100.0)


def test_policy_off_never_cues():
    policy = Policy("off")
    assert not policy.should_cue("fast", 10.0)


def test_policy_sham_decoupled():
    policy = Policy("sham", seed=1)
    assert not policy.should_cue("fast", 10.0)
    fired = [t for t in np.arange(10.0, 120.0, 0.5) if policy.should_cue("normal", t)]
    assert fired
    assert all(t >= 25.0 for t in fired)
