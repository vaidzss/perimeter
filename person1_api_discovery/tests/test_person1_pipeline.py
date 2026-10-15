"""
Comprehensive End-to-End Verification Pipeline for Person 1:
Validates the entire pipeline:
1. Banking API Endpoints & Authentication
2. Structured Telemetry Middleware & JSONL Stream
3. Path Normalization & Entity Collapse (/accounts/1001 and /accounts/1005 -> single record)
4. All 4 Spec-Diff Classifications (documented, shadow, zombie, unused)
5. Passive PII Detection (PAN, GOVT_ID_LIKE, PHONE, UPI_VPA, EMAIL)
6. Inventory REST APIs (endpoints filtering, diff-summary, recent logs)
7. USP Feature: Auto-Swagger Schema Synthesizer for Shadow & Zombie APIs
"""

import os
import json
import pytest
from httpx import AsyncClient, ASGITransport

from person1_api_discovery.app.main import app
from person1_api_discovery.app.inventory_service import inventory_service, generate_endpoint_id
from person1_api_discovery.app.middleware import LOG_FILE_PATH, RECENT_TELEMETRY_LOGS

REQUIRED_LOG_FIELDS = {
    "event_id", "timestamp", "client_ip", "user_agent", "method", "raw_path",
    "normalized_path", "query_params", "path_params_extracted", "auth_type",
    "jwt_sub", "jwt_role", "jwt_jti", "status_code", "req_bytes", "res_bytes",
    "latency_ms", "pii_fields_detected", "ground_truth_label", "raw_request_headers",
    "raw_response_sample"
}


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_complete_person1_pipeline():
    # 0. Reset inventory and logs for fresh baseline
    inventory_service.reset_inventory()
    RECENT_TELEMETRY_LOGS.clear()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # =====================================================================
        # PHASE 1: GENERATE TRAFFIC MIX
        # =====================================================================

        # 1. Documented: Auth login
        login_resp = await client.post(
            "/api/v2/auth/login",
            json={"username": "user_1001", "password": "pass123"},
            headers={"User-Agent": "FinTech-Client/1.0", "X-Ground-Truth": "benign"}
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        auth_h = {"Authorization": f"Bearer {token}"}

        # 2. Documented: User me
        me_resp = await client.get("/api/v2/users/me", headers=auth_h)
        assert me_resp.status_code == 200

        # 3. Documented + BOLA: Multiple Accounts (1001 and 1005) to verify entity collapse
        acc1_resp = await client.get("/api/v2/accounts/1001", headers=auth_h)
        assert acc1_resp.status_code == 200

        acc5_resp = await client.get(
            "/api/v2/accounts/1005",
            headers={**auth_h, "X-Ground-Truth": "attack_bola"}
        )
        assert acc5_resp.status_code == 200

        # 4. Documented: Transactions & Receipts
        txns_resp = await client.get("/api/v2/accounts/1001/transactions", headers=auth_h)
        assert txns_resp.status_code == 200

        rcp_resp = await client.get("/api/v2/transactions/TXN100101/receipt", headers=auth_h)
        assert rcp_resp.status_code == 200

        # 5. Documented: Auth refresh, contact, statements, beneficiaries, payments
        await client.post("/api/v2/auth/refresh", headers=auth_h)
        await client.put("/api/v2/users/me/contact", headers=auth_h, json={"phone": "+91-9876501001"})
        await client.get("/api/v2/accounts/1001/statements", headers=auth_h)
        await client.post("/api/v2/accounts/beneficiaries", headers=auth_h, json={"name": "Kavya", "account_number": "ACCN-IN-1010", "ifsc": "HDFC0001234"})
        await client.post("/api/v2/payments/upi-transfer", headers=auth_h, json={"payee_vpa": "vendor@okaxis", "amount": 100.0})

        # 6. Documented: Merchants search (scraping simulation)
        mrc_resp = await client.get(
            "/api/v2/search/merchants?page=1&limit=5",
            headers={**auth_h, "X-Ground-Truth": "attack_scraping"}
        )
        assert mrc_resp.status_code == 200

        # 6. Zombie API: Legacy bulk users export (NO AUTH #2)
        zombie_resp = await client.get("/api/v1/users/export")
        assert zombie_resp.status_code == 200

        # 7. Shadow API #1: Passbook dump
        pb_resp = await client.get(
            "/api/v1/accounts/1001/passbook-dump",
            headers={**auth_h, "X-Ground-Truth": "attack_shadow"}
        )
        assert pb_resp.status_code == 200

        # 8. Shadow API #2: Admin users dump
        admin_resp = await client.get("/api/internal/admin/users-dump")
        assert admin_resp.status_code == 200

        # 9. Shadow API #3: Debug reset limits
        reset_resp = await client.post("/api/internal/debug/reset-limits", json={"scope": "worker-1"})
        assert reset_resp.status_code == 200

        # 10. Shadow API #4: Config env dump
        env_resp = await client.get("/api/internal/config/env")
        assert env_resp.status_code == 200

        # NOTE: /api/v2/payments/scheduled and /api/v2/accounts/{account_id}/close are intentionally UNTOUCHED

        # =====================================================================
        # PHASE 2: VERIFY TELEMETRY STREAM & LOG CONTRACT
        # =====================================================================
        assert os.path.exists(LOG_FILE_PATH)
        assert len(RECENT_TELEMETRY_LOGS) >= 10

        # Verify every emitted log strictly matches the 21 required contract fields
        for log in RECENT_TELEMETRY_LOGS:
            missing = REQUIRED_LOG_FIELDS - set(log.keys())
            assert not missing, f"Missing fields in log {log.get('raw_path')}: {missing}"
            assert isinstance(log["pii_fields_detected"], list)
            assert isinstance(log["path_params_extracted"], dict)
            assert log["auth_type"] in {"JWT_BEARER", "API_KEY", "NONE"}

        # Check BOLA entry
        bola_logs = [l for l in RECENT_TELEMETRY_LOGS if l["raw_path"] == "/api/v2/accounts/1005"]
        assert len(bola_logs) == 1
        b_log = bola_logs[0]
        assert b_log["ground_truth_label"] == "attack_bola"
        assert b_log["jwt_sub"] == "user_1001"
        assert "account_id" in b_log["path_params_extracted"] or "id" in b_log["path_params_extracted"]
        assert "PAN" in b_log["pii_fields_detected"]

        # Check Zombie entry
        z_logs = [l for l in RECENT_TELEMETRY_LOGS if l["raw_path"] == "/api/v1/users/export"]
        assert len(z_logs) == 1
        z_log = z_logs[0]
        assert z_log["auth_type"] == "NONE"
        assert set(z_log["pii_fields_detected"]) >= {"PAN", "PHONE", "UPI_VPA", "GOVT_ID_LIKE"}

        # =====================================================================
        # PHASE 3: VERIFY INVENTORY REST ENDPOINTS & FILTERING
        # =====================================================================

        # 1. GET /api/inventory/endpoints (All)
        inv_res = await client.get("/api/inventory/endpoints")
        assert inv_res.status_code == 200
        all_endpoints = inv_res.json()
        assert len(all_endpoints) >= 14

        by_route = {f"{e['method']} {e['normalized_path']}": e for e in all_endpoints}

        # Entity Collapse Verification:
        # Accounts endpoint (/api/v2/accounts/{account_id}) must have exactly 1 record with hit_count == 2
        assert "GET /api/v2/accounts/{account_id}" in by_route
        acc_record = by_route["GET /api/v2/accounts/{account_id}"]
        assert acc_record["hit_count"] == 2
        assert acc_record["classification"] == "documented"
        assert len(acc_record["sample_raw_paths"]) == 2

        # 4 Classifications Verification:
        # Documented
        assert by_route["POST /api/v2/auth/login"]["classification"] == "documented"
        # Zombie
        assert by_route["GET /api/v1/users/export"]["classification"] == "zombie"
        # Shadow
        assert by_route["GET /api/internal/config/env"]["classification"] == "shadow"
        assert by_route["GET /api/v1/accounts/{account_id}/passbook-dump"]["classification"] == "shadow"
        # Unused (0 traffic)
        assert by_route["GET /api/v2/payments/scheduled"]["classification"] == "unused"
        assert by_route["GET /api/v2/payments/scheduled"]["hit_count"] == 0
        assert by_route["DELETE /api/v2/accounts/{account_id}/close"]["classification"] == "unused"
        assert by_route["DELETE /api/v2/accounts/{account_id}/close"]["hit_count"] == 0

        # Filter by classification=shadow
        shadow_filter_res = await client.get("/api/inventory/endpoints?classification=shadow")
        assert shadow_filter_res.status_code == 200
        shadow_list = shadow_filter_res.json()
        assert len(shadow_list) >= 4
        assert all(e["classification"] == "shadow" for e in shadow_list)

        # Filter by classification=unused
        unused_filter_res = await client.get("/api/inventory/endpoints?classification=unused")
        assert unused_filter_res.status_code == 200
        unused_list = unused_filter_res.json()
        assert len(unused_list) >= 2
        assert all(e["hit_count"] == 0 for e in unused_list)

        # Filter by has_pii=true
        pii_filter_res = await client.get("/api/inventory/endpoints?has_pii=true")
        assert pii_filter_res.status_code == 200
        pii_list = pii_filter_res.json()
        assert len(pii_list) >= 3
        assert all(len(e["pii_fields_exposed"]) > 0 for e in pii_list)

        # =====================================================================
        # PHASE 4: VERIFY DIFF-SUMMARY REST ENDPOINT
        # =====================================================================
        diff_res = await client.get("/api/inventory/diff-summary")
        assert diff_res.status_code == 200
        summary = diff_res.json()
        assert summary["total_endpoints"] >= 15
        assert summary["documented_count"] >= 4
        assert summary["shadow_count"] >= 4
        assert summary["zombie_count"] >= 1
        assert summary["unused_count"] >= 2
        assert summary["spec_drift_detected"] is True
        assert summary["pii_exposing_count"] >= 3

        # =====================================================================
        # PHASE 5: VERIFY AUTO-SWAGGER SCHEMA SYNTHESIZER REST ENDPOINT (USP)
        # =====================================================================
        # Generate Auto-Swagger for Shadow Config API
        config_ep_id = generate_endpoint_id("GET", "/api/internal/config/env")
        auto_swag_res = await client.get(f"/api/inventory/endpoints/{config_ep_id}/auto-swagger")
        assert auto_swag_res.status_code == 200
        swagger_data = auto_swag_res.json()
        assert swagger_data["openapi"] == "3.0.3"
        assert "/api/internal/config/env" in swagger_data["paths"]
        op = swagger_data["paths"]["/api/internal/config/env"]["get"]
        assert "Auto-Synthesized" in op["summary"]
        schema = op["responses"]["200"]["content"]["application/json"]["schema"]
        assert schema["type"] == "object"
        assert "environment" in schema["properties"]

        # Generate Auto-Swagger for Shadow Passbook API (verifying inferred path params)
        pb_ep_id = generate_endpoint_id("GET", "/api/v1/accounts/{account_id}/passbook-dump")
        pb_swag_res = await client.get(f"/api/inventory/endpoints/{pb_ep_id}/auto-swagger")
        assert pb_swag_res.status_code == 200
        pb_swagger = pb_swag_res.json()
        pb_op = pb_swagger["paths"]["/api/v1/accounts/{account_id}/passbook-dump"]["get"]
        assert len(pb_op["parameters"]) == 1
        assert pb_op["parameters"][0]["name"] == "account_id"
        assert pb_op["parameters"][0]["in"] == "path"
        assert pb_op["security"] == [{"BearerAuth": []}]

        # 404 test on invalid endpoint ID
        not_found_res = await client.get("/api/inventory/endpoints/non_existent_endpoint_id/auto-swagger")
        assert not_found_res.status_code == 404

        # =====================================================================
        # PHASE 6: VERIFY RECENT LOGS REST ENDPOINT (FOR PERSON 2 & PERSON 3)
        # =====================================================================
        recent_res = await client.get("/api/inventory/logs/recent?limit=20")
        assert recent_res.status_code == 200
        recent_data = recent_res.json()
        assert recent_data["count"] >= 10
        assert len(recent_data["logs"]) >= 10
        # Check that newest log is returned first
        first_recent = recent_data["logs"][0]
        assert "event_id" in first_recent
        assert "latency_ms" in first_recent
        assert "pii_fields_detected" in first_recent
