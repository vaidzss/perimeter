"""
Inventory & Discovery REST Router for Person 1:
Exposes clean discovery endpoints for Person 2 (Abuse & Risk Engine) and Person 3 (SOC Dashboard):
1. GET /api/inventory/endpoints: Filterable inventory catalog (classification, has_pii)
2. GET /api/inventory/diff-summary: Drift metrics comparing live traffic vs openapi_partial.json
3. GET /api/inventory/endpoints/{endpoint_id}/auto-swagger: Auto-synthesized OpenAPI 3.0 snippet for Shadow APIs
4. GET /api/inventory/logs/recent: Recent structured telemetry logs
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Query, HTTPException, status

from person1_api_discovery.app.inventory_service import inventory_service
from person1_api_discovery.app.middleware import RECENT_TELEMETRY_LOGS

router = APIRouter(prefix="/api/inventory", tags=["API Discovery & Inventory"])


@router.get("/endpoints", response_model=List[Dict[str, Any]])
async def get_discovered_endpoints(
    classification: Optional[str] = Query(
        None,
        description="Filter by classification status: documented, shadow, zombie, unused"
    ),
    has_pii: Optional[bool] = Query(
        None,
        description="Filter by presence of detected PII (true / false)"
    )
):
    """
    Returns filterable catalog of all discovered and documented endpoints
    with detailed metadata: classification, auth, observed PII, traffic metrics,
    and latency distribution.
    """
    return inventory_service.get_all_endpoints(
        classification=classification,
        has_pii=has_pii
    )


@router.get("/diff-summary")
async def get_spec_diff_summary():
    """
    Returns aggregate specification drift summary metrics:
    - total_endpoints
    - total_discovered
    - documented_count
    - shadow_count
    - zombie_count
    - unused_count
    - unauthenticated_count
    - pii_exposing_count
    - spec_drift_detected flag
    """
    return inventory_service.get_diff_summary()


@router.get("/endpoints/{endpoint_id}/auto-swagger")
async def get_endpoint_auto_swagger(endpoint_id: str):
    """
    USP Feature — Auto-Swagger Schema Synthesizer:
    Returns the auto-synthesized OpenAPI 3.0.3 specification snippet for
    any discovered Shadow or Zombie API inferred from live runtime traffic.
    """
    try:
        return inventory_service.generate_auto_swagger(endpoint_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/logs/recent")
async def get_recent_telemetry_logs(
    limit: int = Query(50, ge=1, le=500, description="Maximum number of logs to return (1-500)")
):
    """
    Returns recent structured telemetry logs matching the shared 21-field contract
    so Person 2 (Abuse Engine) or Person 3 (Dashboard) can poll via REST.
    Logs are returned chronologically from newest to oldest.
    """
    logs_list = list(RECENT_TELEMETRY_LOGS)
    sliced = logs_list[-limit:]
    sliced.reverse()
    return {
        "count": len(sliced),
        "total_buffered": len(logs_list),
        "logs": sliced
    }
