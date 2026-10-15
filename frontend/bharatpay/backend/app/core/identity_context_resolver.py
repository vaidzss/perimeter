"""
Identity Context Resolver & Privileged Detection Engine (Checkpoint 14)
Designed as a clean, separable module for Person 2's ASPM discovery & detection pipeline.

Evaluates API traffic with identity + role + jurisdiction + business campaign awareness,
preventing false positives for sanctioned privileged activity (e.g. Diwali Sale) while
catching stolen privileged identities, scope violations, and impossible geography.
"""

import re
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
import jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.organization import Role, Employee, AccessGrant, Campaign
from app.models.account import Account

# Known suspicious / external non-corporate IPs (Tor exit nodes, bulletproof hosting)
SUSPICIOUS_GEO_IPS = {
    "185.220.101.5": "Netherlands (Tor Exit)",
    "185.220.101.7": "Netherlands (Tor Exit)",
    "45.154.255.8": "Russia (Bulletproof ASN 49304)",
    "194.26.29.112": "Seychelles (Anonymous Proxy)",
    "91.240.118.44": "Germany (Scraping Cloud)"
}

# Recognized corporate Indian networks / local dev IPs
DOMESTIC_ALLOWED_IP_PATTERNS = [
    r"^127\.",
    r"^10\.",
    r"^172\.(1[6-9]|2[0-9]|3[0-1])\.",
    r"^192\.168\.",
    r"^103\.",  # APNIC India
    r"^122\.",  # Airtel India
    r"^49\.",   # Jio India
    r"^106\."   # Vodafone Idea India
]

@dataclass
class IdentityContext:
    is_employee: bool
    employee_id: Optional[str] = None
    role: Optional[str] = None
    declared_scope: Optional[str] = None
    department: Optional[str] = None
    region: Optional[str] = None
    is_fresh_hire: bool = False
    hire_date: Optional[datetime] = None
    active_campaigns: List[str] = field(default_factory=list)
    baseline_limit: int = 100
    campaign_multiplier: int = 1
    effective_limit: int = 100
    allowed_regions: List[str] = field(default_factory=list)
    geo_anomaly: bool = False
    geo_details: Optional[str] = None
    timing_anomaly: bool = False
    timing_details: Optional[str] = None


@dataclass
class DetectionDecision:
    alert_triggered: bool
    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW", "INFORMATIONAL", "NONE"
    attack_type: Optional[str] = None  # "BOLA", "STOLEN_IDENTITY", "OUT_OF_SCOPE_ACCESS", "VOLUME_ABUSE", "AUTOMATED_SCRIPTING", None
    reasoning_chain: List[str] = field(default_factory=list)
    identity_context: Optional[IdentityContext] = None
    action_recommended: str = "ALLOW"  # "ALLOW", "LOG_INFORMATIONAL", "FLAG_FOR_AUDIT", "BLOCK_TOKEN"
    elevated_priority: bool = False


class IdentityContextResolver:
    """
    Core resolver used by Person 2's detector to extract contextual identity signals.
    """

    @staticmethod
    def is_domestic_or_trusted_ip(ip: str) -> bool:
        if ip in SUSPICIOUS_GEO_IPS:
            return False
        for pat in DOMESTIC_ALLOWED_IP_PATTERNS:
            if re.match(pat, ip):
                return True
        # Default allow localhost/private
        return False

    @staticmethod
    def resolve(
        token: Optional[str],
        client_ip: str = "127.0.0.1",
        user_agent: str = "Mozilla/5.0",
        db: Optional[Session] = None,
        simulated_now: Optional[datetime] = None
    ) -> IdentityContext:
        now = simulated_now or datetime.now(timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        # 1. Unauthenticated / Customer Token check
        if not token:
            return IdentityContext(is_employee=False, baseline_limit=100, effective_limit=100)

        claims = {}
        try:
            # Decode without strict verify for context resolution
            claims = jwt.decode(token, options={"verify_signature": False})
        except Exception:
            return IdentityContext(is_employee=False, baseline_limit=100, effective_limit=100)

        # Distinguish customer token vs internal employee token
        token_type = claims.get("token_type")
        if token_type != "internal":
            return IdentityContext(
                is_employee=False,
                baseline_limit=100,
                effective_limit=100,
                declared_scope="customer"
            )

        emp_id = claims.get("employee_id")
        claimed_role = claims.get("role", "Employee (Support)")
        declared_scope = claims.get("scope", "support-tickets")
        department = claims.get("department", "Customer Support")
        region = claims.get("region", "West")

        # Live DB lookup if session provided
        employee = None
        role_obj = None
        if db and emp_id:
            employee = db.query(Employee).filter(Employee.employee_id == emp_id).first()
            if employee and employee.role_rel:
                role_obj = employee.role_rel

        # Baseline & Limits
        base_rate = role_obj.default_rate_limit if role_obj else 200
        campaign_rate = role_obj.campaign_rate_limit if role_obj else (base_rate * 5)

        # Fresh hire check (hire within 14 days)
        hire_date = employee.hire_date if employee else now - timedelta(days=60)
        if hire_date.tzinfo is None:
            hire_date = hire_date.replace(tzinfo=timezone.utc)
        is_fresh = (now - hire_date).days <= 14

        # Active Campaigns check
        active_campaign_names = []
        multiplier = 1
        if db:
            campaigns = db.query(Campaign).all()
            for c in campaigns:
                s_date = c.start_date.replace(tzinfo=timezone.utc if c.start_date.tzinfo is None else None)
                e_date = c.end_date.replace(tzinfo=timezone.utc if c.end_date.tzinfo is None else None)
                if s_date <= now <= e_date:
                    if claimed_role in c.expected_roles:
                        active_campaign_names.append(c.name)
                        if c.expected_volume_multiplier > multiplier:
                            multiplier = c.expected_volume_multiplier

        # Effective limit calculation
        if active_campaign_names:
            effective_limit = campaign_rate if campaign_rate else (base_rate * multiplier)
        else:
            effective_limit = base_rate

        if is_fresh:
            # Fresh hire has tighter baseline
            effective_limit = int(effective_limit * 0.5)

        # Allowed regions calculation
        allowed_regions = []
        if claimed_role == "VP Sales" or region == "org-wide":
            allowed_regions = ["West", "North", "South", "East", "org-wide"]
        else:
            allowed_regions = [region]
            if db and emp_id:
                grants = db.query(AccessGrant).filter(
                    AccessGrant.employee_id == emp_id,
                    AccessGrant.expires_at > now
                ).all()
                for g in grants:
                    if "region:" in g.resource_scope:
                        allowed_regions.append(g.resource_scope.split("region:")[-1].strip())

        # Geography Anomaly Check
        geo_anomaly = False
        geo_details = None
        if client_ip in SUSPICIOUS_GEO_IPS:
            geo_anomaly = True
            geo_details = f"Untrusted origin: {client_ip} ({SUSPICIOUS_GEO_IPS[client_ip]})"
        elif not IdentityContextResolver.is_domestic_or_trusted_ip(client_ip):
            geo_anomaly = True
            geo_details = f"Anomalous non-corporate IP address: {client_ip}"

        return IdentityContext(
            is_employee=True,
            employee_id=emp_id,
            role=claimed_role,
            declared_scope=declared_scope,
            department=department,
            region=region,
            is_fresh_hire=is_fresh,
            hire_date=hire_date,
            active_campaigns=active_campaign_names,
            baseline_limit=base_rate,
            campaign_multiplier=multiplier,
            effective_limit=effective_limit,
            allowed_regions=allowed_regions,
            geo_anomaly=geo_anomaly,
            geo_details=geo_details
        )


def evaluate_access_event(
    token: Optional[str],
    path: str,
    accessed_accounts: List[Dict[str, Any]],  # e.g. [{"id": 1, "region": "West"}, ...]
    client_ip: str = "127.0.0.1",
    user_agent: str = "Mozilla/5.0",
    inter_arrival_times_ms: Optional[List[float]] = None,
    total_volume_count: int = 1,
    db: Optional[Session] = None,
    simulated_now: Optional[datetime] = None
) -> DetectionDecision:
    """
    Evaluates an access event against identity, scope, campaign context, and behavioral baselines.
    Returns DetectionDecision with alert level and clear reasoning chain.
    """
    now = simulated_now or datetime.now(timezone.utc)
    context = IdentityContextResolver.resolve(
        token=token,
        client_ip=client_ip,
        user_agent=user_agent,
        db=db,
        simulated_now=now
    )

    reasoning = []

    # 1. SCENARIO: Customer Token accessing other accounts (Classic BOLA)
    if not context.is_employee:
        reasoning.append("Actor type: Customer (Retail User). Employee privilege suppression does NOT apply.")
        if len(accessed_accounts) > 1 or total_volume_count > 10:
            reasoning.append(f"Volume of distinct accounts accessed ({len(accessed_accounts)}) exceeds customer threshold (1).")
            return DetectionDecision(
                alert_triggered=True,
                severity="CRITICAL",
                attack_type="BOLA",
                reasoning_chain=reasoning + ["Confirmed BOLA / Horizontal privilege abuse on customer statement endpoint."],
                identity_context=context,
                action_recommended="BLOCK_TOKEN"
            )
        return DetectionDecision(
            alert_triggered=False,
            severity="NONE",
            reasoning_chain=reasoning + ["Normal customer single-account interaction."],
            identity_context=context,
            action_recommended="ALLOW"
        )

    # 2. SCENARIO: Privileged Identity - Check Geography & Stolen Identity Anomaly FIRST
    if context.geo_anomaly:
        reasoning.append(f"Privileged identity '{context.employee_id}' ({context.role}) detected from foreign/suspicious network.")
        reasoning.append(context.geo_details or "Unrecognized remote network infrastructure")
        reasoning.append("Alert elevated to HIGH priority: Privileged identity observed under anomalous/compromised context.")
        return DetectionDecision(
            alert_triggered=True,
            severity="HIGH",
            attack_type="STOLEN_IDENTITY",
            reasoning_chain=reasoning,
            identity_context=context,
            action_recommended="BLOCK_TOKEN",
            elevated_priority=True
        )

    # 3. SCENARIO: Inhuman Timing Velocity (<200ms rapid-fire)
    if inter_arrival_times_ms and len(inter_arrival_times_ms) > 5:
        avg_speed = sum(inter_arrival_times_ms) / len(inter_arrival_times_ms)
        min_speed = min(inter_arrival_times_ms)
        if min_speed < 200 or avg_speed < 250:
            reasoning.append(f"Privileged access timing is inhuman: minimum inter-arrival {min_speed:.1f}ms (threshold 200ms).")
            reasoning.append("Flagged as scripted automated scraping / token abuse even though credentials are valid.")
            return DetectionDecision(
                alert_triggered=True,
                severity="HIGH",
                attack_type="AUTOMATED_SCRIPTING",
                reasoning_chain=reasoning,
                identity_context=context,
                action_recommended="FLAG_FOR_AUDIT",
                elevated_priority=True
            )

    # 4. SCENARIO: Scope Violation (Even ONE out-of-scope account accessed)
    out_of_scope_accounts = [
        acc for acc in accessed_accounts
        if acc.get("region") and acc.get("region") not in context.allowed_regions
    ]
    if out_of_scope_accounts:
        reasoning.append(f"Privileged employee '{context.employee_id}' declared scope is {context.allowed_regions}.")
        reasoning.append(f"Violation: Accessed {len(out_of_scope_accounts)} accounts belonging to out-of-scope region(s): {[a.get('region') for a in out_of_scope_accounts]}.")
        reasoning.append("Accessing even one account outside declared scope raises an immediate alert, regardless of seniority.")
        return DetectionDecision(
            alert_triggered=True,
            severity="HIGH",
            attack_type="OUT_OF_SCOPE_ACCESS",
            reasoning_chain=reasoning,
            identity_context=context,
            action_recommended="FLAG_FOR_AUDIT",
            elevated_priority=True
        )

    # 5. SCENARIO: Volume Verification against Role Baseline & Active Campaigns
    volume_used = max(total_volume_count, len(accessed_accounts))
    if volume_used > context.effective_limit:
        # Volume exceeds allowed limit!
        if context.active_campaigns:
            reasoning.append(f"Active campaign(s) present: {context.active_campaigns}, but volume ({volume_used}) exceeds expanded limit ({context.effective_limit}).")
        else:
            reasoning.append(f"No active campaign covering role '{context.role}' at current timestamp.")
            reasoning.append(f"Volume ({volume_used}) strictly exceeds standard role baseline limit ({context.baseline_limit}/day).")

        return DetectionDecision(
            alert_triggered=True,
            severity="HIGH",
            attack_type="VOLUME_ABUSE",
            reasoning_chain=reasoning,
            identity_context=context,
            action_recommended="FLAG_FOR_AUDIT"
        )

    # 6. SCENARIO: Fresh Hire Grace Monitoring
    if context.is_fresh_hire:
        reasoning.append(f"Employee '{context.employee_id}' is a fresh hire (hire date {context.hire_date.strftime('%Y-%m-%d')}, within 14-day grace window).")
        reasoning.append(f"All {volume_used} accessed accounts are in-scope ({context.allowed_regions}).")
        reasoning.append(f"Volume is within grace baseline ({volume_used}/{context.effective_limit}).")
        reasoning.append("Monitoring note: visible on dashboard as Low-severity informational notice, not hidden.")
        return DetectionDecision(
            alert_triggered=True,
            severity="LOW",
            attack_type=None,
            reasoning_chain=reasoning,
            identity_context=context,
            action_recommended="LOG_INFORMATIONAL"
        )

    # 7. SCENARIO: Legitimate privileged access during active campaign or within baseline
    if context.active_campaigns:
        reasoning.append(f"role={context.role}, scope={context.declared_scope}, active_campaign={context.active_campaigns[0]}.")
        reasoning.append(f"All {volume_used} accessed accounts fall strictly within authorized scope {context.allowed_regions}.")
        reasoning.append(f"Volume {volume_used} is within sanctioned campaign multiplier limit ({context.effective_limit}/day).")
        reasoning.append("BOLA alert suppressed: validated legitimate privileged business activity.")
        return DetectionDecision(
            alert_triggered=False,
            severity="INFORMATIONAL",
            attack_type=None,
            reasoning_chain=reasoning,
            identity_context=context,
            action_recommended="ALLOW"
        )

    # 8. Normal day-to-day privileged activity
    reasoning.append(f"Normal operational activity for {context.role} ({context.employee_id}).")
    reasoning.append(f"Volume {volume_used} <= baseline {context.effective_limit}. Scope verified.")
    return DetectionDecision(
        alert_triggered=False,
        severity="NONE",
        reasoning_chain=reasoning,
        identity_context=context,
        action_recommended="ALLOW"
    )
