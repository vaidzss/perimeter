import pytest
import os
import sys
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.db.session import SessionLocal
from app.models.organization import Employee, Role, AccessGrant, Campaign
from app.core.internal_auth import create_internal_token, decode_internal_token

client = TestClient(app)

def test_checkpoint12_onboard_vp_and_receive_scoped_token():
    """
    Acceptance Criteria:
    - A new VP can be onboarded via the API and immediately receives a scoped token
    - Onboarding a VP does NOT grant unlimited access — it grants exactly their role's
      default scope, adjustable only by an explicit access_grant with a reason and expiry
    """
    # Create IT Admin token for authorized caller
    admin_token, _ = create_internal_token(
        employee_id="EMP-1001",
        role="IT Admin",
        scope="ops-only",
        department="IT Ops",
        region="IT-Infra"
    )

    import uuid
    uid = uuid.uuid4().hex[:6]
    onboard_payload = {
        "name": "Suresh Raina",
        "email": f"suresh.raina.{uid}@corp.bharatpay.com",
        "role": "VP Sales",
        "department": "Sales",
        "region": "org-wide",
        "manager_id": "EMP-1001"
    }

    res = client.post(
        "/api/v2/internal/employees/onboard",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=onboard_payload
    )

    assert res.status_code == 200, res.text
    data = res.json()
    assert data["status"] == "PROVISIONED"
    assert data["role"] == "VP Sales"
    assert data["scope"] == "org-wide"  # exactly role's default scope, not unlimited
    assert data["access_token"] is not None

    # Verify returned token claims
    claims = decode_internal_token(data["access_token"])
    assert claims["role"] == "VP Sales"
    assert claims["scope"] == "org-wide"
    assert claims["employee_id"] == data["employee_id"]
    assert claims["token_type"] == "internal"
    assert "provisioned_at" in claims

    # Confirm no implicit extra access grant created
    assert data["has_custom_grant"] is False


def test_checkpoint12_onboard_with_custom_scope_requires_grant_reason():
    """
    Acceptance Criteria:
    - Adjustable only by an explicit access_grant with a reason and expiry
    - Reject if custom scope provided without reason
    """
    admin_token, _ = create_internal_token(
        employee_id="EMP-1001",
        role="IT Admin",
        scope="ops-only",
        department="IT Ops",
        region="IT-Infra"
    )

    # 1. Custom scope with NO reason -> 400 Bad Request
    import uuid
    uid = uuid.uuid4().hex[:6]
    fail_payload = {
        "name": "Kavita Krishnan",
        "email": f"kavita.fail.{uid}@corp.bharatpay.com",
        "role": "Sales Manager",
        "department": "Sales",
        "region": "West",
        "custom_scope": "multi-region",
        "grant_reason": ""  # empty reason!
    }
    fail_res = client.post(
        "/api/v2/internal/employees/onboard",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=fail_payload
    )
    assert fail_res.status_code == 400

    # 2. Custom scope with valid reason and expiry -> 200 Success + AccessGrant stored
    pass_payload = {
        "name": "Kavita Krishnan",
        "email": f"kavita.pass.{uid}@corp.bharatpay.com",
        "role": "Sales Manager",
        "department": "Sales",
        "region": "West",
        "custom_scope": "multi-region",
        "grant_reason": "Covering North-West cluster during regional vacancy",
        "grant_expires_days": 45
    }
    pass_res = client.post(
        "/api/v2/internal/employees/onboard",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=pass_payload
    )
    assert pass_res.status_code == 200
    data = pass_res.json()
    assert data["has_custom_grant"] is True
    assert data["scope"] == "multi-region"


def test_checkpoint12_campaign_window_creation():
    """
    Acceptance Criteria:
    - A campaign window can be created with a start/end date and affected scope
    """
    admin_token, _ = create_internal_token(
        employee_id="EMP-1001",
        role="IT Admin",
        scope="ops-only",
        department="IT Ops",
        region="IT-Infra"
    )

    now = datetime.now(timezone.utc)
    campaign_payload = {
        "name": "Holi Festival Mega Push 2026",
        "start_date": (now + timedelta(days=1)).isoformat(),
        "end_date": (now + timedelta(days=10)).isoformat(),
        "affected_regions": ["North", "West", "East"],
        "expected_roles": ["VP Sales", "Regional Head", "Sales Manager"],
        "expected_volume_multiplier": 8
    }

    res = client.post(
        "/api/v2/internal/campaigns",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=campaign_payload
    )

    assert res.status_code == 200, res.text
    data = res.json()
    assert data["status"] == "REGISTERED"
    assert data["name"] == "Holi Festival Mega Push 2026"
    assert "North" in data["affected_regions"]
    assert data["expected_volume_multiplier"] == 8
    assert data["created_by"] == "EMP-1001"


def test_checkpoint12_privilege_escalation_attempt_rejected_and_logged():
    """
    Acceptance Criteria:
    - Attempting to onboard an employee with a role outside the registrar's own authority
      (e.g. a Sales Manager trying to grant themselves VP scope) is rejected and logged
      as a privilege-escalation attempt
    """
    # Caller is Sales Manager EMP-1006 (region West)
    sm_token, _ = create_internal_token(
        employee_id="EMP-1006",
        role="Sales Manager",
        scope="region:West",
        department="Sales",
        region="West"
    )

    escalation_payload = {
        "name": "Rogue Account",
        "email": "rogue@corp.bharatpay.com",
        "role": "VP Sales",
        "department": "Sales",
        "region": "org-wide",
        "custom_scope": "org-wide"
    }

    # Attempt onboarding -> must be HTTP 403 Forbidden
    res = client.post(
        "/api/v2/internal/employees/onboard",
        headers={"Authorization": f"Bearer {sm_token}"},
        json=escalation_payload
    )

    assert res.status_code == 403
    assert "Privilege escalation attempt" in res.json()["detail"]

    # Verify that the attempt was logged to requests table
    db = SessionLocal()
    try:
        from app.models.request_log import RequestLog
        log_entry = (
            db.query(RequestLog)
            .filter(RequestLog.raw_path == "/api/v2/internal/employees/onboard")
            .filter(RequestLog.status_code == 403)
            .order_by(RequestLog.timestamp.desc())
            .first()
        )
        assert log_entry is not None, "Failed privilege escalation must be recorded in requests table"
        assert log_entry.user_id == "EMP-1006", "Attacker employee_id must be captured in log"
    finally:
        db.close()


def test_checkpoint12_employee_access_log():
    """
    Acceptance Criteria:
    - GET /api/v2/internal/employees/{id}/access-log returns audit trail of employee actions
    """
    admin_token, _ = create_internal_token(
        employee_id="EMP-1001",
        role="IT Admin",
        scope="ops-only",
        department="IT Ops",
        region="IT-Infra"
    )

    res = client.get(
        "/api/v2/internal/employees/EMP-1006/access-log",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert res.status_code == 200
    data = res.json()
    assert data["employee_id"] == "EMP-1006"
    assert "access_logs" in data
    assert isinstance(data["access_logs"], list)
