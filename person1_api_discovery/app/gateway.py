"""
Perimeter Active Defense Gateway & Interceptor Module
Acts as the inline / reverse-proxy security shield protecting target APIs (BharatPay).
Key Capabilities:
1. Real-time IP Blacklisting / Quarantine (Tor nodes, scrapers).
2. Route Virtual Patching / Quarantine (blocks uncataloged Zombie & Shadow backdoors).
3. In-flight PII Redaction & Leak Prevention (masks Aadhaar and PAN before leaving network).
4. Dual Telemetry Emittance (feeds CC6-IC07 JSONL stream and live discovery inventory).
"""

import os
import re
import time
import json
import uuid
import datetime
import httpx
from typing import Optional, Dict, Any
from fastapi import Request, Response
from starlette.responses import JSONResponse, Response as StarletteResponse

from person1_api_discovery.app.inventory_service import inventory_service
from person1_api_discovery.app.normalizer import normalize_path, scan_pii_fields
from person1_api_discovery.app.middleware import RECENT_TELEMETRY_LOGS
from person1_api_discovery.app.deep_inspector import deep_inspector

UPSTREAM_TARGET = os.getenv("UPSTREAM_TARGET", "http://127.0.0.1:8001")

# Precompiled regex for sensitive data redaction
RE_AADHAAR = re.compile(r'\b(\d{4})[\s-]?(\d{4})[\s-]?(\d{4})\b')
RE_PAN = re.compile(r'\b([A-Z]{5})(\d{4})([A-Z])\b')

_http_client: Optional[httpx.AsyncClient] = None


def get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(timeout=10.0, follow_redirects=True)
    return _http_client


def mask_sensitive_pii(text: str) -> str:
    """Masks unmasked Aadhaar and PAN numbers in text/JSON."""
    # Mask Aadhaar: 999988881001 -> 9999-XXXX-1001
    masked = RE_AADHAAR.sub(r'\1-XXXX-\3', text)
    # Mask PAN: ABCDE1234F -> ABCDE****F
    masked = RE_PAN.sub(r'\1****\3', masked)
    return masked


def record_gateway_telemetry(
    request: Request,
    event_id: str,
    method: str,
    raw_path: str,
    normalized_path: str,
    path_params: dict,
    client_ip: str,
    user_agent: str,
    status_code: int,
    req_bytes: int,
    res_bytes: int,
    latency_ms: float,
    pii_fields: list,
    res_sample: str,
    parsed_json_body: Any = None,
    request_body: Any = None,
    raw_req_body_sample: str = ""
):
    # Extract auth details from request headers
    auth_header = request.headers.get("authorization", "")
    auth_type = "NONE"
    jwt_sub = None
    jwt_jti = None
    if auth_header.lower().startswith("bearer "):
        auth_type = "JWT_BEARER"
        try:
            import jwt
            token = auth_header.split(" ")[1]
            unverified = jwt.decode(token, options={"verify_signature": False})
            jwt_sub = unverified.get("sub") or unverified.get("user_id")
            jwt_jti = unverified.get("jti")
        except Exception:
            pass
    elif "x-debug-key" in request.headers or "x-api-key" in request.headers:
        auth_type = "API_KEY"

    explicit_gt = request.headers.get("x-ground-truth") or request.headers.get("x-truth")
    if explicit_gt:
        ground_truth = explicit_gt
    else:
        if client_ip in {"185.220.101.5", "185.220.101.6"} or "python-requests" in user_agent.lower():
            ground_truth = "attack_replay"
        elif "aadhaar-pan-dump" in raw_path:
            ground_truth = "attack_zombie_pii"
        elif "debug" in raw_path or "override-limit" in raw_path:
            ground_truth = "attack_shadow"
        elif "/accounts/" in raw_path and (jwt_sub and not raw_path.endswith(f"/{jwt_sub}")):
            ground_truth = "attack_bola"
        elif "/auth/login" in raw_path:
            ground_truth = "legitimate_auth"
        else:
            ground_truth = "unlabeled"

    # Deep Semantic Ingress Inspection (Sentinel-API Phase 2)
    deep_result = deep_inspector.inspect_request(
        query_params=dict(request.query_params),
        raw_body_sample=raw_req_body_sample,
        parsed_body=request_body,
        latency_ms=latency_ms
    )

    telemetry_event = {
        "event_id": event_id,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "client_ip": client_ip,
        "user_agent": user_agent,
        "method": method,
        "raw_path": raw_path,
        "normalized_path": normalized_path,
        "query_params": dict(request.query_params),
        "path_params_extracted": path_params,
        "auth_type": auth_type,
        "jwt_sub": jwt_sub,
        "jwt_role": "customer",
        "jwt_jti": jwt_jti,
        "status_code": status_code,
        "req_bytes": req_bytes,
        "res_bytes": res_bytes,
        "latency_ms": latency_ms,
        "pii_fields_detected": pii_fields,
        "ground_truth_label": ground_truth,
        "raw_request_body_sample": raw_req_body_sample,
        "parsed_json_body": request_body,
        "raw_response_sample": res_sample[:1000] if res_sample else "",
        # Sentinel Phase 2 telemetry contract additions
        "threat_indicators_detected": deep_result.threat_indicators,
        "owasp_tags": deep_result.owasp_categories,
        "deep_inspection_verdict": "THREAT_DETECTED" if deep_result.is_threat else "CLEAN",
        "deep_inspection_severity": deep_result.severity,
        "deep_inspection_reasons": deep_result.reasons,
        "deep_inspection_details": deep_result.details,
        "deep_inspection_latency_ms": deep_result.execution_latency_ms
    }

    # In-memory buffer for dashboard actor/request queries
    RECENT_TELEMETRY_LOGS.append(telemetry_event)

    # Emit to telemetry_stream.jsonl
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "telemetry_stream.jsonl")
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(telemetry_event) + "\n")
    except Exception as e:
        print(f"[Perimeter Gateway] Log emittance error: {e}")

    # Ingest directly into InventoryService
    inventory_service.ingest_event(telemetry_event)

    if deep_result.is_threat:
        inventory_service.record_deep_threat({
            "event_id": event_id,
            "timestamp": telemetry_event["timestamp"],
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

    # Mirror into Person 2 Traffic Detection & Abuse Engine
    risk_score_obj = None
    try:
        from person1_api_discovery.app.person2_bridge import process_mirrored_telemetry
        risk_score_obj, p2_lat = process_mirrored_telemetry(
            request_id=event_id,
            method=method,
            path=raw_path,
            query_params=dict(request.query_params),
            headers=dict(request.headers),
            request_body=request_body,
            status_code=status_code,
            response_body=parsed_json_body,
            response_size_bytes=res_bytes,
            client_ip=client_ip,
            user_agent=user_agent,
            jwt_sub=jwt_sub,
            jwt_jti=jwt_jti,
            ground_truth=ground_truth
        )
    except Exception as e:
        print(f"[Perimeter Gateway] Person 2 engine error: {e}")

    # Mark request as handled so middleware doesn't duplicate
    request.state.perimeter_forwarded = True
    return risk_score_obj


async def forward_through_perimeter(request: Request) -> Response:
    """
    Core inline gateway handler that inspects, defends, proxies upstream,
    and returns sanitized responses while streaming full telemetry.
    """
    start_time = time.perf_counter()
    event_id = str(uuid.uuid4())
    raw_path = request.url.path
    method = request.method.upper()
    
    # Extract client IP (respecting X-Forwarded-For)
    forwarded = request.headers.get("x-forwarded-for")
    client_ip = forwarded.split(",")[0].strip() if forwarded else (request.client.host if request.client else "127.0.0.1")
    user_agent = request.headers.get("user-agent", "unknown")
    
    # Check normalized path template
    known_templates = [v["path"] for v in inventory_service.spec_endpoints.values()]
    normalized_path, path_params = normalize_path(raw_path, known_templates)

    # -------------------------------------------------------------
    # 1. ACTIVE DEFENSE: IP Blacklist Enforcement
    # -------------------------------------------------------------
    if inventory_service.is_ip_blocked(client_ip):
        inventory_service.log_defense_action(
            action_type="IP_BLOCK_ENFORCED",
            target=client_ip,
            reason="Blocked malicious IP attempt to access target system",
            metadata={"path": raw_path, "method": method}
        )
        block_content = {
            "error": "IP_QUARANTINED_BY_PERIMETER",
            "status": "BLOCKED",
            "client_ip": client_ip,
            "reason": "Host quarantined due to suspicious Tor exit node or credential replay attack.",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "mitigation": "ACTIVE_DEFENSE_ENGAGED"
        }
        record_gateway_telemetry(
            request=request,
            event_id=event_id,
            method=method,
            raw_path=raw_path,
            normalized_path=normalized_path,
            path_params=path_params,
            client_ip=client_ip,
            user_agent=user_agent,
            status_code=403,
            req_bytes=0,
            res_bytes=len(json.dumps(block_content)),
            latency_ms=round((time.perf_counter() - start_time) * 1000, 2),
            pii_fields=[],
            res_sample=json.dumps(block_content),
            parsed_json_body=block_content
        )
        return JSONResponse(status_code=403, content=block_content)

    # -------------------------------------------------------------
    # 2. ACTIVE DEFENSE: Route Quarantine / Virtual Patching
    # -------------------------------------------------------------
    if inventory_service.is_route_quarantined(raw_path, normalized_path):
        inventory_service.log_defense_action(
            action_type="VIRTUAL_PATCH_ENFORCED",
            target=raw_path,
            reason="Quarantined route invocation blocked by Perimeter",
            metadata={"client_ip": client_ip, "method": method}
        )
        quarantine_content = {
            "error": "ROUTE_QUARANTINED_BY_PERIMETER",
            "status": "VIRTUAL_PATCH_ENFORCED",
            "path": raw_path,
            "reason": "Endpoint quarantined: uncataloged route with critical PII leak or privilege escalation risk.",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "mitigation": "ROUTE_ISOLATED"
        }
        record_gateway_telemetry(
            request=request,
            event_id=event_id,
            method=method,
            raw_path=raw_path,
            normalized_path=normalized_path,
            path_params=path_params,
            client_ip=client_ip,
            user_agent=user_agent,
            status_code=403,
            req_bytes=0,
            res_bytes=len(json.dumps(quarantine_content)),
            latency_ms=round((time.perf_counter() - start_time) * 1000, 2),
            pii_fields=[],
            res_sample=json.dumps(quarantine_content),
            parsed_json_body=quarantine_content
        )
        return JSONResponse(status_code=403, content=quarantine_content)

    # -------------------------------------------------------------
    # 3. Upstream Forwarding to Target System
    # -------------------------------------------------------------
    target_url = f"{UPSTREAM_TARGET}{raw_path}"
    if request.url.query:
        target_url = f"{target_url}?{request.url.query}"

    body_bytes = await request.body()
    req_headers = dict(request.headers)
    req_headers.pop("host", None)
    req_headers.pop("content-length", None)

    client = get_http_client()
    try:
        upstream_res = await client.request(
            method=method,
            url=target_url,
            headers=req_headers,
            content=body_bytes
        )
        status_code = upstream_res.status_code
        res_bytes_raw = upstream_res.content
        res_content_type = upstream_res.headers.get("content-type", "application/json")
    except Exception as exc:
        return JSONResponse(
            status_code=502,
            content={
                "error": "UPSTREAM_TARGET_UNAVAILABLE",
                "message": f"Could not reach target banking backend at {UPSTREAM_TARGET}: {str(exc)}"
            }
        )

    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

    # -------------------------------------------------------------
    # 4. In-Flight PII Redaction & Data Leak Prevention
    # -------------------------------------------------------------
    final_res_bytes = res_bytes_raw
    pii_fields = []
    try:
        res_text = res_bytes_raw.decode("utf-8", errors="ignore")
        pii_fields = scan_pii_fields(res_text)
        
        # If PII Masking is active and unmasked sensitive records detected, redact in-flight
        if inventory_service.pii_masking_enabled and (
            "AADHAAR" in pii_fields or "PAN" in pii_fields or "GOVT_ID_LIKE" in pii_fields
        ):
            masked_text = mask_sensitive_pii(res_text)
            final_res_bytes = masked_text.encode("utf-8")
    except Exception:
        pass

    # -------------------------------------------------------------
    # 5. Dual Telemetry Logging & Inventory Ingestion
    # -------------------------------------------------------------
    parsed_body = None
    try:
        parsed_body = json.loads(final_res_bytes.decode("utf-8", errors="ignore"))
    except Exception:
        pass

    parsed_req_body = None
    raw_req_body_sample = body_bytes[:4096].decode("utf-8", errors="replace") if body_bytes else ""
    if body_bytes:
        try:
            parsed_req_body = json.loads(body_bytes.decode("utf-8", errors="ignore"))
        except Exception:
            pass

    risk_score_obj = record_gateway_telemetry(
        request=request,
        event_id=event_id,
        method=method,
        raw_path=raw_path,
        normalized_path=normalized_path,
        path_params=path_params,
        client_ip=client_ip,
        user_agent=user_agent,
        status_code=status_code,
        req_bytes=len(body_bytes),
        res_bytes=len(final_res_bytes),
        latency_ms=latency_ms,
        pii_fields=pii_fields,
        res_sample=final_res_bytes.decode("utf-8", errors="ignore"),
        parsed_json_body=parsed_body,
        request_body=parsed_req_body,
        raw_req_body_sample=raw_req_body_sample
    )

    # Initialize response headers dictionary
    resp_headers = {k: v for k, v in upstream_res.headers.items() if k.lower() not in {"content-length", "content-encoding", "transfer-encoding"}}
    if risk_score_obj:
        resp_headers["X-Perimeter-Risk-Score"] = str(risk_score_obj.risk_score)
        resp_headers["X-Perimeter-Severity"] = risk_score_obj.severity

    # Return response to client
    resp_headers["X-Perimeter-Protected"] = "true"
    resp_headers["X-Perimeter-Latency-Ms"] = str(latency_ms)

    return StarletteResponse(
        content=final_res_bytes,
        status_code=status_code,
        headers=resp_headers,
        media_type=res_content_type
    )
