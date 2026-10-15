"""
Perimeter Active Defense Verification Test
Demonstrates the before-and-after proof of how Perimeter saves BharatPay:
1. PII Redaction in-flight (Aadhaar & PAN never exposed in plaintext)
2. Virtual Patching / Route Quarantine (Zombie & Shadow APIs blocked with 403)
3. IP Blacklisting (Tor botnet IP blocked with 403)
4. Legitimate Traffic Pass-through (Priya's normal banking operations remain 100% uninterrupted)
"""

import sys
import requests
import json

BASE_URL = "http://localhost:8000"

def test_perimeter_saves_bharatpay():
    print("\n" + "=" * 70)
    print("  [SHIELD] VERIFYING PERIMETER ACTIVE DEFENSE: SAVING BHARATPAY [SHIELD]")
    print("=" * 70 + "\n")

    session = requests.Session()

    # -------------------------------------------------------------------------
    # TEST 1: In-Flight PII Redaction
    # -------------------------------------------------------------------------
    print("[1/4] Testing In-Flight PII Redaction on Zombie KYC Dump...")
    # Unquarantine route first to test payload inspection
    session.post(f"{BASE_URL}/api/defense/unquarantine", json={"path": "/api/v1/kyc/aadhaar-pan-dump"})
    session.post(f"{BASE_URL}/api/defense/toggle-pii-masking", json={"enabled": True})

    res = session.get(f"{BASE_URL}/api/v1/kyc/aadhaar-pan-dump")
    assert res.status_code == 200
    data = res.json()
    first_user = data[0]
    
    # Assert raw Aadhaar/PAN are masked
    assert "****" in first_user["pan_unmasked"], f"PAN not masked: {first_user['pan_unmasked']}"
    assert "XXXX" in first_user["aadhaar_unmasked"], f"Aadhaar not masked: {first_user['aadhaar_unmasked']}"
    print(f"      PASS: Raw Aadhaar {first_user['aadhaar_unmasked']} and PAN {first_user['pan_unmasked']} redacted in-flight!")

    # -------------------------------------------------------------------------
    # TEST 2: Route Quarantine (Virtual Patching)
    # -------------------------------------------------------------------------
    print("[2/4] Deploying Route Quarantine Virtual Patch on Zombie & Shadow APIs...")
    # Quarantine zombie dump and shadow debug backdoor
    q1 = session.post(f"{BASE_URL}/api/defense/quarantine", json={
        "path": "/api/v1/kyc/aadhaar-pan-dump",
        "reason": "Virtual patch: prevent bulk KYC exfiltration"
    })
    assert q1.status_code == 200

    q2 = session.post(f"{BASE_URL}/api/defense/quarantine", json={
        "path": "/api/internal/debug/override-limit",
        "reason": "Virtual patch: block privilege escalation backdoor"
    })
    assert q2.status_code == 200

    # Test attacking quarantined zombie route
    zombie_attack = session.get(f"{BASE_URL}/api/v1/kyc/aadhaar-pan-dump")
    assert zombie_attack.status_code == 403
    z_body = zombie_attack.json()
    assert z_body["error"] == "ROUTE_QUARANTINED_BY_PERIMETER"
    print(f"      PASS: Zombie KYC Dump blocked with 403 -> {z_body['reason']}")

    # Test attacking quarantined shadow backdoor
    shadow_attack = session.post(f"{BASE_URL}/api/internal/debug/override-limit", json={"account_id": 1, "new_daily_limit_paise": 99999999})
    assert shadow_attack.status_code == 403
    s_body = shadow_attack.json()
    assert s_body["error"] == "ROUTE_QUARANTINED_BY_PERIMETER"
    print(f"      PASS: Shadow Backdoor blocked with 403 -> {s_body['reason']}")

    # -------------------------------------------------------------------------
    # TEST 3: Tor Botnet IP Quarantine
    # -------------------------------------------------------------------------
    print("[3/4] Testing IP Blacklisting against Tor Botnet Replay...")
    tor_ip = "185.220.101.5"
    b_res = session.post(f"{BASE_URL}/api/defense/block-ip", json={
        "ip": tor_ip,
        "reason": "Tor exit node used in token replay attack"
    })
    assert b_res.status_code == 200

    # Attacker tries to send any request with Tor IP
    botnet_req = session.get(f"{BASE_URL}/api/v2/auth/me", headers={"X-Forwarded-For": tor_ip})
    assert botnet_req.status_code == 403
    b_body = botnet_req.json()
    assert b_body["error"] == "IP_QUARANTINED_BY_PERIMETER"
    print(f"      PASS: Tor Exit Node {tor_ip} dropped at perimeter with 403 -> {b_body['reason']}")

    # -------------------------------------------------------------------------
    # TEST 4: Legitimate Customer Experience Unaffected
    # -------------------------------------------------------------------------
    print("[4/4] Verifying Legitimate Customer Traffic (Priya Sharma) is 100% Uninterrupted...")
    clean_login = session.post(f"{BASE_URL}/api/v2/auth/login", json={
        "identifier": "priya.sharma@bharatpay.com",
        "password": "Password@123"
    })
    assert clean_login.status_code == 200
    token = clean_login.json()["access_token"]
    user_headers = {"Authorization": f"Bearer {token}"}

    # Clean profile fetch
    profile_res = session.get(f"{BASE_URL}/api/v2/auth/me", headers=user_headers)
    assert profile_res.status_code == 200
    print(f"      PASS: Priya Sharma profile loaded cleanly: {profile_res.json()['full_name']}")

    # Clean UPI merchant lookup
    merch_res = session.get(f"{BASE_URL}/api/v2/upi/merchants?page=1&limit=5")
    assert merch_res.status_code == 200
    print(f"      PASS: Merchant directory accessible ({merch_res.json()['total']} merchants)")

    print("\n" + "=" * 70)
    print("  [SUCCESS] ALL 4 ACTIVE DEFENSE CONTROLS VERIFIED END-TO-END! [SUCCESS]")
    print("  Perimeter successfully stopped all attack vectors without breaking legitimate users.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    test_perimeter_saves_bharatpay()
