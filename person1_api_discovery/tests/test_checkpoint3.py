"""
Checkpoint 3 Test Suite & Reviewer:
1. Path Normalization Engine:
   - Evaluates spec template matching against openapi_partial.json
   - Verifies collapse of multiple account IDs (1001, 1005) into single normalized record
   - Evaluates uncataloged shadow route parameterization
2. Inventory & Spec-Diff Service:
   - Validates all 4 classifications: 'documented', 'shadow', 'zombie', 'unused'
   - Verifies diff summary metrics (total discovered, drift detection)
3. USP Feature - Auto-Swagger Schema Synthesizer:
   - Generates valid OpenAPI 3.0 path specification for Shadow and Zombie APIs
   - Validates inferred parameters, auth security, and response JSON schema properties
"""

import os
import json
import pytest
from httpx import AsyncClient, ASGITransport

from person1_api_discovery.app.main import app
from person1_api_discovery.app.normalizer import normalize_path
from person1_api_discovery.app.inventory_service import inventory_service, generate_endpoint_id


@pytest.fixture
def anyio_backend():
    return "asyncio"


def test_path_normalization_spec_matching():
    """Verify paths map accurately to openapi_partial.json templates."""
    # 1. Accounts template
    norm_acc, params_acc = normalize_path("/api/v2/accounts/1004")
    assert norm_acc == "/api/v2/accounts/{account_id}"
    assert params_acc == {"account_id": "1004"}

    # 2. Account transactions template
    norm_txn, params_txn = normalize_path("/api/v2/accounts/1004/transactions")
    assert norm_txn == "/api/v2/accounts/{account_id}/transactions"
    assert params_txn == {"account_id": "1004"}

    # 3. Receipt template
    norm_rcp, params_rcp = normalize_path("/api/v2/transactions/TXN100101/receipt")
    assert norm_rcp == "/api/v2/transactions/{txn_id}/receipt"
    assert params_rcp == {"txn_id": "TXN100101"}

    # 4. Collapse verification: multiple IDs collapse to the EXACT same template
    norm_a, _ = normalize_path("/api/v2/accounts/1001")
    norm_b, _ = normalize_path("/api/v2/accounts/1025")
    assert norm_a == norm_b == "/api/v2/accounts/{account_id}"

    # 5. Shadow route fallback collapse
    norm_shadow, params_shadow = normalize_path("/api/v1/accounts/1004/passbook-dump")
    assert norm_shadow == "/api/v1/accounts/{account_id}/passbook-dump"
    assert params_shadow == {"account_id": "1004"}


@pytest.mark.anyio
async def test_inventory_spec_diff_classifications():
    """Verify live traffic populates all 4 classifications (documented, shadow, zombie, unused)."""
    # Reset inventory state before run
    inventory_service.reset_inventory()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. DOCUMENTED: Login & Accounts
        login_res = await client.post(
            "/api/v2/auth/login",
            json={"username": "user_1001", "password": "pass123"}
        )
        token = login_res.json()["access_token"]
        auth_h = {"Authorization": f"Bearer {token}"}

        # Hit documented endpoints multiple times with different IDs
        await client.get("/api/v2/accounts/1001", headers=auth_h)
        await client.get("/api/v2/accounts/1005", headers=auth_h)
        await client.get("/api/v2/accounts/1001/transactions", headers=auth_h)

        # 2. ZOMBIE: Deprecated V1 Bulk Export
        await client.get("/api/v1/users/export")

        # 3. SHADOW: Uncataloged passbook dump & internal debug/config routes
        await client.get("/api/v1/accounts/1001/passbook-dump", headers=auth_h)
        await client.get("/api/internal/config/env")
        await client.post("/api/internal/debug/reset-limits", json={"scope": "cluster"})

        # (NOTE: /api/v2/payments/scheduled and /api/v2/accounts/{account_id}/close are intentionally NEVER called)

    # Inspect all inventory endpoints
    endpoints = inventory_service.get_all_endpoints()
    endpoints_by_path = {f"{e['method']} {e['normalized_path']}": e for e in endpoints}

    # Verify DOCUMENTED
    assert "GET /api/v2/accounts/{account_id}" in endpoints_by_path
    doc_ep = endpoints_by_path["GET /api/v2/accounts/{account_id}"]
    assert doc_ep["classification"] == "documented"
    assert doc_ep["hit_count"] == 2  # 1001 and 1005 collapsed into single record!
    assert len(doc_ep["sample_raw_paths"]) == 2

    # Verify ZOMBIE
    assert "GET /api/v1/users/export" in endpoints_by_path
    zombie_ep = endpoints_by_path["GET /api/v1/users/export"]
    assert zombie_ep["classification"] == "zombie"
    assert zombie_ep["hit_count"] >= 1
    assert set(zombie_ep["pii_fields_exposed"]) >= {"PAN", "PHONE", "UPI_VPA"}

    # Verify SHADOW
    assert "GET /api/internal/config/env" in endpoints_by_path
    shadow_ep = endpoints_by_path["GET /api/internal/config/env"]
    assert shadow_ep["classification"] == "shadow"
    assert shadow_ep["hit_count"] >= 1

    assert "GET /api/v1/accounts/{account_id}/passbook-dump" in endpoints_by_path
    shadow_pb = endpoints_by_path["GET /api/v1/accounts/{account_id}/passbook-dump"]
    assert shadow_pb["classification"] == "shadow"

    # Verify UNUSED
    assert "GET /api/v2/payments/scheduled" in endpoints_by_path
    unused_ep1 = endpoints_by_path["GET /api/v2/payments/scheduled"]
    assert unused_ep1["classification"] == "unused"
    assert unused_ep1["hit_count"] == 0

    assert "DELETE /api/v2/accounts/{account_id}/close" in endpoints_by_path
    unused_ep2 = endpoints_by_path["DELETE /api/v2/accounts/{account_id}/close"]
    assert unused_ep2["classification"] == "unused"
    assert unused_ep2["hit_count"] == 0

    # Verify Diff Summary Metrics
    summary = inventory_service.get_diff_summary()
    assert summary["documented_count"] >= 3
    assert summary["zombie_count"] >= 1
    assert summary["shadow_count"] >= 3
    assert summary["unused_count"] >= 2
    assert summary["spec_drift_detected"] is True
    assert summary["total_discovered"] >= 7


def test_auto_swagger_schema_synthesizer_usp():
    """Verify Auto-Swagger USP produces valid OpenAPI 3.0 path snippets for Shadow APIs."""
    # Lookup the shadow config/env endpoint
    ep_id = generate_endpoint_id("GET", "/api/internal/config/env")
    swagger = inventory_service.generate_auto_swagger(ep_id)

    assert swagger["openapi"] == "3.0.3"
    assert "/api/internal/config/env" in swagger["paths"]
    op = swagger["paths"]["/api/internal/config/env"]["get"]

    assert "Auto-Synthesized" in op["summary"]
    assert "responses" in op
    assert "200" in op["responses"]
    schema = op["responses"]["200"]["content"]["application/json"]["schema"]

    # Verify inferred schema types from live response
    assert schema["type"] == "object"
    assert "environment" in schema["properties"]
    assert schema["properties"]["environment"]["type"] == "string"
    assert "debug_flags" in schema["properties"]

    # Verify Auto-Swagger for Shadow Passbook with path parameters & auth
    pb_id = generate_endpoint_id("GET", "/api/v1/accounts/{account_id}/passbook-dump")
    pb_swagger = inventory_service.generate_auto_swagger(pb_id)
    pb_op = pb_swagger["paths"]["/api/v1/accounts/{account_id}/passbook-dump"]["get"]

    assert len(pb_op["parameters"]) == 1
    param = pb_op["parameters"][0]
    assert param["name"] == "account_id"
    assert param["in"] == "path"
    assert param["required"] is True

    # Security inferred
    assert pb_op["security"] == [{"BearerAuth": []}]

    # Inferred response properties
    pb_schema = pb_op["responses"]["200"]["content"]["application/json"]["schema"]
    assert pb_schema["type"] == "object"
    assert "passbook_series" in pb_schema["properties"]
    assert "pan" in pb_schema["properties"]
    assert "available_balance" in pb_schema["properties"]
