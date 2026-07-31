# mypy: ignore-errors
from abc import ABC, abstractmethod

from src.domain.entities.ecg_signal import ArrhythmiaAlert, ECGSignal


class IDetectionStrategy(ABC):
    """واجهة تجريدية لتحديد استراتيجية اكتشاف اضطرابات النظم القلبي"""

    @abstractmethod
    def analyze(self, ecg_signal: ECGSignal) -> ArrhythmiaAlert:
        """تحليل إشارة ECG وإرجاع تنبيه بالنتيجة السريرية"""
        pass
