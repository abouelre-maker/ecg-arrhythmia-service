# ISO 14971 Risk Management Matrix & Traceability
## System: ECG Arrhythmia Detection Microservice

| Risk ID | Hazard Description | Cause | Severity | Initial Risk | Software Mitigation | Verification Test | Residual Risk |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **HAZ-001** | False Negative VT Detection (Missed VT) | High noise or peak detection failure | Critical | High | Implement Pan-Tompkins peak filtering + Sensitivity ≥ 95% threshold | `test_vt_ecg_detection` | Low (Acceptable) |
| **HAZ-002** | False Positive VT Alert | Motion artifact mimicking tachycardia | Marginal | Medium | Signal quality check & RR interval verification | `test_normal_ecg_detection` | Low (Acceptable) |
| **HAZ-003** | Malformed FHIR Payload | Schema mismatch | Moderate | Medium | Pydantic strict typing & FHIR validator adapter | `fhir_converter.py` execution | Negligible |
