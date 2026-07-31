from unittest.mock import patch

import numpy as np

from src.domain.entities.ecg_signal import ECGSignal, RhythmType
from src.domain.services.rule_based_detector import RuleBasedDetector


def test_detector_insufficient_peaks():
    """Test the safety fallback when no peaks are detected."""
    detector = RuleBasedDetector()
    
    # Flatline signal to trigger < 2 peaks condition
    signal = ECGSignal(
        patient_id="PAT-123",
        sampling_rate_hz=500.0,
        samples=[0.0] * 1000
    )
    
    result = detector.analyze(signal)
    
    assert result.rhythm_type == RhythmType.UNKNOWN
    assert result.confidence == 0.5
    assert result.heart_rate_bpm == 60.0


@patch("src.domain.services.rule_based_detector.nk.ecg_peaks")
@patch("src.domain.services.rule_based_detector.nk.ecg_clean")
def test_detector_normal_rhythm(mock_clean, mock_peaks):
    """Test Normal Sinus Rhythm detection (60-100 bpm)."""
    mock_clean.return_value = np.zeros(1000)
    
    # 500 Hz sampling rate, peaks every 400 samples = 0.8 sec interval = 75 bpm (NORMAL)
    peaks_array = np.zeros(1000)
    peaks_array[[0, 400, 800]] = 1
    mock_peaks.return_value = ({"ECG_R_Peaks": peaks_array}, None)

    detector = RuleBasedDetector()
    signal = ECGSignal(
        patient_id="PAT-123",
        sampling_rate_hz=500.0,
        samples=[0.0] * 1000
    )
    
    result = detector.analyze(signal)
    
    assert result.rhythm_type == RhythmType.NORMAL_SINUS
    assert result.confidence == 0.95


@patch("src.domain.services.rule_based_detector.nk.ecg_peaks")
@patch("src.domain.services.rule_based_detector.nk.ecg_clean")
def test_detector_tachycardia(mock_clean, mock_peaks):
    """Test Ventricular Tachycardia detection (>100 bpm)."""
    mock_clean.return_value = np.zeros(1000)
    
    # 500 Hz sampling rate, peaks every 250 samples = 0.5 sec interval = 120 bpm (VT)
    peaks_array = np.zeros(1000)
    peaks_array[[0, 250, 500, 750]] = 1
    mock_peaks.return_value = ({"ECG_R_Peaks": peaks_array}, None)

    detector = RuleBasedDetector()
    signal = ECGSignal(
        patient_id="PAT-123",
        sampling_rate_hz=500.0,
        samples=[0.0] * 1000
    )
    
    result = detector.analyze(signal)
    
    assert result.rhythm_type == RhythmType.VENTRICULAR_TACHYCARDIA
    assert result.confidence == 0.92