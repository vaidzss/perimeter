import json
import os
import random
from datetime import datetime, timedelta

random.seed(42)

NOW = datetime(2026, 10, 13, 22, 30, 0)

# ==========================================
# 1. API INVENTORY (20 APIs)
# Must include: >=3 shadow, 1 zombie, 1 unmanaged, 1 unused_documented, documented
# Sensitive data types: PAN, Aadhaar, phone, email
# ==========================================
inventory = [
    # 1. Accounts Detail (Documented, BOLA target)
    {
        "api_id": "api-01",
        "method": "GET",
        "path_template": "/accounts/{id}",
        "auth_type": "jwt",
        "parameters": [
            {"name": "id", "in": "path", "type": "string", "required": True},
            {"name": "include_statement", "in": "query", "type": "boolean", "required": False}
        ],
        "sensitive_types": ["PAN", "Aadhaar", "phone", "email"],
        "status": "documented",
        "first_seen": "2026-08-15T08:00:00Z",
        "last_seen": "2026-10-13T22:29:45Z",
        "request_count": 84520,
        "exposure": "public",
        "risk_score": 92
    },
    # 2. Wire Transfers (Documented)
    {
        "api_id": "api-02",
        "method": "POST",
        "path_template": "/accounts/transfer",
        "auth_type": "oauth2",
        "parameters": [
            {"name": "source_acc", "in": "body", "type": "string", "required": True},
            {"name": "dest_acc", "in": "body", "type": "string", "required": True},
            {"name": "amount", "in": "body", "type": "number", "required": True}
        ],
        "sensitive_types": ["phone"],
        "status": "documented",
        "first_seen": "2026-08-15T08:00:00Z",
        "last_seen": "2026-10-13T22:28:10Z",
        "request_count": 31200,
        "exposure": "public",
        "risk_score": 78
    },
    # 3. User Login (Documented, Brute force target)
    {
        "api_id": "api-03",
        "method": "POST",
        "path_template": "/auth/login",
        "auth_type": "none",
        "parameters": [
            {"name": "username", "in": "body", "type": "string", "required": True},
            {"name": "password", "in": "body", "type": "string", "required": True}
        ],
        "sensitive_types": ["email"],
        "status": "documented",
        "first_seen": "2026-08-10T00:00:00Z",
        "last_seen": "2026-10-13T22:30:00Z",
        "request_count": 245000,
        "exposure": "public",
        "risk_score": 85
    },
    # 4. User Profile (Documented)
    {
        "api_id": "api-04",
        "method": "GET",
        "path_template": "/users/{id}/profile",
        "auth_type": "jwt",
        "parameters": [
            {"name": "id", "in": "path", "type": "string", "required": True}
        ],
        "sensitive_types": ["phone", "email", "PAN"],
        "status": "documented",
        "first_seen": "2026-08-15T08:00:00Z",
        "last_seen": "2026-10-13T22:29:12Z",
        "request_count": 112400,
        "exposure": "public",
        "risk_score": 76
    },
    # 5. User Profile Update (Documented)
    {
        "api_id": "api-05",
        "method": "PUT",
        "path_template": "/users/{id}/profile",
        "auth_type": "jwt",
        "parameters": [
            {"name": "id", "in": "path", "type": "string", "required": True},
            {"name": "phone", "in": "body", "type": "string", "required": False}
        ],
        "sensitive_types": ["phone", "email"],
        "status": "documented",
        "first_seen": "2026-08-15T08:00:00Z",
        "last_seen": "2026-10-13T22:25:30Z",
        "request_count": 18400,
        "exposure": "public",
        "risk_score": 64
    },
    # 6. SHADOW API 1: Internal Debug Tokens (Critical Shadow Route)
    {
        "api_id": "api-06",
        "method": "GET",
        "path_template": "/internal/debug/tokens",
        "auth_type": "none",
        "parameters": [
            {"name": "cluster", "in": "query", "type": "string", "required": False}
        ],
        "sensitive_types": ["email"],
        "status": "shadow",
        "first_seen": "2026-10-09T14:22:00Z",
        "last_seen": "2026-10-13T22:27:14Z",
        "request_count": 1420,
        "exposure": "public",
        "risk_score": 98
    },
    # 7. SHADOW API 2: Unregistered User Export
    {
        "api_id": "api-07",
        "method": "POST",
        "path_template": "/api/v2/test/export-users",
        "auth_type": "none",
        "parameters": [
            {"name": "format", "in": "query", "type": "string", "required": False}
        ],
        "sensitive_types": ["Aadhaar", "PAN", "phone", "email"],
        "status": "shadow",
        "first_seen": "2026-10-11T09:15:00Z",
        "last_seen": "2026-10-13T22:18:40Z",
        "request_count": 890,
        "exposure": "public",
        "risk_score": 95
    },
    # 8. SHADOW API 3: Admin Health Dump
    {
        "api_id": "api-08",
        "method": "GET",
        "path_template": "/admin/v1/health-dump",
        "auth_type": "none",
        "parameters": [],
        "sensitive_types": [],
        "status": "shadow",
        "first_seen": "2026-10-12T11:00:00Z",
        "last_seen": "2026-10-13T22:20:00Z",
        "request_count": 640,
        "exposure": "public",
        "risk_score": 82
    },
    # 9. SHADOW API 4: Telemetry Raw Ingest
    {
        "api_id": "api-09",
        "method": "POST",
        "path_template": "/api/v1/telemetry/raw",
        "auth_type": "api_key",
        "parameters": [],
        "sensitive_types": ["phone"],
        "status": "shadow",
        "first_seen": "2026-10-10T16:40:00Z",
        "last_seen": "2026-10-13T22:15:10Z",
        "request_count": 2150,
        "exposure": "internal",
        "risk_score": 74
    },
    # 10. ZOMBIE API: Legacy Customer Export CSV (Deprecated 12 months ago)
    {
        "api_id": "api-10",
        "method": "GET",
        "path_template": "/v1/legacy/export/customers.csv",
        "auth_type": "basic",
        "parameters": [
            {"name": "limit", "in": "query", "type": "integer", "required": False}
        ],
        "sensitive_types": ["Aadhaar", "PAN", "phone", "email"],
        "status": "zombie",
        "first_seen": "2024-03-01T00:00:00Z",
        "last_seen": "2026-10-13T22:10:05Z",
        "request_count": 520,
        "exposure": "public",
        "risk_score": 94
    },
    # 11. UNMANAGED API: Partner Webhook Sync (Third-party bypasses gateway)
    {
        "api_id": "api-11",
        "method": "POST",
        "path_template": "/webhooks/partner-sync",
        "auth_type": "none",
        "parameters": [
            {"name": "partner_id", "in": "query", "type": "string", "required": True}
        ],
        "sensitive_types": ["PAN", "phone"],
        "status": "unmanaged",
        "first_seen": "2026-09-01T12:00:00Z",
        "last_seen": "2026-10-13T22:26:00Z",
        "request_count": 9400,
        "exposure": "public",
        "risk_score": 88
    },
    # 12. UNUSED DOCUMENTED: Deprecated Tenant Delete
    {
        "api_id": "api-12",
        "method": "DELETE",
        "path_template": "/admin/deprecated/tenants/{id}",
        "auth_type": "jwt",
        "parameters": [
            {"name": "id", "in": "path", "type": "string", "required": True}
        ],
        "sensitive_types": [],
        "status": "unused_documented",
        "first_seen": "2026-08-15T08:00:00Z",
        "last_seen": "2026-08-16T10:00:00Z",
        "request_count": 3,
        "exposure": "internal",
        "risk_score": 35
    },
    # 13. Card Statements (Documented, BOLA target)
    {
        "api_id": "api-13",
        "method": "GET",
        "path_template": "/cards/{id}/statement",
        "auth_type": "jwt",
        "parameters": [
            {"name": "id", "in": "path", "type": "string", "required": True},
            {"name": "month", "in": "query", "type": "string", "required": False}
        ],
        "sensitive_types": ["PAN", "email"],
        "status": "documented",
        "first_seen": "2026-08-20T08:00:00Z",
        "last_seen": "2026-10-13T22:28:40Z",
        "request_count": 48200,
        "exposure": "public",
        "risk_score": 89
    },
    # 14. KYC Verification (Documented)
    {
        "api_id": "api-14",
        "method": "POST",
        "path_template": "/kyc/verify",
        "auth_type": "jwt",
        "parameters": [
            {"name": "aadhaar_number", "in": "body", "type": "string", "required": True},
            {"name": "pan_number", "in": "body", "type": "string", "required": True}
        ],
        "sensitive_types": ["Aadhaar", "PAN", "phone"],
        "status": "documented",
        "first_seen": "2026-08-20T08:00:00Z",
        "last_seen": "2026-10-13T22:24:50Z",
        "request_count": 22100,
        "exposure": "public",
        "risk_score": 81
    },
    # 15. Merchant Transactions (Documented, Scraping target)
    {
        "api_id": "api-15",
        "method": "GET",
        "path_template": "/merchants/{id}/transactions",
        "auth_type": "api_key",
        "parameters": [
            {"name": "id", "in": "path", "type": "string", "required": True},
            {"name": "page", "in": "query", "type": "integer", "required": False},
            {"name": "limit", "in": "query", "type": "integer", "required": False}
        ],
        "sensitive_types": ["phone"],
        "status": "documented",
        "first_seen": "2026-08-25T08:00:00Z",
        "last_seen": "2026-10-13T22:29:50Z",
        "request_count": 184500,
        "exposure": "public",
        "risk_score": 75
    },
    # 16. Loan Application Status (Documented)
    {
        "api_id": "api-16",
        "method": "GET",
        "path_template": "/loans/{id}",
        "auth_type": "jwt",
        "parameters": [
            {"name": "id", "in": "path", "type": "string", "required": True}
        ],
        "sensitive_types": ["Aadhaar", "PAN"],
        "status": "documented",
        "first_seen": "2026-09-01T08:00:00Z",
        "last_seen": "2026-10-13T22:19:15Z",
        "request_count": 14200,
        "exposure": "public",
        "risk_score": 72
    },
    # 17. Subscriptions Cancel (Documented)
    {
        "api_id": "api-17",
        "method": "DELETE",
        "path_template": "/subscriptions/{id}",
        "auth_type": "jwt",
        "parameters": [
            {"name": "id", "in": "path", "type": "string", "required": True}
        ],
        "sensitive_types": ["email"],
        "status": "documented",
        "first_seen": "2026-09-05T08:00:00Z",
        "last_seen": "2026-10-13T22:12:00Z",
        "request_count": 5100,
        "exposure": "public",
        "risk_score": 48
    },
    # 18. Product Catalog (Documented, Low risk)
    {
        "api_id": "api-18",
        "method": "GET",
        "path_template": "/catalog/products",
        "auth_type": "none",
        "parameters": [
            {"name": "category", "in": "query", "type": "string", "required": False}
        ],
        "sensitive_types": [],
        "status": "documented",
        "first_seen": "2026-08-10T00:00:00Z",
        "last_seen": "2026-10-13T22:29:55Z",
        "request_count": 390000,
        "exposure": "public",
        "risk_score": 28
    },
    # 19. System Healthcheck (Documented, Low risk)
    {
        "api_id": "api-19",
        "method": "GET",
        "path_template": "/healthz",
        "auth_type": "none",
        "parameters": [],
        "sensitive_types": [],
        "status": "documented",
        "first_seen": "2026-08-10T00:00:00Z",
        "last_seen": "2026-10-13T22:30:00Z",
        "request_count": 450000,
        "exposure": "public",
        "risk_score": 10
    },
    # 20. Admin System Configuration (Documented, Internal)
    {
        "api_id": "api-20",
        "method": "PATCH",
        "path_template": "/admin/config/flags",
        "auth_type": "jwt",
        "parameters": [
            {"name": "maintenance_mode", "in": "body", "type": "boolean", "required": False}
        ],
        "sensitive_types": [],
        "status": "documented",
        "first_seen": "2026-08-15T08:00:00Z",
        "last_seen": "2026-10-13T22:05:00Z",
        "request_count": 920,
        "exposure": "internal",
        "risk_score": 62
    }
]

# ==========================================
# 2. ALERTS (15 Alerts across 5 types)
# 3 BOLA, 3 token_misuse, 3 scraping, 3 brute_force, 3 unauthorized_access
# ==========================================
alerts = [
    # BOLA ALERTS
    {
        "alert_id": "alt-01",
        "type": "BOLA",
        "owasp": "API1:2023 BOLA",
        "severity": "critical",
        "api": "GET /accounts/{id}",
        "actor": "u_17",
        "first_seen": "2026-10-13T22:20:10Z",
        "last_seen": "2026-10-13T22:24:45Z",
        "status": "open",
        "reason": "u_17 accessed 47 distinct account IDs in 3 min; baseline is 2",
        "request_ids": [f"req-alt01-{i:03d}" for i in range(1, 41)],
        "recommendation": "Enforce object-level ownership check on GET /accounts/{id} and rate-limit actor u_17"
    },
    {
        "alert_id": "alt-02",
        "type": "BOLA",
        "owasp": "API1:2023 BOLA",
        "severity": "critical",
        "api": "GET /cards/{id}/statement",
        "actor": "u_42",
        "first_seen": "2026-10-13T22:15:00Z",
        "last_seen": "2026-10-13T22:19:30Z",
        "status": "investigating",
        "reason": "u_42 enumerated 38 distinct credit card statement IDs; baseline is 1 per session",
        "request_ids": [f"req-alt02-{i:03d}" for i in range(1, 41)],
        "recommendation": "Validate caller token subject matches cardholder account in repository layer"
    },
    {
        "alert_id": "alt-03",
        "type": "BOLA",
        "owasp": "API1:2023 BOLA",
        "severity": "high",
        "api": "GET /loans/{id}",
        "actor": "u_88",
        "first_seen": "2026-10-13T22:05:00Z",
        "last_seen": "2026-10-13T22:09:12Z",
        "status": "resolved",
        "reason": "u_88 requested 25 non-owned loan account dossiers; baseline is 1",
        "request_ids": [f"req-alt03-{i:03d}" for i in range(1, 41)],
        "recommendation": "Apply ABAC filter: reject requests where loan.borrower_id != jwt.user_id"
    },

    # TOKEN MISUSE ALERTS
    {
        "alert_id": "alt-04",
        "type": "token_misuse",
        "owasp": "API2:2023 Broken Authentication",
        "severity": "critical",
        "api": "GET /accounts/{id}",
        "actor": "tok_9918ab",
        "first_seen": "2026-10-13T22:10:00Z",
        "last_seen": "2026-10-13T22:25:00Z",
        "status": "open",
        "reason": "Token tok_9918ab used concurrently across 5 distinct IP addresses and 3 ASNs in 15 min",
        "request_ids": [f"req-alt04-{i:03d}" for i in range(1, 41)],
        "recommendation": "Immediately revoke token tok_9918ab and enforce client IP / TLS fingerprint binding"
    },
    {
        "alert_id": "alt-05",
        "type": "token_misuse",
        "owasp": "API2:2023 Broken Authentication",
        "severity": "high",
        "api": "POST /accounts/transfer",
        "actor": "tok_replay_71",
        "first_seen": "2026-10-13T22:12:00Z",
        "last_seen": "2026-10-13T22:16:40Z",
        "status": "investigating",
        "reason": "Token tok_replay_71 replayed with conflicting User-Agents (iOS Mobile vs Python Requests) in 60s",
        "request_ids": [f"req-alt05-{i:03d}" for i in range(1, 41)],
        "recommendation": "Invalidate session tok_replay_71 and trigger step-up MFA challenge"
    },
    {
        "alert_id": "alt-06",
        "type": "token_misuse",
        "owasp": "API2:2023 Broken Authentication",
        "severity": "medium",
        "api": "GET /users/{id}/profile",
        "actor": "tok_stale_14",
        "first_seen": "2026-10-13T21:50:00Z",
        "last_seen": "2026-10-13T22:00:00Z",
        "status": "resolved",
        "reason": "Token used from geographic impossible travel origin: Mumbai to Frankfurt within 8 min",
        "request_ids": [f"req-alt06-{i:03d}" for i in range(1, 41)],
        "recommendation": "Enable geo-velocity alerting and invalidate distributed JWT sessions"
    },

    # SCRAPING ALERTS
    {
        "alert_id": "alt-07",
        "type": "scraping",
        "owasp": "API4:2023 Unrestricted Resource Consumption",
        "severity": "high",
        "api": "GET /merchants/{id}/transactions",
        "actor": "185.220.101.5",
        "first_seen": "2026-10-13T22:14:00Z",
        "last_seen": "2026-10-13T22:26:00Z",
        "status": "open",
        "reason": "185.220.101.5 downloaded 48 MB across 40 rapid sequential pages; baseline is 120 KB",
        "request_ids": [f"req-alt07-{i:03d}" for i in range(1, 41)],
        "recommendation": "Enforce strict page limit ceiling (max limit=50) and rate-limit client IP to 10 req/min"
    },
    {
        "alert_id": "alt-08",
        "type": "scraping",
        "owasp": "API4:2023 Unrestricted Resource Consumption",
        "severity": "medium",
        "api": "GET /catalog/products",
        "actor": "194.26.29.112",
        "first_seen": "2026-10-13T22:00:00Z",
        "last_seen": "2026-10-13T22:15:00Z",
        "status": "investigating",
        "reason": "Automated harvester scraped 12,000 catalog entries with 0 ms jitter between requests",
        "request_ids": [f"req-alt08-{i:03d}" for i in range(1, 41)],
        "recommendation": "Deploy bot-detection CAPTCHA on unauthenticated catalog scraping"
    },
    {
        "alert_id": "alt-09",
        "type": "scraping",
        "owasp": "API4:2023 Unrestricted Resource Consumption",
        "severity": "low",
        "api": "GET /accounts/{id}",
        "actor": "u_scraper_9",
        "first_seen": "2026-10-13T21:40:00Z",
        "last_seen": "2026-10-13T21:55:00Z",
        "status": "resolved",
        "reason": "High-volume pagination crawl on accounts ledger; 40 requests in 90 seconds",
        "request_ids": [f"req-alt09-{i:03d}" for i in range(1, 41)],
        "recommendation": "Throttle paginated cursor traversal"
    },

    # BRUTE FORCE ALERTS
    {
        "alert_id": "alt-10",
        "type": "brute_force",
        "owasp": "API2:2023 Broken Authentication",
        "severity": "critical",
        "api": "POST /auth/login",
        "actor": "45.154.255.89",
        "first_seen": "2026-10-13T22:21:00Z",
        "last_seen": "2026-10-13T22:27:30Z",
        "status": "open",
        "reason": "38 consecutive 401 Unauthorized credential failures in 6 min followed by 2 successes",
        "request_ids": [f"req-alt10-{i:03d}" for i in range(1, 41)],
        "recommendation": "Block IP 45.154.255.89, lock affected account, and enforce exponential backoff"
    },
    {
        "alert_id": "alt-11",
        "type": "brute_force",
        "owasp": "API2:2023 Broken Authentication",
        "severity": "high",
        "api": "POST /auth/login",
        "actor": "91.240.118.23",
        "first_seen": "2026-10-13T22:11:00Z",
        "last_seen": "2026-10-13T22:18:00Z",
        "status": "investigating",
        "reason": "Distributed credential stuffing pattern rotating 40 distinct user emails from single subnet",
        "request_ids": [f"req-alt11-{i:03d}" for i in range(1, 41)],
        "recommendation": "Activate Cloudflare WAF credential stuffing managed rule set"
    },
    {
        "alert_id": "alt-12",
        "type": "brute_force",
        "owasp": "API2:2023 Broken Authentication",
        "severity": "medium",
        "api": "POST /kyc/verify",
        "actor": "103.21.244.0",
        "first_seen": "2026-10-13T21:45:00Z",
        "last_seen": "2026-10-13T21:58:00Z",
        "status": "resolved",
        "reason": "35 invalid OTP verification attempts against single Aadhaar token",
        "request_ids": [f"req-alt12-{i:03d}" for i in range(1, 41)],
        "recommendation": "Cap OTP attempts to 3 max before 1-hour lockout"
    },

    # UNAUTHORIZED ACCESS ALERTS
    {
        "alert_id": "alt-13",
        "type": "unauthorized_access",
        "owasp": "API5:2023 Broken Function Level Auth",
        "severity": "critical",
        "api": "GET /internal/debug/tokens",
        "actor": "194.26.29.112",
        "first_seen": "2026-10-13T22:22:00Z",
        "last_seen": "2026-10-13T22:28:15Z",
        "status": "open",
        "reason": "Unauthenticated external client invoked internal debug route /internal/debug/tokens 40 times",
        "request_ids": [f"req-alt13-{i:03d}" for i in range(1, 41)],
        "recommendation": "Quarantine /internal/debug/tokens at edge proxy; revoke all leaked signing keys"
    },
    {
        "alert_id": "alt-14",
        "type": "unauthorized_access",
        "owasp": "API9:2023 Improper Inventory Management",
        "severity": "high",
        "api": "GET /v1/legacy/export/customers.csv",
        "actor": "198.51.100.84",
        "first_seen": "2026-10-13T22:08:00Z",
        "last_seen": "2026-10-13T22:15:20Z",
        "status": "investigating",
        "reason": "Deprecated zombie export route queried using stale basic auth credentials",
        "request_ids": [f"req-alt14-{i:03d}" for i in range(1, 41)],
        "recommendation": "Decommission legacy endpoint route and return HTTP 410 Gone"
    },
    {
        "alert_id": "alt-15",
        "type": "unauthorized_access",
        "owasp": "API5:2023 Broken Function Level Auth",
        "severity": "high",
        "api": "PATCH /admin/config/flags",
        "actor": "u_standard_3",
        "first_seen": "2026-10-13T22:01:00Z",
        "last_seen": "2026-10-13T22:06:45Z",
        "status": "resolved",
        "reason": "Standard user role attempted privilege escalation on administrative config endpoint",
        "request_ids": [f"req-alt15-{i:03d}" for i in range(1, 41)],
        "recommendation": "Enforce strict RBAC guard requiring 'SUPERADMIN' role before route execution"
    }
]

# ==========================================
# 3. REQUEST LOG RECORDS (40 per alert = 600 records)
# Matching FROZEN CONTRACT:
# {request_id, timestamp, method, raw_path, path_template, query_params[],
#  status_code, response_size, request_size, latency_ms, client_ip, user_agent,
#  auth_type, token_id, user_id, object_ids[], sensitive_types[]}
# ==========================================
requests = []

user_agents_pool = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "python-requests/2.31.0",
    "PostmanRuntime/7.39.0",
    "curl/8.4.0",
    "Go-http-client/1.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15",
]

for alert in alerts:
    a_id = alert["alert_id"]
    a_type = alert["type"]
    api_template = alert["api"]  # e.g. "GET /accounts/{id}"
    method, path_tmpl = api_template.split(" ", 1)
    base_actor = alert["actor"]
    start_time = datetime.fromisoformat(alert["first_seen"].replace("Z", ""))

    for i in range(1, 41):
        req_id = f"req-{a_id.replace('-', '')}-{i:03d}"
        t = start_time + timedelta(seconds=i * 6 + random.randint(0, 3))
        ts_str = t.isoformat() + "Z"

        # Default properties
        status_code = 200
        resp_size = random.randint(450, 1850)
        req_size = random.randint(120, 680)
        latency_ms = random.randint(22, 115)
        client_ip = "194.26.29.112" if a_type in ["BOLA", "unauthorized_access"] else "185.220.101.5"
        ua = "python-requests/2.31.0"
        auth_type = "jwt"
        token_id = "tok_user17_active"
        user_id = "u_17"
        object_ids = []
        sensitive_types = []
        query_params = []
        raw_path = path_tmpl

        # Pattern customization per alert type
        if a_type == "BOLA":
            auth_type = "jwt"
            user_id = base_actor if base_actor.startswith("u_") else "u_17"
            token_id = f"tok_{user_id}_jwt"
            # Target accounts: first request is user's own account (e.g. acc_1001), next 39 are victims!
            target_obj = "acc_1001" if i == 1 else f"acc_{2000 + i}"
            object_ids = [target_obj]
            raw_path = path_tmpl.replace("{id}", target_obj)
            sensitive_types = ["PAN", "Aadhaar", "phone", "email"]
            status_code = 200
            ua = "python-requests/2.31.0"
            client_ip = "194.26.29.112"
            query_params = ["include_statement=true"] if i % 3 == 0 else []

        elif a_type == "token_misuse":
            auth_type = "jwt"
            token_id = base_actor if base_actor.startswith("tok_") else "tok_9918ab"
            user_id = "u_compromised_victim"
            object_ids = [f"acc_{9000 + (i % 3)}"]
            raw_path = path_tmpl.replace("{id}", object_ids[0])
            # Multiple IPs using same token!
            ip_pool = ["194.26.29.112", "45.154.255.89", "185.220.101.5", "91.240.118.23", "103.21.244.50"]
            client_ip = ip_pool[(i - 1) % len(ip_pool)]
            ua = user_agents_pool[(i - 1) % len(user_agents_pool)]
            sensitive_types = ["phone", "email"]
            status_code = 200

        elif a_type == "scraping":
            auth_type = "api_key"
            token_id = "api_key_partner_crawl"
            user_id = "u_merchant_api"
            client_ip = base_actor if "." in base_actor else "185.220.101.5"
            ua = "Scrapy/2.11.0 (+https://scrapy.org)"
            page_num = i
            limit = 100
            query_params = [f"page={page_num}", f"limit={limit}"]
            target_obj = "merch_550"
            object_ids = [target_obj]
            raw_path = f"{path_tmpl.replace('{id}', target_obj)}?page={page_num}&limit={limit}"
            resp_size = 1250000 + random.randint(10000, 50000)  # Large payload cumulative
            sensitive_types = ["phone"]

        elif a_type == "brute_force":
            auth_type = "none"
            token_id = None
            client_ip = base_actor if "." in base_actor else "45.154.255.89"
            ua = "Hydra/9.5"
            raw_path = path_tmpl
            object_ids = []
            # 38 failures, 2 successes at the end
            if i <= 38:
                status_code = 401
                user_id = f"test_victim_{i}@cybercup.corp"
                resp_size = 180
            else:
                status_code = 200
                user_id = "admin@cybercup.corp"
                resp_size = 850
            sensitive_types = ["email"]
            req_size = 320

        elif a_type == "unauthorized_access":
            auth_type = "none" if "internal" in path_tmpl or "legacy" in path_tmpl else "jwt"
            token_id = None if auth_type == "none" else "tok_standard_role_jwt"
            user_id = base_actor if base_actor.startswith("u_") else None
            client_ip = "194.26.29.112"
            ua = "curl/8.4.0"
            raw_path = path_tmpl.replace("{id}", "tenant_999")
            object_ids = ["tenant_999"] if "{id}" in path_tmpl else []
            # Returns 200 on shadow route (leak!), or 403 on RBAC probe
            status_code = 200 if "internal" in path_tmpl or "legacy" in path_tmpl else 403
            resp_size = 2100 if status_code == 200 else 240
            sensitive_types = ["PAN", "phone", "email"] if "legacy" in path_tmpl else []

        requests.append({
            "request_id": req_id,
            "timestamp": ts_str,
            "method": method,
            "raw_path": raw_path,
            "path_template": path_tmpl,
            "query_params": query_params,
            "status_code": status_code,
            "response_size": resp_size,
            "request_size": req_size,
            "latency_ms": latency_ms,
            "client_ip": client_ip,
            "user_agent": ua,
            "auth_type": auth_type,
            "token_id": token_id,
            "user_id": user_id,
            "object_ids": object_ids,
            "sensitive_types": sensitive_types
        })

# ==========================================
# 4. RISK SCORES
# Breakdown Categories: Exposure (0-40), Data Sensitivity (0-25),
#                       Behavior (0-20), Security Events (0-15)
# ==========================================
risk_scores = {}
for item in inventory:
    aid = item["api_id"]
    score = item["risk_score"]
    
    # Calculate breakdown
    exp_pts = 35 if item["exposure"] == "public" and item["auth_type"] == "none" else (25 if item["exposure"] == "public" else 10)
    sens_pts = min(25, len(item["sensitive_types"]) * 7)
    beh_pts = 18 if item["status"] in ["shadow", "zombie", "unmanaged"] else 6
    sec_pts = 14 if score >= 85 else (8 if score >= 65 else 2)
    
    level = "critical" if score >= 85 else ("high" if score >= 65 else ("medium" if score >= 40 else "low"))

    breakdown = [
        {
            "factor": "Exposure",
            "points": exp_pts,
            "max_points": 40,
            "reason": f"Exposure is {item['exposure']} with auth_type '{item['auth_type']}'"
        },
        {
            "factor": "Data Sensitivity",
            "points": sens_pts,
            "max_points": 25,
            "reason": f"Returns sensitive types: {', '.join(item['sensitive_types']) if item['sensitive_types'] else 'None'}"
        },
        {
            "factor": "Behavior",
            "points": beh_pts,
            "max_points": 20,
            "reason": f"Endpoint status classified as '{item['status']}' with drift indicators"
        },
        {
            "factor": "Security Events",
            "points": sec_pts,
            "max_points": 15,
            "reason": f"{'Active critical or high alert history flagged' if sec_pts > 5 else 'Normal incident baseline'}"
        }
    ]

    risk_scores[aid] = {
        "api_id": aid,
        "score": score,
        "level": level,
        "breakdown": breakdown
    }

# ==========================================
# 5. BASELINES
# Metrics: rate, payload_size, unique_callers, hourly_distribution
# ==========================================
baselines = {}
for item in inventory:
    aid = item["api_id"]
    baselines[aid] = [
        {
            "api_id": aid,
            "metric": "rate",
            "baseline_values": {"p50": 12, "p95": 35, "max_normal": 50},
            "live_values": {"current_rate": 142 if aid in ["api-01", "api-06"] else 18, "anomaly": aid in ["api-01", "api-06"]}
        },
        {
            "api_id": aid,
            "metric": "payload_size",
            "baseline_values": {"avg_bytes": 1250, "p95_bytes": 2800},
            "live_values": {"current_avg_bytes": 28500 if aid == "api-15" else 1400, "anomaly": aid == "api-15"}
        },
        {
            "api_id": aid,
            "metric": "unique_callers",
            "baseline_values": {"distinct_actors_per_hour": 15},
            "live_values": {"distinct_actors_per_hour": 48 if aid == "api-03" else 14, "anomaly": aid == "api-03"}
        },
        {
            "api_id": aid,
            "metric": "hourly_distribution",
            "baseline_values": [10, 8, 5, 4, 3, 5, 12, 35, 60, 85, 95, 100, 98, 92, 88, 90, 85, 78, 65, 50, 42, 30, 22, 15],
            "live_values": [12, 7, 6, 4, 3, 5, 14, 38, 65, 90, 110, 125, 140, 130, 95, 92, 88, 80, 70, 55, 48, 35, 25, 18]
        }
    ]

# ==========================================
# 6. POSTURE OVERVIEW
# ==========================================
status_counts = {
    "documented": sum(1 for i in inventory if i["status"] == "documented"),
    "shadow": sum(1 for i in inventory if i["status"] == "shadow"),
    "zombie": sum(1 for i in inventory if i["status"] == "zombie"),
    "unmanaged": sum(1 for i in inventory if i["status"] == "unmanaged"),
    "unused_documented": sum(1 for i in inventory if i["status"] == "unused_documented")
}

alerts_severity_counts = {
    "critical": sum(1 for a in alerts if a["severity"] == "critical"),
    "high": sum(1 for a in alerts if a["severity"] == "high"),
    "medium": sum(1 for a in alerts if a["severity"] == "medium"),
    "low": sum(1 for a in alerts if a["severity"] == "low")
}

alerts_type_counts = {
    "BOLA": sum(1 for a in alerts if a["type"] == "BOLA"),
    "token_misuse": sum(1 for a in alerts if a["type"] == "token_misuse"),
    "scraping": sum(1 for a in alerts if a["type"] == "scraping"),
    "brute_force": sum(1 for a in alerts if a["type"] == "brute_force"),
    "unauthorized_access": sum(1 for a in alerts if a["type"] == "unauthorized_access")
}

top_risky = sorted(inventory, key=lambda x: x["risk_score"], reverse=True)[:5]
top_risky_formatted = [
    {
        "api_id": x["api_id"],
        "method": x["method"],
        "path_template": x["path_template"],
        "risk_score": x["risk_score"],
        "reason_chip": f"{x['status'].upper()} • {', '.join(x['sensitive_types'][:2]) if x['sensitive_types'] else 'No Auth'}"
    }
    for x in top_risky
]

posture = {
    "posture_score": 64,
    "posture_explanation": "Posture score 64/100 computed from weighted risk average across 20 APIs, penalised by 4 shadow APIs, 1 zombie route, and 5 active critical alerts.",
    "total_apis": len(inventory),
    "counts_by_status": status_counts,
    "alerts_by_severity": alerts_severity_counts,
    "alerts_by_type": alerts_type_counts,
    "top_risky_apis": top_risky_formatted,
    "requests_over_time": [
        {"timestamp": "21:00", "count": 1820},
        {"timestamp": "21:15", "count": 2100},
        {"timestamp": "21:30", "count": 2450},
        {"timestamp": "21:45", "count": 2980},
        {"timestamp": "22:00", "count": 3840},
        {"timestamp": "22:15", "count": 4620},
        {"timestamp": "22:30", "count": 4200}
    ]
}

# ==========================================
# 7. TRAFFIC STATS
# ==========================================
traffic_stats = {
    "window": "1h",
    "requests_over_time": [
        {"timestamp": "21:30", "requests_per_min": 245, "error_rate": 1.2},
        {"timestamp": "21:40", "requests_per_min": 280, "error_rate": 1.8},
        {"timestamp": "21:50", "requests_per_min": 310, "error_rate": 2.1},
        {"timestamp": "22:00", "requests_per_min": 420, "error_rate": 6.8},
        {"timestamp": "22:10", "requests_per_min": 510, "error_rate": 9.4},
        {"timestamp": "22:20", "requests_per_min": 590, "error_rate": 11.2},
        {"timestamp": "22:30", "requests_per_min": 520, "error_rate": 8.5}
    ],
    "error_rates": {
        "rate_4xx": 7.4,
        "rate_5xx": 0.8
    },
    "latency_percentiles": {
        "p50": 34,
        "p90": 88,
        "p99": 195
    },
    "top_consumers": [
        {"actor": "u_17 (Tor Exit)", "requests": 2140, "error_rate": 2.1},
        {"actor": "tok_9918ab (Distributed)", "requests": 1840, "error_rate": 4.5},
        {"actor": "45.154.255.89 (Brute Force)", "requests": 1280, "error_rate": 92.4},
        {"actor": "185.220.101.5 (Scraper)", "requests": 940, "error_rate": 0.0},
        {"actor": "Legitimate Mobile App", "requests": 34500, "error_rate": 0.4}
    ],
    "top_endpoints": [
        {"api": "GET /accounts/{id}", "requests": 84520, "error_rate": 4.2},
        {"api": "POST /auth/login", "requests": 245000, "error_rate": 14.8},
        {"api": "GET /catalog/products", "requests": 390000, "error_rate": 0.2},
        {"api": "GET /internal/debug/tokens", "requests": 1420, "error_rate": 0.0},
        {"api": "GET /cards/{id}/statement", "requests": 48200, "error_rate": 2.8}
    ],
    "status_codes": [
        {"code": "200 OK", "count": 782000, "percentage": 82.5},
        {"code": "201 Created", "count": 64000, "percentage": 6.8},
        {"code": "400 Bad Request", "count": 12400, "percentage": 1.3},
        {"code": "401 Unauthorized", "count": 38200, "percentage": 4.0},
        {"code": "403 Forbidden", "count": 31500, "percentage": 3.3},
        {"code": "404 Not Found", "count": 9200, "percentage": 1.0},
        {"code": "429 Rate Limited", "count": 7800, "percentage": 0.8},
        {"code": "500 Server Error", "count": 2900, "percentage": 0.3}
    ],
    "ip_geo_breakdown": [
        {"country": "India (Domestic Mobile/Web)", "ip_count": 4820, "requests": 680000},
        {"country": "Netherlands (Tor / Datacenter)", "ip_count": 42, "requests": 14200},
        {"country": "Russia (Bulletproof ASN)", "ip_count": 28, "requests": 9400},
        {"country": "United States (Cloud Scrapers)", "ip_count": 115, "requests": 18200},
        {"country": "Germany (Exit Relays)", "ip_count": 34, "requests": 7600}
    ],
    "auth_split": [
        {"auth_type": "jwt", "percentage": 52.4},
        {"auth_type": "none (public)", "percentage": 34.2},
        {"auth_type": "oauth2", "percentage": 8.1},
        {"auth_type": "api_key", "percentage": 4.8},
        {"auth_type": "basic", "percentage": 0.5}
    ]
}

# ==========================================
# 8. EVALUATION DATA
# ==========================================
evaluation = {
    "overall": {
        "detection_rate": 0.942,
        "fp_rate": 0.018,
        "precision": 0.965,
        "f1": 0.953,
        "mean_time_to_detect_s": 24.6
    },
    "per_scenario": [
        {"scenario": "BOLA / IDOR Account Harvest", "recall": 0.96, "detected": 48, "total": 50, "mean_ttd_s": 18.2},
        {"scenario": "Distributed Token Misuse / Replay", "recall": 0.92, "detected": 46, "total": 50, "mean_ttd_s": 32.4},
        {"scenario": "High-Volume Data Scraping", "recall": 0.98, "detected": 49, "total": 50, "mean_ttd_s": 14.5},
        {"scenario": "Credential Stuffing & Brute Force", "recall": 0.94, "detected": 47, "total": 50, "mean_ttd_s": 22.0},
        {"scenario": "Shadow Route Probe & BFLA", "recall": 0.91, "detected": 45, "total": 50, "mean_ttd_s": 36.0}
    ],
    "confusion_matrix": {
        "tp": 235,
        "fp": 8,
        "tn": 442,
        "fn": 15
    },
    "before_after_tuning": [
        {"metric": "Detection Rate (Recall)", "before": 0.812, "after": 0.942},
        {"metric": "False Positive Rate", "before": 0.084, "after": 0.018},
        {"metric": "Precision", "before": 0.871, "after": 0.965},
        {"metric": "Mean Time to Detect (s)", "before": 58.4, "after": 24.6}
    ],
    "known_limitations": [
        "Slow-and-low BOLA probes (< 1 request / 10 minutes) require a larger observation window (> 24h) to exceed anomaly thresholds.",
        "Token sharing within corporate NAT gateways can exhibit multi-IP behavior that requires TLS JA4 fingerprinting to disambiguate from true token theft."
    ]
}

# Write files into both mock/ and dashboard/public/mock/
targets = ["mock", os.path.join("dashboard", "public", "mock")]

data_files = {
    "inventory.json": inventory,
    "alerts.json": alerts,
    "requests.json": requests,
    "risk_scores.json": risk_scores,
    "baselines.json": baselines,
    "posture.json": posture,
    "traffic_stats.json": traffic_stats,
    "evaluation.json": evaluation
}

for folder in targets:
    os.makedirs(folder, exist_ok=True)
    for filename, data in data_files.items():
        filepath = os.path.join(folder, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Wrote {filepath} ({os.path.getsize(filepath):,} bytes)")

print("\nAll mock JSON files generated successfully!")
