"""
Box C: Explainable Risk Scoring Engine.
Calculates a 0-100 composite risk score with complete mathematical explainability,
structured Reason Vectors, and Native OWASP API Security Top 10 (2023) Mappings.
"""

from typing import List, Dict, Optional, Tuple, Any
from core.models import (
    TelemetryEvent,
    RiskScore,
    ReasonFactor,
    SpecDriftStatus,
    PIISeverity,
    PIIMatch,
    AbuseAlert,
    AbuseAlertType,
    OWASPCategory
)


class RiskScorer:
    """
    Computes explainable weighted risk score (0-100):
    - 35% Exposure (Public unauth vs auth strength) -> OWASP API2:2023
    - 25% PII Data Sensitivity (PAN / Aadhaar) -> OWASP API3:2023
    - 20% Spec Drift (Shadow / Zombie Status) -> OWASP API9:2023
    - 20% Active Anomaly & Attack Frequency (BOLA, Scraping, Replay, Workflow)
    """

    @classmethod
    def calculate_score(cls,
                        event: TelemetryEvent,
                        parameterized_path: str,
                        extracted_params: Dict[str, str],
                        spec_status: SpecDriftStatus,
                        pii_matches: List[PIIMatch],
                        pii_severity: PIISeverity,
                        abuse_alerts: List[AbuseAlert],
                        session_graph: Optional[Dict[str, Any]] = None) -> RiskScore:
        factors: List[ReasonFactor] = []
        reason_vector_items: List[str] = []

        # ---------------------------------------------------------
        # 1. Exposure (Max 35 points) - OWASP API2:2023
        # ---------------------------------------------------------
        exposure_pts = 0
        auth_header = event.headers.get("authorization", "") or event.headers.get("Authorization", "")

        if not auth_header and not event.jwt_sub:
            # Exclude inherently public routes like login, auth, health, ifsc search from unauth exposure penalties
            path_lower = event.path.lower()
            if any(p in path_lower for p in ("/auth/login", "/auth/", "health", "/search/ifsc")):
                exposure_pts = 0
            else:
                exposure_pts = 35
                factors.append(ReasonFactor(
                    factor="Exposure",
                    points=35,
                    description="+35 Unauthenticated Exposure",
                    owasp_category=OWASPCategory.API2_BROKEN_AUTH
                ))
                reason_vector_items.append("+35 Unauth")
        elif "basic" in auth_header.lower():
            exposure_pts = 20
            factors.append(ReasonFactor(
                factor="Exposure",
                points=20,
                description="+20 Weak Basic Authentication",
                owasp_category=OWASPCategory.API2_BROKEN_AUTH
            ))
            reason_vector_items.append("+20 Weak Auth")
        else:
            exposure_pts = 0

        # ---------------------------------------------------------
        # 2. PII Data Sensitivity (Max 25 points) - OWASP API3:2023
        # ---------------------------------------------------------
        pii_pts = 0
        path_lower = event.path.lower()
        is_auth_endpoint = any(p in path_lower for p in ("/auth/login", "/auth/", "health", "/auth/refresh"))

        if pii_severity == PIISeverity.CRITICAL:
            pii_pts = 25
            crit_types = [m.entity_type for m in pii_matches if m.severity == PIISeverity.CRITICAL]
            label = "/".join(set(crit_types)) if crit_types else "PAN/Aadhaar"
            factors.append(ReasonFactor(
                factor="PII",
                points=25,
                description=f"+25 Critical PII Exposure ({label})",
                owasp_category=OWASPCategory.API3_PROPERTY_AUTH
            ))
            reason_vector_items.append(f"+25 PII ({label})")
        elif pii_severity == PIISeverity.SENSITIVE:
            # Identity credentials (email/phone) transmitted during legitimate authentication are not data leaks
            if is_auth_endpoint:
                pii_pts = 0
            else:
                pii_pts = 15
                sens_types = [m.entity_type for m in pii_matches if m.severity == PIISeverity.SENSITIVE]
                label = "/".join(set(sens_types)) if sens_types else "UPI/Phone"
                factors.append(ReasonFactor(
                    factor="PII",
                    points=15,
                    description=f"+15 Sensitive PII Exposure ({label})",
                    owasp_category=OWASPCategory.API3_PROPERTY_AUTH
                ))
                reason_vector_items.append(f"+15 PII ({label})")

        # ---------------------------------------------------------
        # 3. Spec Drift Status (Max 20 points) - OWASP API9:2023
        # ---------------------------------------------------------
        spec_pts = 0
        if spec_status == SpecDriftStatus.SHADOW:
            spec_pts = 20
            factors.append(ReasonFactor(
                factor="SpecDrift",
                points=20,
                description="+20 Undocumented Shadow Route",
                owasp_category=OWASPCategory.API9_IMPROPER_INVENTORY
            ))
            reason_vector_items.append("+20 Shadow")
        elif spec_status == SpecDriftStatus.ZOMBIE:
            spec_pts = 15
            factors.append(ReasonFactor(
                factor="SpecDrift",
                points=15,
                description="+15 Deprecated Zombie v1 Endpoint",
                owasp_category=OWASPCategory.API9_IMPROPER_INVENTORY
            ))
            reason_vector_items.append("+15 Zombie")

        # ---------------------------------------------------------
        # 4. Active Anomaly & Attack Frequency (Max 20 points)
        # ---------------------------------------------------------
        anomaly_pts = 0
        if abuse_alerts:
            alert_types = set(a.alert_type for a in abuse_alerts)
            if AbuseAlertType.BOLA_IDOR in alert_types:
                anomaly_pts = 20
                factors.append(ReasonFactor(
                    factor="AbuseAnomaly",
                    points=20,
                    description="+20 BOLA / IDOR Violation",
                    owasp_category=OWASPCategory.API1_BOLA
                ))
                reason_vector_items.append("+20 BOLA")
            elif AbuseAlertType.WORKFLOW_VIOLATION in alert_types:
                anomaly_pts = 20
                factors.append(ReasonFactor(
                    factor="AbuseAnomaly",
                    points=20,
                    description="+20 Workflow Sequence / Graph Violation",
                    owasp_category=OWASPCategory.API6_BUSINESS_FLOW
                ))
                reason_vector_items.append("+20 Workflow Violation")
            elif AbuseAlertType.TOKEN_REPLAY in alert_types:
                anomaly_pts = 20
                factors.append(ReasonFactor(
                    factor="AbuseAnomaly",
                    points=20,
                    description="+20 Token Replay Misuse",
                    owasp_category=OWASPCategory.API2_BROKEN_AUTH
                ))
                reason_vector_items.append("+20 Replay")
            elif AbuseAlertType.DATA_SCRAPING in alert_types or AbuseAlertType.BYTE_SPIKE in alert_types:
                anomaly_pts = 15
                factors.append(ReasonFactor(
                    factor="AbuseAnomaly",
                    points=15,
                    description="+15 High-Velocity Scraping / Byte Spike",
                    owasp_category=OWASPCategory.API4_UNRESTRICTED_RESOURCE
                ))
                reason_vector_items.append("+15 Scraping")

        # ---------------------------------------------------------
        # Composite Calculation (Capped at 100)
        # ---------------------------------------------------------
        raw_total = exposure_pts + pii_pts + spec_pts + anomaly_pts
        final_score = min(100, raw_total)

        # Severity categorization
        if final_score >= 85:
            severity = "CRITICAL"
        elif final_score >= 70:
            severity = "HIGH"
        elif final_score >= 40:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        # Determine Primary OWASP Category
        primary_owasp = None
        for alert in abuse_alerts:
            if alert.owasp_category:
                primary_owasp = alert.owasp_category
                break
        if not primary_owasp:
            for factor in factors:
                if factor.owasp_category:
                    primary_owasp = factor.owasp_category
                    break

        # Evaluation against simulation ground truth if provided
        evaluation_label = None
        if event.ground_truth and event.ground_truth.lower() not in ("unlabeled", "none", ""):
            is_predicted_threat = (
                final_score >= 35 
                or bool(abuse_alerts) 
                or (spec_status in (SpecDriftStatus.SHADOW, SpecDriftStatus.ZOMBIE) and final_score >= 30)
            )
            is_actual_attack = event.ground_truth.lower().startswith("attack_")

            if is_actual_attack and is_predicted_threat:
                evaluation_label = "TP"
            elif not is_actual_attack and is_predicted_threat:
                evaluation_label = "FP"
            elif not is_actual_attack and not is_predicted_threat:
                evaluation_label = "TN"
            elif is_actual_attack and not is_predicted_threat:
                evaluation_label = "FN"

        return RiskScore(
            request_id=event.request_id,
            risk_score=final_score,
            severity=severity,
            primary_owasp_category=primary_owasp,
            reason_vector=reason_vector_items,
            factors=factors,
            parameterized_path=parameterized_path,
            extracted_params=extracted_params,
            spec_status=spec_status,
            pii_matches=pii_matches,
            abuse_alerts=abuse_alerts,
            session_graph=session_graph,
            timestamp=event.timestamp,
            evaluation_label=evaluation_label
        )
