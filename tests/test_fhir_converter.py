"""
Unit Tests — FHIRObservationConverter

IEC 62304 §5.7: Software unit verification — infrastructure adapter layer.
ISO 14971: Each test class maps to a specific hazard control in the Risk Register.

Coverage Target: 100% for fhir_converter.py
Test Count:      29 cases across 6 test classes
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from domain.entities.ecg_signal import ClassificationResult, RhythmType
from infrastructure.adapters.fhir_converter import (
    _RHYTHM_SNOMED_MAP,
    FHIRConversionError,
    FHIRObservationConverter,
)

# ── Shared Fixtures ────────────────────────────────────────────────────────────

_FIXED_TS = datetime(2024, 6, 15, 10, 30, 0, tzinfo=timezone.utc)


@pytest.fixture()
def converter() -> FHIRObservationConverter:
    return FHIRObservationConverter()


@pytest.fixture()
def normal_result() -> ClassificationResult:
    return ClassificationResult(
        rhythm_type=RhythmType.NORMAL_SINUS,
        confidence=0.95,
        heart_rate_bpm=72.0,
        rr_intervals_ms=[833.0, 830.0, 835.0],
        analysis_timestamp=_FIXED_TS,
    )


@pytest.fixture()
def vt_result() -> ClassificationResult:
    return ClassificationResult(
        rhythm_type=RhythmType.VENTRICULAR_TACHYCARDIA,
        confidence=0.88,
        heart_rate_bpm=160.0,
        rr_intervals_ms=[375.0, 371.0, 378.0],
        analysis_timestamp=_FIXED_TS,
    )


@pytest.fixture()
def af_result() -> ClassificationResult:
    return ClassificationResult(
        rhythm_type=RhythmType.ATRIAL_FIBRILLATION,
        confidence=0.82,
        heart_rate_bpm=110.0,
        rr_intervals_ms=[545.0, 423.0, 621.0, 398.0],
        analysis_timestamp=_FIXED_TS,
    )


# ── 1. FHIR R4 Structural Requirements ────────────────────────────────────────


class TestFHIRObservationStructure:
    """Validates mandatory FHIR R4 Observation structural requirements."""

    def test_resource_type_is_observation(
        self,
        converter: FHIRObservationConverter,
        normal_result: ClassificationResult,
    ) -> None:
        obs = converter.to_fhir_observation(normal_result, patient_id="p-001")
        assert obs["resourceType"] == "Observation"

    def test_status_is_final(
        self,
        converter: FHIRObservationConverter,
        normal_result: ClassificationResult,
    ) -> None:
        """Malaffi and NABIDH require status='final' on all submitted Observations."""
        obs = converter.to_fhir_observation(normal_result, patient_id="p-001")
        assert obs["status"] == "final"

    def test_each_observation_has_unique_id(
        self,
        converter: FHIRObservationConverter,
        normal_result: ClassificationResult,
    ) -> None:
        obs_a = converter.to_fhir_observation(normal_result, patient_id="p-001")
        obs_b = converter.to_fhir_observation(normal_result, patient_id="p-001")
        assert obs_a["id"] != obs_b["id"], (
            "Each Observation must carry a unique UUID. "
            "Duplicate IDs violate FHIR R4 §6.3.6."
        )

    def test_patient_reference_format(
        self,
        converter: FHIRObservationConverter,
        normal_result: ClassificationResult,
    ) -> None:
        """NPHIES requires subject.reference in 'Patient/{id}' literal format."""
        obs = converter.to_fhir_observation(normal_result, patient_id="nphies-SA-42")
        assert obs["subject"]["reference"] == "Patient/nphies-SA-42"

    def test_all_mandatory_fields_present(
        self,
        converter: FHIRObservationConverter,
        normal_result: ClassificationResult,
    ) -> None:
        obs = converter.to_fhir_observation(normal_result, patient_id="p-001")
        mandatory_fields = [
            "resourceType", "id", "status", "category",
            "code", "subject", "effectiveDateTime", "issued",
            "valueCodeableConcept", "component", "extension",
        ]
        for field_name in mandatory_fields:
            assert field_name in obs, (
                f"Mandatory FHIR R4 field '{field_name}' is missing from output."
            )

    def test_device_reference_included_when_provided(
        self,
        converter: FHIRObservationConverter,
        normal_result: ClassificationResult,
    ) -> None:
        obs = converter.to_fhir_observation(
            normal_result,
            patient_id="p-001",
            device_id="samd-ecg-v1",
        )
        assert obs["device"]["reference"] == "Device/samd-ecg-v1"

    def test_device_reference_absent_when_not_provided(
        self,
        converter: FHIRObservationConverter,
        normal_result: ClassificationResult,
    ) -> None:
        obs = converter.to_fhir_observation(normal_result, patient_id="p-001")
        assert "device" not in obs


# ── 2. LOINC Code Validation ───────────────────────────────────────────────────


class TestFHIRLOINCCodes:
    """
    Validates LOINC codes for clinical interoperability.
    IEC 62304 REQ-004: Incorrect LOINC codes are a software defect.
    """

    def test_observation_code_is_cardiac_rhythm_loinc(
        self,
        converter: FHIRObservationConverter,
        normal_result: ClassificationResult,
    ) -> None:
        obs = converter.to_fhir_observation(normal_result, patient_id="p-001")
        code_coding = obs["code"]["coding"][0]
        assert code_coding["system"] == "http://loinc.org"
        assert code_coding["code"] == "8625-6"

    def test_heart_rate_component_loinc_code(
        self,
        converter: FHIRObservationConverter,
        normal_result: ClassificationResult,
    ) -> None:
        obs = converter.to_fhir_observation(normal_result, patient_id="p-001")
        hr_coding = obs["component"][0]["code"]["coding"][0]
        assert hr_coding["system"] == "http://loinc.org"
        assert hr_coding["code"] == "8867-4"

    def test_heart_rate_ucum_unit(
        self,
        converter: FHIRObservationConverter,
        normal_result: ClassificationResult,
    ) -> None:
        obs = converter.to_fhir_observation(normal_result, patient_id="p-001")
        quantity = obs["component"][0]["valueQuantity"]
        assert quantity["unit"] == "beats/minute"
        assert quantity["system"] == "http://unitsofmeasure.org"
        assert quantity["code"] == "/min"


# ── 3. SNOMED CT Rhythm Codes ──────────────────────────────────────────────────


class TestFHIRSNOMEDCodes:
    """
    Validates SNOMED CT coding for each RhythmType.
    ISO 14971 HAZARD-007: Incorrect clinical codes = regulatory defect.
    """

    @pytest.mark.parametrize(
        ("rhythm", "expected_snomed"),
        [
            (RhythmType.NORMAL_SINUS, "17621005"),
            (RhythmType.ATRIAL_FIBRILLATION, "49436004"),
            (RhythmType.VENTRICULAR_TACHYCARDIA, "25569003"),
            (RhythmType.PREMATURE_VENTRICULAR_CONTRACTION, "17338001"),
            (RhythmType.BRADYCARDIA, "48867003"),
            (RhythmType.UNKNOWN, "74400008"),
        ],
    )
    def test_snomed_code_per_rhythm_type(
        self,
        converter: FHIRObservationConverter,
        rhythm: RhythmType,
        expected_snomed: str,
    ) -> None:
        result = ClassificationResult(
            rhythm_type=rhythm,
            confidence=0.80,
            heart_rate_bpm=70.0,
            rr_intervals_ms=[857.0],
            analysis_timestamp=_FIXED_TS,
        )
        obs = converter.to_fhir_observation(result, patient_id="p-test")
        value_coding = obs["valueCodeableConcept"]["coding"][0]
        assert value_coding["system"] == "http://snomed.info/sct"
        assert value_coding["code"] == expected_snomed, (
            f"SNOMED CT code mismatch for {rhythm.name}: "
            f"expected {expected_snomed}, got {value_coding['code']}."
        )

    def test_all_rhythm_types_have_snomed_mapping(self) -> None:
        """
        Completeness guard — ensures no new RhythmType is added to the enum
        without a corresponding SNOMED CT entry in _RHYTHM_SNOMED_MAP.
        IEC 62304: Traceability requirement — all enum values must be mapped.
        """
        for rhythm_type in RhythmType:
            assert rhythm_type in _RHYTHM_SNOMED_MAP, (
                f"RhythmType.{rhythm_type.name} has no SNOMED CT mapping. "
                "This is a regulatory traceability defect. "
                "Update _RHYTHM_SNOMED_MAP in fhir_converter.py."
            )


# ── 4. Extension Validation ────────────────────────────────────────────────────


class TestFHIRExtensions:
    """Validates custom FHIR extensions required for SaMD audit trail."""

    def test_confidence_extension_is_present(
        self,
        converter: FHIRObservationConverter,
        normal_result: ClassificationResult,
    ) -> None:
        obs = converter.to_fhir_observation(normal_result, patient_id="p-001")
        ext_urls = [ext["url"] for ext in obs["extension"]]
        assert any("confidence" in url for url in ext_urls), (
            "Algorithm confidence extension must be present for SFDA AI/ML traceability."
        )

    def test_confidence_extension_value_is_rounded_to_4dp(
        self,
        converter: FHIRObservationConverter,
    ) -> None:
        result = ClassificationResult(
            rhythm_type=RhythmType.NORMAL_SINUS,
            confidence=0.123456789,
            heart_rate_bpm=72.0,
            rr_intervals_ms=[833.0],
            analysis_timestamp=_FIXED_TS,
        )
        obs = converter.to_fhir_observation(result, patient_id="p-001")
        confidence_ext = next(
            e for e in obs["extension"] if "confidence" in e["url"]
        )
        assert confidence_ext["valueDecimal"] == round(0.123456789, 4)

    def test_iec62304_extension_is_present(
        self,
        converter: FHIRObservationConverter,
        normal_result: ClassificationResult,
    ) -> None:
        obs = converter.to_fhir_observation(normal_result, patient_id="p-001")
        iec_ext = next(
            (e for e in obs["extension"] if "iec62304" in e["url"]),
            None,
        )
        assert iec_ext is not None, "IEC 62304 software class extension must be present."
        assert iec_ext["valueString"] == "IEC 62304 Class B"


# ── 5. Input Validation & Error Handling ──────────────────────────────────────


class TestFHIRInputValidation:
    """
    ISO 14971 HAZARD-007: Infrastructure boundary validation.
    All invalid inputs must raise FHIRConversionError — never pass silently.
    """

    def test_empty_patient_id_raises(
        self,
        converter: FHIRObservationConverter,
        normal_result: ClassificationResult,
    ) -> None:
        with pytest.raises(FHIRConversionError, match="patient_id"):
            converter.to_fhir_observation(normal_result, patient_id="")

    def test_whitespace_only_patient_id_raises(
        self,
        converter: FHIRObservationConverter,
        normal_result: ClassificationResult,
    ) -> None:
        with pytest.raises(FHIRConversionError, match="patient_id"):
            converter.to_fhir_observation(normal_result, patient_id="   ")

    def test_confidence_above_one_raises(
        self,
        converter: FHIRObservationConverter,
    ) -> None:
        result = ClassificationResult(
            rhythm_type=RhythmType.NORMAL_SINUS,
            confidence=1.01,
            heart_rate_bpm=72.0,
            rr_intervals_ms=[833.0],
            analysis_timestamp=_FIXED_TS,
        )
        with pytest.raises(FHIRConversionError, match="Confidence"):
            converter.to_fhir_observation(result, patient_id="p-001")

    def test_confidence_below_zero_raises(
        self,
        converter: FHIRObservationConverter,
    ) -> None:
        result = ClassificationResult(
            rhythm_type=RhythmType.NORMAL_SINUS,
            confidence=-0.01,
            heart_rate_bpm=72.0,
            rr_intervals_ms=[833.0],
            analysis_timestamp=_FIXED_TS,
        )
        with pytest.raises(FHIRConversionError, match="Confidence"):
            converter.to_fhir_observation(result, patient_id="p-001")

    def test_zero_heart_rate_raises(
        self,
        converter: FHIRObservationConverter,
    ) -> None:
        result = ClassificationResult(
            rhythm_type=RhythmType.NORMAL_SINUS,
            confidence=0.90,
            heart_rate_bpm=0.0,
            rr_intervals_ms=[],
            analysis_timestamp=_FIXED_TS,
        )
        with pytest.raises(FHIRConversionError, match="heart_rate_bpm"):
            converter.to_fhir_observation(result, patient_id="p-001")

    def test_negative_heart_rate_raises(
        self,
        converter: FHIRObservationConverter,
    ) -> None:
        result = ClassificationResult(
            rhythm_type=RhythmType.NORMAL_SINUS,
            confidence=0.90,
            heart_rate_bpm=-75.0,
            rr_intervals_ms=[],
            analysis_timestamp=_FIXED_TS,
        )
        with pytest.raises(FHIRConversionError, match="heart_rate_bpm"):
            converter.to_fhir_observation(result, patient_id="p-001")


# ── 6. Clinical Correctness (End-to-End) ──────────────────────────────────────


class TestFHIRClinicalCorrectness:
    """
    End-to-end clinical validation.
    ISO 14971 HAZARD-001: VT must never be mislabelled — highest severity risk.
    """

    def test_vt_snomed_code_is_clinically_correct(
        self,
        converter: FHIRObservationConverter,
        vt_result: ClassificationResult,
    ) -> None:
        """ISO 14971 HAZARD-001: Mislabelled VT in FHIR output = patient safety risk."""
        obs = converter.to_fhir_observation(vt_result, patient_id="icu-patient-07")
        code = obs["valueCodeableConcept"]["coding"][0]["code"]
        assert code == "25569003", (
            f"VT SNOMED CT code mismatch. Expected 25569003, got {code}. "
            "This is a critical clinical safety defect."
        )

    def test_af_heart_rate_preserved_accurately(
        self,
        converter: FHIRObservationConverter,
        af_result: ClassificationResult,
    ) -> None:
        obs = converter.to_fhir_observation(af_result, patient_id="p-af-01")
        hr_value = obs["component"][0]["valueQuantity"]["value"]
        assert hr_value == 110.0

    def test_effective_datetime_matches_analysis_timestamp(
        self,
        converter: FHIRObservationConverter,
        normal_result: ClassificationResult,
    ) -> None:
        obs = converter.to_fhir_observation(normal_result, patient_id="p-001")
        assert obs["effectiveDateTime"] == _FIXED_TS.isoformat()

    def test_boundary_confidence_zero_is_valid(
        self,
        converter: FHIRObservationConverter,
    ) -> None:
        """Boundary value: confidence = 0.0 is the minimum valid value."""
        result = ClassificationResult(
            rhythm_type=RhythmType.UNKNOWN,
            confidence=0.0,
            heart_rate_bpm=60.0,
            rr_intervals_ms=[1000.0],
            analysis_timestamp=_FIXED_TS,
        )
        obs = converter.to_fhir_observation(result, patient_id="p-boundary")
        assert obs["status"] == "final"

    def test_boundary_confidence_one_is_valid(
        self,
        converter: FHIRObservationConverter,
    ) -> None:
        """Boundary value: confidence = 1.0 is the maximum valid value."""
        result = ClassificationResult(
            rhythm_type=RhythmType.NORMAL_SINUS,
            confidence=1.0,
            heart_rate_bpm=70.0,
            rr_intervals_ms=[857.0],
            analysis_timestamp=_FIXED_TS,
        )
        obs = converter.to_fhir_observation(result, patient_id="p-boundary")
        assert obs["status"] == "final"