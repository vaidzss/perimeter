"""
Person 1 FastAPI Test Banking Application.
Exposes 19 realistic endpoints across 8 functional banking domains:
- Auth (2 endpoints)
- Users (2 endpoints)
- Accounts (3 endpoints - BOLA vulnerable)
- Transactions (2 endpoints - BOLA vulnerable)
- Payments (3 endpoints - includes unused scheduled payments)
- Search (2 endpoints - includes public IFSC lookup)
- Export & Legacy V1 (2 endpoints - includes Zombie export & Shadow passbook)
- Admin & Internal (3 Shadow endpoints - includes debug reset & config leak)
"""

import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from person1_api_discovery.app.routers.auth_routes import router as auth_router
from person1_api_discovery.app.routers.user_routes import router as user_router
from person1_api_discovery.app.routers.account_routes import router as account_router
from person1_api_discovery.app.routers.transaction_routes import router as transaction_router
from person1_api_discovery.app.routers.payment_routes import router as payment_router
from person1_api_discovery.app.routers.search_routes import router as search_router
from person1_api_discovery.app.routers.export_routes import router as export_router
from person1_api_discovery.app.routers.admin_routes import router as admin_router

app = FastAPI(
    title="FinTech DPI Core Test Banking Service",
    description="Test Banking API with 19 realistic endpoints, JWT Auth, synthetic Indian PII, BOLA, Zombie, and Shadow routes.",
    version="2.1.0"
)

import os
from person1_api_discovery.app.inventory_service import inventory_service

# Load BharatPay's documented OpenAPI specification
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
bharatpay_spec = os.path.join(ROOT_DIR, "frontend", "bharatpay", "spec", "openapi.json")
if os.path.exists(bharatpay_spec):
    inventory_service.load_additional_spec(bharatpay_spec)

from person1_api_discovery.app.middleware import StructuredTelemetryMiddleware

# Standard CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Structured Telemetry Middleware
app.add_middleware(StructuredTelemetryMiddleware)

from person1_api_discovery.app.routers.inventory_router import router as inventory_router
from person1_api_discovery.app.routers.dashboard_compat_router import router as dashboard_router
from person1_api_discovery.app.routers.defense_router import router as defense_router
from person1_api_discovery.app.gateway import forward_through_perimeter
from fastapi import Request

# Include all 8 banking domain routers + Discovery Inventory Router + Dashboard Adapter + Active Defense
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(account_router)
app.include_router(transaction_router)
app.include_router(payment_router)
app.include_router(search_router)
app.include_router(export_router)
app.include_router(admin_router)
app.include_router(inventory_router)
app.include_router(dashboard_router)
app.include_router(defense_router)


from person1_api_discovery.app.person2_bridge import ws_manager, person2_engine, TelemetryEvent
from fastapi import WebSocket, WebSocketDisconnect


@app.post("/api/telemetry", tags=["Person 2 Telemetry Engine"])
async def ingest_telemetry_endpoint(event: TelemetryEvent):
    """Direct ingestion endpoint for Person 2's TelemetryEvent matching CC6-IC07 contract."""
    risk_score, latency_ms = person2_engine.process_telemetry(event)
    return {
        "status": "processed",
        "request_id": event.request_id,
        "risk_score": risk_score.risk_score,
        "severity": risk_score.severity,
        "spec_status": risk_score.spec_status.value,
        "reason_vector": risk_score.reason_vector,
        "latency_ms": round(latency_ms, 3)
    }


@app.get("/api/metrics/confusion-matrix", tags=["Person 2 Telemetry Engine"])
def get_confusion_matrix_endpoint():
    """Returns live TPR, FPR, and raw TP/FP/TN/FN counters from Person 2's engine."""
    return person2_engine.get_confusion_matrix()


@app.get("/api/session-graph/{session_id}", tags=["Person 2 Telemetry Engine"])
def get_session_graph_endpoint(session_id: str):
    """Returns Directed Behavioral Graph (nodes & edges) for SOC visualization."""
    return person2_engine.get_session_graph(session_id)


@app.websocket("/ws/telemetry")
async def websocket_telemetry_stream(websocket: WebSocket):
    """Real-time push stream for SOC Command Center dashboard."""
    await ws_manager.connect(websocket)
    try:
        snapshot = {
            "event_type": "INITIAL_SNAPSHOT",
            "confusion_matrix": person2_engine.get_confusion_matrix(),
            "inventory_count": len(person2_engine.get_inventory())
        }
        await websocket.send_json(snapshot)
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)


# Fallback Perimeter Gateway Forwarder for unrouted BharatPay API requests
@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def fallback_gateway_router(request: Request, path: str):
    """
    Directs unrouted API requests through the Perimeter Active Defense Gateway
    to upstream target services (BharatPay on Port 8001).
    """
    return await forward_through_perimeter(request)


@app.get("/health", tags=["Health"])
async def health_check():
    """Service health and readiness check."""
    return {
        "status": "healthy",
        "service": "person1-banking-testbed",
        "version": "2.1.0",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("person1_api_discovery.app.main:app", host="0.0.0.0", port=8000, reload=True)
