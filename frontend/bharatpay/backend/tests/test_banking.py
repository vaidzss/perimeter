import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import SessionLocal
from app.models.account import Account

client = TestClient(app)

@pytest.fixture
def auth_headers_user1():
    """Returns auth headers for Priya Sharma (account_id = 1)."""
    res = client.post("/api/v2/auth/login", json={"identifier": "priya.sharma@bharatpay.com", "password": "Password@123"})
    assert res.status_code == 200
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def auth_headers_user2():
    """Returns auth headers for Rohit Verma (account_id = 2)."""
    res = client.post("/api/v2/auth/login", json={"identifier": "rohit.verma@bharatpay.com", "password": "Password@123"})
    assert res.status_code == 200
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_statement_authorized_success(auth_headers_user1):
    """Test 1: User 1 can view their own account statement."""
    res = client.get("/api/v2/accounts/1/statement", headers=auth_headers_user1)
    assert res.status_code == 200
    data = res.json()
    assert data["account_id"] == 1
    assert data["vpa"] == "priya.sharma@bharatpay"
    assert data["masked_pan"] == "ABCDE****F"
    assert isinstance(data["balance_paise"], int)
    assert len(data["transactions"]) > 0

    # Guardrail check: No unmasked PII
    assert "ABCDE1234F" not in res.text
    assert "999988881001" not in res.text

def test_statement_unauthorized_bola_rejected(auth_headers_user1):
    """Test 2: User 1 attempting to view User 2's account (id=2) returns 403 Forbidden."""
    res = client.get("/api/v2/accounts/2/statement", headers=auth_headers_user1)
    assert res.status_code == 403
    assert "Forbidden" in res.json()["detail"]

def test_merchant_directory_pagination():
    """Test 3: Merchant directory paginates correctly with total >= 200."""
    res = client.get("/api/v2/upi/merchants?page=1&limit=10")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 200
    assert len(data["items"]) == 10
    assert data["page"] == 1

    # Page 2 has different merchants
    res_p2 = client.get("/api/v2/upi/merchants?page=2&limit=10")
    assert res_p2.status_code == 200
    data_p2 = res_p2.json()
    assert data_p2["total"] == data["total"]
    assert data_p2["items"][0]["id"] != data["items"][0]["id"]

    # Search filter
    res_search = client.get("/api/v2/upi/merchants?search=Swiggy")
    assert res_search.status_code == 200
    assert len(res_search.json()["items"]) > 0

def test_upi_transfer_success_and_idempotency(auth_headers_user1):
    """Test 4: Normal transfer succeeds and repeated idempotency key prevents double deduction."""
    db = SessionLocal()
    acc1 = db.query(Account).filter(Account.id == 1).first()
    initial_balance = acc1.balance_paise
    db.close()

    import uuid
    test_idem_key = f"idem-key-{uuid.uuid4().hex[:8]}"
    payload = {
        "from_vpa": "priya.sharma@bharatpay",
        "to_vpa": "swiggy@bharatpay",
        "amount_paise": 25000,  # ₹250.00
        "note": "Lunch order",
        "idempotency_key": test_idem_key
    }

    # First call: Transfer should succeed
    res1 = client.post("/api/v2/payments/upi-transfer", json=payload, headers=auth_headers_user1)
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["status"] == "SUCCESS"
    assert data1["idempotent_replay"] is False
    assert data1["remaining_balance_paise"] == initial_balance - 25000

    # Second call with same idempotency key: Should return cached receipt without deducting again
    res2 = client.post("/api/v2/payments/upi-transfer", json=payload, headers=auth_headers_user1)
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["txn_reference"] == data1["txn_reference"]
    assert data2["idempotent_replay"] is True

    # Verify balance in DB was only deducted once
    db = SessionLocal()
    acc1_after = db.query(Account).filter(Account.id == 1).first()
    assert acc1_after.balance_paise == initial_balance - 25000
    db.close()

def test_upi_transfer_enforces_daily_limit(auth_headers_user2):
    """Test 5: Transfer exceeding daily limit is rejected with 400 Bad Request."""
    # Rohit (user 2) has balance ₹1,25,000 and daily limit ₹1,00,000
    payload = {
        "from_vpa": "rohit.verma@bharatpay",
        "to_vpa": "priya.sharma@bharatpay",
        "amount_paise": 11000000,  # ₹1,10,000 exceeds ₹1,00,000 daily limit, but is within balance
        "note": "Exceeding daily limit"
    }
    res = client.post("/api/v2/payments/upi-transfer", json=payload, headers=auth_headers_user2)
    assert res.status_code == 400
    assert "Daily transfer limit exceeded" in res.json()["detail"]
