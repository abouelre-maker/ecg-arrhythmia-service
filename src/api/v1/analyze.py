from fastapi import APIRouter, HTTPException

from src.domain.entities.ecg_signal import ECGSignal
from src.domain.services.rule_based_detector import RuleBasedDetector
from src.infrastructure.adapters.fhir_converter import FHIRConverterAdapter

router = APIRouter()


@router.post("/analyze")
def analyze_ecg(signal: ECGSignal):
    try:
        # 1. تنفيذ خوارزمية الاكتشاف
        detector = RuleBasedDetector()
        alert = detector.analyze(signal)

        # 2. تحويل النتيجة إلى معيار FHIR R4
        fhir_obs = FHIRConverterAdapter.create_observation(alert)

        return {
            "alert": alert,
            "fhir_observation": fhir_obs.dict(),
        }
    except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"خطأ أثناء معالجة الإشارة: {str(e)}"
            ) from e
