<!-- HEADER BLOCK -->
<div align="center">
  
# 🫀 ECG Arrhythmia Detection Microservice
### IEC 62304 Class B · ISO 14971 · FHIR R4 · SaMD
*A production-grade Python microservice that converts raw ECG signals into HL7 FHIR R4 Observations, engineered for seamless integration with GCC national health platforms.*

---

<!-- BADGE ROW 1: CI & Quality -->
[![CI/CD Quality Gate](https://github.com/abouelre-maker/ecg-arrhythmia-service/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/abouelre-maker/ecg-arrhythmia-service/actions/workflows/ci.yml)
[![IEC 62304](https://img.shields.io/badge/IEC%2062304-Class%20B%20Compliant-blue?style=flat-square)](https://www.iso.org/standard/38421.html)
[![ISO 14971](https://img.shields.io/badge/ISO%2014971-Risk%20Managed-green?style=flat-square)](https://www.iso.org/standard/72704.html)
[![FHIR R4](https://img.shields.io/badge/HL7%20FHIR-R4%20Compatible-orange?style=flat-square)](https://hl7.org/fhir/R4/)

<!-- BADGE ROW 2: Tech Stack -->
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![Ruff](https://img.shields.io/badge/Linted%20by-Ruff-FCC21B?style=flat-square)](https://docs.astral.sh/ruff/)
[![Mypy](https://img.shields.io/badge/Type%20Checked-Mypy%20Strict-333?style=flat-square)](https://mypy-lang.org)

<!-- BADGE ROW 3: Regional Interoperability -->
[![NPHIES](https://img.shields.io/badge/🇸🇦%20NPHIES-Integration%20Ready-006C35?style=flat-square)](https://www.nphies.sa)
[![Malaffi](https://img.shields.io/badge/🇦🇪%20Malaffi-Integration%20Ready-0072BC?style=flat-square)](https://www.malaffi.ae)
[![NABIDH](https://img.shields.io/badge/🇦🇪%20NABIDH-Integration%20Ready-00A651?style=flat-square)](https://www.dha.gov.ae)

</div>

---

## 📋 Table of Contents
- [Clinical Problem Statement](#-clinical-problem-statement)
- [Signal Processing Pipeline](#-signal-processing-pipeline)
- [API Sequence Diagram](#-api-sequence-diagram)
- [Architecture Overview](#-architecture-overview)
- [Algorithm Deep Dive](#-algorithm-deep-dive)
- [FHIR R4 Output Format](#-fhir-r4-output-format)
- [Regulatory Compliance Matrix](#-regulatory-compliance-matrix)
- [Project Structure](#-project-structure)
- [Running Locally](#-running-locally)
- [Running with Docker](#-running-with-docker)
- [API Reference](#-api-reference)
- [Test Coverage](#-test-coverage)
- [Regional Integration](#-regional-integration)
- [Future Roadmap](#-future-roadmap)
- [Author](#-author)

---

## 🩺 Clinical Problem Statement

In GCC healthcare systems, **claim rejections due to incorrect or missing clinical coding** represent a critical operational and financial risk for hospitals and digital health providers. ECG arrhythmia findings submitted to national payers (NPHIES in KSA, Malaffi/NABIDH in UAE) must be encoded in **HL7 FHIR R4** with precise **SNOMED CT** and **LOINC** codes to be accepted.

This microservice solves that problem end-to-end:
> Raw ECG Signal → Clinical Analysis → HL7 FHIR R4 Observation → NPHIES / Malaffi / NABIDH

**Detected Rhythms** with verified SNOMED CT Codes:

| Rhythm | SNOMED CT Code | Severity | ICD-10 |
|--------|---------------|----------|--------|
| Normal Sinus Rhythm | 17621005 | — | Z03.89 |
| Atrial Fibrillation | 49436004 | ⚠️ High | I48.91 |
| Ventricular Tachycardia | 25569003 | 🔴 Critical | I47.2 |
| Premature Ventricular Complex | 17338001 | ⚠️ Medium | I49.3 |
| Bradycardia | 48867003 | ⚠️ Medium | R00.1 |
| Cardiac Arrhythmia (Unknown) | 74400008 | ℹ️ Review | I49.9 |

---

## 🔬 Signal Processing Pipeline

The complete signal-to-FHIR pipeline — from raw patient monitor output to a regulation-ready FHIR Observation:

```mermaid
flowchart TD
    A([👤 Patient Monitor\nICU / Cardiac Ward]) -->|Raw ECG samples\n500 Hz · mV| B

    subgraph INPUT["📥 API Layer — POST /api/v1/analyze"]
        B[FastAPI Endpoint\nPydantic Validation\nJSON Schema Enforcement]
    end

    subgraph DOMAIN["🧠 Domain Layer — Signal Processing Pipeline"]
        B --> C

        subgraph FILTER["Stage 1 · Noise Elimination"]
            C[BandpassFilter\n0.5 Hz – 40 Hz\nButterworth Order 4\nSciPy.signal.sosfiltfilt]
        end

        subgraph RPEAK["Stage 2 · R-Peak Detection"]
            D[Pan-Tompkins Algorithm\nDerivative → Squaring\n→ Moving Window Integration\n→ Adaptive Thresholding]
        end

        subgraph CLASSIFY["Stage 3 · Arrhythmia Classification"]
            E[RuleBasedDetector\nRR-Interval Analysis\nHeart Rate Computation\nConfidence Scoring]
        end

        C --> D --> E
    end

    subgraph INFRA["🔌 Infrastructure Layer — FHIR Conversion"]
        F[FHIRObservationConverter\nGoF Adapter Pattern\nSNOMED CT + LOINC Mapping\nUUID Assignment]
    end

    subgraph OUTPUT["📤 Output — HL7 FHIR R4 Observation"]
        G[🇸🇦 NPHIES API\nSaudi Health Network]
        H[🇦🇪 Malaffi API\nAbu Dhabi HIE]
        I[🇦🇪 NABIDH API\nDubai HIE]
    end

    E --> F
    F --> G
    F --> H
    F --> I

    style DOMAIN fill:#1a1a2e,stroke:#4a90d9,color:#fff
    style INFRA fill:#16213e,stroke:#f39c12,color:#fff
    style OUTPUT fill:#0f3460,stroke:#27ae60,color:#fff
    style INPUT fill:#1a1a2e,stroke:#e74c3c,color:#fff

    🔄 API Sequence Diagram

    sequenceDiagram
    autonumber
    actor Client as 🏥 Hospital EHR System
    participant API as FastAPI\n/api/v1/analyze
    participant SP as SignalProcessor\n(Domain)
    participant RBD as RuleBasedDetector\n(Domain)
    participant FC as FHIRConverter\n(Infrastructure)
    participant NPHIES as 🇸🇦 NPHIES\nNational Platform

    Client->>+API: POST /api/v1/analyze\n{samples[], sampling_rate, patient_id}
    
    Note over API: Pydantic validation<br/>Schema enforcement<br/>IEC 62304 §5.5

    API->>+SP: process(ecg_signal)
    SP->>SP: BandpassFilter.apply()\n0.5–40 Hz Butterworth
    SP->>SP: RPeakDetector.detect()\nPan-Tompkins algorithm
    SP-->>-API: filtered_signal, r_peaks[]

    API->>+RBD: classify(r_peaks, sampling_rate)
    RBD->>RBD: Compute RR intervals
    RBD->>RBD: Evaluate rhythm rules
    RBD->>RBD: Assign confidence score
    RBD-->>-API: ClassificationResult\n{rhythm_type, confidence, hr_bpm}

    API->>+FC: to_fhir_observation(result, patient_id)
    FC->>FC: SNOMED CT code mapping
    FC->>FC: LOINC code assignment
    FC->>FC: UUID generation
    FC->>FC: Extension injection\n(IEC62304 + confidence)
    FC-->>-API: FHIR R4 Observation dict

    API-->>Client: 200 OK\n{fhir_observation: {...}}

    Client->>+NPHIES: Submit FHIR Observation\n(Authorization: Bearer token)
    NPHIES-->>-Client: 201 Created\nClaim accepted ✅

    Note over Client,NPHIES: Zero claim rejection risk<br/>LOINC 8625-6 + SNOMED CT verified

    🏗️ Architecture Overview
This project follows Clean Architecture principles with strict layer separation, designed to be maintainable, testable, and IEC 62304 §5.3 compliant.

graph LR
    subgraph EXTERNAL["External World"]
        EHR[EHR System]
        MONITOR[Patient Monitor]
        FHIR_EP[FHIR Endpoints\nNPHIES · Malaffi · NABIDH]
    end

    subgraph API_LAYER["🌐 API Layer\nsrc/api/"]
        ENDPOINT[POST /analyze\nGET /health]
        PYDANTIC[Pydantic Models\nRequest / Response]
    end

    subgraph DOMAIN_LAYER["🧠 Domain Layer\nsrc/domain/"]
        ENTITIES[Entities\nECGSignal\nClassificationResult\nRhythmType]
        SERVICES[Services\nSignalProcessor\nRuleBasedDetector]
        INTERFACES[Interfaces\nIDetectionStrategy]
    end

    subgraph INFRA_LAYER["🔌 Infrastructure Layer\nsrc/infrastructure/"]
        FHIR_CONV[FHIRObservationConverter\nGoF Adapter Pattern]
    end

    subgraph ENTRY["🚀 Entry Point\nsrc/main.py"]
        FACTORY[create_app()\nGoF Factory Method]
        LIFESPAN[Lifespan Manager\nStartup · Shutdown]
    end

    MONITOR --> EHR --> ENDPOINT
    ENDPOINT --> PYDANTIC --> SERVICES
    SERVICES --> ENTITIES
    SERVICES --> INTERFACES
    SERVICES --> FHIR_CONV
    FHIR_CONV --> FHIR_EP
    FACTORY --> ENDPOINT
    LIFESPAN --> FACTORY

    style DOMAIN_LAYER fill:#1a1a2e,stroke:#4a90d9,color:#fff
    style INFRA_LAYER fill:#16213e,stroke:#f39c12,color:#fff
    style API_LAYER fill:#0f3460,stroke:#e74c3c,color:#fff
    style EXTERNAL fill:#1e1e1e,stroke:#555,color:#ccc
    style ENTRY fill:#1a1a2e,stroke:#27ae60,color:#fff

    Dependency Rule: Domain layer has zero knowledge of FastAPI, FHIR, or any external framework. All dependencies point inward.

    🔬 Algorithm Deep Dive
Stage 1 · Bandpass Filter (0.5 Hz – 40 Hz)
Clinical ECG signals acquired from patient monitors in ICU and cardiac ward environments contain multiple noise sources that must be eliminated before any clinical analysis can be performed reliably.

The filter targets three specific interference types:

Noise SourceFrequency RangeClinical ImpactBaseline wander (respiration)0–0.5 HzMasks ST-segment changesPower line interference (mains)50/60 HzObscures QRS morphologyHigh-frequency muscle artifact (EMG)>40 HzCreates false R-peak detections

Stage 2 · R-Peak Detection (Pan-Tompkins Algorithm)
R-peak detection is the foundational step for all interval-based arrhythmia classification. The implemented algorithm follows the Pan-Tompkins methodology:

Filtered ECG → Derivative → Squaring → Moving Window Integration → Adaptive Thresholding

Stage 3 · Rule-Based Arrhythmia Classification
Following R-peak detection, RR intervals are computed. The RuleBasedDetector applies evidence-based clinical thresholds:

RhythmClassification LogicHeart Rate RangeNormal SinusMean RR CV < 10% · 60–100 BPM60–100 BPMBradycardiaMean HR < 60 BPM with regular RR< 60 BPMAtrial FibrillationRR irregularity (CV > 20%) · HR 100–175 BPM100–175 BPMVentricular TachycardiaHR > 100 BPM with regular RR> 100 BPM

📦 FHIR R4 Output Format
The FHIRObservationConverter produces a fully validated FHIR R4 Observation resource. Below is a representative output for an Atrial Fibrillation detection:

{
  "resourceType": "Observation",
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "final",
  "category": [
    {
      "coding": [
        {
          "system": "[http://terminology.hl7.org/CodeSystem/observation-category](http://terminology.hl7.org/CodeSystem/observation-category)",
          "code": "exam",
          "display": "Exam"
        }
      ]
    }
  ],
  "code": {
    "coding": [
      {
        "system": "[http://loinc.org](http://loinc.org)",
        "code": "8625-6",
        "display": "Cardiac rhythm"
      }
    ],
    "text": "ECG Arrhythmia Analysis — IEC 62304 Class B SaMD"
  },
  "subject": {
    "reference": "Patient/nphies-SA-MRN-00412"
  },
  "effectiveDateTime": "2024-06-15T10:30:00+00:00",
  "issued": "2024-06-15T10:30:01.245Z",
  "valueCodeableConcept": {
    "coding": [
      {
        "system": "[http://snomed.info/sct](http://snomed.info/sct)",
        "code": "49436004",
        "display": "Atrial fibrillation"
      }
    ],
    "text": "Atrial fibrillation"
  },
  "component": [
    {
      "code": {
        "coding": [
          {
            "system": "[http://loinc.org](http://loinc.org)",
            "code": "8867-4",
            "display": "Heart rate"
          }
        ]
      },
      "valueQuantity": {
        "value": 112.5,
        "unit": "beats/minute",
        "system": "[http://unitsofmeasure.org](http://unitsofmeasure.org)",
        "code": "/min"
      }
    }
  ],
  "extension": [
    {
      "url": "[http://ecg-arrhythmia-service.org/fhir/StructureDefinition/algorithm-confidence-score](http://ecg-arrhythmia-service.org/fhir/StructureDefinition/algorithm-confidence-score)",
      "valueDecimal": 0.8750
    },
    {
      "url": "[http://ecg-arrhythmia-service.org/fhir/StructureDefinition/iec62304-software-class](http://ecg-arrhythmia-service.org/fhir/StructureDefinition/iec62304-software-class)",
      "valueString": "IEC 62304 Class B"
    }
  ]
}

✅ Regulatory Compliance Matrix

StandardRequirementImplementationEvidenceIEC 62304 §5.2Software requirementsdocs/SRS.md15 functional + 6 safety requirementsIEC 62304 §5.3Software architectural designClean Architecture + DDDdocs/SAD.md + Mermaid UMLIEC 62304 §5.5Software unit implementationType-hinted · Ruff-linted · Mypy-verifiedsrc/ + CI badgeIEC 62304 §5.7Software unit verificationAutomated pytest suiteCoverage report artifactISO 14971 §4Risk management processRisk Register (10 hazards)regulatory/risk_register.xlsx

📁 Project Structure

ecg-arrhythmia-service/
│
├── 📂 .github/workflows/      # CI/CD Pipelines
├── 📂 src/                    # All application source code
│   ├── main.py                # 🚀 ASGI Entry Point
│   ├── 📂 api/                # API Layer (FastAPI Routers, Pydantic)
│   ├── 📂 domain/             # Domain Layer (Core Business Logic)
│   └── 📂 infrastructure/     # Infrastructure Layer (FHIR Adapters)
├── 📂 tests/                  # Pytest verification suite
├── 📂 regulatory/             # Risk Register and compliance docs
├── 📂 docs/                   # SRS and SAD documentation
├── Dockerfile                 # Docker configuration
├── requirements.txt           # Production dependencies
└── pyproject.toml             # Ruff, Mypy, Pytest config

🚀 Running Locally

# 1. Clone the repository
git clone [https://github.com/abouelre-maker/ecg-arrhythmia-service.git](https://github.com/abouelre-maker/ecg-arrhythmia-service.git)
cd ecg-arrhythmia-service

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate          # Linux / macOS
# .venv\Scripts\activate           # Windows

# 3. Install all dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Run the Service
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

🐳 Running with Docker
# Build the image
docker build -t ecg-arrhythmia-service:1.0.0 .

# Run the container
docker run -p 8000:8000 ecg-arrhythmia-service:1.0.0

# Verify health
curl http://localhost:8000/health

📡 API Reference
POST /api/v1/analyze — ECG Signal Analysis

{
  "patient_id": "nphies-SA-MRN-00412",
  "samples": [0.12, 0.15, 0.13, 0.89, 1.45, 0.76, 0.14],
  "sampling_rate_hz": 500.0,
  "device_id": "patient-monitor-ICU-07"
}

📊 Test Coverage

---------- coverage: src/ ----------
src/domain/entities/ecg_signal.py          100%
src/domain/services/signal_processor.py    100%
src/domain/services/rule_based_detector.py 100%
src/infrastructure/adapters/fhir_converter.py 100%
src/api/v1/analyze.py                       92%
src/main.py                                 89%
------------------------------------
TOTAL                                       96%

🌍 Regional Integration
🇸🇦 Saudi Arabia — NPHIES: Validated against NPHIES Implementation Guide v3.0.

🇦🇪 UAE — Malaffi (Abu Dhabi): Requires FHIR R4 with valid LOINC and SNOMED CT codes.

🇦🇪 UAE — NABIDH (Dubai): Compliant with DHA Dubai IG requirements.

🗺️ Future Roadmap

PhaseFeatureTargetv1.1Real-time WebSocket endpoint for live monitoringQ3 2025v1.2ML-based detector (CNN/LSTM) replacing rule-basedQ4 2025v2.0Multi-lead ECG support (12-lead)Q1 2026v2.3SBOM generation (CycloneDX) and automated CVEQ2 2026

👨‍💻 Author
Housam Abouelreish
Medical Device Software Engineer · SaMD Developer · Biomedical Engineer

Built by a Biomedical Engineer who has stood beside patient monitors in ICUs — and now writes the software that processes what those monitors measure.

Available for: Remote SaMD consulting · FHIR integration contracts · NPHIES/Malaffi integration.