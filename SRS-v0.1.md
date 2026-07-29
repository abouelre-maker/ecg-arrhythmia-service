# Software Requirements Specification (SRS)
## System: ECG Arrhythmia Detection Microservice
- **IEC 62304 Software Safety Class:** Class B
- **System Purpose:** Processing raw ECG signals and detecting critical arrhythmias (VT, AF, PVC) to issue FHIR R4 Observations.

### 1. Functional Requirements (SYS-FUN)
- **SYS-FUN-001:** The system shall ingest raw 2-lead ECG signals sampled at 360Hz to 500Hz.
- **SYS-FUN-002:** The system shall detect Ventricular Tachycardia (VT) episodes lasting > 3 seconds.
- **SYS-FUN-003:** The output shall be formatted as an HL7/FHIR R4 `Observation` resource compatible with NPHIES (KSA) and Malaffi (UAE).

### 2. Safety & Performance Requirements (SYS-SAF)
- **SYS-SAF-001:** Sensitivity for VT detection shall be ≥ 95%.
- **SYS-SAF-002:** Specificity for VT detection shall be ≥ 90%.

### 3. Cybersecurity Requirements (SYS-SEC)
- **SYS-SEC-001:** API endpoints must enforce TLS 1.3 encryption and JWT authentication.
