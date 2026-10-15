"""
Outbound Supply-Chain Guard (Sentinel-API Phase 2 - Blind Spot #5).
Mitigates OWASP API10:2023 Unsafe Consumption of APIs:
1. Strict Pydantic Schema Contracts (rejects rogue fields and schema drift).
2. Second-Order Injection & Stored XSS scanning using InjectionInspector.
3. Numerical sanity bounds on financial rates and supplier metrics.
4. Telemetry emission with dedicated OWASP_API10_SUPPLY_CHAIN_POISONING events.
"""

import re
import math
import time
import logging
from typing import Dict, Any, List, Optional, Tuple, Type
from pydantic import BaseModel, ConfigDict, ValidationError

from person1_api_discovery.app.deep_inspector import InjectionInspector

logger = logging.getLogger("sentinel.egress_guard")

# =============================================================================
# 1. COMPILED PATTERNS & SCHEMAS
# =============================================================================

XSS_PATTERNS = [
    re.compile(r"(?i)<\s*script[^>]*>.*?</\s*script\s*>", re.DOTALL),
    re.compile(r"(?i)<\s*script[^>]*>", re.IGNORECASE),
    re.compile(r"(?i)javascript\s*:", re.IGNORECASE),
    re.compile(r"(?i)\bon\w+\s*=", re.IGNORECASE),  # onerror=, onload=, onclick=
    re.compile(r"(?i)alert\s*\(", re.IGNORECASE),
    re.compile(r"(?i)document\.(?:cookie|location|domain)", re.IGNORECASE)
]


class FXRateVendorResponse(BaseModel):
    """Strict schema contract for external FX rate provider."""
    model_config = ConfigDict(extra="forbid")

    vendor: str
    from_currency: str
    to_currency: str
    rate: float
    quote_id: str
    timestamp: str


class FedExTrackingVendorResponse(BaseModel):
    """Strict schema contract for external logistics/delivery webhook provider."""
    model_config = ConfigDict(extra="forbid")

    tracking_id: str
    carrier: str
    status: str
    estimated_delivery_days: int
    timestamp: str


# =============================================================================
# 2. RESULT & EXCEPTION STRUCTURES
# =============================================================================

class SupplyChainPoisoningException(Exception):
    """Raised when third-party vendor response contains poisoned payloads or violates contract."""
    def __init__(self, message: str, threat_indicators: List[str], details: Dict[str, Any]):
        super().__init__(message)
        self.message = message
        self.threat_indicators = threat_indicators
        self.details = details


class EgressInspectionResult:
    """Detailed verdict of vendor response evaluation."""
    def __init__(self):
        self.is_poisoned: bool = False
        self.threat_indicators: List[str] = []
        self.owasp_categories: List[str] = []
        self.severity: str = "LOW"
        self.confidence: float = 0.0
        self.reasons: List[str] = []
        self.details: Dict[str, Any] = {}
        self.sanitized_payload: Optional[Dict[str, Any]] = None
        self.execution_latency_ms: float = 0.0

    def add_finding(self, indicator: str, owasp: str, severity: str, confidence: float, reason: str, meta: Optional[Dict[str, Any]] = None):
        self.is_poisoned = True
        if indicator not in self.threat_indicators:
            self.threat_indicators.append(indicator)
        if owasp not in self.owasp_categories:
            self.owasp_categories.append(owasp)
        self.reasons.append(reason)
        self.confidence = max(self.confidence, confidence)

        sev_hierarchy = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
        if sev_hierarchy.get(severity, 1) > sev_hierarchy.get(self.severity, 1):
            self.severity = severity

        if meta:
            self.details.setdefault(indicator, []).append(meta)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_poisoned": self.is_poisoned,
            "threat_indicators": self.threat_indicators,
            "owasp_categories": self.owasp_categories,
            "severity": self.severity,
            "confidence": round(self.confidence, 2),
            "reasons": self.reasons,
            "details": self.details,
            "execution_latency_ms": round(self.execution_latency_ms, 3)
        }


# =============================================================================
# 3. SAFE EXTERNAL API CLIENT (SUPPLY-CHAIN GUARD)
# =============================================================================

class SafeExternalAPIClient:
    """
    Secure client wrapper protecting the banking backend from poisoned third-party APIs.
    Enforces strict Pydantic contract validation, second-order SQLi/XSS scanning,
    and numerical sanity checks.
    """

    def __init__(self):
        self.injection_inspector = InjectionInspector()
        self.threat_telemetry_log: List[Dict[str, Any]] = []

    def inspect_vendor_response(
        self,
        vendor_payload: Dict[str, Any],
        schema_model: Optional[Type[BaseModel]] = None,
        numeric_bounds: Optional[Dict[str, Tuple[float, float]]] = None
    ) -> EgressInspectionResult:
        """
        Runs comprehensive supply-chain poisoning inspection on third-party API payload.
        """
        t0 = time.perf_counter()
        result = EgressInspectionResult()

        if not isinstance(vendor_payload, dict):
            result.add_finding(
                "INVALID_VENDOR_PAYLOAD_STRUCTURE",
                "API10:2023 Unsafe Consumption of APIs",
                "HIGH",
                0.90,
                f"Expected JSON object from external vendor, got {type(vendor_payload).__name__}"
            )
            result.execution_latency_ms = (time.perf_counter() - t0) * 1000.0
            return result

        # 1. Strict Schema Contract Validation (Extra Fields & Type Drift)
        if schema_model:
            try:
                validated_obj = schema_model.model_validate(vendor_payload)
                result.sanitized_payload = validated_obj.model_dump()
            except ValidationError as ve:
                for err in ve.errors():
                    err_type = err.get("type", "")
                    field_loc = ".".join(str(x) for x in err.get("loc", []))
                    err_msg = err.get("msg", "")

                    if err_type == "extra_forbidden":
                        result.add_finding(
                            "VENDOR_SCHEMA_DRIFT",
                            "API10:2023 Unsafe Consumption of APIs",
                            "HIGH",
                            0.95,
                            f"Unexpected extra field '{field_loc}' injected into vendor payload (schema drift / prototype pollution)",
                            {"field": field_loc, "error": err_msg}
                        )
                    else:
                        result.add_finding(
                            "VENDOR_TYPE_DRIFT",
                            "API10:2023 Unsafe Consumption of APIs",
                            "HIGH",
                            0.92,
                            f"Field '{field_loc}' violates vendor contract: {err_msg}",
                            {"field": field_loc, "error": err_msg}
                        )

        # 2. Second-Order Injection Scanning (SQLi, NoSQLi, OS Command Injection)
        injection_findings = self.injection_inspector.inspect_json(vendor_payload, "vendor_response")
        for ind, owasp, sev, conf, reason in injection_findings:
            result.add_finding(
                f"SECOND_ORDER_{ind}",
                "API10:2023 Unsafe Consumption of APIs",
                "CRITICAL",
                conf,
                f"Second-Order injection detected in vendor response: {reason}",
                {"raw_finding": ind}
            )

        # 3. Stored XSS / Script Tag Scanning
        def scan_xss(data: Any, path: str = "vendor_response"):
            if isinstance(data, dict):
                for k, v in data.items():
                    scan_xss(v, f"{path}.{k}")
            elif isinstance(data, list):
                for idx, v in enumerate(data):
                    scan_xss(v, f"{path}[{idx}]")
            elif isinstance(data, str):
                for pattern in XSS_PATTERNS:
                    if pattern.search(data):
                        result.add_finding(
                            "STORED_XSS_DETECTED",
                            "API10:2023 Unsafe Consumption of APIs",
                            "CRITICAL",
                            0.98,
                            f"Stored XSS / malicious HTML script tag detected in vendor field '{path}'",
                            {"field": path, "sample": data[:100]}
                        )
                        break

        scan_xss(vendor_payload)

        # 4. Numerical Sanity Bounds
        bounds = numeric_bounds or {
            "rate": (0.0001, 1_000_000.0),
            "amount": (0.0, 100_000_000.0),
            "estimated_delivery_days": (0, 365)
        }

        def check_numbers(data: Any, path: str = "vendor_response"):
            if isinstance(data, dict):
                for k, v in data.items():
                    k_lower = str(k).lower()
                    cur_path = f"{path}.{k}"
                    if isinstance(v, (int, float)):
                        if math.isnan(v) or math.isinf(v):
                            result.add_finding(
                                "NUMERICAL_SANITY_VIOLATION",
                                "API10:2023 Unsafe Consumption of APIs",
                                "CRITICAL",
                                0.99,
                                f"Vendor returned non-numeric float (NaN/Inf) at '{cur_path}'"
                            )
                        elif k_lower in bounds:
                            min_val, max_val = bounds[k_lower]
                            if v < min_val or v > max_val:
                                result.add_finding(
                                    "NUMERICAL_SANITY_VIOLATION",
                                    "API10:2023 Unsafe Consumption of APIs",
                                    "CRITICAL",
                                    0.97,
                                    f"Vendor field '{cur_path}' value ({v}) outside valid domain bounds [{min_val}, {max_val}]"
                                )
                    elif isinstance(v, (dict, list)):
                        check_numbers(v, cur_path)
            elif isinstance(data, list):
                for idx, item in enumerate(data):
                    check_numbers(item, f"{path}[{idx}]")

        check_numbers(vendor_payload)

        # If any poisoning detected, add the primary umbrella OWASP tag
        if result.is_poisoned:
            if "OWASP_API10_SUPPLY_CHAIN_POISONING" not in result.threat_indicators:
                result.threat_indicators.insert(0, "OWASP_API10_SUPPLY_CHAIN_POISONING")

            # Record in telemetry buffer
            telemetry_entry = {
                "timestamp": time.time(),
                "verdict": "POISONED_SUPPLY_CHAIN_BLOCKED",
                "indicators": result.threat_indicators,
                "reasons": result.reasons,
                "vendor_sample": {k: str(v)[:80] for k, v in vendor_payload.items()}
            }
            self.threat_telemetry_log.append(telemetry_entry)
            if len(self.threat_telemetry_log) > 200:
                self.threat_telemetry_log.pop(0)

        result.execution_latency_ms = (time.perf_counter() - t0) * 1000.0
        return result

    def ingest_fx_rate(self, vendor_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Safe gateway method for ingesting FX rate provider responses.
        Raises SupplyChainPoisoningException if vendor response is poisoned.
        """
        inspection = self.inspect_vendor_response(
            vendor_payload,
            schema_model=FXRateVendorResponse,
            numeric_bounds={"rate": (0.0001, 1_000_000.0)}
        )

        if inspection.is_poisoned:
            logger.warning(
                f"[GUARD_DEFENSE] Blocked poisoned FX vendor response: {inspection.reasons}"
            )
            raise SupplyChainPoisoningException(
                message="External FX vendor returned a corrupted or malicious payload",
                threat_indicators=inspection.threat_indicators,
                details=inspection.to_dict()
            )

        return inspection.sanitized_payload or vendor_payload

    def ingest_fedex_tracking(self, vendor_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Safe gateway method for ingesting shipping/logistics webhook provider responses.
        """
        inspection = self.inspect_vendor_response(
            vendor_payload,
            schema_model=FedExTrackingVendorResponse,
            numeric_bounds={"estimated_delivery_days": (0, 365)}
        )

        if inspection.is_poisoned:
            logger.warning(
                f"[GUARD_DEFENSE] Blocked poisoned FedEx vendor response: {inspection.reasons}"
            )
            raise SupplyChainPoisoningException(
                message="External logistics vendor returned an untrusted or poisoned payload",
                threat_indicators=inspection.threat_indicators,
                details=inspection.to_dict()
            )

        return inspection.sanitized_payload or vendor_payload


# Global Singleton Guard
safe_external_client = SafeExternalAPIClient()
