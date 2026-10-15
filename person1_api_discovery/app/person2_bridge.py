"""
Perimeter <-> Person 2 (Traffic Detection Engine) Integration Bridge.
Unifies Person 1's Active Gateway & Telemetry Logger with Person 2's:
- Box A: Discovery & Shadow Diff Engine (Parameterizer, Verhoeff PII, Spec Diff)
- Box B: Runtime Behavior & Abuse Detector (Welford baseline, BOLA, Scraping, Replay)
- Box C: Explainable Risk Scoring Engine (0-100 composite formula + Reason Vectors)
- Live WebSocket push feed (/ws/telemetry)
- Real-time Confusion Matrix (TPR, FPR, TP/FP/TN/FN)
"""

import os
import sys
import time
import json
import asyncio
from typing import Optional, Dict, Any, List, Set, Tuple
from fastapi import WebSocket

# Ensure traffic-detection-engine is in Python path
ENGINE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "traffic-detection-engine"))
if ENGINE_DIR not in sys.path:
    sys.path.insert(0, ENGINE_DIR)

from core.models import (
    TelemetryEvent,
    RiskScore,
    AbuseAlert,
    SpecDriftStatus,
    PIISeverity
)
from pipeline import CoreDetectionEngine

# Paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SPEC_PATH_P1 = os.path.join(BASE_DIR, "specs", "openapi_partial.json")
SPEC_PATH_BP = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend", "bharatpay", "spec", "openapi.json"))
DB_PATH = os.path.join(ENGINE_DIR, "telemetry.db")


class WebSocketManager:
    """Manages active WebSocket connections to SOC dashboards."""
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)

    async def broadcast_json(self, data: dict):
        disconnected = []
        for connection in list(self.active_connections):
            try:
                await connection.send_json(data)
            except Exception:
                disconnected.append(connection)
        for dead in disconnected:
            self.active_connections.discard(dead)


# Global instances
ws_manager = WebSocketManager()
person2_engine = CoreDetectionEngine(openapi_spec_path=SPEC_PATH_P1, db_path=DB_PATH)

# Also load BharatPay spec into Person 2's comparator if available
if os.path.exists(SPEC_PATH_BP):
    try:
        with open(SPEC_PATH_BP, "r", encoding="utf-8") as f:
            bp_spec = json.load(f)
        # Append BharatPay routes to compiled routes
        for path_template, path_item in bp_spec.get("paths", {}).items():
            import re
            regex_str = "^" + re.sub(r'\{[^}]+\}', r'[^/]+', path_template) + "$"
            compiled_regex = re.compile(regex_str, re.IGNORECASE)
            methods: Dict[str, Dict[str, Any]] = {}
            for method, op_data in path_item.items():
                if method.lower() in ("get", "post", "put", "delete", "patch"):
                    methods[method.upper()] = op_data if isinstance(op_data, dict) else {}
            person2_engine.spec_comparator.compiled_routes.append({
                "template": path_template,
                "regex": compiled_regex,
                "methods": methods
            })
    except Exception as e:
        print(f"[Person2Bridge] Error loading BharatPay spec into engine: {e}")


def process_mirrored_telemetry(
    request_id: str,
    method: str,
    path: str,
    query_params: Optional[Dict[str, str]] = None,
    headers: Optional[Dict[str, str]] = None,
    request_body: Optional[Any] = None,
    status_code: int = 200,
    response_headers: Optional[Dict[str, str]] = None,
    response_body: Optional[Any] = None,
    response_size_bytes: int = 0,
    client_ip: Optional[str] = None,
    user_agent: Optional[str] = None,
    jwt_sub: Optional[str] = None,
    jwt_jti: Optional[str] = None,
    ground_truth: Optional[str] = None,
    session_id: Optional[str] = None
) -> Tuple[RiskScore, float]:
    """
    Feeds an intercepted telemetry event directly into Person 2's CoreDetectionEngine.
    Returns: (RiskScore, latency_ms)
    """
    event = TelemetryEvent(
        request_id=request_id,
        session_id=session_id or jwt_sub or client_ip or "anonymous_session",
        timestamp=time.time(),
        method=method.upper(),
        path=path,
        query_params=query_params or {},
        headers=headers or {},
        request_body=request_body,
        status_code=status_code,
        response_headers=response_headers or {},
        response_body=response_body,
        response_size_bytes=response_size_bytes,
        client_ip=client_ip,
        user_agent=user_agent,
        jwt_sub=jwt_sub,
        jwt_jti=jwt_jti,
        ground_truth=ground_truth
    )

    risk_score, latency_ms = person2_engine.process_telemetry(event)

    # Asynchronously broadcast to connected WebSocket dashboards
    broadcast_payload = {
        "event_type": "TELEMETRY_PROCESSED",
        "telemetry": event.model_dump(),
        "risk": risk_score.model_dump(),
        "latency_ms": round(latency_ms, 3)
    }

    try:
        loop = asyncio.get_running_loop()
        loop.create_task(ws_manager.broadcast_json(broadcast_payload))
    except RuntimeError:
        pass  # No running event loop (e.g., synchronous test runner)

    return risk_score, latency_ms
