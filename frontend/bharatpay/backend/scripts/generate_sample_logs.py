import sys
import os
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def generate_traffic():
    print("[Traffic Generator] Starting generation of 200+ diverse log lines...")
    session = requests.Session()

    # 1. Benign Health Checks (20 reqs)
    print("  -> Generating benign health checks...")
    for _ in range(20):
        session.get(f"{BASE_URL}/health", headers={"User-Agent": "HealthCheck/1.0"})

    # 2. Benign User Logins & Profiles (30 reqs)
    print("  -> Generating user logins and profile lookups...")
    user_credentials = [
        ("priya.sharma@bharatpay.com", "Password@123"),
        ("rohit.verma@bharatpay.com", "Password@123"),
        ("ananya.iyer@bharatpay.com", "Password@123"),
        ("vikram.rao@bharatpay.com", "Password@123"),
        ("sneha.patel@bharatpay.com", "Password@123"),
    ]

    active_tokens = []
    for email, pwd in user_credentials:
        r = session.post(f"{BASE_URL}/api/v2/auth/login", json={"identifier": email, "password": pwd})
        if r.status_code == 200:
            data = r.json()
            token = data["access_token"]
            active_tokens.append((data["account_id"], token))
            # Fetch profile
            session.get(f"{BASE_URL}/api/v2/auth/me", headers={"Authorization": f"Bearer {token}", "User-Agent": "Mozilla/5.0 Chrome/120.0"})

    # 3. Legitimate Account Statements & Merchants (40 reqs)
    print("  -> Generating authorized account statements and merchant searches...")
    for acc_id, token in active_tokens:
        session.get(f"{BASE_URL}/api/v2/accounts/{acc_id}/statement", headers={"Authorization": f"Bearer {token}"})
        for p in range(1, 4):
            session.get(f"{BASE_URL}/api/v2/upi/merchants?page={p}&limit=10")

    # 4. Attack Scenario 1: BOLA Enumeration Scan (48 reqs)
    print("  -> Generating Attack 1: BOLA Account Enumeration (#1002-#1050)...")
    target_token = active_tokens[0][1]
    for target_id in range(1002, 1050):
        session.get(
            f"{BASE_URL}/api/v2/accounts/{target_id}/statement",
            headers={"Authorization": f"Bearer {target_token}", "User-Agent": "BOLA-Probe/1.0"}
        )

    # 5. Attack Scenario 2: High-Rate Directory & Zombie Scraping (50 reqs)
    print("  -> Generating Attack 2: Directory and Zombie KYC Dump scraping...")
    for p in range(1, 20):
        session.get(f"{BASE_URL}/api/v2/upi/merchants?page={p}&limit=20", headers={"User-Agent": "Scrapy/2.11"})
    for _ in range(30):
        session.get(f"{BASE_URL}/api/v1/kyc/aadhaar-pan-dump", headers={"User-Agent": "Fast-Scraper/1.0"})

    # 6. Attack Scenario 3: Botnet Token Replay (25 reqs)
    print("  -> Generating Attack 3: Botnet Token Replay from foreign IP/UA...")
    for i in range(25):
        session.post(
            f"{BASE_URL}/api/v2/payments/upi-transfer",
            json={
                "from_vpa": "priya.sharma@bharatpay",
                "to_vpa": "swiggy@bharatpay",
                "amount_paise": 1000 + i,
                "note": f"Botnet Replay Exploit #{i}",
                "idempotency_key": f"replay_key_{time.time()}_{i}"
            },
            headers={
                "Authorization": f"Bearer {target_token}",
                "X-Forwarded-For": "185.220.101.5",
                "User-Agent": "python-requests/2.31.0"
            }
        )

    # 7. Read generated logs and write exactly 200+ lines to /spec/sample_logs.jsonl
    log_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../logs/requests.jsonl"))
    if not os.path.exists(log_src):
        log_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "../logs/bharatpay_requests.jsonl"))

    with open(log_src, "r", encoding="utf-8") as f:
        all_lines = [l.strip() for l in f.readlines() if l.strip()]

    print(f"[Traffic Generator] Total records captured in {log_src}: {len(all_lines)}")

    out_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../spec/sample_logs.jsonl"))
    with open(out_file, "w", encoding="utf-8") as f:
        for line in all_lines[-220:]:
            f.write(line + "\n")

    print(f"[Traffic Generator] Successfully exported {len(all_lines[-220:])} records to {out_file}")

if __name__ == "__main__":
    generate_traffic()
