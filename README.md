# ECG Arrhythmia Detection Microservice (SaMD)

[![Quality Gate](https://github.com/abouelre-maker/ecg-arrhythmia-service/actions/workflows/ci.yml/badge.svg)](https://github.com/abouelre-maker/ecg-arrhythmia-service/actions)
[![Standard](https://img.shields.io/badge/IEC%2062304-Class%20B-blue.svg)](https://www.iso.org/standard/38421.html)
[![Risk Management](https://img.shields.io/badge/ISO%2014971-Compliant-green.svg)](https://www.iso.org/standard/72704.html)
[![FHIR](https://img.shields.io/badge/HL7%20FHIR-R4-orange.svg)](https://hl7.org/fhir/R4/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)

An enterprise-grade **Software as a Medical Device (SaMD)** microservice built for automated ECG signal analysis, arrhythmia classification, and real-time HL7 FHIR R4 observation generation.

Designed specifically for seamless integration into hospital information systems (HIS), telemetry platforms, and electronic health record (EHR) systems across the **GCC Healthcare Ecosystem**:
- 🇸🇦 **NPHIES** — National Platform for Health and Insurance Services (Kingdom of Saudi Arabia)
- 🇦🇪 **Malaffi** — Abu Dhabi Health Data Platform (UAE-AD)
- 🇦🇪 **NABIDH** — Dubai Health Data Platform (UAE-DXB)

---

## 🏥 Product Overview & Value Proposition

Manual interpretation of continuous ECG monitoring stream data in telemetry wards creates significant clinical overhead and risk of delayed intervention. Furthermore, unstructured clinical measurements sent to regional insurance and health exchange platforms often result in **claim rejections and audit failures**.

This service solves both problems:
1. **Clinical Decision Support**: Processes raw lead-II ECG signals, applies bandpass filtering, detects R-peaks, and classifies rhythms into 6 distinct categories.
2. **Interoperability & Monetization**: Converts detected clinical arrhythmias instantly into validated **HL7 FHIR R4 `Observation`** payloads encoded with LOINC and SNOMED-CT standards, preventing compliance rejections during reimbursement processing.

---

## 🛡️ Regulatory & Compliance Architecture

This project is architected and verified according to international medical software standards:

| Standard | Designation | Implementation Details |
| :--- | :--- | :--- |
| **IEC 62304** | Class B | Full software development lifecycle trace, modular separation (Domain / Infrastructure / API), unit and integration testing. |
| **ISO 14971** | Risk-Managed | Boundary exception shielding (`HAZARD-008`), safety audit logs without sensitive data leakage, fail-safe HTTP error responses. |
| **HL7 FHIR R4** | Interoperability | Standardized payload wrapping (`Observation` resource) for direct integration into NPHIES, Malaffi, and NABIDH pipelines. |

---

## ⚡ Detected Arrhythmia Rhythms

The rule-based algorithmic pipeline evaluates signal properties to identify:
- **Normal Sinus Rhythm (NSR)**
- **Atrial Fibrillation (AF)**
- **Ventricular Tachycardia (VT)**
- **Premature Ventricular Contraction (PVC)**
- **Bradycardia**
- **Unknown / Unclassifiable Rhythm**

---

## 🏗️ Software Architecture

Built using Clean Architecture principles and the **GoF Factory Method Pattern**:
graph TD
    A[Patient Monitor / Telemetry] -->|Raw ECG Signal| B(SaMD Microservice)
    B -->|Bandpass Filter| C{R-Peak Detection}
    C -->|Feature Extraction| D[Arrhythmia Classifier]
    D -->|NSR, AF, VT, PVC| E(FHIR R4 Adapter)
    E -->|Observation Resource| F[(HIS / EMR System)]
    F -->|Integration| G((NPHIES / Malaffi))
    
    classDef saudi fill:#006A4E,stroke:#fff,stroke-width:2px,color:#fff;
    classDef uae fill:#FF0000,stroke:#fff,stroke-width:2px,color:#fff;
    classDef service fill:#005b96,stroke:#fff,stroke-width:2px,color:#fff;
    
    class G saudi;
    class B,D service;
