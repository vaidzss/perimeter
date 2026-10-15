"""
Checkpoint 2 Test Suite & Reviewer:
1. Validates openapi_partial.json contains exactly 13 paths:
   - 12 active/unused /api/v2/* routes (including payments/scheduled and accounts/{account_id}/close)
   - 1 deprecated /api/v1/users/export route
   - Intentionally omits the 4 shadow endpoints
2. Validates StructuredTelemetryMiddleware:
   - Non-blocking execution
   - Full 21-field JSON log schema contract compliance
   - Passive PII classification (PAN, GOVT_ID_LIKE, PHONE, UPI_VPA, EMAIL)
   - Dynamic path normalization and parameter extraction
   - JWT claims extraction (sub, role, jti)
   - Ground truth label header ingestion
"""

import os
import json
import pytest
from httpx import AsyncClient, ASGITransport

from person1_api_discovery.app.main import app
from person1_api_discovery.app.middleware import (
    LOG_FILE_PATH,
    RECENT_TELEMETRY_LOGS,
    normalize_request_path,
    scan_pii_fields
)

REQUIRED_LOG_FIELDS = {
    "event_id",
    "timestamp",
    "client_ip",
    "user_agent",
    "method",
    "raw_path",
    "normalized_path",
    "query_params",
    "path_params_extracted",
    "auth_type",
    "jwt_sub",
    "jwt_role",
    "jwt_jti",
    "status_code",
    "req_bytes",
    "res_bytes",
    "latency_ms",
    "pii_fields_detected",
    "ground_truth_label",
    "raw_request_headers",
    "raw_response_sample"
}


@pytest.fixture
def anyio_backend():
    return "asyncio"


def test_openapi_partial_spec_contract():
    """Verify openapi_partial.json strictly complies with Checkpoint 2 requirements."""
    spec_path = os.path.join(os.path.dirname(__file__), "..", "specs", "openapi_partial.json")
    assert os.path.exists(spec_path), f"Spec file not found at {spec_path}"

    with open(spec_path, "r", encoding="utf-8") as f:
        spec = json.load(f)

    assert spec.get("openapi") == "3.0.3"
    paths = spec.get("paths", {})

    # Exactly 13 endpoints must be documented
    assert len(paths) == 13, f"Expected exactly 13 documented endpoints, found {len(paths)}"

    # Check 12 V2 endpoints (including scheduled and close)
    assert "/api/v2/auth/login" in paths
    assert "/api/v2/auth/refresh" in paths
    assert "/api/v2/users/me" in paths
    assert "/api/v2/users/me/contact" in paths
    assert "/api/v2/accounts/{account_id}" in paths
    assert "/api/v2/accounts/{account_id}/statements" in paths
    assert "/api/v2/accounts/beneficiaries" in paths
    assert "/api/v2/accounts/{account_id}/transactions" in paths
    assert "/api/v2/transactions/{txn_id}/receipt" in paths
    assert "/api/v2/payments/upi-transfer" in paths
    assert "/api/v2/payments/scheduled" in paths  # UNUSED #1
    assert "/api/v2/accounts/{account_id}/close" in paths  # UNUSED #2

    # Check 1 deprecated endpoint
    assert "/api/v1/users/export" in paths
    assert paths["/api/v1/users/export"]["get"].get("deprecated") is True

    # OMISSION AUDIT: The 4 shadow endpoints MUST be omitted
    omitted_shadows = [
        "/api/v1/accounts/{account_id}/passbook-dump",
        "/api/internal/admin/users-dump",
        "/api/internal/debug/reset-limits",
        "/api/internal/config/env"
    ]
    for shadow_path in omitted_shadows:
        assert shadow_path not in paths, f"Shadow API {shadow_path} leaked into openapi_partial.json!"


def test_path_normalizer_unit():
    """Verify dynamic path parameterization."""
    norm1, p1 = normalize_request_path("/api/v2/accounts/1004/transactions")
    assert norm1 == "/api/v2/accounts/{id}/transactions"
    assert p1 == {"id": "1004"}

    norm2, p2 = normalize_request_path("/api/v2/transactions/TXN100101/receipt")
    assert norm2 == "/api/v2/transactions/{id}/receipt"
    assert p2 == {"id": "TXN100101"}

    norm3, p3 = normalize_request_path("/api/v2/search/ifsc/HDFC0001234")
    assert norm3 == "/api/v2/search/ifsc/{id}"
    assert p3 == {"id": "HDFC0001234"}


def test_pii_scanner_unit():
    """Verify compiled regexes for Indian synthetic PII."""
    sample = '{"account": 1004, "pan": "ABCDE1004F", "phone": "+91-9876501004", "upi": "user@okaxis", "id": "[GOVT-ID-XXXX-1004]", "email": "test@examplebank.in"}'
    detected = scan_pii_fields(sample)
    assert "PAN" in detected
    assert "PHONE" in detected
    assert "UPI_VPA" in detected
    assert "GOVT_ID_LIKE" in detected
    assert "EMAIL" in detected


@pytest.mark.anyio
async def test_telemetry_middleware_end_to_end():
    """Verify middleware produces schema-compliant logs on real request traffic."""
    # Reset recent logs buffer for isolated test
    RECENT_TELEMETRY_LOGS.clear()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Step 1: Login to get token
        login_res = await client.post(
            "/api/v2/auth/login",
            json={"username": "user_1001", "password": "pass123"},
            headers={"User-Agent": "Pytest-Audit-Agent/1.0", "X-Ground-Truth": "benign"}
        )
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]

        # Step 2: Call BOLA vulnerable endpoint with ground-truth header
        bola_res = await client.get(
            "/api/v2/accounts/1004",
            headers={
                "Authorization": f"Bearer {token}",
                "User-Agent": "BOLA-Probe-Scanner/2.1",
                "X-Ground-Truth": "attack_bola"
            }
        )
        assert bola_res.status_code == 200

        # Step 3: Call Zombie export API (dumps bulk PII, NO AUTH)
        zombie_res = await client.get(
            "/api/v1/users/export",
            headers={"User-Agent": "Legacy-Scraper/1.0"}
        )
        assert zombie_res.status_code == 200

        # Step 4: Call Shadow internal route
        shadow_res = await client.get("/api/internal/config/env")
        assert shadow_res.status_code == 200

    # Verify logs were captured in-memory and in telemetry_stream.jsonl
    assert len(RECENT_TELEMETRY_LOGS) >= 4
    assert os.path.exists(LOG_FILE_PATH)

    # Validate the BOLA telemetry log entry
    bola_log = [l for l in RECENT_TELEMETRY_LOGS if l["raw_path"] == "/api/v2/accounts/1004"][0]

    # Field presence audit against exact required contract
    missing_fields = REQUIRED_LOG_FIELDS - set(bola_log.keys())
    assert not missing_fields, f"Missing fields in telemetry log: {missing_fields}"

    # Field content audit
    assert bola_log["normalized_path"] in {"/api/v2/accounts/{account_id}", "/api/v2/accounts/{id}"}
    assert bola_log["path_params_extracted"] in [{"account_id": "1004"}, {"id": "1004"}]
    assert bola_log["auth_type"] == "JWT_BEARER"
    assert bola_log["jwt_sub"] == "user_1001"
    assert bola_log["jwt_role"] == "customer"
    assert bola_log["jwt_jti"].startswith("tok_")
    assert bola_log["status_code"] == 200
    assert bola_log["ground_truth_label"] == "attack_bola"
    assert bola_log["user_agent"] == "BOLA-Probe-Scanner/2.1"
    assert bola_log["latency_ms"] >= 0.0
    assert "PAN" in bola_log["pii_fields_detected"]
    assert "GOVT_ID_LIKE" in bola_log["pii_fields_detected"]

    # Validate Zombie bulk export telemetry entry
    zombie_log = [l for l in RECENT_TELEMETRY_LOGS if l["raw_path"] == "/api/v1/users/export"][0]
    assert zombie_log["auth_type"] == "NONE"
    assert zombie_log["jwt_sub"] is None
    assert set(zombie_log["pii_fields_detected"]) >= {"PAN", "PHONE", "UPI_VPA", "GOVT_ID_LIKE"}
    assert zombie_log["ground_truth_label"] == "unlabeled"

    # Validate file integrity: check last line in file is valid JSON
    with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
        assert len(lines) >= 4
        last_entry = json.loads(lines[-1])
        assert "event_id" in last_entry
        assert "normalized_path" in last_entry
