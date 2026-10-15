import os
import json
import asyncio
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Query, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Configuration
USE_MOCK = os.getenv("USE_MOCK", "true").lower() in ("true", "1", "yes")
MOCK_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mock"))

app = FastAPI(
    title="CC6-IC07 Security Dashboard API",
    description="Read-only query API over shared SQLite/PostgreSQL for API Discovery, Security & Abuse Prevention",
    version="1.0.0"
)

# Enable CORS for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper to load mock JSON
def load_mock(filename: str) -> Any:
    filepath = os.path.join(MOCK_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=500, detail=f"Mock file {filename} not found at {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

# Models for request bodies
class AlertStatusUpdate(BaseModel):
    status: str  # "open" | "investigating" | "resolved"

# ========================================================
# REST ENDPOINTS (Frozen Data Contracts)
# ========================================================

# 1. GET /api/health
@app.get("/api/health")
def get_health():
    return {
        "status": "healthy",
        "service": "CC6-IC07 Security Dashboard API",
        "use_mock": USE_MOCK,
        "database": "sqlite_ready"
    }

# 2. GET /api/posture
@app.get("/api/posture")
def get_posture():
    return load_mock("posture.json")

# 3. GET /api/inventory
@app.get("/api/inventory")
def get_inventory(
    status: Optional[str] = Query(None),
    auth: Optional[str] = Query(None),
    sensitive: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    sort: Optional[str] = Query("risk_desc")
):
    items: List[Dict[str, Any]] = load_mock("inventory.json")
    
    if q:
        query = q.lower()
        items = [
            i for i in items
            if query in i["path_template"].lower()
            or query in i["api_id"].lower()
            or any(query in s.lower() for s in i.get("sensitive_types", []))
        ]
    if status and status != "all":
        items = [i for i in items if i.get("status") == status]
    if auth and auth != "all":
        items = [i for i in items if i.get("auth_type") == auth]
    if sensitive and sensitive != "all":
        items = [i for i in items if sensitive in i.get("sensitive_types", [])]

    if sort == "risk_desc":
        items.sort(key=lambda x: x.get("risk_score", 0), reverse=True)
    elif sort == "risk_asc":
        items.sort(key=lambda x: x.get("risk_score", 0))
    elif sort == "requests_desc":
        items.sort(key=lambda x: x.get("request_count", 0), reverse=True)

    return items

# 4. GET /api/inventory/{api_id}
@app.get("/api/inventory/{api_id}")
def get_inventory_item(api_id: str = Path(...)):
    items = load_mock("inventory.json")
    item = next((i for i in items if i["api_id"] == api_id), None)
    if not item:
        item = items[0]

    risk_scores = load_mock("risk_scores.json")
    risk = risk_scores.get(api_id, {
        "api_id": api_id,
        "score": item.get("risk_score", 50),
        "level": "high",
        "breakdown": []
    })

    baselines = load_mock("baselines.json")
    item_baselines = baselines.get(api_id, [])

    alerts = load_mock("alerts.json")
    related_alerts = [a for a in alerts if item["path_template"] in a["api"]]

    return {
        "inventory_item": item,
        "risk_breakdown": risk,
        "baselines": item_baselines,
        "related_alerts": related_alerts
    }

# 5. GET /api/alerts
@app.get("/api/alerts")
def get_alerts(
    severity: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    api: Optional[str] = Query(None),
    actor: Optional[str] = Query(None),
    from_date: Optional[str] = Query(None, alias="from"),
    to_date: Optional[str] = Query(None, alias="to")
):
    alerts: List[Dict[str, Any]] = load_mock("alerts.json")
    
    if severity and severity != "all":
        alerts = [a for a in alerts if a.get("severity") == severity]
    if type and type != "all":
        alerts = [a for a in alerts if a.get("type") == type]
    if status and status != "all":
        alerts = [a for a in alerts if a.get("status") == status]
    if api:
        alerts = [a for a in alerts if api.lower() in a.get("api", "").lower()]
    if actor:
        alerts = [a for a in alerts if actor.lower() in a.get("actor", "").lower()]

    return alerts

# 6. GET /api/alerts/{id}
@app.get("/api/alerts/{id}")
def get_alert_by_id(id: str = Path(...)):
    alerts = load_mock("alerts.json")
    alert = next((a for a in alerts if a["alert_id"] == id), None)
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert {id} not found")
    return alert

# 7. GET /api/alerts/{id}/requests
@app.get("/api/alerts/{id}/requests")
def get_alert_requests(id: str = Path(...)):
    all_requests = load_mock("requests.json")
    prefix = f"req-{id.replace('-', '')}-"
    matches = [r for r in all_requests if r["request_id"].startswith(prefix)]
    if matches:
        return matches
    return all_requests[:40]

# 8. GET /api/actors/{actor}/activity
@app.get("/api/actors/{actor}/activity")
def get_actor_activity(actor: str = Path(...)):
    all_requests = load_mock("requests.json")
    actor_reqs = [
        r for r in all_requests
        if r.get("user_id") == actor
        or r.get("token_id") == actor
        or r.get("client_ip") == actor
    ]
    if not actor_reqs:
        actor_reqs = all_requests[:40]

    endpoints_map: Dict[str, Dict[str, Any]] = {}
    ips = set()
    uas = set()

    for r in actor_reqs:
        ips.add(r["client_ip"])
        uas.add(r["user_agent"])
        key = f"{r['method']} {r['path_template']}"
        if key not in endpoints_map:
            endpoints_map[key] = {"path_template": r["path_template"], "method": r["method"], "count": 0}
        endpoints_map[key]["count"] += 1

    return {
        "actor": actor,
        "total_requests": len(actor_reqs),
        "distinct_endpoints": len(endpoints_map),
        "requests": actor_reqs,
        "endpoints_hit": list(endpoints_map.values()),
        "ip_changes": list(ips),
        "user_agents": list(uas)
    }

# 9. PATCH /api/alerts/{id}
@app.patch("/api/alerts/{id}")
def update_alert_status(id: str = Path(...), body: AlertStatusUpdate = ...):
    alerts = load_mock("alerts.json")
    alert = next((a for a in alerts if a["alert_id"] == id), None)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert["status"] = body.status
    return {
        "success": True,
        "alert_id": id,
        "status": body.status
    }

# 10. GET /api/risk/{api_id}
@app.get("/api/risk/{api_id}")
def get_risk(api_id: str = Path(...)):
    risk_scores = load_mock("risk_scores.json")
    if api_id in risk_scores:
        return risk_scores[api_id]
    return {
        "api_id": api_id,
        "score": 50,
        "level": "medium",
        "breakdown": []
    }

# 11. GET /api/traffic/stats
@app.get("/api/traffic/stats")
def get_traffic_stats(window: str = Query("1h")):
    stats = load_mock("traffic_stats.json")
    stats["window"] = window
    return stats

# 12. GET /api/evaluation
@app.get("/api/evaluation")
def get_evaluation():
    return load_mock("evaluation.json")

# 13. SSE /api/stream/alerts for live alert push
@app.get("/api/stream/alerts")
async def stream_alerts():
    async def event_generator():
        alerts = load_mock("alerts.json")
        idx = 0
        while True:
            await asyncio.sleep(5)
            sample_alert = alerts[idx % len(alerts)]
            idx += 1
            data = json.dumps({"event": "NEW_ALERT", "alert": sample_alert})
            yield f"data: {data}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
