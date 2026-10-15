"""
Telemetry Middleware for Person 1:
Intercepts all HTTP traffic, extracts JWT auth claims, normalizes paths,
scans response payloads for synthetic Indian PII using fast compiled regexes,
and outputs structured JSON telemetry to logs/telemetry_stream.jsonl and in-memory buffer.
"""

import os
import re
import json
import time
import uuid
import datetime
from collections import deque
from typing import Dict, Any, List, Tuple, Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from person1_api_discovery.app.auth import decode_jwt_token
from person1_api_discovery.app.normalizer import normalize_path, scan_pii_fields
from person1_api_discovery.app.inventory_service import inventory_service
from person1_api_discovery.app.deep_inspector import deep_inspector

# Thread-safe in-memory sliding buffer for fast query access (shared with Checkpoint 3 & 4)
MAX_LOG_BUFFER_SIZE = 2000
RECENT_TELEMETRY_LOGS: deque = deque(maxlen=MAX_LOG_BUFFER_SIZE)

# Target log file path
LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
LOG_FILE_PATH = os.path.join(LOG_DIR, "telemetry_stream.jsonl")

# Compiled PII detection patterns
PII_PATTERNS = {
    "PAN": re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"),
    "GOVT_ID_LIKE": re.compile(r"(\[GOVT-ID-[A-Z0-9-]+\]|GOVT-ID-XXXX-[0-9]{4}|AADHAAR-[A-Z0-9-]+|VOTER-ID-[A-Z0-9-]+)"),
    "PHONE": re.compile(r"(\+91-?[6-9]\d{9}|\+91-\d{10})"),
    "UPI_VPA": re.compile(r"\b[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}\b"),
    "EMAIL": re.compile(r"\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b")
}

# Dynamic URL path segment parameterizer
NUMERIC_SEGMENT_REGEX = re.compile(r"^\d+$")
TXN_SEGMENT_REGEX = re.compile(r"^TXN\d+$", re.IGNORECASE)
IFSC_SEGMENT_REGEX = re.compile(r"^[A-Z]{4}0[A-Z0-9]{6}$", re.IGNORECASE)
UUID_SEGMENT_REGEX = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE)


def normalize_request_path(raw_path: str) -> Tuple[str, Dict[str, str]]:
    """
    Normalizes path segments into parameterized templates:
    /api/v2/accounts/1004 -> /api/v2/accounts/{id}, {'id': '1004'}
    /api/v2/transactions/TXN100101/receipt -> /api/v2/transactions/{id}/receipt, {'id': 'TXN100101'}
    /api/v2/search/ifsc/HDFC0001234 -> /api/v2/search/ifsc/{id}, {'id': 'HDFC0001234'}
    """
    segments = raw_path.strip("/").split("/")
    normalized_parts = []
    extracted_params: Dict[str, str] = {}
    param_idx = 1

    for seg in segments:
        if (NUMERIC_SEGMENT_REGEX.match(seg) or
            TXN_SEGMENT_REGEX.match(seg) or
            IFSC_SEGMENT_REGEX.match(seg) or
            UUID_SEGMENT_REGEX.match(seg)):
            param_key = "id" if param_idx == 1 else f"id_{param_idx}"
            normalized_parts.append(f"{{{param_key}}}")
            extracted_params[param_key] = seg
            param_idx += 1
        else:
            normalized_parts.append(seg)

    normalized_path = "/" + "/".join(normalized_parts)
    return normalized_path, extracted_params


def scan_pii_fields(text_content: str) -> List[str]:
    """Scans text content for sensitive Indian PII patterns."""
    detected = []
    if not text_content:
        return detected
    for pii_type, pattern in PII_PATTERNS.items():
        if pattern.search(text_content):
            detected.append(pii_type)
    return detected


def append_telemetry_log(entry: Dict[str, Any]) -> None:
    """Appends telemetry log to in-memory buffer and JSONL log file."""
    RECENT_TELEMETRY_LOGS.append(entry)
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"[TelemetryMiddleware] Failed to write to {LOG_FILE_PATH}: {e}")


class StructuredTelemetryMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()

        # 1. Capture Client IP & Headers
        client_ip = request.headers.get("x-forwarded-for")
        if client_ip:
            client_ip = client_ip.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "127.0.0.1"

        user_agent = request.headers.get("user-agent", "unknown")
        raw_path = request.url.path
        method = request.method
        query_params = dict(request.query_params)

        # Early Active Defense Enforcement across all gateway endpoints
        CONTROL_PLANE_PATHS = (
            "/api/posture", "/api/alerts", "/api/defense", "/api/traffic",
            "/api/evaluation", "/api/telemetry", "/api/inventory", "/api/actors",
            "/ws", "/health", "/docs", "/openapi.json", "/redoc", "/favicon.ico"
        )
        is_control_plane = raw_path.startswith(CONTROL_PLANE_PATHS)

        if not is_control_plane and inventory_service.is_ip_blocked(client_ip):
            inventory_service.log_defense_action(
                action_type="IP_BLOCK_ENFORCED",
                target=client_ip,
                reason="Blocked malicious IP attempt to access target system",
                metadata={"path": raw_path, "method": method}
            )
            block_content = json.dumps({
                "error": "IP_QUARANTINED_BY_PERIMETER",
                "status": "BLOCKED",
                "client_ip": client_ip,
                "reason": "Host quarantined due to suspicious Tor exit node or credential replay attack.",
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "mitigation": "ACTIVE_DEFENSE_ENGAGED"
            }).encode("utf-8")
            return Response(content=block_content, status_code=403, media_type="application/json")

        normalized_path_check, _ = normalize_path(raw_path)
        if not is_control_plane and inventory_service.is_route_quarantined(raw_path, normalized_path_check):
            inventory_service.log_defense_action(
                action_type="VIRTUAL_PATCH_ENFORCED",
                target=raw_path,
                reason="Quarantined route invocation blocked by Perimeter",
                metadata={"client_ip": client_ip, "method": method}
            )
            quarantine_content = json.dumps({
                "error": "ROUTE_QUARANTINED_BY_PERIMETER",
                "status": "VIRTUAL_PATCH_ENFORCED",
                "path": raw_path,
                "reason": "Endpoint quarantined: uncataloged route with critical PII leak or privilege escalation risk.",
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "mitigation": "ROUTE_ISOLATED"
            }).encode("utf-8")
            return Response(content=quarantine_content, status_code=403, media_type="application/json")

        # 2. Extract Auth Claims & Type
        auth_header = request.headers.get("authorization", "")
        auth_type = "NONE"
        jwt_sub = None
        jwt_role = None
        jwt_jti = None

        if auth_header.startswith("Bearer "):
            auth_type = "JWT_BEARER"
            token = auth_header.split(" ", 1)[1].strip()
            try:
                claims = decode_jwt_token(token)
                jwt_sub = claims.get("sub")
                jwt_role = claims.get("role")
                jwt_jti = claims.get("jti")
            except Exception:
                pass
        elif "x-api-key" in request.headers or "api-key" in request.headers:
            auth_type = "API_KEY"

        # 3. Ground Truth Header (for Person 2's accuracy evaluation)
        ground_truth_label = (
            request.headers.get("x-ground-truth") or
            request.headers.get("x-truth") or
            "unlabeled"
        )

        # 4. Safely read and capture bounded request body sample without consuming stream
        req_body_bytes = await request.body()
        req_bytes = len(req_body_bytes)
        raw_req_body_sample = req_body_bytes[:4096].decode("utf-8", errors="replace") if req_body_bytes else ""

        parsed_json_body = None
        if req_body_bytes:
            try:
                parsed_json_body = json.loads(req_body_bytes.decode("utf-8", errors="ignore"))
            except Exception:
                pass

        # Re-populate request body receive channel for downstream route handlers
        async def receive():
            return {"type": "http.request", "body": req_body_bytes, "more_body": False}
        request = Request(request.scope, receive=receive)

        # 5. Execute downstream call
        response = await call_next(request)

        # 6. Capture response payload and compute metrics
        res_body_bytes = b""
        async for chunk in response.body_iterator:
            res_body_bytes += chunk

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        res_bytes = len(res_body_bytes)

        # 7. Decode response sample for PII scanning
        try:
            res_text = res_body_bytes.decode("utf-8", errors="replace")
        except Exception:
            res_text = ""

        pii_fields_detected = scan_pii_fields(res_text)

        # 8. Path normalization
        normalized_path, extracted_params = normalize_path(raw_path)

        # 9. Deep Semantic Ingress Inspection (Sentinel-API Phase 2)
        deep_result = deep_inspector.inspect_request(
            query_params=query_params,
            raw_body_sample=raw_req_body_sample,
            parsed_body=parsed_json_body,
            latency_ms=latency_ms
        )

        # 10. Build structured telemetry record
        log_entry = {
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "client_ip": client_ip,
            "user_agent": user_agent,
            "method": method,
            "raw_path": raw_path,
            "normalized_path": normalized_path,
            "query_params": query_params,
            "path_params_extracted": extracted_params,
            "auth_type": auth_type,
            "jwt_sub": jwt_sub,
            "jwt_role": jwt_role,
            "jwt_jti": jwt_jti,
            "status_code": response.status_code,
            "req_bytes": req_bytes,
            "res_bytes": res_bytes,
            "latency_ms": latency_ms,
            "pii_fields_detected": pii_fields_detected,
            "ground_truth_label": ground_truth_label,
            "raw_request_headers": dict(request.headers),
            "raw_request_body_sample": raw_req_body_sample,
            "parsed_json_body": parsed_json_body,
            "raw_response_sample": res_text[:1000] if res_text else "",
            # Sentinel Phase 2 telemetry contract additions
            "threat_indicators_detected": deep_result.threat_indicators,
            "owasp_tags": deep_result.owasp_categories,
            "deep_inspection_verdict": "THREAT_DETECTED" if deep_result.is_threat else "CLEAN",
            "deep_inspection_severity": deep_result.severity,
            "deep_inspection_reasons": deep_result.reasons,
            "deep_inspection_details": deep_result.details,
            "deep_inspection_latency_ms": deep_result.execution_latency_ms
        }

        # Define internal control-plane paths that must NOT be logged as target app traffic
        CONTROL_PLANE_PATHS = (
            "/api/posture",
            "/api/alerts",
            "/api/defense",
            "/api/traffic",
            "/api/evaluation",
            "/api/telemetry",
            "/api/inventory",
            "/api/actors",
            "/ws",
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/favicon.ico"
        )
        is_control_plane = raw_path.startswith(CONTROL_PLANE_PATHS)
        already_handled = getattr(request.state, "perimeter_forwarded", False)

        # 11. Non-blocking log emission & inventory ingestion ONLY for target application traffic
        if not is_control_plane and not already_handled:
            append_telemetry_log(log_entry)
            try:
                inventory_service.ingest_event(log_entry)

                # Record deep semantic threat event if flagged
                if deep_result.is_threat:
                    inventory_service.record_deep_threat({
                        "event_id": log_entry["event_id"],
                        "timestamp": log_entry["timestamp"],
                        "endpoint": normalized_path,
                        "raw_path": raw_path,
                        "method": method,
                        "client_ip": client_ip,
                        "user_id": jwt_sub,
                        "verdict": "THREAT_DETECTED",
                        "threat_indicators": deep_result.threat_indicators,
                        "owasp_tags": deep_result.owasp_categories,
                        "reasons": deep_result.reasons,
                        "severity": deep_result.severity,
                        "details": deep_result.details
                    })
                # Mirror to Person 2 Engine
                try:
                    from person1_api_discovery.app.person2_bridge import process_mirrored_telemetry
                    parsed_res = None
                    try:
                        parsed_res = json.loads(res_text)
                    except Exception:
                        pass
                    process_mirrored_telemetry(
                        request_id=log_entry["event_id"],
                        method=method,
                        path=raw_path,
                        query_params=query_params,
                        headers=dict(request.headers),
                        request_body=parsed_json_body,
                        status_code=response.status_code,
                        response_body=parsed_res,
                        response_size_bytes=res_bytes,
                        client_ip=client_ip,
                        user_agent=user_agent,
                        jwt_sub=jwt_sub,
                        jwt_jti=jwt_jti,
                        ground_truth=ground_truth_label
                    )
                except Exception:
                    pass
            except Exception as e:
                print(f"[TelemetryMiddleware] Ingestion error: {e}")

        # 11. Return response cleanly
        headers = dict(response.headers)
        headers["content-length"] = str(res_bytes)
        return Response(
            content=res_body_bytes,
            status_code=response.status_code,
            headers=headers,
            media_type=response.media_type
        )
