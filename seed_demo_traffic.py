"""
Demo Traffic Seeder for SentinelAPI ASPM Platform.
Sends ~35 realistic requests to populate:
1. Documented routes (Auth, Users, Accounts, Transactions, Payments, Search)
2. BOLA Exploitation sequence (User 1001 reading accounts 1004, 1005, 1008)
3. High-speed scraping on Merchant search
4. Zombie API bulk PII leaks (/api/v1/users/export)
5. 4 Shadow APIs (/passbook-dump, /admin/users-dump, /debug/reset-limits, /config/env)
6. Leaves the 2 Unused endpoints untouched.
"""

import time
import httpx

BASE_URL = "http://127.0.0.1:8000"


def seed_traffic():
    print(f"\n[Seeder] Connecting to SentinelAPI at {BASE_URL}...")
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        # Check health
        try:
            r = client.get("/health")
            print(f"[Seeder] Backend is online: {r.status_code}")
        except Exception as e:
            print(f"[Seeder] Could not connect to backend at {BASE_URL}: {e}")
            return False

        # 1. Authenticate users & obtain JWT tokens
        tokens = {}
        for uid in ["user_1001", "user_1002", "user_1003", "user_1004"]:
            res = client.post(
                "/api/v2/auth/login",
                json={"username": uid, "password": "pass123"},
                headers={"X-Ground-Truth": "benign"}
            )
            if res.status_code == 200:
                tokens[uid] = res.json()["access_token"]
        print(f"[Seeder] Authenticated {len(tokens)} test users.")

        token_1001 = tokens.get("user_1001")
        auth_1001 = {"Authorization": f"Bearer {token_1001}"}

        # 2. Legitimate Documented Traffic
        print("[Seeder] Sending legitimate Documented API requests...")
        client.get("/api/v2/users/me", headers=auth_1001)
        client.put("/api/v2/users/me/contact", headers=auth_1001, json={"phone": "+91-9876501001"})
        client.get("/api/v2/accounts/1001", headers=auth_1001)
        client.get("/api/v2/accounts/1001/statements", headers=auth_1001)
        client.post(
            "/api/v2/accounts/beneficiaries",
            headers=auth_1001,
            json={"name": "Kavya Deshmukh", "account_number": "ACCN-IN-1010", "ifsc": "HDFC0001234"}
        )
        client.get("/api/v2/accounts/1001/transactions", headers=auth_1001)
        client.get("/api/v2/transactions/TXN100101/receipt", headers=auth_1001)
        client.post(
            "/api/v2/payments/upi-transfer",
            headers=auth_1001,
            json={"payee_vpa": "sharmakiran@okhdfcbank", "amount": 250.0}
        )
        client.post(
            "/api/v2/payments/neft",
            headers=auth_1001,
            json={"beneficiary_account": "ACCN-IN-1002", "beneficiary_ifsc": "HDFC0001234", "beneficiary_name": "Priya Patel", "amount": 2000.0}
        )
        client.get("/api/v2/search/ifsc/HDFC0001234")
        client.get("/api/v2/search/ifsc/SBIN0000456")

        # 3. Data Scraping Traffic Simulation
        print("[Seeder] Sending high-speed merchant directory scraping requests...")
        for page in [1, 2, 3]:
            client.get(
                f"/api/v2/search/merchants?page={page}&limit=5",
                headers={**auth_1001, "X-Ground-Truth": "attack_scraping"}
            )

        # 4. BOLA / IDOR Attack Simulation (User 1001 accesses victims 1004, 1005, 1008)
        print("[Seeder] Sending BOLA/IDOR manipulation probes...")
        for victim_id in ["1004", "1005", "1008"]:
            client.get(
                f"/api/v2/accounts/{victim_id}",
                headers={**auth_1001, "X-Ground-Truth": "attack_bola"}
            )
            client.get(
                f"/api/v2/accounts/{victim_id}/transactions",
                headers={**auth_1001, "X-Ground-Truth": "attack_bola"}
            )

        # 5. Zombie API Deprecated Bulk PII Export (Unauthenticated)
        print("[Seeder] Triggering Zombie API (/api/v1/users/export)...")
        client.get("/api/v1/users/export", headers={"X-Ground-Truth": "attack_zombie_pii"})

        # 6. Shadow APIs Probing (4 Undocumented routes)
        print("[Seeder] Triggering 4 live Shadow APIs...")
        client.get(
            "/api/v1/accounts/1004/passbook-dump",
            headers={**auth_1001, "X-Ground-Truth": "attack_shadow"}
        )
        client.get(
            "/api/v1/accounts/1005/passbook-dump",
            headers={**auth_1001, "X-Ground-Truth": "attack_shadow"}
        )
        client.get("/api/internal/admin/users-dump", headers={"X-Ground-Truth": "attack_shadow"})
        client.post(
            "/api/internal/debug/reset-limits",
            json={"scope": "cluster-worker-01"},
            headers={"X-Ground-Truth": "attack_shadow"}
        )
        client.get("/api/internal/config/env", headers={"X-Ground-Truth": "attack_shadow"})

        # 7. Verify Inventory State via REST
        diff = client.get("/api/inventory/diff-summary").json()
        print("\n[Seeder] Live ASPM Posture Summary:")
        print(f"  * Total Endpoints Cataloged: {diff.get('total_endpoints')}")
        print(f"  * Documented (Active):      {diff.get('documented_count')}")
        print(f"  * Shadow APIs Discovered:   {diff.get('shadow_count')}")
        print(f"  * Zombie APIs Detected:     {diff.get('zombie_count')}")
        print(f"  * Unused Documented APIs:   {diff.get('unused_count')}")
        print(f"  * PII Exposing Routes:      {diff.get('pii_exposing_count')}")
        print(f"  * Spec Drift Detected:      {diff.get('spec_drift_detected')}")
        print("[Seeder] Seed traffic successfully delivered!\n")
        return True


if __name__ == "__main__":
    seed_traffic()
