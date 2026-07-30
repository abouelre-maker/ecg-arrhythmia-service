import numpy as np
import numpy.typing as npt
from scipy.signal import butter, filtfilt, find_peaks


# ==========================================
# 1. Custom Exceptions (IEC 62304 Compliance)
# ==========================================
class SignalProcessingError(Exception):
    """Base exception for signal processing errors."""

    pass


class InvalidInputError(SignalProcessingError):
    """Raised when input data is invalid (e.g., empty, contains NaNs)."""

    pass


# ==========================================
# 2. Bandpass Filter
# ==========================================
class BandpassFilter:
    """
    Applies a Butterworth bandpass filter to remove baseline wander
    and high-frequency noise from ECG signals.
    """

    def __init__(
        self, fs: float, lowcut: float = 0.5, highcut: float = 40.0, order: int = 4
    ) -> None:
        if fs <= 0:
            raise InvalidInputError(
                "Sampling frequency (fs) must be strictly positive."
            )
        if lowcut >= highcut:
            raise InvalidInputError("lowcut must be strictly less than highcut.")

        self.fs = fs
        self.lowcut = lowcut
        self.highcut = highcut
        self.order = order

    def apply(self, signal: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
        if signal.size == 0:
            raise InvalidInputError("Input signal cannot be empty.")
        if np.isnan(signal).any():
            raise InvalidInputError("Input signal contains NaN values. Cannot process.")

        nyq = 0.5 * self.fs
        low = self.lowcut / nyq
        high = self.highcut / nyq

        if low <= 0 or high >= 1:
            raise InvalidInputError(
                f"Filter frequencies must be between 0 and Nyquist ({nyq} Hz)."
            )

        b, a = butter(self.order, [low, high], btype="bandpass")
        try:
            filtered_signal = filtfilt(b, a, signal)
            return filtered_signal
        except Exception as e:
            raise SignalProcessingError(f"Filtering operation failed: {str(e)}")


# ==========================================
# 3. R-Peak Detector
# ==========================================
class RPeakDetector:
    """
    Detects R-peaks in an ECG signal using a simplified Pan-Tompkins approach.
    """

    def __init__(self, fs: float) -> None:
        if fs <= 0:
            raise InvalidInputError("Sampling frequency must be strictly positive.")
        self.fs = fs

    def find_r_peaks(self, signal: npt.NDArray[np.float64]) -> npt.NDArray[np.int64]:
        if signal.size < int(self.fs):
            raise InvalidInputError(
                "Signal is too short (less than 1 second) for reliable detection."
            )

        diff_signal = np.diff(signal)
        squared_signal = diff_signal**2

        window_size = max(1, int(0.15 * self.fs))
        integrated_signal = np.convolve(
            squared_signal, np.ones(window_size) / window_size, mode="same"
        )

        threshold = np.mean(integrated_signal) * 1.5
        min_distance = int(0.2 * self.fs)

        peaks, _ = find_peaks(
            integrated_signal, height=threshold, distance=min_distance
        )
        return peaks.astype(np.int64)


# ==========================================
# 4. Arrhythmia Classifier
# ==========================================
class ArrhythmiaClassifier:
    """
    Classifies arrhythmias based on RR-intervals extracted from R-peaks.
    """

    def __init__(self, fs: float) -> None:
        if fs <= 0:
            raise InvalidInputError("Sampling frequency must be strictly positive.")
        self.fs = fs

    def classify(self, r_peaks: npt.NDArray[np.int64]) -> str:
        if r_peaks.size < 3:
            return "INSUFFICIENT_DATA"

        rr_intervals = np.diff(r_peaks) / self.fs
        mean_rr = float(np.mean(rr_intervals))
        if mean_rr <= 0:
            raise SignalProcessingError("Invalid mean RR interval (<= 0).")

        heart_rate = 60.0 / mean_rr

        if heart_rate > 120.0:
            return "TACHYCARDIA_OR_VT"
        elif heart_rate < 50.0:
            return "BRADYCARDIA"

        for rr in rr_intervals:
            if rr < 0.8 * mean_rr:
                return "PVC_DETECTED"

        return "NORMAL"
