import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import SessionLocal
from app.models.account import Account
from app.models.request_log import RequestLog

client = TestClient(app)

def test_zombie_kyc_dump_is_live_and_leaks_unmasked_pii():
    """Test 1: /api/v1/kyc/aadhaar-pan-dump works without auth and leaks unmasked PAN & Aadhaar."""
    res = client.get("/api/v1/kyc/aadhaar-pan-dump")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 3

    # Check for unmasked PII
    priya_record = next(item for item in data if item["user_code"] == "u_101")
    assert priya_record["pan_unmasked"] == "ABCDE1234F"
    assert priya_record["aadhaar_unmasked"] == "999988881001"
    assert priya_record["phone"] == "9876501001"

    # Verify structured logging flagged sensitive types
    db = SessionLocal()
    last_log = db.query(RequestLog).filter(RequestLog.raw_path == "/api/v1/kyc/aadhaar-pan-dump").order_by(RequestLog.id.desc()).first()
    assert last_log is not None
    assert "pan" in last_log.sensitive_types
    assert "aadhaar" in last_log.sensitive_types
    db.close()

def test_shadow_debug_override_limit_requires_key():
    """Test 2: /api/internal/debug/override-limit rejects unauthorized access without key."""
    payload = {"account_id": 1, "new_daily_limit_paise": 50000000}
    res = client.post("/api/internal/debug/override-limit", json=payload)
    assert res.status_code == 401
    assert "X-Debug-Key" in res.json()["detail"]

def test_shadow_debug_override_limit_succeeds_with_debug_key():
    """Test 3: /api/internal/debug/override-limit mutates database limit when valid debug key provided."""
    db = SessionLocal()
    acc = db.query(Account).filter(Account.id == 1).first()
    initial_limit = acc.daily_limit_paise
    db.close()

    new_limit = 50000000  # ₹5,00,000.00
    payload = {"account_id": 1, "new_daily_limit_paise": new_limit}
    res = client.post(
        "/api/internal/debug/override-limit",
        json=payload,
        headers={"X-Debug-Key": "dev123"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "OVERRIDDEN"
    assert data["new_daily_limit_paise"] == new_limit

    # Verify mutation in DB
    db = SessionLocal()
    acc_updated = db.query(Account).filter(Account.id == 1).first()
    assert acc_updated.daily_limit_paise == new_limit
    # Reset limit back
    acc_updated.daily_limit_paise = initial_limit
    db.commit()
    db.close()

def test_shadow_endpoints_excluded_from_fastapi_schema():
    """Test 4: include_in_schema=False guarantees routes are not exposed in FastAPI OpenAPI schema."""
    openapi_schema = app.openapi()
    all_documented_paths = openapi_schema.get("paths", {}).keys()

    assert "/api/v1/kyc/aadhaar-pan-dump" not in all_documented_paths
    assert "/api/internal/debug/override-limit" not in all_documented_paths
