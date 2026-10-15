"""
Identity Trust Risk Scoring Engine (Checkpoint 15)
Applies Identity Trust Modifiers to alerts (not to API base catalog score).

Guarantees:
- Flagged events with provisioned, in-scope, campaign-aware identities are
  downgraded (e.g. High -> Informational) with full reasoning chains visible.
- Events with compromised/out-of-scope/spoofed privileged context receive NO discount
  and are tagged "elevated priority: privileged identity + anomalous context".
"""

from typing import Dict, Any, List, Optional
from app.core.identity_context_resolver import IdentityContext, DetectionDecision

SEVERITY_LEVELS = ["INFORMATIONAL", "LOW", "MEDIUM", "HIGH", "CRITICAL"]

def calculate_alert_risk(
    base_severity: str,
    context: IdentityContext,
    is_in_scope: bool,
    has_geo_anomaly: bool,
    has_timing_anomaly: bool,
    volume_used: int
) -> Dict[str, Any]:
    """
    Computes modified alert severity and reasoning chain based on Identity Trust.
    """
    reasoning_chain = []
    elevated_priority = False
    is_downgraded = False

    # 1. Retail Customer - No modifier
    if not context.is_employee:
        return {
            "effective_severity": base_severity,
            "is_downgraded": False,
            "is_elevated": False,
            "priority_tag": "standard: retail customer",
            "identity_trust_modifier": 0,
            "reasoning_chain": [
                "Actor is retail customer (unprivileged). Standard baseline rules apply.",
                f"Base severity '{base_severity}' retained with no identity trust discount."
            ]
        }

    # 2. Privileged Identity with Anomalous Context (Stolen token, Foreign IP, Inhuman velocity, Out-of-scope)
    if has_geo_anomaly or has_timing_anomaly or not is_in_scope:
        elevated_priority = True
        anomalies = []
        if has_geo_anomaly:
            anomalies.append(f"anomalous geography ({context.geo_details or 'Foreign untrusted IP'})")
        if has_timing_anomaly:
            anomalies.append("inhuman timing velocity (<200ms)")
        if not is_in_scope:
            anomalies.append(f"access outside declared scope {context.allowed_regions}")

        reasoning = (
            f"Privileged identity '{context.employee_id}' ({context.role}) detected with {', '.join(anomalies)}. "
            "No identity trust discount applied. elevated priority: privileged identity + anomalous context."
        )
        reasoning_chain.append(reasoning)

        return {
            "effective_severity": "CRITICAL" if base_severity == "HIGH" else base_severity,
            "is_downgraded": False,
            "is_elevated": True,
            "priority_tag": "elevated priority: privileged identity + anomalous context",
            "identity_trust_modifier": +25,
            "reasoning_chain": reasoning_chain
        }

    # 3. Privileged Identity with Sanctioned Campaign Context (Downgrade to Informational)
    if context.active_campaigns and is_in_scope and volume_used <= context.effective_limit:
        is_downgraded = True
        campaign_name = context.active_campaigns[0]
        reason = (
            f"role={context.role}, scope={context.declared_scope}, campaign={campaign_name} active, "
            f"volume within {context.effective_limit}/day limit -> informational"
        )
        reasoning_chain.append(reason)
        reasoning_chain.append(
            f"Provisioned {context.role}, in-scope, active campaign — downgraded from {base_severity} to Informational."
        )

        return {
            "effective_severity": "INFORMATIONAL",
            "is_downgraded": True,
            "is_elevated": False,
            "priority_tag": "downgraded: sanctioned campaign activity",
            "identity_trust_modifier": -50,
            "reasoning_chain": reasoning_chain
        }

    # 4. Standard in-scope employee within standard baseline
    if is_in_scope and volume_used <= context.effective_limit:
        is_downgraded = True
        reason = (
            f"role={context.role}, scope={context.declared_scope}, volume {volume_used} <= baseline {context.effective_limit} -> informational"
        )
        reasoning_chain.append(reason)
        return {
            "effective_severity": "INFORMATIONAL",
            "is_downgraded": True,
            "is_elevated": False,
            "priority_tag": "verified employee routine operational activity",
            "identity_trust_modifier": -30,
            "reasoning_chain": reasoning_chain
        }

    # 5. Privileged identity exceeding even campaign limit
    reasoning_chain.append(
        f"role={context.role}, volume {volume_used} exceeds limit {context.effective_limit}. Alert retained."
    )
    return {
        "effective_severity": base_severity,
        "is_downgraded": False,
        "is_elevated": False,
        "priority_tag": "volume threshold exceeded",
        "identity_trust_modifier": 0,
        "reasoning_chain": reasoning_chain
    }
