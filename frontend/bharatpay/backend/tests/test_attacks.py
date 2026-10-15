import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import SessionLocal
from app.models.account import Account
from app.models.request_log import RequestLog

client = TestClient(app)

@pytest.fixture
def auth_session():
    res = client.post("/api/v2/auth/login", json={"identifier": "priya.sharma@bharatpay.com", "password": "Password@123"})
    assert res.status_code == 200
    data = res.json()
    return data["access_token"], data["jti"], data["user_id"]

def test_attack_1_bola_enumeration_telemetry(auth_session):
    """Test Attack 1: BOLA enumeration sweep across accounts #1002-#1010 logs object_ids and 403 status."""
    token, jti, user_id = auth_session

    probed_ids = [1002, 1003, 1004, 1005]
    for acc_id in probed_ids:
        res = client.get(f"/api/v2/accounts/{acc_id}/statement", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 403

    # Check telemetry
    db = SessionLocal()
    for acc_id in probed_ids:
        log_entry = db.query(RequestLog).filter(
            RequestLog.raw_path == f"/api/v2/accounts/{acc_id}/statement",
            RequestLog.token_id == jti
        ).first()
        assert log_entry is not None
        assert str(acc_id) in log_entry.object_ids
        assert log_entry.status_code == 403
    db.close()

def test_attack_2_scraper_telemetry():
    """Test Attack 2: Directory & KYC scraper generates rapid queries and flags sensitive PII types."""
    # Hit zombie dump and merchant directory
    res_dump = client.get("/api/v1/kyc/aadhaar-pan-dump")
    assert res_dump.status_code == 200
    res_merch = client.get("/api/v2/upi/merchants?page=1&limit=25")
    assert res_merch.status_code == 200

    db = SessionLocal()
    last_dump_log = db.query(RequestLog).filter(RequestLog.raw_path == "/api/v1/kyc/aadhaar-pan-dump").order_by(RequestLog.id.desc()).first()
    assert last_dump_log is not None
    assert "pan" in last_dump_log.sensitive_types
    assert "aadhaar" in last_dump_log.sensitive_types
    db.close()

def test_attack_3_token_replay_telemetry(auth_session):
    """Test Attack 3: Token replay with spoofed IP and non-browser User-Agent matches session jti."""
    token, jti, user_id = auth_session

    spoofed_ip = "185.220.101.5"
    spoofed_ua = "python-requests/2.31.0"

    res = client.post(
        "/api/v2/payments/upi-transfer",
        json={
            "from_vpa": "priya.sharma@bharatpay",
            "to_vpa": "swiggy@bharatpay",
            "amount_paise": 1000,
            "note": "Replay Test",
            "idempotency_key": "test_replay_token_call_01"
        },
        headers={
            "Authorization": f"Bearer {token}",
            "X-Forwarded-For": spoofed_ip,
            "User-Agent": spoofed_ua
        }
    )
    assert res.status_code in [200, 400]

    # Verify structured logging correlated the token_id with the spoofed client_ip and python UA
    db = SessionLocal()
    replay_log = db.query(RequestLog).filter(
        RequestLog.token_id == jti,
        RequestLog.client_ip == spoofed_ip
    ).first()
    assert replay_log is not None
    assert replay_log.user_agent == spoofed_ua
    assert replay_log.auth_type == "bearer"
    db.close()

def test_reset_demo_state():
    """Test Reset: /api/internal/demo/reset-state restores balances and limits."""
    # Mutate balance first
    db = SessionLocal()
    acc = db.query(Account).filter(Account.id == 1).first()
    acc.balance_paise = 100
    db.commit()
    db.close()

    # Call reset
    res = client.post("/api/internal/demo/reset-state")
    assert res.status_code == 200
    assert res.json()["status"] == "RESET_SUCCESSFUL"

    # Verify balance restored to seed default (48,50,000 paise = ₹48,500)
    db = SessionLocal()
    acc_restored = db.query(Account).filter(Account.id == 1).first()
    assert acc_restored.balance_paise == 4850000
    assert acc_restored.daily_limit_paise == 10000000
    db.close()
