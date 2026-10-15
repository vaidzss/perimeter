import pytest
import os
import sys
import json
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.db.session import SessionLocal
from app.models.organization import Employee, Role, Campaign
from app.models.account import Account
from app.core.internal_auth import create_internal_token, decode_internal_token
from app.core.identity_context_resolver import evaluate_access_event
from app.core.security import create_access_token

client = TestClient(app)

def test_checkpoint16_live_judge_workflow_vp_onboard_normal_then_stolen():
    """
    Acceptance Criteria:
    - A judge can watch, live:
      new VP onboarded -> normal high-volume access -> no actionable attack alert (informational only) ->
      same token from a suspicious context -> alert fires with full reasoning shown
    """
    admin_token, _ = create_internal_token(
        employee_id="EMP-1001",
        role="IT Admin",
        scope="ops-only",
        department="IT Ops",
        region="IT-Infra"
    )

    # 1. Onboard a fresh VP live
    new_vp_email = f"arvind.swaminathan.{int(datetime.now().timestamp())}@corp.bharatpay.com"
    onboard_res = client.post(
        "/api/v2/internal/employees/onboard",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Arvind Swaminathan",
            "email": new_vp_email,
            "role": "VP Sales",
            "department": "Sales",
            "region": "org-wide",
            "manager_id": "EMP-1001"
        }
    )
    assert onboard_res.status_code == 200
    vp_data = onboard_res.json()
    vp_token = vp_data["access_token"]
    vp_emp_id = vp_data["employee_id"]

    db = SessionLocal()
    try:
        # 2. Normal high-volume access during campaign -> NO ACTIONABLE ATTACK ALERT (Informational / Low monitoring only)
        now = datetime.now(timezone.utc)
        accounts_2000 = [{"id": i, "region": "West"} for i in range(1, 2001)]

        legit_decision = evaluate_access_event(
            token=vp_token,
            path="/api/v2/internal/reports/regional-sales",
            accessed_accounts=accounts_2000,
            client_ip="103.21.244.1",  # Indian domestic
            total_volume_count=2000,
            db=db,
            simulated_now=now
        )

        # No attack alert (attack_type is None, severity is not HIGH/CRITICAL)
        assert legit_decision.attack_type is None
        assert legit_decision.severity in ["INFORMATIONAL", "LOW", "NONE"]
        assert legit_decision.elevated_priority is False
        assert legit_decision.action_recommended in ["ALLOW", "LOG_INFORMATIONAL"]

        # 3. Same token from suspicious geography (Netherlands Tor Exit) -> ALERT FIRES WITH FULL REASONING
        tor_ip = "185.220.101.5"
        malicious_decision = evaluate_access_event(
            token=vp_token,
            path="/api/v2/internal/reports/regional-sales",
            accessed_accounts=[{"id": 1, "region": "West"}],
            client_ip=tor_ip,
            total_volume_count=1,
            db=db,
            simulated_now=now
        )

        assert malicious_decision.alert_triggered is True
        assert malicious_decision.severity == "HIGH"
        assert malicious_decision.attack_type == "STOLEN_IDENTITY"
        assert malicious_decision.elevated_priority is True
        assert any("foreign/suspicious network" in r for r in malicious_decision.reasoning_chain)

    finally:
        db.close()


def test_checkpoint16_employee_directory_and_campaign_list_update_live():
    """
    Acceptance Criteria:
    - Employee directory and campaign list are visible and update live
    """
    admin_token, _ = create_internal_token(
        employee_id="EMP-1001",
        role="IT Admin",
        scope="ops-only",
        department="IT Ops",
        region="IT-Infra"
    )

    # 1. Fetch directory
    emp_res = client.get(
        "/api/v2/internal/employees",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert emp_res.status_code == 200
    emps = emp_res.json()
    assert len(emps) >= 12
    assert any(e["role"] == "VP Sales" for e in emps)

    # 2. Fetch campaigns
    camp_res = client.get("/api/v2/internal/campaigns")
    assert camp_res.status_code == 200
    camps = camp_res.json()
    assert len(camps) >= 1
    assert any("Diwali" in c["name"] for c in camps)


def test_checkpoint16_customer_attacks_remain_intact_and_fire():
    """
    Acceptance Criteria:
    - Nothing about this new layer breaks or hides the original 3 customer-facing
      attacks (BOLA, scraping, token replay) — run all of Checkpoint 7's attacks
      again and confirm they still fire exactly as before
    """
    customer_token, _ = create_access_token(user_id="u_101", account_id=1, role="customer")

    # ATTACK 1: BOLA sweep against victim account 2
    bola_res = client.get(
        "/api/v2/accounts/2/statement",
        headers={"Authorization": f"Bearer {customer_token}"}
    )
    # Target backend returns 403 Forbidden with BOLA guard
    assert bola_res.status_code == 403
    assert "Forbidden" in bola_res.json()["detail"]

    # ATTACK 2: Bulk scraping against public merchant catalog
    merchants_res = client.get("/api/v2/upi/merchants?limit=100")
    assert merchants_res.status_code == 200
    data = merchants_res.json()
    assert "items" in data
    assert len(data["items"]) > 0

    # ATTACK 3: Token replay / duplicate payment attempt with same idempotency key
    idem_key = f"IDEM-TEST-{int(datetime.now().timestamp())}"
    pay_payload = {
        "from_vpa": "priya.sharma@bharatpay",
        "to_vpa": "swiggy@bpaymerchant",
        "amount_paise": 25000,
        "note": "Replay test",
        "idempotency_key": idem_key
    }

    # First attempt: 200 Success
    res1 = client.post(
        "/api/v2/payments/upi-transfer",
        headers={"Authorization": f"Bearer {customer_token}"},
        json=pay_payload
    )
    assert res1.status_code == 200
    assert res1.json()["idempotent_replay"] is False

    # Second attempt (replay): returns 200 with idempotent_replay = True
    res2 = client.post(
        "/api/v2/payments/upi-transfer",
        headers={"Authorization": f"Bearer {customer_token}"},
        json=pay_payload
    )
    assert res2.status_code == 200
    assert res2.json()["idempotent_replay"] is True
