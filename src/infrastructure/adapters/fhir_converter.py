"""
FHIR R4 Observation Converter — ECG Arrhythmia Classification Results.

IEC 62304: Infrastructure Layer — External Interface Adapter (GoF Adapter Pattern).
ISO 14971: Last boundary before data exits the system; mandatory field validation
           prevents corrupt FHIR resources (HAZARD-007).

FHIR Compatibility:
  - NPHIES Integration Guide (KSA / SFDA)
  - Malaffi IG — DOH Abu Dhabi (UAE)
  - NABIDH — DHA Dubai (UAE)
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Final
from uuid import uuid4

from domain.entities.ecg_signal import ClassificationResult, RhythmType

# ── FHIR Terminology System URLs ───────────────────────────────────────────────

LOINC_SYSTEM: Final[str] = "http://loinc.org"
SNOMED_SYSTEM: Final[str] = "http://snomed.info/sct"
UCUM_SYSTEM: Final[str] = "http://unitsofmeasure.org"
OBS_CATEGORY_SYSTEM: Final[str] = (
    "http://terminology.hl7.org/CodeSystem/observation-category"
)

# LOINC 8625-6 → Cardiac rhythm  (Observation.code)
CARDIAC_RHYTHM_LOINC: Final[str] = "8625-6"

# LOINC 8867-4 → Heart rate  (Observation.component)
HEART_RATE_LOINC: Final[str] = "8867-4"

# ── SNOMED CT Rhythm Code Map ──────────────────────────────────────────────────
# Source: SNOMED CT International Edition — Clinical Findings hierarchy.
# ISO 14971 HAZARD-007: Any missing entry here is a regulatory defect.

_RHYTHM_SNOMED_MAP: Final[dict[RhythmType, tuple[str, str]]] = {
    RhythmType.NORMAL_SINUS: (
        "17621005",
        "Normal sinus rhythm",
    ),
    RhythmType.ATRIAL_FIBRILLATION: (
        "49436004",
        "Atrial fibrillation",
    ),
    RhythmType.VENTRICULAR_TACHYCARDIA: (
        "25569003",
        "Ventricular tachycardia",
    ),
    RhythmType.PREMATURE_VENTRICULAR_CONTRACTION: (
        "17338001",
        "Premature ventricular complex",
    ),
    RhythmType.BRADYCARDIA: (
        "48867003",
        "Bradycardia",
    ),
    RhythmType.UNKNOWN: (
        "74400008",
        "Cardiac arrhythmia",
    ),
}

# ── Custom Extension Base URL ──────────────────────────────────────────────────

_EXT_BASE: Final[str] = (
    "http://ecg-arrhythmia-service.org/fhir/StructureDefinition"
)
_CONFIDENCE_EXT_URL: Final[str] = f"{_EXT_BASE}/algorithm-confidence-score"
_IEC62304_EXT_URL: Final[str] = f"{_EXT_BASE}/iec62304-software-class"


# ── Custom Exception ───────────────────────────────────────────────────────────


class FHIRConversionError(Exception):
    """
    Raised when FHIR Observation creation fails.

    ISO 14971 HAZARD-007: Must never be silently swallowed at any boundary.
    IEC 62304 §5.8: All errors at the external interface are safety-relevant.
    """


# ── Converter ─────────────────────────────────────────────────────────────────


class FHIRObservationConverter:
    """
    Adapts a domain ClassificationResult → FHIR R4 Observation dict.

    Design:  GoF Adapter Pattern — translates domain objects to the external
             FHIR R4 wire format without coupling domain logic to FHIR types.
    State:   Stateless — safe for concurrent use within a FastAPI service.
    Output:  JSON-serializable dict; no external library dependency required
             for serialization (stdlib-only + domain imports).
    """

    def to_fhir_observation(
        self,
        result: ClassificationResult,
        patient_id: str,
        device_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Convert ClassificationResult → FHIR R4 Observation dict.

        Args:
            result:     Arrhythmia classification result from the domain layer.
            patient_id: FHIR Patient logical ID — wrapped as Patient/{id} internally.
                        Required by NPHIES (KSA) and Malaffi (UAE) profiles.
            device_id:  Optional FHIR Device ID for SaMD audit trail traceability.

        Returns:
            JSON-serializable dict conforming to FHIR R4 Observation profile.

        Raises:
            FHIRConversionError: On validation failure or unexpected conversion error.

        ISO 14971: This method is the last safe boundary before data leaves the system.
        """
        try:
            self._validate_inputs(patient_id=patient_id, result=result)

            snomed_code, snomed_display = _RHYTHM_SNOMED_MAP[result.rhythm_type]

            observation: dict[str, Any] = {
                "resourceType": "Observation",
                "id": str(uuid4()),
                "status": "final",
                "category": [self._build_category()],
                "code": self._build_observation_code(),
                "subject": {"reference": f"Patient/{patient_id}"},
                "effectiveDateTime": result.analysis_timestamp.isoformat(),
                "issued": datetime.now(tz=timezone.utc).isoformat(),
                "valueCodeableConcept": self._build_value(
                    snomed_code, snomed_display
                ),
                "component": [
                    self._build_heart_rate_component(result.heart_rate_bpm)
                ],
                "extension": [
                    self._build_confidence_extension(result.confidence),
                    self._build_iec62304_extension(),
                ],
            }

            if device_id is not None:
                observation["device"] = {"reference": f"Device/{device_id}"}

            return observation

        except FHIRConversionError:
            raise  # Re-raise infrastructure validation errors unchanged
        except (KeyError, ValueError, AttributeError, TypeError) as e:
            raise FHIRConversionError(
                f"Unexpected error during FHIR conversion — "
                f"patient='{patient_id}', rhythm='{result.rhythm_type}': {e}"
            ) from e

    # ── Validation ─────────────────────────────────────────────────────────────

    @staticmethod
    def _validate_inputs(
        patient_id: str,
        result: ClassificationResult,
    ) -> None:
        """
        Validates mandatory fields before any FHIR resource is built.

        ISO 14971 HAZARD-007: Prevents incomplete or corrupt Observations
        from propagating to NPHIES / Malaffi integration endpoints.
        """
        if not patient_id or not patient_id.strip():
            raise FHIRConversionError(
                "patient_id must be a non-empty string. "
                "NPHIES and Malaffi require a valid Patient reference."
            )
        if not 0.0 <= result.confidence <= 1.0:
            raise FHIRConversionError(
                f"Confidence score {result.confidence!r} is outside valid "
                "range [0.0, 1.0]. ClassificationResult is corrupt."
            )
        if result.heart_rate_bpm <= 0.0:
            raise FHIRConversionError(
                f"heart_rate_bpm must be a positive value. "
                f"Got {result.heart_rate_bpm!r}."
            )

    # ── FHIR Resource Builders ─────────────────────────────────────────────────

    @staticmethod
    def _build_category() -> dict[str, Any]:
        return {
            "coding": [
                {
                    "system": OBS_CATEGORY_SYSTEM,
                    "code": "exam",
                    "display": "Exam",
                }
            ]
        }

    @staticmethod
    def _build_observation_code() -> dict[str, Any]:
        return {
            "coding": [
                {
                    "system": LOINC_SYSTEM,
                    "code": CARDIAC_RHYTHM_LOINC,
                    "display": "Cardiac rhythm",
                }
            ],
            "text": "ECG Arrhythmia Analysis — IEC 62304 Class B SaMD",
        }

    @staticmethod
    def _build_value(
        snomed_code: str,
        snomed_display: str,
    ) -> dict[str, Any]:
        return {
            "coding": [
                {
                    "system": SNOMED_SYSTEM,
                    "code": snomed_code,
                    "display": snomed_display,
                }
            ],
            "text": snomed_display,
        }

    @staticmethod
    def _build_heart_rate_component(heart_rate_bpm: float) -> dict[str, Any]:
        return {
            "code": {
                "coding": [
                    {
                        "system": LOINC_SYSTEM,
                        "code": HEART_RATE_LOINC,
                        "display": "Heart rate",
                    }
                ]
            },
            "valueQuantity": {
                "value": round(heart_rate_bpm, 1),
                "unit": "beats/minute",
                "system": UCUM_SYSTEM,
                "code": "/min",
            },
        }

    @staticmethod
    def _build_confidence_extension(confidence: float) -> dict[str, Any]:
        return {
            "url": _CONFIDENCE_EXT_URL,
            "valueDecimal": round(confidence, 4),
        }

    @staticmethod
    def _build_iec62304_extension() -> dict[str, Any]:
        return {
            "url": _IEC62304_EXT_URL,
            "valueString": "IEC 62304 Class B",
        }