import numpy as np
import pytest

from src.domain.services.signal_processor import (
    ArrhythmiaClassifier,
    BandpassFilter,
    InvalidInputError,
    RPeakDetector,
)


@pytest.fixture
def sampling_rate() -> float:
    return 250.0


@pytest.fixture
def dummy_ecg_signal(sampling_rate: float) -> np.ndarray:
    t = np.linspace(0, 5, int(5 * sampling_rate), endpoint=False)
    signal = np.sin(2 * np.pi * 1 * t) + 0.5 * np.sin(2 * np.pi * 50 * t)
    return signal.astype(np.float64)


def test_bandpass_filter_success(dummy_ecg_signal, sampling_rate):
    filter_op = BandpassFilter(fs=sampling_rate, lowcut=0.5, highcut=40.0)
    filtered_signal = filter_op.apply(dummy_ecg_signal)
    assert filtered_signal.shape == dummy_ecg_signal.shape
    assert not np.isnan(filtered_signal).any()


def test_bandpass_filter_empty_array_raises_error():
    filter_op = BandpassFilter(fs=250.0)
    with pytest.raises(InvalidInputError, match="cannot be empty"):
        filter_op.apply(np.array([], dtype=np.float64))


def test_bandpass_filter_nan_raises_error():
    filter_op = BandpassFilter(fs=250.0)
    signal_with_nan = np.array([1.0, 2.0, np.nan, 4.0])
    with pytest.raises(InvalidInputError, match="contains NaN"):
        filter_op.apply(signal_with_nan)


def test_r_peak_detector_success(sampling_rate):
    detector = RPeakDetector(fs=sampling_rate)
    signal = np.zeros(int(5 * sampling_rate))
    for i in range(1, 5):
        signal[int(i * sampling_rate)] = 5.0

    peaks = detector.find_r_peaks(signal)
    assert len(peaks) > 0


def test_classifier_normal_rhythm(sampling_rate):
    classifier = ArrhythmiaClassifier(fs=sampling_rate)
    r_peaks = np.array([250, 500, 750, 1000], dtype=np.int64)
    result = classifier.classify(r_peaks)
    assert result == "NORMAL"


def test_classifier_tachycardia(sampling_rate):
    classifier = ArrhythmiaClassifier(fs=sampling_rate)
    r_peaks = np.array([100, 200, 300, 400], dtype=np.int64)
    result = classifier.classify(r_peaks)
    assert result == "TACHYCARDIA_OR_VT"
