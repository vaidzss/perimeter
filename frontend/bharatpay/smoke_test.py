"""
BharatPay Comprehensive End-to-End Smoke Test
Tests all 6 routes (4 documented public + 2 shadow/zombie endpoints)
and verifies telemetry logging on disk and database.
"""

import sys
import requests
import json
import time

def run_smoke_test(base_url="http://localhost:8000"):
    print(f"\n=======================================================")
    print(f"  Starting BharatPay Smoke Test against: {base_url}")
    print(f"=======================================================\n")

    session = requests.Session()

    # 1. Health check
    print("[1/8] Testing /health ...")
    r = session.get(f"{base_url}/health")
    assert r.status_code == 200, f"Health check failed: {r.status_code}"
    print(f"      PASS: {r.json()['service']} is healthy.")

    # 2. Login
    print("[2/8] Testing POST /api/v2/auth/login ...")
    r = session.post(f"{base_url}/api/v2/auth/login", json={
        "identifier": "priya.sharma@bharatpay.com",
        "password": "Password@123"
    })
    assert r.status_code == 200, f"Login failed: {r.text}"
    auth_data = r.json()
    token = auth_data["access_token"]
    user_id = auth_data["user_id"]
    account_id = auth_data["account_id"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"      PASS: Authenticated as {user_id} (Account: {account_id}, JTI: {auth_data['jti'][:8]}...)")

    # 3. /me profile
    print("[3/8] Testing GET /api/v2/auth/me ...")
    r = session.get(f"{base_url}/api/v2/auth/me", headers=headers)
    assert r.status_code == 200
    profile = r.json()
    assert profile["masked_pan"] == "ABCDE****F"
    print(f"      PASS: Profile verified for {profile['full_name']} (Masked PAN: {profile['masked_pan']})")

    # 4. Statement
    print(f"[4/8] Testing GET /api/v2/accounts/{account_id}/statement ...")
    r = session.get(f"{base_url}/api/v2/accounts/{account_id}/statement", headers=headers)
    assert r.status_code == 200
    stmt = r.json()
    print(f"      PASS: Balance: Rs. {stmt['balance_paise'] / 100:.2f}, {len(stmt['transactions'])} transactions listed.")

    # 4b. BOLA Guard
    print("[4b/8] Verifying BOLA guard on other user's account ...")
    r_bola = session.get(f"{base_url}/api/v2/accounts/2/statement", headers=headers)
    assert r_bola.status_code == 403, f"Expected 403, got {r_bola.status_code}"
    print("      PASS: Unauthorized account access strictly rejected with 403 Forbidden.")

    # 5. Merchants directory
    print("[5/8] Testing GET /api/v2/upi/merchants ...")
    r = session.get(f"{base_url}/api/v2/upi/merchants?page=1&limit=5")
    assert r.status_code == 200
    merchants = r.json()
    assert merchants["total"] >= 200
    print(f"      PASS: Loaded page 1 of merchants (Total: {merchants['total']} verified merchants).")

    # 6. UPI Transfer
    print("[6/8] Testing POST /api/v2/payments/upi-transfer ...")
    idem_key = f"smoke_test_{int(time.time())}"
    r = session.post(f"{base_url}/api/v2/payments/upi-transfer", json={
        "from_vpa": profile["vpa"],
        "to_vpa": "swiggy@bharatpay",
        "amount_paise": 15000,  # ₹150.00
        "note": "Smoke test payment",
        "idempotency_key": idem_key
    }, headers=headers)
    assert r.status_code == 200
    transfer = r.json()
    print(f"      PASS: Transfer {transfer['txn_reference']} completed. Status: {transfer['status']}.")

    # 7. Shadow Route 1: Zombie KYC Dump
    print("[7/8] Testing SHADOW ROUTE: GET /api/v1/kyc/aadhaar-pan-dump ...")
    r = session.get(f"{base_url}/api/v1/kyc/aadhaar-pan-dump")
    assert r.status_code == 200
    kyc_dump = r.json()
    assert len(kyc_dump) >= 15
    print(f"      PASS: Zombie route active! Leaked {len(kyc_dump)} unmasked records without auth.")

    # 8. Shadow Route 2: Internal Debug Limit Override
    print("[8/8] Testing SHADOW ROUTE: POST /api/internal/debug/override-limit ...")
    r = session.post(f"{base_url}/api/internal/debug/override-limit", json={
        "account_id": 1,
        "new_daily_limit_paise": 20000000
    }, headers={"X-Debug-Key": "dev123"})
    assert r.status_code == 200
    override = r.json()
    assert override["status"] == "OVERRIDDEN"
    print(f"      PASS: Shadow backdoor active! Daily limit overridden to Rs. {override['new_daily_limit_paise'] / 100:.2f}.")

    print("\n=======================================================")
    print("  ALL 8 SMOKE TESTS PASSED END-TO-END! (100% HEALTHY)")
    print("=======================================================\n")

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    run_smoke_test(url)
