import pytest
import os
import sys
import json
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.db.session import SessionLocal
from app.models.account import Account
from app.models.organization import Employee
from app.core.internal_auth import create_internal_token
from app.core.security import create_access_token

client = TestClient(app)

def test_checkpoint13_regional_sales_server_side_scope_enforcement():
    """
    Acceptance Criteria:
    - Each endpoint enforces scope server-side (test: try to query outside your region, confirm 403)
    """
    # Sales Manager in West region (EMP-1006)
    sm_west_token, _ = create_internal_token(
        employee_id="EMP-1006",
        role="Sales Manager",
        scope="region:West",
        department="Sales",
        region="West"
    )

    # 1. Querying own region (West) -> 200 OK
    res_in_scope = client.get(
        "/api/v2/internal/reports/regional-sales?region=West",
        headers={"Authorization": f"Bearer {sm_west_token}"}
    )
    assert res_in_scope.status_code == 200, res_in_scope.text
    data = res_in_scope.json()
    assert data["caller_employee_id"] == "EMP-1006"
    assert "West" in data["scope_used"]

    # 2. Attempting to query outside region (East or North) -> 403 Forbidden
    res_out_of_scope = client.get(
        "/api/v2/internal/reports/regional-sales?region=East",
        headers={"Authorization": f"Bearer {sm_west_token}"}
    )
    assert res_out_of_scope.status_code == 403
    assert "declared scope is limited" in res_out_of_scope.json()["detail"]


def test_checkpoint13_account_lookup_requires_reason_and_enforces_region():
    """
    Acceptance Criteria:
    - Support/escalation lookup (Employee+) logged with required reason field
    - Enforces scope: querying account outside region gives 403
    """
    # Sales Manager in West (EMP-1006)
    sm_token, _ = create_internal_token(
        employee_id="EMP-1006",
        role="Sales Manager",
        scope="region:West",
        department="Sales",
        region="West"
    )

    db = SessionLocal()
    try:
        west_acc = db.query(Account).filter(Account.region == "West").first()
        east_acc = db.query(Account).filter(Account.region == "East").first()
        assert west_acc is not None
        assert east_acc is not None
        west_id = west_acc.id
        east_id = east_acc.id
    finally:
        db.close()

    # 1. Missing reason parameter -> 422 or 400
    res_no_reason = client.get(
        f"/api/v2/internal/reports/account-lookup/{west_id}",
        headers={"Authorization": f"Bearer {sm_token}"}
    )
    assert res_no_reason.status_code in [400, 422]

    # 2. In-scope account lookup with valid reason -> 200 OK
    res_valid = client.get(
        f"/api/v2/internal/reports/account-lookup/{west_id}?reason=Dispute%20investigation%20ticket%201092",
        headers={"Authorization": f"Bearer {sm_token}"}
    )
    assert res_valid.status_code == 200
    data = res_valid.json()
    assert data["account_id"] == west_id
    assert data["lookup_audit"]["performed_by"] == "EMP-1006"
    assert "Dispute investigation" in data["lookup_audit"]["reason"]

    # 3. Out-of-scope account (East account) accessed by West manager -> 403 Forbidden
    res_out_of_scope = client.get(
        f"/api/v2/internal/reports/account-lookup/{east_id}?reason=Cross-region%20curiosity",
        headers={"Authorization": f"Bearer {sm_token}"}
    )
    assert res_out_of_scope.status_code == 403
    assert "Scope violation" in res_out_of_scope.json()["detail"]


def test_checkpoint13_org_wide_summary_restricted_to_vp():
    """
    Acceptance Criteria:
    - GET /api/v2/internal/reports/org-wide-summary (VP only)
    """
    # 1. Sales Manager attempts VP endpoint -> 403 Forbidden
    sm_token, _ = create_internal_token(
        employee_id="EMP-1006",
        role="Sales Manager",
        scope="region:West",
        department="Sales",
        region="West"
    )
    res_sm = client.get(
        "/api/v2/internal/reports/org-wide-summary",
        headers={"Authorization": f"Bearer {sm_token}"}
    )
    assert res_sm.status_code == 403

    # 2. VP Sales (EMP-1002) accesses -> 200 OK
    vp_token, _ = create_internal_token(
        employee_id="EMP-1002",
        role="VP Sales",
        scope="org-wide",
        department="Sales",
        region="org-wide"
    )
    res_vp = client.get(
        "/api/v2/internal/reports/org-wide-summary",
        headers={"Authorization": f"Bearer {vp_token}"}
    )
    assert res_vp.status_code == 200
    data = res_vp.json()
    assert "org_wide_kpis" in data
    assert "total_accounts" in data["org_wide_kpis"]
    assert "regional_breakdown" in data["org_wide_kpis"]


def test_checkpoint13_customer_token_rejected_on_internal_endpoints():
    """
    Acceptance Criteria:
    - Customer JWT cannot be used to call internal endpoints
    """
    customer_token, _ = create_access_token(user_id="u_101", account_id=1, role="customer")
    res = client.get(
        "/api/v2/internal/reports/regional-sales",
        headers={"Authorization": f"Bearer {customer_token}"}
    )
    assert res.status_code in [401, 403]


def test_checkpoint13_openapi_spec_has_internal_tag_and_no_shadow():
    """
    Acceptance Criteria:
    - These endpoints are added to openapi.json as a separate "internal" tag, so they
      are documented but clearly distinguished from the two shadow endpoints (which
      remain deliberately undocumented)
    """
    spec_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../spec/openapi.json"))
    with open(spec_path, "r", encoding="utf-8") as f:
        spec = json.load(f)

    paths = spec["paths"]

    # Check internal endpoints are present and tagged "internal"
    internal_routes = [
        "/api/v2/internal/reports/regional-sales",
        "/api/v2/internal/reports/account-lookup/{account_id}",
        "/api/v2/internal/reports/org-wide-summary",
        "/api/v2/internal/reports/bulk-export"
    ]
    for r in internal_routes:
        assert r in paths, f"Route {r} must be documented in openapi.json"
        method_def = list(paths[r].values())[0]
        assert "internal" in method_def["tags"]

    # Check shadow endpoints remain omitted
    assert "/api/v1/kyc/aadhaar-pan-dump" not in paths
    assert "/api/internal/debug/override-limit" not in paths
