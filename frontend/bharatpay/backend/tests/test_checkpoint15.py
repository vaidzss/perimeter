import pytest
import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.identity_context_resolver import IdentityContext
from app.core.risk_scoring import calculate_alert_risk

def test_checkpoint15_downgraded_alert_shows_reasoning_chain():
    """
    Acceptance Criteria:
    - Every downgraded alert shows its reasoning chain
      ("role=VP, scope=org-wide, campaign=Diwali Sale 2026 active, volume within 5000/day limit -> informational")
    - Never silently deleted — remains visible and auditable
    """
    context = IdentityContext(
        is_employee=True,
        employee_id="EMP-1002",
        role="VP Sales",
        declared_scope="org-wide",
        department="Sales",
        region="org-wide",
        active_campaigns=["Diwali Sale 2026"],
        baseline_limit=200,
        campaign_multiplier=10,
        effective_limit=5000,
        allowed_regions=["West", "North", "South", "East", "org-wide"]
    )

    result = calculate_alert_risk(
        base_severity="HIGH",
        context=context,
        is_in_scope=True,
        has_geo_anomaly=False,
        has_timing_anomaly=False,
        volume_used=2000
    )

    assert result["is_downgraded"] is True
    assert result["effective_severity"] == "INFORMATIONAL"
    assert result["identity_trust_modifier"] < 0
    assert "downgraded: sanctioned campaign activity" in result["priority_tag"]

    # Check exact reasoning chain text
    chain = " ".join(result["reasoning_chain"])
    assert "role=VP Sales" in chain
    assert "scope=org-wide" in chain
    assert "campaign=Diwali Sale 2026 active" in chain
    assert "volume within 5000/day limit -> informational" in chain


def test_checkpoint15_upgraded_alert_visibly_marked_elevated_priority():
    """
    Acceptance Criteria:
    - An out-of-scope or spoofed-identity event gets NO discount and is tagged
      "elevated priority: privileged identity + anomalous context"
      so it's prioritized higher for investigation
    """
    context = IdentityContext(
        is_employee=True,
        employee_id="EMP-1002",
        role="VP Sales",
        declared_scope="org-wide",
        department="Sales",
        region="org-wide",
        active_campaigns=["Diwali Sale 2026"],
        baseline_limit=200,
        campaign_multiplier=10,
        effective_limit=5000,
        allowed_regions=["West", "North", "South", "East", "org-wide"],
        geo_anomaly=True,
        geo_details="Untrusted origin: 185.220.101.5 (Netherlands Tor Exit)"
    )

    result = calculate_alert_risk(
        base_severity="HIGH",
        context=context,
        is_in_scope=True,
        has_geo_anomaly=True,  # Foreign Tor IP!
        has_timing_anomaly=False,
        volume_used=150
    )

    assert result["is_downgraded"] is False
    assert result["is_elevated"] is True
    assert result["effective_severity"] == "CRITICAL"
    assert result["priority_tag"] == "elevated priority: privileged identity + anomalous context"
    assert any("elevated priority: privileged identity + anomalous context" in r for r in result["reasoning_chain"])


def test_checkpoint15_alerts_in_mock_and_server_have_required_metadata():
    """
    Acceptance Criteria:
    - Ensure Sentinel mock/alerts.json contains both downgraded and elevated alerts
      with required reasoning chains and tags
    """
    alerts_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../mock/alerts.json"))
    with open(alerts_path, "r", encoding="utf-8") as f:
        alerts = json.load(f)

    # 1. Check downgraded alert
    downgraded = [a for a in alerts if a.get("is_downgraded")]
    assert len(downgraded) >= 1
    d_alert = downgraded[0]
    assert d_alert["severity"] == "informational"
    assert "reasoning_chain" in d_alert
    assert any("Diwali Sale 2026 active" in r for r in d_alert["reasoning_chain"])

    # 2. Check elevated priority alert
    elevated = [a for a in alerts if a.get("elevated_priority")]
    assert len(elevated) >= 1
    e_alert = elevated[0]
    assert e_alert["priority_tag"] == "elevated priority: privileged identity + anomalous context"
    assert any("elevated priority" in r for r in e_alert["reasoning_chain"])
