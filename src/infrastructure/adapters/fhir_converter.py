from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.observation import Observation
from fhir.resources.reference import Reference
from src.domain.entities.ecg_signal import ArrhythmiaAlert


class FHIRConverterAdapter:
    """تحويل تنبيهات اضطراب النظم إلى موارد HL7/FHIR R4 Observation طبية معتمدة"""

    @staticmethod
    def create_observation(alert: ArrhythmiaAlert) -> Observation:
        observation = Observation(
            status="final",
            code=CodeableConcept(
                coding=[
                    Coding(
                        system="http://loinc.org",
                        code="131328",
                        display="MDC_ECG_EVAL_STAT",
                    )
                ],
                text="ECG Analysis Result",
            ),
            subject=Reference(reference=f"Patient/{alert.patient_id}"),
            valueCodeableConcept=CodeableConcept(
                coding=[
                    Coding(
                        system="http://snomed.info/sct",
                        code="251146004",
                        display=alert.rhythm.value,
                    )
                ],
                text=alert.rhythm.value,
            ),
        )
        return observation


if __name__ == "__main__":
    from src.domain.entities.ecg_signal import ArrhythmiaType

    sample_alert = ArrhythmiaAlert(
        patient_id="PATIENT-101",
        rhythm=ArrhythmiaType.VT,
        confidence=0.95,
        requires_immediate_action=True,
    )

    fhir_obs = FHIRConverterAdapter.create_observation(sample_alert)
    print("تم توليد كائن FHIR R4 بنجاح!")
    print(fhir_obs.json(indent=2))
    