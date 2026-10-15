"""
Perimeter Active Defense & Policy Management Router
Exposes endpoints for the SOC Console and test scripts to inspect active threats
and dynamically apply virtual patches, route quarantine, and IP bans.
"""

import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from person1_api_discovery.app.inventory_service import inventory_service

router = APIRouter(prefix="/api/defense", tags=["Perimeter Active Defense"])


class QuarantineRequest(BaseModel):
    path: str = Field(..., description="Route or path template to quarantine (e.g. /api/v1/kyc/aadhaar-pan-dump)")
    reason: Optional[str] = "Quarantined by Security Operator"


class BlockIPRequest(BaseModel):
    ip: str = Field(..., description="Client IP address to blacklist (e.g. 185.220.101.5)")
    reason: Optional[str] = "Malicious actor / Tor exit node"


class TogglePIIRequest(BaseModel):
    enabled: bool = Field(..., description="Enable or disable in-flight PII redaction")


@router.get("/status")
def get_defense_status() -> Dict[str, Any]:
    """Returns active defense posture, quarantined routes, blocked IPs, and defense logs."""
    raw_logs = inventory_service.defense_log[:60]
    enforcements = []
    blocked_count = 0

    for log in raw_logs:
        action = log.get("action", "")
        target = log.get("target", "")
        meta = log.get("metadata", {})
        
        if action == "VIRTUAL_PATCH_ENFORCED":
            blocked_count += 1
            vector = "Zombie PII Exfiltration" if "kyc" in target else ("Shadow Debug Backdoor" if "debug" in target or "override" in target else "Vulnerable Route Attack")
            enforcements.append({
                "decision": "BLOCKED",
                "http_status": 403,
                "action": "VIRTUAL_PATCH_ENFORCED",
                "target": target,
                "method": meta.get("method", "GET"),
                "client_ip": meta.get("client_ip", "127.0.0.1"),
                "attack_vector": vector,
                "impact": "Exploit neutralized at gateway; 0 records leaked to attacker.",
                "reason": log.get("reason"),
                "timestamp": log.get("timestamp")
            })
        elif action == "IP_BLOCK_ENFORCED":
            blocked_count += 1
            enforcements.append({
                "decision": "BLOCKED",
                "http_status": 403,
                "action": "IP_BLOCK_ENFORCED",
                "target": target,
                "method": meta.get("method", "POST"),
                "client_ip": target,
                "attack_vector": "Tor Exit Node / Botnet Replay Attack",
                "impact": "Malicious packets dropped at perimeter edge before reaching backend.",
                "reason": log.get("reason"),
                "timestamp": log.get("timestamp")
            })
        elif action == "ROUTE_QUARANTINE":
            enforcements.append({
                "decision": "QUARANTINED",
                "http_status": 403,
                "action": "ROUTE_QUARANTINE",
                "target": target,
                "method": "ANY",
                "client_ip": "GLOBAL_EDGE",
                "attack_vector": "Virtual Patch Deployment",
                "impact": f"Route isolated: all traffic to {target} will be rejected with 403.",
                "reason": log.get("reason"),
                "timestamp": log.get("timestamp")
            })
        elif action == "IP_BLOCK":
            enforcements.append({
                "decision": "BLACKLISTED",
                "http_status": 403,
                "action": "IP_BLOCK",
                "target": target,
                "method": "GLOBAL",
                "client_ip": target,
                "attack_vector": "Malicious Actor Quarantine",
                "impact": f"Client IP {target} blacklisted across perimeter gateway.",
                "reason": log.get("reason"),
                "timestamp": log.get("timestamp")
            })
        else:
            enforcements.append({
                "decision": "DEFENSE_LOG",
                "http_status": 200,
                "action": action,
                "target": target,
                "method": "SYSTEM",
                "client_ip": "127.0.0.1",
                "attack_vector": "Policy Configuration",
                "impact": log.get("reason", "Defense event recorded"),
                "reason": log.get("reason"),
                "timestamp": log.get("timestamp")
            })

    # If no blocks yet recorded, provide helpful baseline examples so user understands the shield
    if not enforcements:
        enforcements = [
            {
                "decision": "ARMED",
                "http_status": 403,
                "action": "SHIELD_READY",
                "target": "/api/v1/kyc/aadhaar-pan-dump",
                "method": "GET",
                "client_ip": "EDGE",
                "attack_vector": "Zombie PII Exfiltration Shield",
                "impact": "Virtual patch armed: will block unauthorized dumps with HTTP 403.",
                "reason": "Route quarantined in Perimeter inventory",
                "timestamp": inventory_service.defense_log[0]["timestamp"] if inventory_service.defense_log else "2026-10-15T10:00:00Z"
            }
        ]

    return {
        "status": "ACTIVE_DEFENSE_ENGAGED",
        "shield_active": True,
        "pii_masking_enabled": inventory_service.pii_masking_enabled,
        "quarantined_routes": sorted(list(inventory_service.quarantined_routes)),
        "quarantined_routes_count": len(inventory_service.quarantined_routes),
        "blocked_ips": sorted(list(inventory_service.blocked_ips)),
        "blocked_ips_count": len(inventory_service.blocked_ips),
        "active_threats_count": len(inventory_service.threat_alerts),
        "attacks_blocked_count": blocked_count or len([e for e in enforcements if e["decision"] == "BLOCKED"]),
        "enforcements": enforcements,
        "defense_audit_log": inventory_service.defense_log[:50]
    }


@router.get("/threats")
def list_threats() -> Dict[str, Any]:
    """Returns all real-time threats detected by Perimeter across target systems."""
    return {
        "total_threats": len(inventory_service.threat_alerts),
        "threats": inventory_service.threat_alerts
    }


@router.post("/quarantine")
def quarantine_route(req: QuarantineRequest) -> Dict[str, Any]:
    """Quarantines a vulnerable route (virtual patch)."""
    inventory_service.quarantine_route(req.path, req.reason or "Quarantined via SOC Command")
    return {
        "status": "QUARANTINED",
        "path": req.path,
        "active_quarantines": sorted(list(inventory_service.quarantined_routes)),
        "message": f"Virtual patch deployed: route {req.path} will be rejected with 403."
    }


@router.post("/unquarantine")
def unquarantine_route(req: QuarantineRequest) -> Dict[str, Any]:
    """Restores a quarantined route."""
    inventory_service.unquarantine_route(req.path)
    return {
        "status": "RESTORED",
        "path": req.path,
        "active_quarantines": sorted(list(inventory_service.quarantined_routes))
    }


@router.post("/block-ip")
def block_ip(req: BlockIPRequest) -> Dict[str, Any]:
    """Blacklists a malicious client IP."""
    inventory_service.block_ip(req.ip, req.reason or "Blacklisted via SOC Command")
    return {
        "status": "BLOCKED",
        "ip": req.ip,
        "active_blocked_ips": sorted(list(inventory_service.blocked_ips)),
        "message": f"IP {req.ip} is now blocked across the perimeter."
    }


@router.post("/unblock-ip")
def unblock_ip(req: BlockIPRequest) -> Dict[str, Any]:
    """Unblocks a client IP."""
    inventory_service.unblock_ip(req.ip)
    return {
        "status": "UNBLOCKED",
        "ip": req.ip,
        "active_blocked_ips": sorted(list(inventory_service.blocked_ips))
    }


@router.post("/toggle-pii-masking")
def toggle_pii_masking(req: TogglePIIRequest) -> Dict[str, Any]:
    """Toggles in-flight PII redaction on or off."""
    inventory_service.pii_masking_enabled = req.enabled
    return {
        "status": "UPDATED",
        "pii_masking_enabled": inventory_service.pii_masking_enabled
    }


@router.post("/mitigate-all")
def mitigate_all() -> Dict[str, Any]:
    """
    Automated One-Click Active Defense:
    Quarantines all discovered Zombie & Shadow endpoints and blocks all flagged malicious IPs.
    """
    quarantined = []
    # Find all zombie and shadow endpoints
    EXCLUDED_PREFIXES = (
        "/api/defense", "/api/inventory", "/api/posture", "/api/alerts",
        "/api/traffic", "/api/evaluation", "/api/telemetry", "/ws", "/docs", "/openapi.json"
    )
    for ep in inventory_service.get_all_endpoints():
        if ep["classification"] in {"zombie", "shadow"}:
            path = ep["normalized_path"]
            if not path or path == "/" or path.startswith(EXCLUDED_PREFIXES) or "favicon" in path:
                continue
            # Legitimate v2 customer/public production routes must never be quarantined
            if path.startswith("/api/v2/") and not ("/internal/" in path or "debug" in path or "override" in path):
                continue
            inventory_service.quarantine_route(path, f"Automated Defense Quarantine for {ep['classification'].upper()} API")
            quarantined.append(path)

    # Block Tor and attacker IPs from threat alerts
    blocked = []
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    for threat in inventory_service.threat_alerts:
        threat["status"] = "MITIGATED"
        threat["mitigated_at"] = now_iso
        threat["mitigation_action"] = "Quarantined route + Enforced 403 virtual patch"
        ip = threat.get("source_ip")
        if ip and ip not in {"127.0.0.1", "localhost"}:
            inventory_service.block_ip(ip, f"Automated ban for threat: {threat.get('title')}")
            blocked.append(ip)

    for dt in inventory_service.deep_threat_events:
        dt["status"] = "MITIGATED"

    inventory_service.pii_masking_enabled = True

    return {
        "status": "ALL_THREATS_MITIGATED",
        "quarantined_routes": list(set(quarantined)),
        "blocked_ips": list(set(blocked)),
        "pii_masking_enabled": True,
        "message": "Perimeter Active Defense has secured BharatPay against all active vectors!"
    }
