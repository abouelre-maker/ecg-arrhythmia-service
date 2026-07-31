# mypy: ignore-errors
# mypy: ignore-errors
import neurokit2 as nk
import numpy as np

from src.domain.entities.ecg_signal import (
    ArrhythmiaAlert,
    ArrhythmiaType,
    ECGSignal,
)
from src.domain.interfaces.detection_strategy import IDetectionStrategy


class RuleBasedDetector(IDetectionStrategy):
    """Ø®ÙˆØ§Ø±Ø²Ù…ÙŠØ© ØªØ­Ù„ÙŠÙ„ Ø¥Ø´Ø§Ø±Ø© ECG Ø¨Ù†Ø§Ø¡Ù‹ Ø¹Ù„Ù‰ Ù…Ø¹Ø§Ù„Ø¬Ø© Ø§Ù„Ø¥Ø´Ø§Ø±Ø© ÙˆØ§Ø³ØªØ®Ø±Ø§Ø¬ R-Peaks"""

    def analyze(self, ecg_signal: ECGSignal) -> ArrhythmiaAlert:
        signal_array = np.array(ecg_signal.raw_data)

        # Ø§Ø³ØªØ®Ø±Ø§Ø¬ R-peaks ÙˆØªÙ†Ø¸ÙŠÙ Ø§Ù„Ø¥Ø´Ø§Ø±Ø©
        cleaned_signal = nk.ecg_clean(signal_array, sampling_rate=ecg_signal.sampling_rate)
        peaks, _ = nk.ecg_peaks(cleaned_signal, sampling_rate=ecg_signal.sampling_rate)

        r_peaks = np.where(peaks["ECG_R_Peaks"] == 1)[0]

        if len(r_peaks) < 2:
            return ArrhythmiaAlert(
                patient_id=ecg_signal.patient_id,
                rhythm=ArrhythmiaType.NORMAL,
                confidence=0.5,
                requires_immediate_action=False,
            )

        # Ø­Ø³Ø§Ø¨ ÙØªØ±Ø§Øª RR ÙˆÙ…Ø¹Ø¯Ù„ Ø¶Ø±Ø¨Ø§Øª Ø§Ù„Ù‚Ù„Ø¨ (Heart Rate)
        rr_intervals = np.diff(r_peaks) / ecg_signal.sampling_rate
        heart_rate = 60.0 / np.mean(rr_intervals)

        # Ù…Ø¹Ø§ÙŠÙŠØ± Ø§Ù„ØªØ´Ø®ÙŠØµ Ø§Ù„Ø³Ø±ÙŠØ±ÙŠ Ø§Ù„Ø£ÙˆÙ„ÙŠ (Class B IEC 62304)
        if heart_rate > 100:
            return ArrhythmiaAlert(
                patient_id=ecg_signal.patient_id,
                rhythm=ArrhythmiaType.VT,
                confidence=0.92,
                requires_immediate_action=True,
            )
        else:
            return ArrhythmiaAlert(
                patient_id=ecg_signal.patient_id,
                rhythm=ArrhythmiaType.NORMAL,
                confidence=0.95,
                requires_immediate_action=False,
            )


if __name__ == "__main__":
    from src.infrastructure.adapters.ecg_simulator import ECGDataSimulator

    simulator = ECGDataSimulator()
    raw_data = simulator.generate_normal_ecg(duration_sec=10, heart_rate=75)

    signal_entity = ECGSignal(
        patient_id="PATIENT-101",
        sampling_rate=500,
        raw_data=raw_data.tolist(),
    )

    detector = RuleBasedDetector()
    alert = detector.analyze(signal_entity)
    print(
        f"Ù†ØªÙŠØ¬Ø© Ø§Ù„ØªØ­Ù„ÙŠÙ„ Ù„Ù„Ù…Ø±ÙŠØ¶ {alert.patient_id}: {alert.rhythm.value} (Ù†Ø³Ø¨Ø© Ø§Ù„Ø«Ù‚Ø©: {alert.confidence * 100}%)"
    )

