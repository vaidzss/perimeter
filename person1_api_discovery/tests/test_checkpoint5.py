"""
Tests for Checkpoint 5: Advanced OWASP API Security Testbed Endpoints & Body Sampling Telemetry.
Validates:
1. GET /api/v2/search/merchants?q=... (OWASP API8 SQLi / Command Injection target)
2. POST /api/v2/users/me/webhook-avatar (OWASP API7 SSRF target)
3. POST /api/v2/payments/upi-transfer (OWASP API3/API6 Negative Amount & Duplicate Coupon target)
4. POST /api/v2/accounts/import-statement (OWASP API4 ReDoS / Complexity target)
5. GET /api/v2/payments/fx-rate (OWASP API10 Third-Party Vendor Poisoning target)
6. Middleware request body bounded sampling (raw_request_body_sample up to 4KB)
"""

import json
import pytest
from httpx import AsyncClient, ASGITransport

from person1_api_discovery.app.main import app
from person1_api_discovery.app.auth import create_jwt_token


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def auth_headers():
    token = create_jwt_token(sub="user_1001", role="customer", account_id="1001")
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.anyio
async def test_sqli_search_endpoint(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Standard search
        res1 = await client.get("/api/v2/search/merchants?q=Swiggy", headers=auth_headers)
        assert res1.status_code == 200
        data1 = res1.json()
        assert "merchants" in data1

        # SQLi tautology target
        res2 = await client.get("/api/v2/search/merchants?q=' OR 1=1 --", headers=auth_headers)
        assert res2.status_code == 200
        data2 = res2.json()
        assert len(data2["merchants"]) > 0


@pytest.mark.anyio
async def test_ssrf_webhook_avatar_endpoint(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Legitimate avatar
        res_valid = await client.post(
            "/api/v2/users/me/webhook-avatar",
            json={"avatar_url": "https://cdn.examplebank.in/avatars/user1.png"},
            headers=auth_headers
        )
        assert res_valid.status_code == 200
        assert res_valid.json()["status"] == "success"

        # SSRF malicious target
        res_ssrf = await client.post(
            "/api/v2/users/me/webhook-avatar",
            json={"avatar_url": "http://169.254.169.254/latest/meta-data/"},
            headers=auth_headers
        )
        assert res_ssrf.status_code == 200
        assert "169.254.169.254" in res_ssrf.json()["avatar_url"]


@pytest.mark.anyio
async def test_business_logic_negative_amount_and_coupons(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Negative amount exploit
        res_neg = await client.post(
            "/api/v2/payments/upi-transfer",
            json={
                "payee_vpa": "swiggy@bharatpay",
                "amount": -5000.0,
                "coupons": ["SAVE10", "SAVE10", "SAVE10"]
            },
            headers=auth_headers
        )
        assert res_neg.status_code == 200
        data = res_neg.json()
        assert data["amount"] == -5000.0
        assert len(data["coupons_applied"]) == 3


@pytest.mark.anyio
async def test_redos_and_complexity_endpoint(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Deeply nested JSON payload
        nested = {"val": "bottom"}
        for _ in range(12):
            nested = {"layer": nested}

        res = await client.post(
            "/api/v2/accounts/import-statement",
            json=nested,
            headers=auth_headers
        )
        assert res.status_code == 200
        assert res.json()["is_json"] is True


@pytest.mark.anyio
async def test_fx_rate_vendor_poisoning_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Clean FX rate
        res_clean = await client.get("/api/v2/payments/fx-rate?from_currency=USD&to_currency=INR")
        assert res_clean.status_code == 200
        clean_data = res_clean.json()
        assert clean_data["rate"] > 0

        # Poisoned vendor response
        res_poisoned = await client.get("/api/v2/payments/fx-rate?from_currency=USD&to_currency=INR&vendor_poisoned=true")
        assert res_poisoned.status_code == 200
        p_data = res_poisoned.json()
        assert p_data["rate"] < 0
        assert "DROP TABLE" in p_data["quote_id"]


@pytest.mark.anyio
async def test_middleware_body_sampling_telemetry(auth_headers):
    transport = ASGITransport(app=app)
    from person1_api_discovery.app.middleware import RECENT_TELEMETRY_LOGS

    test_payload = {"test_marker": "sample_body_12345", "amount": 100}
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/api/v2/payments/upi-transfer",
            json=test_payload,
            headers=auth_headers
        )
        assert res.status_code == 200

    # Verify latest telemetry log captured the body
    last_log = RECENT_TELEMETRY_LOGS[-1]
    assert "sample_body_12345" in last_log.get("raw_request_body_sample", "")
    assert last_log.get("parsed_json_body", {}).get("test_marker") == "sample_body_12345"
