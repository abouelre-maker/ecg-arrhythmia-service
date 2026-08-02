# Clinical Context — Why This Code Was Built This Way

## ICU Device Experience That Shaped This Codebase

The author of this service worked as a Biomedical Service Engineer in an ICU environment, maintaining:

- Patient Monitors (multi-parameter vital sign acquisition)
- Defibrillators (DC Shock devices — trigger sensitivity critical)
- Mechanical Ventilators (alarm threshold engineering)
- Infusion and Syringe Pumps (flow rate precision)

### How Clinical Reality Maps to Code Decisions

| Clinical Observation | Code Decision | File |
|---|---|---|
| False alarms desensitize ICU staff | Specificity ≥ 0.90 enforced in tests | test_signal_processor.py |
| VT missed = immediate cardiac arrest risk | VT SNOMED code 25569003 verified by dedicated test | test_fhir_converter.py L201 |
| Device interoperability failures cause delays | FHIR R4 as the integration standard | fhir_converter.py |
| Noise from electrical equipment in ORs | Bandpass 0.5–40 Hz eliminates 50Hz mains interference | signal_processor.py |
