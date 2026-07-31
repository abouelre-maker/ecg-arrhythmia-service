from abc import ABC, abstractmethod

from src.domain.entities.ecg_signal import ClassificationResult, ECGSignal


class IDetectionStrategy(ABC):
    """واجهة تجريدية لتحديد استراتيجية اكتشاف اضطرابات النظم القلبي"""  # noqa: E501

    @abstractmethod
    def analyze(self, ecg_signal: ECGSignal) -> ClassificationResult:
        """تحليل إشارة ECG وإرجاع تنبيه بالنتيجة السريرية"""  # noqa: E501
        pass