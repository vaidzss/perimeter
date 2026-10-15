import os
import re
import time
import json
import uuid
from datetime import datetime, timezone
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Match

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.request_log import RequestLog

# Precompiled regex patterns for sensitive data detection in response bodies
RE_PAN = re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b')
RE_AADHAAR = re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b')
RE_PHONE = re.compile(r'\b(?:\+91|91)?[6-9]\d{9}\b')
RE_ACCOUNT = re.compile(r'\b[1-9]\d{10,15}\b')
RE_PATH_ID = re.compile(r'/(?P<id>[0-9]+|[0-9a-fA-F-]{36}|u_[0-9]+|m_[a-z0-9_]+)')

class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        os.makedirs(os.path.dirname(os.path.abspath(settings.LOG_FILE_PATH)), exist_ok=True)

    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        request_id = str(uuid.uuid4())
        
        # Read request size
        request_size = 0
        try:
            content_length = request.headers.get("content-length")
            if content_length:
                request_size = int(content_length)
        except Exception:
            request_size = 0

        # Process request
        response = None
        error_occurred = None
        try:
            response = await call_next(request)
        except Exception as exc:
            error_occurred = exc
            raise exc
        finally:
            latency_ms = int((time.perf_counter() - start_time) * 1000)
            
            # Read response body for size & PII inspection
            response_body_bytes = b""
            if response is not None and hasattr(response, "body_iterator"):
                try:
                    chunks = [chunk async for chunk in response.body_iterator]
                    response_body_bytes = b"".join(chunks)
                    response = Response(
                        content=response_body_bytes,
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        media_type=response.media_type
                    )
                except Exception:
                    response_body_bytes = b""

            response_size = len(response_body_bytes)
            status_code = response.status_code if response else 500

            # Determine path_template via Starlette route matching
            path_template = self._resolve_path_template(request)
            
            # Extract object_ids from URL path
            object_ids = self._extract_object_ids(request.url.path)
            
            # Scan response body for sensitive types
            sensitive_types = self._detect_sensitive_types(response_body_bytes)

            # Determine client IP (handles X-Forwarded-For)
            client_ip = self._extract_client_ip(request)

            # Extract auth information
            auth_type, token_id, user_id = self._extract_auth_info(request)

            # Build log payload strictly matching CC6-IC07 contract
            log_record = {
                "request_id": request_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "method": request.method,
                "raw_path": request.url.path,
                "path_template": path_template,
                "query_params": list(request.query_params.keys()),
                "status_code": status_code,
                "response_size": response_size,
                "request_size": request_size,
                "latency_ms": latency_ms,
                "client_ip": client_ip,
                "user_agent": request.headers.get("user-agent", "unknown"),
                "auth_type": auth_type,
                "token_id": token_id,
                "user_id": user_id,
                "object_ids": object_ids,
                "sensitive_types": sensitive_types
            }

            # Dual write: File + SQLite
            self._write_log(log_record)

        return response

    def _resolve_path_template(self, request: Request) -> str:
        """Finds the matched route path template from request scope."""
        route = request.scope.get("route")
        if route:
            path = getattr(route, "path", getattr(route, "path_format", None))
            if path:
                if request.url.path.startswith("/api/v2") and not path.startswith("/api/v2"):
                    return "/api/v2" + path
                elif request.url.path.startswith("/api/v1") and not path.startswith("/api/v1"):
                    return "/api/v1" + path
                elif request.url.path.startswith("/api/internal") and not path.startswith("/api/internal"):
                    return "/api/internal" + path
                return path
        return request.url.path

    def _extract_object_ids(self, path: str) -> list[str]:
        """Extracts identifier-like tokens from the request path."""
        matches = RE_PATH_ID.findall(path)
        return list(dict.fromkeys(matches))  # remove duplicates while preserving order

    def _detect_sensitive_types(self, body_bytes: bytes) -> list[str]:
        """Regex scans response text for PAN, Aadhaar, Phone, and Account numbers."""
        if not body_bytes or len(body_bytes) > 1024 * 512:  # skip huge bodies
            return []
        
        try:
            text = body_bytes.decode("utf-8", errors="ignore")
        except Exception:
            return []

        sensitive = []
        if RE_PAN.search(text):
            sensitive.append("pan")
        if RE_AADHAAR.search(text):
            sensitive.append("aadhaar")
        if RE_PHONE.search(text):
            sensitive.append("phone")
        if RE_ACCOUNT.search(text):
            sensitive.append("account_number")

        return sensitive

    def _extract_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        if request.client and request.client.host:
            return request.client.host
        return "127.0.0.1"

    def _extract_auth_info(self, request: Request) -> tuple[str, str | None, str | None]:
        # Check if auth details were captured by deps.py or internal_auth.py
        token_id = getattr(request.state, "token_id", None)
        user_id = getattr(request.state, "user_id", None) or getattr(request.state, "actor_employee_id", None)
        auth_type = getattr(request.state, "auth_type", None)

        auth_header = request.headers.get("authorization", "")
        if auth_header.lower().startswith("bearer "):
            if not auth_type:
                auth_type = "bearer"
            if not user_id or not token_id:
                try:
                    import jwt
                    raw_token = auth_header.split(" ", 1)[1].strip()
                    unverified = jwt.decode(raw_token, options={"verify_signature": False})
                    if not token_id:
                        token_id = unverified.get("jti")
                    if not user_id:
                        user_id = unverified.get("employee_id") or (str(unverified.get("sub")) if unverified.get("sub") is not None else None)
                except Exception:
                    pass
        elif "x-debug-key" in request.headers:
            auth_type = "debug_key"
        elif not auth_type:
            auth_type = "none"

        return auth_type, token_id, user_id

    def _write_log(self, record: dict):
        """Asynchronously/safely dual-writes to JSONL file and requests table."""
        try:
            # 1. Write to JSONL file
            line = json.dumps(record) + "\n"
            with open(settings.LOG_FILE_PATH, "a", encoding="utf-8") as f:
                f.write(line)
        except Exception as e:
            print(f"[LoggingMiddleware] File log error: {e}")

        try:
            # 2. Write to SQLite requests table
            db = SessionLocal()
            try:
                db_record = RequestLog(
                    request_id=record["request_id"],
                    timestamp=datetime.fromisoformat(record["timestamp"].replace("Z", "+00:00")),
                    method=record["method"],
                    raw_path=record["raw_path"],
                    path_template=record["path_template"],
                    query_params=json.dumps(record["query_params"]),
                    status_code=record["status_code"],
                    response_size=record["response_size"],
                    request_size=record["request_size"],
                    latency_ms=record["latency_ms"],
                    client_ip=record["client_ip"],
                    user_agent=record["user_agent"],
                    auth_type=record["auth_type"],
                    token_id=record["token_id"],
                    user_id=record["user_id"],
                    object_ids=json.dumps(record["object_ids"]),
                    sensitive_types=json.dumps(record["sensitive_types"])
                )
                db.add(db_record)
                db.commit()
            finally:
                db.close()
        except Exception as e:
            print(f"[LoggingMiddleware] DB log error: {e}")
