import pytest
import os
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal
from app.models.organization import Employee, Role, Campaign
from app.models.account import Account
from app.core.internal_auth import create_internal_token
from app.core.security import create_access_token
from app.core.identity_context_resolver import (
    IdentityContextResolver,
    evaluate_access_event,
    SUSPICIOUS_GEO_IPS
)

def test_checkpoint14_scenario_1_vp_accesses_2000_during_campaign():
    """
    Acceptance Criteria:
    - Simulate: VP accesses 2,000 accounts org-wide during an active,
      correctly-scoped campaign window -> NO alert (or informational only)
    """
    db = SessionLocal()
    try:
        # Sunita Rao (VP Sales, EMP-1002)
        vp = db.query(Employee).filter(Employee.employee_id == "EMP-1002").first()
        assert vp is not None

        vp_token, _ = create_internal_token(
            employee_id=vp.employee_id,
            role="VP Sales",
            scope="org-wide",
            department=vp.department,
            region="org-wide"
        )

        # Active campaign window time (e.g. today during Diwali Sale)
        now = datetime.now(timezone.utc)

        # 2,000 mock in-scope accounts across all regions
        mock_accounts = [{"id": i, "region": "West"} for i in range(1, 2001)]

        # Evaluate access event
        decision = evaluate_access_event(
            token=vp_token,
            path="/api/v2/internal/reports/regional-sales",
            accessed_accounts=mock_accounts,
            client_ip="103.21.244.1",  # Indian domestic IP
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            inter_arrival_times_ms=[350.0] * 10,  # Human/enterprise pacing
            total_volume_count=2000,
            db=db,
            simulated_now=now
        )

        assert decision.alert_triggered is False
        assert decision.severity in ["INFORMATIONAL", "NONE"]
        assert decision.action_recommended == "ALLOW"
        assert any("active_campaign" in r or "suppressed" in r for r in decision.reasoning_chain)

    finally:
        db.close()


def test_checkpoint14_scenario_2_vp_accesses_accounts_day_after_campaign():
    """
    Acceptance Criteria:
    - Simulate: same VP accesses accounts the day AFTER the campaign ends
      at the same volume -> alert fires (context-aware, not role-aware alone)
    """
    db = SessionLocal()
    try:
        vp = db.query(Employee).filter(Employee.employee_id == "EMP-1002").first()
        vp_token, _ = create_internal_token(
            employee_id=vp.employee_id,
            role="VP Sales",
            scope="org-wide",
            department=vp.department,
            region="org-wide"
        )

        # Set simulated time to 30 days in future (campaign has ended!)
        post_campaign_time = datetime.now(timezone.utc) + timedelta(days=30)

        mock_accounts = [{"id": i, "region": "West"} for i in range(1, 2001)]

        decision = evaluate_access_event(
            token=vp_token,
            path="/api/v2/internal/reports/regional-sales",
            accessed_accounts=mock_accounts,
            client_ip="103.21.244.1",
            total_volume_count=2000,
            db=db,
            simulated_now=post_campaign_time
        )

        # Must fire alert because 2,000 > VP baseline of 200/day outside campaign!
        assert decision.alert_triggered is True
        assert decision.severity == "HIGH"
        assert decision.attack_type == "VOLUME_ABUSE"
        assert any("exceeds standard role baseline" in r for r in decision.reasoning_chain)

    finally:
        db.close()


def test_checkpoint14_scenario_3_sales_manager_accesses_out_of_scope_region():
    """
    Acceptance Criteria:
    - Simulate: a Sales Manager (region=West) accesses 5 accounts in region=East ->
      alert fires immediately, even though volume is low
    """
    db = SessionLocal()
    try:
        # Sanjay Patel (EMP-1006, Sales Manager, West)
        sm = db.query(Employee).filter(Employee.employee_id == "EMP-1006").first()
        sm_token, _ = create_internal_token(
            employee_id=sm.employee_id,
            role="Sales Manager",
            scope="region:West",
            department=sm.department,
            region="West"
        )

        # Accessing 5 accounts in region East
        east_accounts = [{"id": 100 + i, "region": "East"} for i in range(5)]

        decision = evaluate_access_event(
            token=sm_token,
            path="/api/v2/internal/reports/account-lookup",
            accessed_accounts=east_accounts,
            client_ip="103.21.244.1",
            total_volume_count=5,  # Very low volume!
            db=db
        )

        # Must fire alert immediately despite low volume!
        assert decision.alert_triggered is True
        assert decision.severity == "HIGH"
        assert decision.attack_type == "OUT_OF_SCOPE_ACCESS"
        assert any("Accessing even one account outside declared scope" in r for r in decision.reasoning_chain)

    finally:
        db.close()


def test_checkpoint14_scenario_4_stolen_token_replayed_from_suspicious_geography():
    """
    Acceptance Criteria:
    - Simulate: an attacker steals a real Sales Manager's token and replays it
      from a new device/geography with in-scope-looking requests ->
      still flagged, via the stolen-identity checks
    """
    db = SessionLocal()
    try:
        sm = db.query(Employee).filter(Employee.employee_id == "EMP-1006").first()
        stolen_token, _ = create_internal_token(
            employee_id=sm.employee_id,
            role="Sales Manager",
            scope="region:West",
            department=sm.department,
            region="West"
        )

        # Attacker replays from Tor Exit Node in Netherlands
        tor_ip = "185.220.101.5"

        # The request uses in-scope West accounts to look benign
        in_scope_accounts = [{"id": 1, "region": "West"}]

        decision = evaluate_access_event(
            token=stolen_token,
            path="/api/v2/internal/reports/regional-sales",
            accessed_accounts=in_scope_accounts,
            client_ip=tor_ip,  # Netherlands Tor exit
            user_agent="python-requests/2.31.0",
            total_volume_count=1,
            db=db
        )

        # Must flag stolen identity due to anomalous geography
        assert decision.alert_triggered is True
        assert decision.severity == "HIGH"
        assert decision.attack_type == "STOLEN_IDENTITY"
        assert decision.elevated_priority is True
        assert any("foreign/suspicious network" in r for r in decision.reasoning_chain)

    finally:
        db.close()


def test_checkpoint14_scenario_5_genuine_customer_bola_still_flagged():
    """
    Acceptance Criteria:
    - Simulate: a genuine BOLA attack on CUSTOMER accounts
      (Checkpoint 7's original attack, unrelated to any employee role) ->
      still flagged exactly as before, unchanged
    """
    # Customer Priya Sharma (u_101) token
    customer_token, _ = create_access_token(user_id="u_101", account_id=1, role="customer")

    # Attacking 15 different customer accounts via BOLA enumeration sweep
    enumerated_accounts = [{"id": i, "region": "West"} for i in range(1, 16)]

    decision = evaluate_access_event(
        token=customer_token,
        path="/api/v2/accounts/{account_id}/statement",
        accessed_accounts=enumerated_accounts,
        client_ip="127.0.0.1",
        total_volume_count=15
    )

    # Must flag CRITICAL BOLA alert
    assert decision.alert_triggered is True
    assert decision.severity == "CRITICAL"
    assert decision.attack_type == "BOLA"
    assert any("Customer (Retail User)" in r for r in decision.reasoning_chain)
    assert any("Confirmed BOLA" in r for r in decision.reasoning_chain)


def test_checkpoint14_scenario_6_normal_day_false_positive_check():
    """
    Acceptance Criteria:
    - False-positive check: run a full normal day of all employee roles
      doing their normal jobs, confirm zero or near-zero false alerts
    """
    db = SessionLocal()
    try:
        employees = db.query(Employee).all()
        normal_day_alerts = []

        now = datetime.now(timezone.utc)

        for emp in employees:
            role_name = emp.role_rel.role_name
            emp_region = emp.region if emp.region != "org-wide" else "West"

            # Create employee token
            tok, _ = create_internal_token(
                employee_id=emp.employee_id,
                role=role_name,
                scope=emp.role_rel.default_scope,
                department=emp.department,
                region=emp.region
            )

            # Normal activity: 10 queries within their declared region
            sample_accounts = [{"id": i, "region": emp_region} for i in range(1, 11)]

            decision = evaluate_access_event(
                token=tok,
                path="/api/v2/internal/reports/account-lookup",
                accessed_accounts=sample_accounts,
                client_ip="103.45.120.10",  # Domestic Indian IP
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                inter_arrival_times_ms=[500.0] * 5,  # Normal user speed
                total_volume_count=10,
                db=db,
                simulated_now=now
            )

            # For regular established employees: NO alert
            # For fresh hire (< 14 days): LOW severity informational note only
            if decision.alert_triggered and decision.severity != "LOW":
                normal_day_alerts.append((emp.employee_id, emp.name, decision.reasoning_chain))

        # Must have ZERO false-positive actionable alerts during normal operations
        assert len(normal_day_alerts) == 0, f"False positives detected: {normal_day_alerts}"

    finally:
        db.close()
