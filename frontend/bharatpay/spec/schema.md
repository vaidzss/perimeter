# BharatPay Telemetry Log Schema Specification (CC6-IC07)
> **Shared Interface Contract between Target Banking System and ASPM Discovery & Abuse Prevention Pipeline**

Every HTTP request and response cycle processed by the BharatPay application is converted into a structured JSON line emitted to `/var/log/bharatpay/requests.jsonl` and persisted in the SQLite `requests` table.

---

## 📋 JSON Schema Field Definitions

| Field Name | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `request_id` | `string (uuid)` | Globally unique identifier generated for each incoming HTTP request. | `"c1f78ab4-5e12-4e58-9a3c-1b752df8c48a"` |
| `timestamp` | `string (iso8601)` | UTC timestamp with microsecond resolution when the request was received. | `"2026-10-15T12:20:00.123456Z"` |
| `method` | `string` | HTTP verb in uppercase (`GET`, `POST`, `PUT`, `DELETE`). | `"GET"` |
| `raw_path` | `string` | The exact URL path requested by the client. | `"/api/v2/accounts/1042/statement"` |
| `path_template` | `string` | The parameterized route path matched by the backend routing engine. Used for API inventory aggregation. | `"/api/v2/accounts/{account_id}/statement"` |
| `query_params` | `array[string]` | List of query parameter keys present in the request URL. | `["page", "limit", "search"]` |
| `status_code` | `integer` | Final HTTP response status code sent to the client (`200`, `401`, `403`, etc.). | `200` |
| `response_size` | `integer` | Byte size of the HTTP response payload. | `1834` |
| `request_size` | `integer` | Byte size of the HTTP request payload (from `Content-Length`). | `64` |
| `latency_ms` | `integer` | Total processing time in milliseconds from ingress to egress. | `12` |
| `client_ip` | `string` | Origin client IP address (extracted from `X-Forwarded-For` or socket). | `"203.0.113.5"` |
| `user_agent` | `string` | Full `User-Agent` header value sent by client. | `"Mozilla/5.0 ..."` or `"python-requests/2.31.0"` |
| `auth_type` | `string` | Authentication mechanism detected: `"bearer"`, `"debug_key"`, or `"none"`. | `"bearer"` |
| `token_id` | `string \| null` | The unique JWT ID (`jti`) extracted from the token claim. Used to correlate token replay across disparate IPs and User-Agents. | `"82ea9f49-d028-4013-be37-f1f815167e44"` |
| `user_id` | `string \| null` | User code associated with authenticated session (e.g. `u_101`). | `"u_101"` |
| `object_ids` | `array[string]` | Numeric and resource identifiers extracted from the URL path. Used to detect BOLA horizontal authorization scans. | `["1042"]` |
| `sensitive_types`| `array[string]` | Data sensitivity tags flagged via regex scanning of the response body: `"pan"`, `"aadhaar"`, `"phone"`, `"account_number"`. | `["pan", "account_number"]` |

---

## 🔍 Log Ingestion Locations
- **Container Path**: `/var/log/bharatpay/requests.jsonl`
- **Host Path (Docker Volume)**: `./logs/requests.jsonl`
- **SQLite Database Table**: `requests` in `bharatpay.db`
- **Nginx Gateway Log**: `./logs/nginx_access.log` (Gateway JSON format with upstream timings)
