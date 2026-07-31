# mypy: ignore-errors
# mypy: ignore-errors
from abc import ABC, abstractmethod

from src.domain.entities.ecg_signal import ArrhythmiaAlert, ECGSignal


class IDetectionStrategy(ABC):
    """ÙˆØ§Ø¬Ù‡Ø© ØªØ¬Ø±ÙŠØ¯ÙŠØ© Ù„ØªØ­Ø¯ÙŠØ¯ Ø§Ø³ØªØ±Ø§ØªÙŠØ¬ÙŠØ© Ø§ÙƒØªØ´Ø§Ù Ø§Ø¶Ø·Ø±Ø§Ø¨Ø§Øª Ø§Ù„Ù†Ø¸Ù… Ø§Ù„Ù‚Ù„Ø¨ÙŠ"""

    @abstractmethod
    def analyze(self, ecg_signal: ECGSignal) -> ArrhythmiaAlert:
        """ØªØ­Ù„ÙŠÙ„ Ø¥Ø´Ø§Ø±Ø© ECG ÙˆØ¥Ø±Ø¬Ø§Ø¹ ØªÙ†Ø¨ÙŠÙ‡ Ø¨Ø§Ù„Ù†ØªÙŠØ¬Ø© Ø§Ù„Ø³Ø±ÙŠØ±ÙŠØ©"""
        pass

