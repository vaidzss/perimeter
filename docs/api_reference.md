# Perimeter: REST API & Gateway Reference

## 1. Overview & Base URLs

Perimeter exposes both **Data-Plane Reverse-Proxy** routes and **Control-Plane Management** routes:

* **Perimeter Gateway Ingress:** `http://localhost:8000`
* **SOC Console Vite Proxy:** `http://localhost:3000/api`
* **Target Banking Service:** `http://localhost:8001`
* **Interactive OpenAPI Docs:** `http://localhost:8000/docs`

---

## 2. Active Defense & Mitigation APIs

### `GET /api/defense/status`
Returns the real-time active defense posture, quarantined routes, blocked IPs, and chronological enforcement decisions.

**Response `200 OK`:**
```json
{
  "status": "ACTIVE_DEFENSE_ENGAGED",
  "shield_active": true,
  "pii_masking_enabled": true,
  "quarantined_routes": [
    "/api/internal/debug/override-limit",
    "/api/v1/kyc/aadhaar-pan-dump"
  ],
  "quarantined_routes_count": 2,
  "blocked_ips": [
    "185.220.101.5"
  ],
  "blocked_ips_count": 1,
  "active_threats_count": 4,
  "attacks_blocked_count": 3,
  "enforcements": [
    {
      "decision": "BLOCKED",
      "http_status": 403,
      "action": "VIRTUAL_PATCH_ENFORCED",
      "target": "/api/v1/kyc/aadhaar-pan-dump",
      "method": "GET",
      "client_ip": "127.0.0.1",
      "attack_vector": "Zombie PII Exfiltration",
      "impact": "Exploit neutralized at gateway; 0 records leaked to attacker.",
      "reason": "Endpoint quarantined: uncataloged route with critical PII leak",
      "timestamp": "2026-10-15T10:24:42.672634+00:00"
    }
  ]
}
```

---

### `POST /api/defense/quarantine`
Deploys a virtual patch on a route, rejecting all future requests to it with `HTTP 403 Forbidden`.

**Request Body:**
```json
{
  "path": "/api/v1/kyc/aadhaar-pan-dump",
  "reason": "Virtual patch: prevent bulk KYC exfiltration"
}
```

**Response `200 OK`:**
```json
{
  "status": "QUARANTINED",
  "path": "/api/v1/kyc/aadhaar-pan-dump",
  "active_quarantines": ["/api/v1/kyc/aadhaar-pan-dump"],
  "message": "Virtual patch deployed: route /api/v1/kyc/aadhaar-pan-dump will be rejected with 403."
}
```

---

### `POST /api/defense/unquarantine`
Restores a previously quarantined route to active service.

**Request Body:**
```json
{
  "path": "/api/v1/kyc/aadhaar-pan-dump"
}
```

---

### `POST /api/defense/block-ip`
Blacklists a malicious client IP across the perimeter gateway.

**Request Body:**
```json
{
  "ip": "185.220.101.5",
  "reason": "Tor exit node used in token replay attack"
}
```

**Response `200 OK`:**
```json
{
  "status": "BLOCKED",
  "ip": "185.220.101.5",
  "active_blocked_ips": ["185.220.101.5"],
  "message": "IP 185.220.101.5 is now blocked across the perimeter."
}
```

---

### `POST /api/defense/unblock-ip`
Unbans a previously blacklisted client IP.

**Request Body:**
```json
{
  "ip": "185.220.101.5"
}
```

---

### `POST /api/defense/toggle-pii-masking`
Toggles automatic in-flight redaction of Indian PII (Aadhaar, PAN) on or off.

**Request Body:**
```json
{
  "enabled": true
}
```

---

### `POST /api/defense/mitigate-all`
Automated One-Click Defense: Discovers all active zombie and shadow endpoints and applies route quarantine virtual patches, while banning all flagged malicious IPs.

**Response `200 OK`:**
```json
{
  "status": "ALL_THREATS_MITIGATED",
  "quarantined_routes": [
    "/api/internal/debug/override-limit",
    "/api/v1/kyc/aadhaar-pan-dump"
  ],
  "blocked_ips": [
    "185.220.101.5"
  ],
  "pii_masking_enabled": true,
  "message": "Perimeter Active Defense has secured BharatPay against all active vectors!"
}
```

---

## 3. Inventory & OpenAPI Discovery APIs

### `GET /api/inventory`
Returns the complete list of discovered, documented, shadow, and zombie APIs.

**Query Parameters:**
* `status`: Filter by `documented`, `shadow`, `zombie`, `unused_documented`, or `all`.
* `auth`: Filter by `JWT_BEARER`, `API_KEY`, `NONE`, or `all`.
* `sensitive`: Filter by PII type (`pan`, `aadhaar`, `email`, `phone`).
* `q`: Fuzzy text search on path or endpoint ID.
* `sort`: `risk_desc`, `risk_asc`, `requests_desc`.

---

### `GET /api/inventory/diff-summary`
Returns high-level inventory categorization metrics:
```json
{
  "total_discovered": 16,
  "documented_count": 10,
  "shadow_count": 4,
  "zombie_count": 2,
  "unused_count": 0
}
```

---

### `GET /api/inventory/endpoints/{id}/auto-swagger`
Synthesizes a compliant OpenAPI 3.1 schema for an uncataloged shadow endpoint using observed request/response telemetry.

---

## 4. Posture, Alerts & Forensics APIs

### `GET /api/posture`
Returns the overall Security Posture Score (0–100), grade (A to F), breakdown counts, and traffic velocity trend.

---

### `GET /api/alerts`
Returns prioritized security incidents. Supports filtering by `severity` (`critical`, `high`, `medium`, `low`), `type` (`bola`, `shadow_api`, `zombie_leak`, `token_replay`), `status`, and `actor`.

---

### `GET /api/alerts/{id}`
Returns details for a specific security alert (supports ID aliasing: `alt-01`, `alt_01`, `ALT-1001`).

---

### `GET /api/alerts/{id}/requests`
Returns raw forensic evidence logs associated with the incident for cURL export and replay analysis.

---

### `GET /api/actors/{actor}/activity`
Returns the full lateral movement profile, endpoints accessed, observed IPs, and user agents for an actor or client IP.

---

## 5. Person 2 Telemetry & Streaming APIs

### `POST /api/telemetry`
Direct ingestion point for Person 2's Telemetry Engine matching the CC6-IC07 specification.

**Request Payload:**
```json
{
  "request_id": "req-9842",
  "method": "GET",
  "path": "/api/v2/accounts/1004/statement",
  "status_code": 200,
  "latency_ms": 4.2,
  "client_ip": "185.220.101.5",
  "user_agent": "python-requests/2.31.0",
  "user_id": "u_17",
  "ground_truth": "bola_attack"
}
```

---

### `GET /api/metrics/confusion-matrix`
Returns live True Positive (TP), False Positive (FP), True Negative (TN), False Negative (FN), TPR, FPR, and F1 metrics:
```json
{
  "tp": 18,
  "fp": 0,
  "tn": 50,
  "fn": 1,
  "tpr_percentage": 94.7,
  "fpr_percentage": 0.0,
  "precision_percentage": 100.0,
  "f1_score": 97.3
}
```

---

### `WebSocket /ws/telemetry`
WebSocket push connection streaming real-time security events and confusion matrix updates directly to connected SOC command centers.

---

## 6. Context-Aware Session Graphing API

### `GET /api/session-graph/{session_id}`
Returns the stateful Directed Behavioral Graph (DAG) for a given session, including visited route nodes, directed edge transition counts, and recent chronological sequence.

**Parameters:**
* `session_id` (path, string): Unique session identifier, user ID (`jwt_sub`), or client IP.

**Response `200 OK`:**
```json
{
  "session_id": "sess_usr_1001",
  "total_steps": 3,
  "current_node": "GET:/api/v2/accounts/{id}/balance",
  "nodes": [
    { "id": "POST:/api/v2/auth/login", "label": "/login", "method": "POST", "count": 1 },
    { "id": "GET:/api/v2/users/me", "label": "/me", "method": "GET", "count": 1 },
    { "id": "GET:/api/v2/accounts/{id}/balance", "label": "/balance", "method": "GET", "count": 1 }
  ],
  "edges": [
    { "source": "POST:/api/v2/auth/login", "target": "GET:/api/v2/users/me", "weight": 1 },
    { "source": "GET:/api/v2/users/me", "target": "GET:/api/v2/accounts/{id}/balance", "weight": 1 }
  ]
}
```

---

## 7. Identity Governance, Provisioning & Internal Reporting APIs

### `POST /api/v2/internal/employees/login`
Authenticates an internal corporate employee and returns a scoped JWT bearing role, scope, department, and region claims.

**Request Body:**
```json
{
  "email": "rajesh.sharma@corp.bharatpay.com",
  "password": "Employee@123"
}
```

**Response `200 OK`:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "jti": "a53c0ec3-aae4-4e8b-88d9-49bda311bda8",
  "employee_id": "EMP-1001",
  "name": "Rajesh Sharma",
  "role": "IT Admin",
  "scope": "ops-only",
  "region": "IT-Infra",
  "department": "IT Ops"
}
```

---

### `POST /api/v2/internal/employees/onboard`
Registers a new corporate identity into the organizational hierarchy.
* **Security Guard:** Strictly restricted to **IT Admin** (`EMP-1001`). Unauthorized calls return `HTTP 403 Forbidden` and trigger a privilege escalation audit event.

**Request Body:**
```json
{
  "name": "Arun Kumar",
  "email": "arun.kumar@corp.bharatpay.com",
  "role": "Sales Manager",
  "department": "Sales",
  "region": "North"
}
```

---

### `GET /api/v2/internal/campaigns`
Lists all active and historical sanctioned business campaign windows with regional scopes and expected traffic multipliers.

**Response `200 OK`:**
```json
[
  {
    "id": 1,
    "campaign_code": "CAMP-DIWALI-2026",
    "name": "Diwali Sale 2026",
    "start_date": "2026-10-13T00:00:00Z",
    "end_date": "2026-10-22T23:59:59Z",
    "affected_regions": ["West", "North", "South", "East", "org-wide"],
    "expected_roles": ["VP Sales", "Regional Head", "Sales Manager"],
    "expected_volume_multiplier": 10,
    "created_by": "EMP-1001",
    "is_active": true
  }
]
```

---

### `POST /api/v2/internal/campaigns`
Registers a new sanctioned high-traffic campaign window.
* **Security Guard:** Restricted to **IT Admin** or **VP Sales**.

**Request Body:**
```json
{
  "name": "IPL Season Bonanza",
  "start_date": "2026-10-16T00:00:00Z",
  "end_date": "2026-10-26T23:59:59Z",
  "affected_regions": ["West", "North", "South", "East"],
  "expected_roles": ["VP Sales", "Regional Head", "Sales Manager"],
  "expected_volume_multiplier": 8
}
```

---

### `GET /api/v2/internal/reports/regional-sales`
Returns regional performance metrics. Validates that the requesting token's home region matches the requested query region.
* **Security Guard:** Cross-region queries by non-executive roles return `HTTP 403 Forbidden: Scope mismatch`.

**Query Parameters:**
* `region` (string, optional): e.g. `West`

---

### `GET /api/v2/internal/reports/account-lookup/{account_id}`
Allows authorized customer support and sales managers to retrieve customer account details.
* **Security Guard:** Requires an explicit, non-empty `reason` query parameter (e.g. `?reason=Customer+disputed+charge+ticket+491`). Failure to supply an audit reason returns `HTTP 400 Bad Request`.
* **Jurisdiction Enforcement:** Queries for accounts outside the caller's regional jurisdiction return `HTTP 403 Forbidden`.
