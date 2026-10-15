"""
Checkpoint 1 Test Suite & Security Reviewer:
Validates all 19 endpoints across 8 functional banking domains:
1. Health check
2. Auth (login, refresh, 401 rejection on bad credentials)
3. Users (me, contact update)
4. Accounts (details, BOLA vulnerability verification, statements, beneficiaries)
5. Transactions (account transactions, receipts)
6. Payments (UPI transfer, NEFT transfer, scheduled payments for unused test)
7. Search (paginated merchants, unauthenticated IFSC lookup #1)
8. Export & Legacy V1 (unauthenticated Zombie bulk PII export #2, Shadow passbook dump #1)
9. Admin & Internal (Shadow admin dump #2, Shadow reset-limits #3, Shadow config env #4)
10. Cyberscan audit: Synthetic PII regex compliance and auth enforcement
"""

import re
import pytest
from httpx import AsyncClient, ASGITransport
import jwt

from person1_api_discovery.app.main import app
from person1_api_discovery.app.auth import SECRET_KEY, ALGORITHM

PAN_REGEX = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")
PHONE_REGEX = re.compile(r"^\+91-98765[0-9]{5}$")
UPI_REGEX = re.compile(r"^[a-zA-Z0-9._]+@okaxis$")
GOVT_ID_REGEX = re.compile(r"^\[GOVT-ID-XXXX-[0-9]{4}\]$")


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"


@pytest.mark.anyio
async def test_auth_login_and_refresh():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. POST /api/v2/auth/login
        login_resp = await client.post(
            "/api/v2/auth/login",
            json={"username": "user_1001", "password": "pass123"}
        )
        assert login_resp.status_code == 200
        data = login_resp.json()
        assert "access_token" in data
        token = data["access_token"]
        assert data["user"]["user_id"] == "user_1001"
        assert data["user"]["account_id"] == "1001"

        # Verify decoded JWT structure
        claims = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert claims["sub"] == "user_1001"
        assert claims["account_id"] == "1001"
        assert "jti" in claims

        # Test invalid password rejection
        bad_resp = await client.post(
            "/api/v2/auth/login",
            json={"username": "user_1001", "password": "wrongpassword"}
        )
        assert bad_resp.status_code == 401

        # 2. POST /api/v2/auth/refresh
        refresh_resp = await client.post(
            "/api/v2/auth/refresh",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert refresh_resp.status_code == 200
        assert "access_token" in refresh_resp.json()


@pytest.mark.anyio
async def test_user_routes():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login_resp = await client.post(
            "/api/v2/auth/login",
            json={"username": "user_1001", "password": "pass123"}
        )
        token = login_resp.json()["access_token"]
        auth_h = {"Authorization": f"Bearer {token}"}

        # 3. GET /api/v2/users/me
        me_resp = await client.get("/api/v2/users/me", headers=auth_h)
        assert me_resp.status_code == 200
        me_data = me_resp.json()
        assert me_data["user_id"] == "user_1001"
        assert PAN_REGEX.match(me_data["pan"])
        assert PHONE_REGEX.match(me_data["phone"])
        assert GOVT_ID_REGEX.match(me_data["govt_id_like"])

        # 4. PUT /api/v2/users/me/contact
        put_resp = await client.put(
            "/api/v2/users/me/contact",
            headers=auth_h,
            json={"phone": "+91-9876599999", "email": "aarav.updated@examplebank.in"}
        )
        assert put_resp.status_code == 200
        assert put_resp.json()["status"] == "success"


@pytest.mark.anyio
async def test_accounts_and_bola_vulnerability():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Login as user_1001 (account 1001)
        login_resp = await client.post(
            "/api/v2/auth/login",
            json={"username": "user_1001", "password": "pass123"}
        )
        token = login_resp.json()["access_token"]
        auth_h = {"Authorization": f"Bearer {token}"}

        # 5. GET /api/v2/accounts/1001 (Own account)
        own_resp = await client.get("/api/v2/accounts/1001", headers=auth_h)
        assert own_resp.status_code == 200
        assert own_resp.json()["account_id"] == "1001"

        # BOLA EXPLOIT: user_1001 requests account 1002
        victim_resp = await client.get("/api/v2/accounts/1002", headers=auth_h)
        assert victim_resp.status_code == 200
        victim_data = victim_resp.json()
        assert victim_data["account_id"] == "1002"
        assert victim_data["account_holder"] == "Priya Patel"
        assert PAN_REGEX.match(victim_data["pan"])
        assert GOVT_ID_REGEX.match(victim_data["govt_id_like"])

        # 6. GET /api/v2/accounts/{account_id}/statements (BOLA vulnerable)
        stmt_resp = await client.get("/api/v2/accounts/1002/statements", headers=auth_h)
        assert stmt_resp.status_code == 200
        assert stmt_resp.json()["account_id"] == "1002"

        # 7. POST /api/v2/accounts/beneficiaries
        ben_resp = await client.post(
            "/api/v2/accounts/beneficiaries",
            headers=auth_h,
            json={"name": "Neha Gupta", "account_number": "ACCN-IN-1006", "ifsc": "SBIN0000456"}
        )
        assert ben_resp.status_code == 200
        assert ben_resp.json()["status"] == "success"


@pytest.mark.anyio
async def test_transactions_and_receipts():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login_resp = await client.post(
            "/api/v2/auth/login",
            json={"username": "user_1001", "password": "pass123"}
        )
        token = login_resp.json()["access_token"]
        auth_h = {"Authorization": f"Bearer {token}"}

        # 8. GET /api/v2/accounts/1001/transactions
        txns_resp = await client.get("/api/v2/accounts/1001/transactions", headers=auth_h)
        assert txns_resp.status_code == 200
        txns = txns_resp.json()
        assert len(txns) >= 1

        # 9. GET /api/v2/transactions/{txn_id}/receipt
        txn_id = txns[0]["txn_id"]
        rcp_resp = await client.get(f"/api/v2/transactions/{txn_id}/receipt", headers=auth_h)
        assert rcp_resp.status_code == 200
        assert rcp_resp.json()["txn_id"] == txn_id


@pytest.mark.anyio
async def test_payments():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login_resp = await client.post(
            "/api/v2/auth/login",
            json={"username": "user_1001", "password": "pass123"}
        )
        token = login_resp.json()["access_token"]
        auth_h = {"Authorization": f"Bearer {token}"}

        # 10. POST /api/v2/payments/upi-transfer
        upi_resp = await client.post(
            "/api/v2/payments/upi-transfer",
            headers=auth_h,
            json={"payee_vpa": "sharmakiran@okhdfcbank", "amount": 250.00, "remarks": "Groceries"}
        )
        assert upi_resp.status_code == 200
        assert upi_resp.json()["status"] == "SUCCESS"

        # 11. POST /api/v2/payments/neft
        neft_resp = await client.post(
            "/api/v2/payments/neft",
            headers=auth_h,
            json={
                "beneficiary_account": "ACCN-IN-1002",
                "beneficiary_ifsc": "HDFC0001234",
                "beneficiary_name": "Priya Patel",
                "amount": 5000.00
            }
        )
        assert neft_resp.status_code == 200
        assert neft_resp.json()["status"] == "PENDING_BATCH_SETTLEMENT"

        # 12. GET /api/v2/payments/scheduled (Unused target endpoint)
        sched_resp = await client.get("/api/v2/payments/scheduled", headers=auth_h)
        assert sched_resp.status_code == 200
        assert "scheduled_payments" in sched_resp.json()


@pytest.mark.anyio
async def test_search():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login_resp = await client.post(
            "/api/v2/auth/login",
            json={"username": "user_1001", "password": "pass123"}
        )
        token = login_resp.json()["access_token"]
        auth_h = {"Authorization": f"Bearer {token}"}

        # 13. GET /api/v2/search/merchants (JWT Auth)
        mrc_resp = await client.get("/api/v2/search/merchants?page=1&limit=5", headers=auth_h)
        assert mrc_resp.status_code == 200
        mrc_data = mrc_resp.json()
        assert mrc_data["page"] == 1
        assert len(mrc_data["merchants"]) == 5

        # 14. GET /api/v2/search/ifsc/{ifsc_code} (NO AUTH #1)
        ifsc_resp = await client.get("/api/v2/search/ifsc/HDFC0001234")
        assert ifsc_resp.status_code == 200
        assert ifsc_resp.json()["bank_name"] == "HDFC Bank"


@pytest.mark.anyio
async def test_export_and_shadow_apis():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 15. GET /api/v1/users/export (ZOMBIE API - NO AUTH #2)
        zombie_resp = await client.get("/api/v1/users/export")
        assert zombie_resp.status_code == 200
        zombie_data = zombie_resp.json()
        assert zombie_data["total_records"] == 25
        first_user = zombie_data["users"][0]
        assert PAN_REGEX.match(first_user["pan"])
        assert PHONE_REGEX.match(first_user["phone"])
        assert UPI_REGEX.match(first_user["upi_vpa"])
        assert GOVT_ID_REGEX.match(first_user["govt_id_like"])

        # Authenticate for Shadow passbook dump
        login_resp = await client.post(
            "/api/v2/auth/login",
            json={"username": "user_1001", "password": "pass123"}
        )
        token = login_resp.json()["access_token"]
        auth_h = {"Authorization": f"Bearer {token}"}

        # 16. GET /api/v1/accounts/1001/passbook-dump (SHADOW API #1)
        pb_resp = await client.get("/api/v1/accounts/1001/passbook-dump", headers=auth_h)
        assert pb_resp.status_code == 200
        assert pb_resp.json()["account_id"] == "1001"
        assert PAN_REGEX.match(pb_resp.json()["pan"])

        # 17. GET /api/internal/admin/users-dump (SHADOW API #2)
        admin_dump = await client.get("/api/internal/admin/users-dump")
        assert admin_dump.status_code == 200
        assert admin_dump.json()["status"] == "internal_dump_complete"
        assert admin_dump.json()["total_accounts"] == 25

        # 18. POST /api/internal/debug/reset-limits (SHADOW API #3 - NO AUTH)
        reset_resp = await client.post("/api/internal/debug/reset-limits", json={"scope": "global"})
        assert reset_resp.status_code == 200
        assert reset_resp.json()["status"] == "acknowledged"

        # 19. GET /api/internal/config/env (SHADOW API #4 - NO AUTH)
        env_resp = await client.get("/api/internal/config/env")
        assert env_resp.status_code == 200
        assert env_resp.json()["environment"] == "fintech-core-prod-ap-south"


@pytest.mark.anyio
async def test_cyberscan_unauthorized_rejection():
    """
    Security scan: Ensure all protected endpoints reject unauthenticated requests with 401.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Protected endpoints that MUST return 401 when no token is passed
        endpoints = [
            ("GET", "/api/v2/users/me"),
            ("PUT", "/api/v2/users/me/contact"),
            ("GET", "/api/v2/accounts/1001"),
            ("GET", "/api/v2/accounts/1001/statements"),
            ("POST", "/api/v2/accounts/beneficiaries"),
            ("GET", "/api/v2/accounts/1001/transactions"),
            ("GET", "/api/v2/transactions/TXN100101/receipt"),
            ("POST", "/api/v2/payments/upi-transfer"),
            ("POST", "/api/v2/payments/neft"),
            ("GET", "/api/v2/payments/scheduled"),
            ("GET", "/api/v2/search/merchants"),
            ("GET", "/api/v1/accounts/1001/passbook-dump"),
        ]

        for method, path in endpoints:
            if method == "GET":
                resp = await client.get(path)
            elif method == "POST":
                resp = await client.post(path, json={})
            elif method == "PUT":
                resp = await client.put(path, json={})
            assert resp.status_code == 401, f"Expected 401 for unauthenticated {method} {path}, got {resp.status_code}"
