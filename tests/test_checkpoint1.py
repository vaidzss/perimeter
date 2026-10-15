"""
Test suite for Checkpoint 1: Vulnerable FinTech Target Cluster & OpenAPI Spec.
Validates:
1. Documented endpoints (/api/v2/*)
2. BOLA vulnerability reproduction
3. High-speed scraping pagination
4. Zombie PII leaks (/api/v1/users/export-all) with Indian PII patterns
5. Shadow endpoints (/api/internal/*) presence in live app
6. OpenAPI official spec compliance (Shadow endpoints strictly absent, Zombie tagged deprecated)
"""

import json
import os
import re
import pytest
from httpx import AsyncClient, ASGITransport
import jwt

from target_service.main import app, JWT_SECRET, JWT_ALGORITHM

PAN_REGEX = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")
UPI_REGEX = re.compile(r"^[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}$")
PHONE_REGEX = re.compile(r"^\+91-[0-9]{10}$")
EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert data["service"] == "fintech-dpi-target-cluster"
        assert data["port"] == 8001


@pytest.mark.anyio
async def test_login_and_jwt_issuance():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Valid login
        response = await client.post(
            "/api/v2/auth/login",
            json={"username": "user_101", "password": "password123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["sub"] == "user_101"
        assert data["user"]["account_id"] == "101"

        # Verify JWT payload structure
        token = data["access_token"]
        decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        assert decoded["sub"] == "user_101"
        assert decoded["account_id"] == "101"
        assert decoded["role"] == "retail_user"
        assert "jti" in decoded
        assert "iat" in decoded
        assert "exp" in decoded

        # Invalid login
        bad_resp = await client.post(
            "/api/v2/auth/login",
            json={"username": "user_101", "password": "wrongpassword"}
        )
        assert bad_resp.status_code == 401


@pytest.mark.anyio
async def test_bola_idor_vulnerability():
    """
    Verify BOLA/IDOR vulnerability:
    User 101 logs in, receives token with sub='user_101', account_id='101'.
    Then requests balance of account '102' and '103'.
    The service MUST return account 102 and 103 details without rejecting the mismatch.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Step 1: Login as user_101
        login_resp = await client.post(
            "/api/v2/auth/login",
            json={"username": "user_101", "password": "password123"}
        )
        token = login_resp.json()["access_token"]
        auth_header = {"Authorization": f"Bearer {token}"}

        # Step 2: Access own account 101
        own_resp = await client.get("/api/v2/accounts/101/balance", headers=auth_header)
        assert own_resp.status_code == 200
        assert own_resp.json()["account_id"] == "101"
        assert own_resp.json()["account_holder"] == "Aarav Sharma"

        # Step 3: BOLA Exploit - Access foreign account 102 with user_101 token
        victim_resp = await client.get("/api/v2/accounts/102/balance", headers=auth_header)
        assert victim_resp.status_code == 200
        victim_data = victim_resp.json()
        assert victim_data["account_id"] == "102"
        assert victim_data["account_holder"] == "Priya Patel"
        assert victim_data["available_balance"] == 682400.00

        # Step 4: Arbitrary probe account 9841
        probe_resp = await client.get("/api/v2/accounts/9841/balance", headers=auth_header)
        assert probe_resp.status_code == 200
        assert probe_resp.json()["account_id"] == "9841"


@pytest.mark.anyio
async def test_merchant_directory_scraping_target():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v2/directory/merchants?page=1&limit=5")
        assert resp.status_code == 200
        data = resp.json()
        assert data["page"] == 1
        assert data["limit"] == 5
        assert len(data["data"]) == 5
        assert data["total"] >= 20

        # Check fields of merchants
        first_merchant = data["data"][0]
        assert "merchant_id" in first_merchant
        assert "business_name" in first_merchant
        assert "upi_vpa" in first_merchant
        assert UPI_REGEX.match(first_merchant["upi_vpa"])


@pytest.mark.anyio
async def test_zombie_v1_pii_export():
    """
    Verify Zombie API leaks synthetic Indian PII and is unauthenticated.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/users/export-all")
        assert resp.status_code == 200
        users = resp.json()
        assert isinstance(users, list)
        assert len(users) >= 4

        for user in users:
            assert PAN_REGEX.match(user["pan_card"]), f"Invalid PAN format: {user['pan_card']}"
            assert UPI_REGEX.match(user["upi_vpa"]), f"Invalid UPI format: {user['upi_vpa']}"
            assert PHONE_REGEX.match(user["phone_number"]), f"Invalid Phone format: {user['phone_number']}"
            assert EMAIL_REGEX.match(user["email"]), f"Invalid Email format: {user['email']}"
            assert "govt_id_reference" in user
            assert "session_token_sample" in user


@pytest.mark.anyio
async def test_shadow_apis_live_execution():
    """
    Verify Shadow APIs are active on the service even though undocumented.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Debug reset shadow route
        reset_resp = await client.post("/api/internal/debug/reset", json={"target": "cache"})
        assert reset_resp.status_code == 200
        assert reset_resp.json()["status"] == "acknowledged"
        assert reset_resp.json()["command"] == "DEBUG_SYSTEM_RESET"

        # Config dump shadow route
        dump_resp = await client.get("/api/internal/config/dump")
        assert dump_resp.status_code == 200
        config = dump_resp.json()
        assert "database_url" in config
        assert "redis_cache_host" in config
        assert "kafka_brokers" in config
        assert config["debug_mode"] is True


def test_openapi_spec_structure_and_shadow_exclusion():
    """
    Verify target_service/openapi_official.json:
    1. Contains documented /api/v2/* endpoints
    2. Contains deprecated /api/v1/users/export-all with deprecated: true
    3. Strictly DOES NOT contain /api/internal/* shadow endpoints
    """
    spec_path = os.path.join(os.path.dirname(__file__), "..", "target_service", "openapi_official.json")
    assert os.path.exists(spec_path), f"Spec file not found at {spec_path}"

    with open(spec_path, "r", encoding="utf-8") as f:
        spec = json.load(f)

    assert spec.get("openapi", "").startswith("3.")
    paths = spec.get("paths", {})

    # Documented endpoints MUST be present
    assert "/api/v2/auth/login" in paths
    assert "post" in paths["api/v2/auth/login".replace("api", "/api")]
    assert "/api/v2/accounts/{account_id}/balance" in paths
    assert "get" in paths["/api/v2/accounts/{account_id}/balance"]
    assert "/api/v2/directory/merchants" in paths
    assert "get" in paths["/api/v2/directory/merchants"]

    # Zombie endpoint MUST be present and marked deprecated
    assert "/api/v1/users/export-all" in paths
    assert paths["/api/v1/users/export-all"]["get"].get("deprecated") is True

    # Shadow endpoints MUST be absent from official spec
    assert "/api/internal/debug/reset" not in paths
    assert "/api/internal/config/dump" not in paths

    # No internal paths should leak into official spec
    for path in paths.keys():
        assert not path.startswith("/api/internal"), f"Shadow route leaked into official spec: {path}"
