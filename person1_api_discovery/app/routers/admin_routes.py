"""
Admin & Internal Shadow Router:
17. GET /api/internal/admin/users-dump (SHADOW API #2 - undocumented, weak/missing role check, leaks all accounts)
18. POST /api/internal/debug/reset-limits (SHADOW API #3 - undocumented, NO AUTH, resets rate limits)
19. GET /api/internal/config/env (SHADOW API #4 - undocumented, NO AUTH, exposes internal feature flags & masked keys)
"""

import datetime
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel

from person1_api_discovery.app.seed_data import USERS_DB, ACCOUNTS_DB

router = APIRouter(prefix="/api/internal", tags=["Internal & Shadow"])


class ResetLimitsPayload(BaseModel):
    scope: Optional[str] = "global"
    target_ip: Optional[str] = None


@router.get("/admin/users-dump")
async def shadow_admin_users_dump(authorization: Optional[str] = Header(None)):
    """
    SHADOW API #2 (Undocumented):
    Internal administrative diagnostic route left exposed without robust role validation.
    Absent from openapi_partial.json. Leaks complete user and account balances.
    """
    all_users = []
    for user_id, user in USERS_DB.items():
        acc = ACCOUNTS_DB.get(user["account_id"], {})
        all_users.append({
            "user_id": user_id,
            "full_name": user["full_name"],
            "role": user["role"],
            "account_id": user["account_id"],
            "balance": acc.get("available_balance", 0.0),
            "pan": user["pan"],
            "phone": user["phone"],
            "email": user["email"],
            "upi_vpa": user["upi_vpa"]
        })

    return {
        "status": "internal_dump_complete",
        "node": "core-banking-primary-worker-01",
        "total_accounts": len(all_users),
        "accounts": all_users
    }


@router.post("/debug/reset-limits")
async def shadow_debug_reset_limits(payload: Optional[ResetLimitsPayload] = None):
    """
    SHADOW API #3 (Undocumented, NO AUTH):
    Developer backdoor left active in production.
    Resets sliding-window rate limit counters for testing.
    Absent from openapi_partial.json.
    """
    scope = payload.scope if payload else "global"
    return {
        "status": "acknowledged",
        "action": "RATE_LIMITS_CLEARED",
        "scope": scope,
        "affected_counters": 128,
        "reset_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "warning": "Internal maintenance endpoint executed without authentication"
    }


@router.get("/config/env")
async def shadow_config_env():
    """
    SHADOW API #4 (Undocumented, NO AUTH):
    Configuration and feature flag disclosure endpoint.
    Absent from openapi_partial.json.
    Exposes internal architecture, service mesh routes, and environment settings.
    """
    return {
        "environment": "fintech-core-prod-ap-south",
        "debug_flags": {
            "allow_legacy_v1_export": True,
            "bypass_waf_in_staging": False,
            "enable_synthetic_honeypots": True,
            "rate_limit_redis_cluster": "redis://mesh-redis.internal:6379/0"
        },
        "service_dependencies": {
            "npci_upi_gateway": "https://upi-switch.internal.npci.org.in/v2",
            "cibil_credit_bureau": "https://bureau-api.cibil.mesh:8443",
            "rbi_neft_clearing": "https://neft-clearing.rbi.org.in/rtgs/v1"
        },
        "build_version": "v2.1.0-rc4-shadow",
        "database_backend": "PostgreSQL 16 (Async Engine)",
        "security_policy": "STRICT_OPENAPI_ENFORCEMENT_REQUIRED"
    }
