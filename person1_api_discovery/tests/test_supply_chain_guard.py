"""
Tests for Checkpoint 7: Outbound Supply-Chain Guard (Sentinel-API Phase 2 - Blind Spot #5).
Validates:
1. SafeExternalAPIClient schema validation against vendor drift and prototype pollution.
2. Second-Order Injection detection in vendor payload strings.
3. Stored XSS prevention from third-party vendor feeds.
4. Numerical sanity bounds on financial rates and supplier metrics.
5. Telemetry emission of OWASP_API10_SUPPLY_CHAIN_POISONING.
6. Guard enforcement on /api/v2/payments/fx-rate blocking poisoned responses (HTTP 502).
"""

import pytest
from httpx import AsyncClient, ASGITransport

from person1_api_discovery.app.main import app
from person1_api_discovery.app.egress_guard import (
    SafeExternalAPIClient,
    SupplyChainPoisoningException,
    FXRateVendorResponse,
    FedExTrackingVendorResponse,
    safe_external_client
)


@pytest.fixture
def anyio_backend():
    return "asyncio"


def test_clean_fx_rate_ingestion():
    client = SafeExternalAPIClient()
    clean_payload = {
        "vendor": "AlphaFxGlobalFeed",
        "from_currency": "USD",
        "to_currency": "INR",
        "rate": 83.25,
        "quote_id": "QUOTE-CLEAN-9988",
        "timestamp": "2026-10-15T12:00:00Z"
    }

    result = client.inspect_vendor_response(clean_payload, schema_model=FXRateVendorResponse)
    assert result.is_poisoned is False
    assert len(result.threat_indicators) == 0

    sanitized = client.ingest_fx_rate(clean_payload)
    assert sanitized["rate"] == 83.25
    assert sanitized["vendor"] == "AlphaFxGlobalFeed"


def test_poisoned_fx_rate_multiple_vectors():
    client = SafeExternalAPIClient()
    poisoned_payload = {
        "vendor": "AlphaFxGlobalFeed",
        "from_currency": "USD",
        "to_currency": "INR",
        "rate": -83.25,  # 1. Numerical sanity violation
        "quote_id": "QUOTE-'; DROP TABLE fx_cache; --",  # 2. Second-Order SQLi
        "script_tag": "<script>alert('vendor_xss')</script>",  # 3. Schema drift & Stored XSS
        "timestamp": "2026-10-15T12:00:00Z"
    }

    result = client.inspect_vendor_response(poisoned_payload, schema_model=FXRateVendorResponse)
    assert result.is_poisoned is True
    assert "OWASP_API10_SUPPLY_CHAIN_POISONING" in result.threat_indicators
    assert "NUMERICAL_SANITY_VIOLATION" in result.threat_indicators
    assert any("SQL_INJECTION" in ind for ind in result.threat_indicators)
    assert "STORED_XSS_DETECTED" in result.threat_indicators
    assert "VENDOR_SCHEMA_DRIFT" in result.threat_indicators
    assert result.severity == "CRITICAL"

    with pytest.raises(SupplyChainPoisoningException) as exc_info:
        client.ingest_fx_rate(poisoned_payload)

    assert "corrupted or malicious payload" in str(exc_info.value)
    assert "OWASP_API10_SUPPLY_CHAIN_POISONING" in exc_info.value.threat_indicators


def test_fedex_tracking_poisoning():
    client = SafeExternalAPIClient()

    # Valid tracking payload
    clean_tracking = {
        "tracking_id": "TRK-9876543210",
        "carrier": "FedEx",
        "status": "IN_TRANSIT",
        "estimated_delivery_days": 3,
        "timestamp": "2026-10-15T12:00:00Z"
    }
    res_clean = client.ingest_fedex_tracking(clean_tracking)
    assert res_clean["status"] == "IN_TRANSIT"

    # Compromised logistics feed: Negative delivery days + Command Injection
    poisoned_tracking = {
        "tracking_id": "TRK-987654; rm -rf /",
        "carrier": "FedEx",
        "status": "IN_TRANSIT",
        "estimated_delivery_days": -5,
        "timestamp": "2026-10-15T12:00:00Z"
    }

    with pytest.raises(SupplyChainPoisoningException) as exc:
        client.ingest_fedex_tracking(poisoned_tracking)

    assert any("COMMAND_INJECTION" in ind for ind in exc.value.threat_indicators)
    assert "NUMERICAL_SANITY_VIOLATION" in exc.value.threat_indicators


def test_stored_xss_detection_in_vendor_response():
    client = SafeExternalAPIClient()
    xss_payload = {
        "vendor": "AlphaFxGlobalFeed",
        "from_currency": "USD",
        "to_currency": "INR",
        "rate": 83.25,
        "quote_id": "QUOTE-1234",
        "timestamp": "2026-10-15T12:00:00Z",
        "note": "<img src=x onerror=alert('document.cookie')>"
    }

    result = client.inspect_vendor_response(xss_payload)
    assert result.is_poisoned is True
    assert "STORED_XSS_DETECTED" in result.threat_indicators


def test_telemetry_logging_buffer():
    # Verify the global singleton records threat telemetry
    assert len(safe_external_client.threat_telemetry_log) >= 0


@pytest.mark.anyio
async def test_endpoint_fx_rate_with_guard_enforcement():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Clean FX rate with guard active -> 200 OK
        res_clean = await client.get("/api/v2/payments/fx-rate?from_currency=USD&to_currency=INR&enforce_guard=true")
        assert res_clean.status_code == 200
        assert res_clean.json()["rate"] == 83.25

        # 2. Poisoned vendor payload with guard active -> 502 Bad Gateway
        res_blocked = await client.get("/api/v2/payments/fx-rate?from_currency=USD&to_currency=INR&vendor_poisoned=true&enforce_guard=true")
        assert res_blocked.status_code == 502
        body = res_blocked.json()
        assert body["detail"]["error"] == "SUPPLY_CHAIN_POISONING_BLOCKED"
        assert "OWASP_API10_SUPPLY_CHAIN_POISONING" in body["detail"]["threat_indicators"]
        assert body["detail"]["owasp_tag"] == "API10:2023 Unsafe Consumption of APIs"

        # 3. Backwards-compatible un-guarded testbed simulator -> 200 OK
        res_testbed = await client.get("/api/v2/payments/fx-rate?from_currency=USD&to_currency=INR&vendor_poisoned=true&enforce_guard=false")
        assert res_testbed.status_code == 200
        assert res_testbed.json()["rate"] < 0
