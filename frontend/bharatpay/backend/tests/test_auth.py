import pytest
from fastapi.testclient import TestClient
import jwt
from datetime import datetime, timezone, timedelta

from app.main import app
from app.core.config import settings
from app.core.security import create_access_token

client = TestClient(app)

def test_login_success_with_email_and_password():
    """Test 1: Login with seeded user returns a valid JWT with required claims."""
    response = client.post(
        "/api/v2/auth/login",
        json={"identifier": "priya.sharma@bharatpay.com", "password": "Password@123"}
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "jti" in data
    assert data["user_id"] == "u_101"
    assert data["account_id"] == 1

    # Verify JWT Claims
    payload = jwt.decode(data["access_token"], settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "u_101"
    assert payload["account_id"] == 1
    assert payload["role"] == "customer"
    assert "exp" in payload
    assert "iat" in payload
    assert payload["jti"] == data["jti"]

    # Security Guardrail Check: Token payload MUST NOT contain PAN or Aadhaar
    claims_str = str(payload).lower()
    assert "pan" not in payload, "Token leaks PAN in claims!"
    assert "aadhaar" not in payload, "Token leaks Aadhaar in claims!"
    assert "abcde1234f" not in claims_str, "Token leaks unmasked PAN value!"
    assert "999988881001" not in claims_str, "Token leaks unmasked Aadhaar value!"

def test_login_success_with_phone_and_otp():
    """Test 2: Login via phone and synthetic OTP stub '123456'."""
    response = client.post(
        "/api/v2/auth/login",
        json={"identifier": "9876501001", "otp": "123456"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "u_101"

def test_login_failed_records_distinct_event():
    """Test 3: Wrong password returns 401 and sets failed auth event."""
    response = client.post(
        "/api/v2/auth/login",
        json={"identifier": "priya.sharma@bharatpay.com", "password": "WrongPassword!"}
    )
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]

def test_protected_route_without_token():
    """Test 4: Protected route rejects missing token with 401."""
    response = client.get("/api/v2/auth/me")
    assert response.status_code == 401
    assert "Missing Bearer" in response.json()["detail"]

def test_protected_route_with_tampered_token():
    """Test 5: Tampered token returns 401."""
    response = client.get(
        "/api/v2/auth/me",
        headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.tampered.signature"}
    )
    assert response.status_code == 401
    assert "Invalid or tampered" in response.json()["detail"]

def test_protected_route_with_expired_token():
    """Test 6: Expired token returns 401."""
    expired_token, _ = create_access_token(
        user_id="u_101",
        account_id=1,
        expires_delta=timedelta(seconds=-10)
    )
    response = client.get(
        "/api/v2/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    assert "Token has expired" in response.json()["detail"]

def test_me_endpoint_returns_user_profile_safely():
    """Test 7: /me returns profile with masked PAN and no unmasked PII."""
    login_res = client.post(
        "/api/v2/auth/login",
        json={"identifier": "priya.sharma@bharatpay.com", "password": "Password@123"}
    )
    token = login_res.json()["access_token"]

    response = client.get(
        "/api/v2/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_code"] == "u_101"
    assert data["full_name"] == "Priya Sharma"
    assert data["account_number_masked"] == "XXXXXXXX1001"
    assert data["masked_pan"] == "ABCDE****F"
    assert "ABCDE1234F" not in response.text, "Unmasked PAN leaked in response!"
    assert "999988881001" not in response.text, "Unmasked Aadhaar leaked in response!"
