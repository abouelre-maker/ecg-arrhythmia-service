import neurokit2 as nk
import numpy as np
from src.domain.entities.ecg_signal import (
    ArrhythmiaAlert,
    ArrhythmiaType,
    ECGSignal,
)
from src.domain.interfaces.detection_strategy import IDetectionStrategy


class RuleBasedDetector(IDetectionStrategy):
    """خوارزمية تحليل إشارة ECG بناءً على معالجة الإشارة واستخراج R-Peaks"""

    def analyze(self, ecg_signal: ECGSignal) -> ArrhythmiaAlert:
        signal_array = np.array(ecg_signal.raw_data)

        # التحقق من أن مدة الإشارة لا تقل عن ثانيتين للفلترة الرقمية
        min_required_samples = ecg_signal.sampling_rate * 2
        if len(signal_array) < min_required_samples:
            raise ValueError(
                f"طول الإشارة غير كافٍ. يلزم {min_required_samples} نقطة على الأقل (ثانيتان)."
            )

        # استخراج R-peaks وتنظيف الإشارة
        cleaned_signal = nk.ecg_clean(
            signal_array, sampling_rate=ecg_signal.sampling_rate
        )
        peaks, _ = nk.ecg_peaks(cleaned_signal, sampling_rate=ecg_signal.sampling_rate)

        r_peaks = np.where(peaks["ECG_R_Peaks"] == 1)[0]

        if len(r_peaks) < 2:
            return ArrhythmiaAlert(
                patient_id=ecg_signal.patient_id,
                rhythm=ArrhythmiaType.NORMAL,
                confidence=0.5,
                requires_immediate_action=False,
            )

        # حساب فترات RR ومعدل ضربات القلب
        rr_intervals = np.diff(r_peaks) / ecg_signal.sampling_rate
        heart_rate = 60.0 / np.mean(rr_intervals)

        # معايير التشخيص السريري
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
        