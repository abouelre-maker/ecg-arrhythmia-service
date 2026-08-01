"""
Integration Tests — Application Entry Point (main.py).

IEC 62304 §5.7: Software system integration verification.
ISO 14971:      Confirms liveness and readiness probes behave correctly
                under the nominal case — incorrect probes could route
                patient data to an unready service instance.

Test Count: 12 cases across 3 classes.
"""

from __future__ import annotations

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from main import _APP_TITLE, _APP_VERSION, app

# ── Shared Client ──────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def client() -> TestClient:
    """
    Module-scoped TestClient — avoids repeated app startup overhead.
    FastAPI TestClient handles the lifespan context automatically.
    """
    return TestClient(app)


# ── 1. Liveness Probe (/health) ───────────────────────────────────────────────


class TestHealthEndpoint:
    """
    IEC 62304 §5.8: Liveness probe must always return 200 when the
    process is alive. A false negative here causes unnecessary pod restarts.
    """

    def test_health_returns_200(self, client: TestClient) -> None:
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK

    def test_health_status_is_healthy(self, client: TestClient) -> None:
        data = client.get("/health").json()
        assert data["status"] == "healthy"

    def test_health_contains_correct_service_name(
        self, client: TestClient
    ) -> None:
        data = client.get("/health").json()
        assert data["service"] == _APP_TITLE

    def test_health_contains_correct_version(
        self, client: TestClient
    ) -> None:
        data = client.get("/health").json()
        assert data["version"] == _APP_VERSION

    def test_health_declares_iec62304_class_b(
        self, client: TestClient
    ) -> None:
        """
        IEC 62304 §5.1: The SaMD class must be identifiable at runtime
        for regulatory audit and incident investigation purposes.
        """
        data = client.get("/health").json()
        assert data["samd_class"] == "IEC 62304 Class B"


# ── 2. Readiness Probe (/ready) ───────────────────────────────────────────────


class TestReadinessEndpoint:
    """
    ISO 14971: Readiness probe failures must gate all patient traffic.
    These tests confirm the probe returns correct metadata for orchestrators.
    """

    def test_ready_returns_200(self, client: TestClient) -> None:
        response = client.get("/ready")
        assert response.status_code == status.HTTP_200_OK

    def test_ready_status_is_ready(self, client: TestClient) -> None:
        data = client.get("/ready").json()
        assert data["status"] == "ready"

    def test_ready_declares_nphies_profile(
        self, client: TestClient
    ) -> None:
        """NPHIES (KSA/SFDA) must be listed in the readiness response."""
        data = client.get("/ready").json()
        assert "NPHIES" in data["fhir_profiles"]

    def test_ready_declares_malaffi_profile(
        self, client: TestClient
    ) -> None:
        """Malaffi (UAE/DOH Abu Dhabi) must be listed."""
        data = client.get("/ready").json()
        assert "Malaffi" in data["fhir_profiles"]

    def test_ready_declares_nabidh_profile(
        self, client: TestClient
    ) -> None:
        """NABIDH (UAE/DHA Dubai) must be listed."""
        data = client.get("/ready").json()
        assert "NABIDH" in data["fhir_profiles"]

    def test_ready_pipeline_all_operational(
        self, client: TestClient
    ) -> None:
        """
        All three pipeline components must report 'operational'.
        ISO 14971: A degraded pipeline must not be considered ready.
        """
        pipeline = client.get("/ready").json()["pipeline"]
        assert pipeline["signal_processor"] == "operational"
        assert pipeline["fhir_converter"] == "operational"
        assert pipeline["ecg_router"] == "operational"


# ── 3. OpenAPI Documentation ───────────────────────────────────────────────────


class TestOpenAPIAvailability:
    """
    IEC 62304 §5.2: Software requirements — the OpenAPI schema is a
    machine-readable regulatory artifact. Its availability must be verified.
    """

    def test_openapi_schema_is_reachable(
        self, client: TestClient
    ) -> None:
        response = client.get("/openapi.json")
        assert response.status_code == status.HTTP_200_OK

    def test_openapi_title_matches_samd_identity(
        self, client: TestClient
    ) -> None:
        schema = client.get("/openapi.json").json()
        assert schema["info"]["title"] == _APP_TITLE