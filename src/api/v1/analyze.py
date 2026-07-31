from fastapi import APIRouter, HTTPException

from src.domain.entities.ecg_signal import ECGSignal
from src.domain.services.rule_based_detector import RuleBasedDetector
from src.infrastructure.adapters.fhir_converter import FHIRObservationConverter

router = APIRouter()


@router.post("/analyze")
def analyze_ecg(signal: ECGSignal):
    try:
        # 1. تنفيذ خوارزمية الاكتشاف
        detector = RuleBasedDetector()
        result = detector.analyze(signal)

        # 2. تحويل النتيجة إلى معيار FHIR R4
        converter = FHIRObservationConverter()
        fhir_obs = converter.to_fhir_observation(
            result=result,
            patient_id=signal.patient_id,
        )

        return {
            "alert": result,
            "fhir_observation": fhir_obs,
        }
    except Exception as e:
        error_msg = f"خطأ أثناء معالجة الإشارة: {str(e)}"  # noqa: E501
        raise HTTPException(status_code=500, detail=error_msg) from e