from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class ArrhythmiaType(StrEnum):
    NORMAL = "Normal Sinus Rhythm"
    VT = "Ventricular Tachycardia"
    AF = "Atrial Fibrillation"
    PVC = "Premature Ventricular Contraction"


class ECGSignal(BaseModel):
    patient_id: str
    sampling_rate: int = Field(default=500, description="معدل العينات بالهرتز")
    raw_data: list[float] = Field(..., description="نقاط إشارة ECG الخام")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ArrhythmiaAlert(BaseModel):
    patient_id: str
    rhythm: ArrhythmiaType
    confidence: float = Field(..., ge=0.0, le=1.0, description="نسبة الثقة في الاكتشاف")
    requires_immediate_action: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)
