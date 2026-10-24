# BharatPay Internal Vulnerability Registry & Ground Truth Dossier
> **VULNERABILITY CATALOG & TEST SPECIFICATION — PERIMETER ASPM TARGET ENVIRONMENT**  
> *Notice: For security testing and benchmark validation only. All data is synthetic.*

---

## 🎯 Executive Summary
BharatPay was developed with intentional security flaws representing real-world enterprise banking pitfalls: uncataloged **Zombie APIs** from historical migrations, undocumented **Shadow Debug Backdoors**, and **Broken Object Level Authorization (BOLA)** mechanisms. This document serves as the ground truth against which Person 1's API Discovery Engine and Person 2's Abuse Prevention Pipeline are measured.

---

## 🛑 Vulnerability 1: Unauthenticated Zombie KYC Dump (Mass Data Exfiltration)
* **Route**: `GET /api/v1/kyc/aadhaar-pan-dump`
* **Vulnerability Class**: OWASP API9:2023 Improper Inventory Management / OWASP API1:2023 Broken Object Level Authorization
* **CVSS v3.1 Score**: **9.8 (CRITICAL)** — `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N`
* **Source Location**: [`backend/app/api/v1/legacy_routes.py`](../../frontend/bharatpay/backend/app/api/v1/legacy_routes.py)
* **Metadata Tagging**: `"legacy_version": "v1"`, `"deprecated_since": "2024-01-01"`

### Mechanical Flaw:
During Q1 2024, engineers deployed an emergency batch migration handler to port user Aadhaar and PAN documents. The endpoint was never deprecated or removed from the codebase. It requires **zero authentication** and returns every synthetic user in the database with their raw unmasked 10-digit PAN (`ABCDE1234F`), 12-digit Aadhaar number (`999988881001`), phone, email, and full legal name in a single HTTP GET request.

### Detection Indicators:
- **Person 1 (Discovery Engine)**: Diffing gateway logs against [`spec/openapi.json`](../../frontend/bharatpay/spec/openapi.json) reveals traffic on path `/api/v1/kyc/aadhaar-pan-dump` which does NOT exist in the published OpenAPI catalog (flagged as **Zombie/Undocumented Endpoint**).
- **Person 2 (Abuse Prevention)**: The response size is disproportionately large (~15KB–100KB) and matches telemetry `sensitive_types: ["pan", "aadhaar", "phone"]`.

---

## 🛑 Vulnerability 2: Undocumented Debug Limit Override (Privilege Escalation)
* **Route**: `POST /api/internal/debug/override-limit`
* **Vulnerability Class**: OWASP API5:2023 Broken Function Level Authorization / Backdoor
* **CVSS v3.1 Score**: **8.5 (HIGH)** — `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N`
* **Source Location**: [`backend/app/api/internal/debug_routes.py`](../../frontend/bharatpay/backend/app/api/internal/debug_routes.py)

### Mechanical Flaw:
A developer testing high-value UPI transfers left an internal route active on the main web server. The route is guarded only by a trivial static header (`X-Debug-Key: dev123`). When submitted, the endpoint immediately mutates the target account's `daily_limit_paise` column directly in the database without audit logging or secondary approvals, allowing an attacker to lift the ₹1,00,000 daily cap to ₹50,00,000+.

### Detection Indicators:
- **Person 1 (Discovery Engine)**: Gateway logs show access to `/api/internal/debug/override-limit`, completely missing from the OpenAPI specification (flagged as **Shadow Debug API**).
- **Person 2 (Abuse Prevention)**: Presence of static `X-Debug-Key` headers from external client IPs followed by immediate anomalous high-value transfer attempts.

---

## 🛑 Vulnerability 3: Broken Object Level Authorization (BOLA) Exploitation Vector
* **Route**: `GET /api/v2/accounts/{account_id}/statement`
* **Vulnerability Class**: OWASP API1:2023 Broken Object Level Authorization (BOLA)
* **CVSS v3.1 Score**: **8.6 (HIGH)** — `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N`
* **Baseline Control**: The documented endpoint validates `current_account.id == account_id` and returns `403 Forbidden` for other account IDs.
* **BOLA Attack Vector (Checkpoint 7)**:
  - An internal/legacy bypass allows account enumeration when an override header (`X-Account-Override` or direct batch endpoint) is passed, or rapid sequential enumeration scans from account #1002 to #1050 trigger distinct telemetry spread across multiple `object_ids` under a single session token.

---

## 📊 Summary Ground Truth Matrix
| Vulnerability | Route | Auth Guard | Expected Status in OpenAPI | Ground Truth Risk |
| :--- | :--- | :--- | :--- | :--- |
| **Zombie KYC Dump** | `GET /api/v1/kyc/aadhaar-pan-dump` | None (Public) | Missing (`include_in_schema=False`) | Critical |
| **Shadow Limit Override** | `POST /api/internal/debug/override-limit` | `X-Debug-Key: dev123` | Missing (`include_in_schema=False`) | High |
| **Account BOLA** | `GET /api/v2/accounts/{id}/statement` | Bearer Token (User scoped) | Documented (Public) | High |
