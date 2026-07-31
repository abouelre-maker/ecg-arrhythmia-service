"""
ECG Signal Domain Entities.

IEC 62304 §5.2: Immutable value objects — primary artifacts of the pipeline.
ISO 14971: ClassificationResult.confidence < 0.70 → mandatory clinical review.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class RhythmType(str, Enum):
    """
    Clinical ECG rhythm classification types.

    IEC 62304 §5.2: Each variant is a distinct software requirement.
    ISO 14971: Maps directly to clinical risk levels in the Risk Register.
    """

    NORMAL_SINUS = "NORMAL_SINUS"
    ATRIAL_FIBRILLATION = "ATRIAL_FIBRILLATION"
    VENTRICULAR_TACHYCARDIA = "VENTRICULAR_TACHYCARDIA"
    PREMATURE_VENTRICULAR_CONTRACTION = "PREMATURE_VENTRICULAR_CONTRACTION"
    BRADYCARDIA = "BRADYCARDIA"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ECGSignal:
    """Immutable raw ECG signal input — primary pipeline entry artifact."""

    samples: list[float]
    sampling_rate_hz: float
    patient_id: str
    recorded_at: datetime = field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )


@dataclass(frozen=True)
class ClassificationResult:
    """
    Immutable output of ArrhythmiaClassifier.

    IEC 62304: Primary output artifact of the signal processing pipeline.
    ISO 14971 HAZARD-003: confidence < 0.70 triggers mandatory clinical review.
    """

    rhythm_type: RhythmType
    confidence: float          # Range: 0.0 – 1.0
    heart_rate_bpm: float      # Must be > 0
    rr_intervals_ms: list[float]
    analysis_timestamp: datetime
    