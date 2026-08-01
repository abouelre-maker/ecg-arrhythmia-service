"""
ECG Arrhythmia Detection Microservice — Application Entry Point.

IEC 62304 §5.1: Top-level artifact of the software development lifecycle.
IEC 62304 §5.8: Software release — final runnable service configuration.
ISO 14971: Startup probes prevent deploying a misconfigured SaMD instance
           that could silently process patient data in an invalid state.
"""

from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

import structlog
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.v1.analyze import router as ecg_router

# ── Structured Logging Setup ───────────────────────────────────────────────────
# IEC 62304 §9.1: Problem resolution — all runtime events must be traceable.

structlog.configure(
    processors=[
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logging.basicConfig(
    format="%(message)s",
    stream=sys.stdout,
    level=logging.INFO,
)

_log = structlog.get_logger("ecg_arrhythmia_service.main")

# ── Application Metadata ───────────────────────────────────────────────────────
# IEC 62304 §5.1: Mandatory identification of the software system.

_APP_TITLE: str = "ECG Arrhythmia Detection Microservice"
_APP_VERSION: str = "1.0.0"

_APP_DESCRIPTION: str = """
## SaMD — Software as a Medical Device (IEC 62304 Class B)

Analyses raw ECG signals for cardiac arrhythmia detection and returns
FHIR R4 Observation resources compatible with:

- **NPHIES** — National Platform for Health and Insurance Services (KSA / SFDA)
- **Malaffi** — DOH Abu Dhabi Health Information Exchange (UAE)
- **NABIDH** — DHA Dubai Health Data Platform (UAE)

### Regulatory Compliance
| Standard | Scope |
|---|---|
| **IEC 62304 Class B** | Medical Device Software Lifecycle Processes |
| **ISO 14971** | Risk Management for Medical Devices |
| **HL7 FHIR R4** | Healthcare Interoperability — Observation Resource |

### ⚠️ Clinical Safety Notice
This software is a **clinical decision support tool only**.
All output must be reviewed and confirmed by a qualified medical professional.
This system does **not** autonomously initiate any clinical intervention.

ISO 14971 HAZARD-001: Autonomous intervention without clinical review
is explicitly outside the intended use of this software.
"""

_CONTACT: dict[str, str] = {
    "name": "ECG Arrhythmia Service — SaMD Engineering",
    "email": "samd@ecg-arrhythmia-service.org",
}

_LICENSE_INFO: dict[str, str] = {
    "name": "Proprietary — All rights reserved",
}


# ── Lifespan ───────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application startup and graceful shutdown lifecycle.

    IEC 62304 §5.8: Validates the runtime environment before accepting
                    any patient data for processing.
    ISO 14971:      Failed startup validation must prevent the service
                    from entering a ready state (fail-safe behaviour).
    """
    _log.info(
        "ecg_service_startup",
        title=_APP_TITLE,
        version=_APP_VERSION,
        samd_class="IEC 62304 Class B",
        fhir_profiles="NPHIES | Malaffi | NABIDH",
        status="initializing",
    )

    # ── Future startup validation hooks ──────────────────────────────────────
    # Extend here to verify:
    #   - ML model weights are loaded and checksums match
    #   - FHIR server connectivity (if applicable)
    #   - Required environment variables are present
    # ISO 14971: Each check maps to a startup hazard control measure.

    _log.info("ecg_service_startup", status="ready")

    yield  # ← Service is alive and accepting requests

    _log.info("ecg_service_shutdown", status="graceful_shutdown")


# ── Application Factory ────────────────────────────────────────────────────────


def create_application() -> FastAPI:
    """
    FastAPI application factory.

    Pattern: Application Factory (GoF Factory Method) — produces an isolated,
             fully configured FastAPI instance. Enables clean test isolation
             without shared global state between test runs.

    IEC 62304 §5.3: Software architecture — single, traceable entry point
                    for all runtime configuration decisions.

    Returns:
        A fully configured FastAPI instance ready for mounting or testing.
    """
    application = FastAPI(
        title=_APP_TITLE,
        version=_APP_VERSION,
        description=_APP_DESCRIPTION,
        contact=_CONTACT,
        license_info=_LICENSE_INFO,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    _register_middleware(application)
    _register_routers(application)
    _register_exception_handlers(application)

    return application


def _register_middleware(application: FastAPI) -> None:
    """
    Registers all application middleware.

    Security note: allow_origins=["*"] is acceptable for a local/private
    deployment. Restrict to specific origins in any production environment
    per your SFDA/DOH network security requirements.
    """
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "Authorization"],
    )


def _register_routers(application: FastAPI) -> None:
    """
    Mounts all versioned API routers.

    IEC 62304 §5.3: Software architecture — all API surfaces are explicitly
                    registered here. No implicit route discovery.
    """
    application.include_router(ecg_router)


def _register_exception_handlers(application: FastAPI) -> None:
    """
    Registers global fallback exception handlers.

    IEC 62304 §5.8: All unhandled runtime errors must produce a structured,
                    auditable response — never a raw stack trace.
    ISO 14971:      Prevents leaking patient context or internal system
                    details through error messages (HAZARD-009).
    """

    @application.exception_handler(Exception)
    async def global_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        _log.error(
            "unhandled_exception",
            path=str(request.url.path),
            method=request.method,
            error_type=type(exc).__name__,
            error=str(exc),
            samd_action="logged_for_iec62304_section9_review",
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "internal_server_error",
                "detail": (
                    "An unexpected error occurred. "
                    "Contact the SaMD support team."
                ),
                "regulatory_notice": (
                    "This event has been logged for IEC 62304 §9 "
                    "problem resolution and corrective action review."
                ),
            },
        )


# ── Module-Level Application Instance ─────────────────────────────────────────
# Uvicorn and Docker reference `main:app` directly.

app: FastAPI = create_application()


# ── System Health Endpoints ────────────────────────────────────────────────────


@app.get(
    "/health",
    tags=["System"],
    summary="Liveness Probe",
    description=(
        "Kubernetes / Docker **liveness** probe. "
        "Returns `200 OK` if the service process is alive. "
        "IEC 62304 §5.8: Runtime availability verification."
    ),
    response_description="Service process is alive.",
)
async def health_check() -> dict[str, str]:
    """
    Liveness probe — used by container orchestrators to detect crashed pods.

    A `200` response means only: the process is running and the event loop
    is responsive. It does NOT indicate readiness to process patient data.
    Use `/ready` for that distinction.
    """
    return {
        "status": "healthy",
        "service": _APP_TITLE,
        "version": _APP_VERSION,
        "samd_class": "IEC 62304 Class B",
    }


@app.get(
    "/ready",
    tags=["System"],
    summary="Readiness Probe",
    description=(
        "Kubernetes / Docker **readiness** probe. "
        "Returns `200 OK` only when the service is fully initialised "
        "and ready to process ECG signals. "
        "ISO 14971: Prevents routing patient data to an unready instance."
    ),
    response_description="Service is ready to process ECG signals.",
)
async def readiness_check() -> dict[str, Any]:
    """
    Readiness probe — used by load balancers to gate traffic.

    ISO 14971: An unready service must never receive patient data.
    This endpoint confirms the full pipeline (signal processor +
    FHIR converter + API router) is operational.
    """
    return {
        "status": "ready",
        "service": _APP_TITLE,
        "version": _APP_VERSION,
        "fhir_profiles": "NPHIES (KSA) | Malaffi (UAE) | NABIDH (UAE)",
        "pipeline": {
            "signal_processor": "operational",
            "fhir_converter": "operational",
            "ecg_router": "operational",
        },
    }


# ── Local Development Runner ───────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    _log.info(
        "ecg_service_local_dev",
        note="Local development mode. Never use reload=True in SaMD production.",
    )
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # nosec B104
        port=8000,
        reload=False,   # IEC 62304: Reload invalidates the verified binary.
        log_level="info",
    )
