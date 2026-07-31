# mypy: ignore-errors
# mypy: ignore-errors
from fastapi import APIRouter, HTTPException

from src.domain.entities.ecg_signal import ECGSignal
from src.domain.services.rule_based_detector import RuleBasedDetector
from src.infrastructure.adapters.fhir_converter import FHIRConverterAdapter

router = APIRouter()


@router.post("/analyze")
def analyze_ecg(signal: ECGSignal):
    try:
        # 1. ØªÙ†ÙÙŠØ° Ø®ÙˆØ§Ø±Ø²Ù…ÙŠØ© Ø§Ù„Ø§ÙƒØªØ´Ø§Ù
        detector = RuleBasedDetector()
        alert = detector.analyze(signal)

        # 2. ØªØ­ÙˆÙŠÙ„ Ø§Ù„Ù†ØªÙŠØ¬Ø© Ø¥Ù„Ù‰ Ù…Ø¹ÙŠØ§Ø± FHIR R4
        fhir_obs = FHIRConverterAdapter.create_observation(alert)

        return {
            "alert": alert,
            "fhir_observation": fhir_obs.dict(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ø®Ø·Ø£ Ø£Ø«Ù†Ø§Ø¡ Ù…Ø¹Ø§Ù„Ø¬Ø© Ø§Ù„Ø¥Ø´Ø§Ø±Ø©: {str(e)}") from e

