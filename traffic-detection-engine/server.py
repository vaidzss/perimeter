"""
FastAPI Server for Layer 2: Core Discovery, Abuse Detection & Risk Engine.
Provides REST ingestion & queries, plus WebSocket live feed for the SOC Command Center.
"""

import os
import json
import asyncio
from typing import List, Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.models import TelemetryEvent, RiskScore
from pipeline import CoreDetectionEngine

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SPEC_PATH = os.path.join(BASE_DIR, "config", "openapi.json")
DB_PATH = os.path.join(BASE_DIR, "telemetry.db")

app = FastAPI(
    title="API Discovery, Shadow Detection & Runtime Abuse Prevention Engine",
    version="1.0.0",
    description="Layer 2 Engine matching CC6-IC07 Blueprint."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Engine
engine = CoreDetectionEngine(openapi_spec_path=SPEC_PATH, db_path=DB_PATH)


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
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except Exception:
                disconnected.append(connection)
        for dead in disconnected:
            self.active_connections.discard(dead)


ws_manager = WebSocketManager()


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "engine": "Layer 2 Core Discovery, Abuse & Risk Engine",
        "spec_loaded": os.path.exists(SPEC_PATH)
    }


@app.post("/api/telemetry")
async def ingest_telemetry(event: TelemetryEvent):
    """
    Ingests mirrored HTTP telemetry from API Gateway.
    Processes Box A, Box B, Box C and broadcasts to SOC.
    """
    risk_score, latency_ms = engine.process_telemetry(event)

    broadcast_payload = {
        "event_type": "TELEMETRY_PROCESSED",
        "telemetry": event.model_dump(),
        "risk": risk_score.model_dump(),
        "latency_ms": round(latency_ms, 3)
    }

    # Broadcast asynchronously without blocking HTTP response
    asyncio.create_task(ws_manager.broadcast_json(broadcast_payload))

    return {
        "status": "processed",
        "request_id": event.request_id,
        "risk_score": risk_score.risk_score,
        "severity": risk_score.severity,
        "spec_status": risk_score.spec_status.value,
        "reason_vector": risk_score.reason_vector,
        "latency_ms": round(latency_ms, 3)
    }


@app.get("/api/inventory")
def get_inventory():
    """Returns auto-discovered API inventory table with Shadow/Zombie tags."""
    return engine.get_inventory()


@app.get("/api/session-graph/{session_id}")
def get_session_graph(session_id: str):
    """Returns Directed Behavioral Graph (nodes & edges) for SOC visualization."""
    return engine.get_session_graph(session_id)


@app.get("/api/alerts")
def get_alerts(min_score: int = 60, limit: int = 50):
    """Returns recent alerts for SOC Command Center Alert Queue."""
    return engine.get_recent_alerts(min_score=min_score, limit=limit)


@app.get("/api/metrics/confusion-matrix")
def get_confusion_matrix():
    """Returns live TPR, FPR, and raw TP/FP/TN/FN counters."""
    return engine.get_confusion_matrix()


@app.websocket("/ws/telemetry")
async def websocket_telemetry_stream(websocket: WebSocket):
    """Real-time push stream for SOC Command Center dashboard."""
    await ws_manager.connect(websocket)
    try:
        # Send initial snapshot of matrix and inventory
        snapshot = {
            "event_type": "INITIAL_SNAPSHOT",
            "confusion_matrix": engine.get_confusion_matrix(),
            "inventory_count": len(engine.get_inventory())
        }
        await websocket.send_json(snapshot)
        while True:
            # Keep connection open, client can send pings
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)
