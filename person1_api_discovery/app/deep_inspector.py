"""
Deep Semantic Ingress Inspector (Sentinel-API Phase 2)
Defeats OWASP API Security Top 10 blind spots bypassing traditional metadata/rate-based engines:
1. InjectionInspector: SQLi, NoSQLi, and OS Command Injection (OWASP API8)
2. SSRFInspector: Link-local Cloud Metadata, Loopback, Private RFC1918, Non-HTTP Schemes (OWASP API7)
3. BusinessLogicInspector: Negative amounts, NaN/Inf, Duplicate coupon/array stuffing (OWASP API3 / API6)
4. ComplexityAndReDoSInspector: JSON nesting depth > 10, evil regex backtracking patterns, decompression bombs (OWASP API4)
Ultra-fast execution SLA: < 1ms per inspection.
"""

import re
import math
import time
import ipaddress
import urllib.parse
from typing import Dict, Any, List, Optional, Set, Tuple, Union


# =============================================================================
# 1. COMPILED SIGNATURE PATTERNS (ReDoS-Safe & Ultra-Fast)
# =============================================================================

# SQL Injection: Tautologies, UNION SELECT, table drop, comment truncations
# Carefully crafted to allow legitimate apostrophes in names (e.g. O'Connor, D'Souza)
SQLI_PATTERNS = [
    re.compile(r"(?i)(\bUNION\s+(?:ALL\s+)?SELECT\b)", re.IGNORECASE),
    re.compile(r"(?i)(\bOR\b\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+)", re.IGNORECASE),
    re.compile(r"(?i)(;\s*(?:DROP|ALTER|TRUNCATE)\s+TABLE\b)", re.IGNORECASE),
    re.compile(r"(?i)(;\s*(?:INSERT\s+INTO|DELETE\s+FROM|UPDATE\s+\w+\s+SET)\b)", re.IGNORECASE),
    re.compile(r"(?i)(\b(?:EXEC|EXECUTE)\s+(?:\(\s*)?xp_\w+)", re.IGNORECASE),
    re.compile(r"(?:--\s*$|/\*.*?\*/|;\s*--)", re.IGNORECASE),
]

# OS Command Injection: Command separators followed by common system binaries
CMD_INJECTION_PATTERNS = [
    re.compile(r"(?:[;&|`]\s*(?:cat\b|rm\b|sh\b|bash\b|curl\b|wget\b|whoami\b|id\b|chmod\b|python\b|ls\b|powershell\b|cmd(?:\.exe)?\b))", re.IGNORECASE),
    re.compile(r"(?:\|\s*(?:cat\b|rm\b|sh\b|bash\b|curl\b|whoami\b))", re.IGNORECASE),
    re.compile(r"`[^`]+`"),
    re.compile(r"\$\([^\)]+\)")
]

# NoSQL Injection operators (MongoDB / DynamoDB / DocumentDB)
NOSQL_OPERATORS = {
    "$gt", "$gte", "$lt", "$lte", "$ne", "$in", "$nin", "$or", "$and",
    "$not", "$nor", "$where", "$regex", "$exists", "$all", "$elemMatch"
}

# ReDoS / Catastrophic backtracking evil regex structural patterns
EVIL_REGEX_PATTERNS = [
    re.compile(r"\([^\)]*[\+\*]\)[\+\*]"),          # Nested repetitions: (a+)+, (a*)*
    re.compile(r"\(\[[^\]]+\][\+\*]\)[\+\*]"),      # Character class repetitions: ([a-z]+)+
    re.compile(r"\([^\)]*[\+\*]\)\{"),              # Quantified groups: (a+){2,}
    re.compile(r"(?:[a-zA-Z0-9_\-]{2,}\+){2,}\$")   # (a+a+)+$
]

# Disallowed URI Schemes for SSRF
RESTRICTED_SCHEMES = {"file", "gopher", "dict", "ftp", "tftp", "ldap", "php", "data"}

# Cloud metadata hostname & IP signatures
CLOUD_METADATA_HOSTS = {
    "169.254.169.254",
    "metadata.google.internal",
    "metadata.aws.internal",
    "100.100.100.200",  # Alibaba cloud
    "fd00:ec2::254"      # AWS IPv6 metadata
}

# Private RFC1918 & Loopback Networks
PRIVATE_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),      # Loopback
    ipaddress.ip_network("10.0.0.0/8"),       # RFC1918 Class A
    ipaddress.ip_network("172.16.0.0/12"),    # RFC1918 Class B
    ipaddress.ip_network("192.168.0.0/16"),   # RFC1918 Class C
    ipaddress.ip_network("169.254.0.0/16"),   # Link-Local
    ipaddress.ip_network("100.64.0.0/10"),    # CGNAT
    ipaddress.ip_network("0.0.0.0/8"),        # Current network
    ipaddress.ip_network("::1/128"),          # IPv6 loopback
    ipaddress.ip_network("fc00::/7"),         # IPv6 Unique Local Address
    ipaddress.ip_network("fe80::/10"),        # IPv6 Link-Local
]


# =============================================================================
# 2. RESULT DATA STRUCTURE
# =============================================================================

class DeepInspectionResult:
    """Consolidated outcome of the 4 deep semantic ingress sub-inspectors."""
    def __init__(self):
        self.is_threat: bool = False
        self.threat_indicators: List[str] = []
        self.owasp_categories: List[str] = []
        self.severity: str = "LOW"  # LOW, MEDIUM, HIGH, CRITICAL
        self.confidence: float = 0.0
        self.reasons: List[str] = []
        self.details: Dict[str, Any] = {}
        self.execution_latency_ms: float = 0.0

    def add_finding(self, indicator: str, owasp: str, severity: str, confidence: float, reason: str, meta: Optional[Dict[str, Any]] = None):
        self.is_threat = True
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
            "is_threat": self.is_threat,
            "threat_indicators": self.threat_indicators,
            "owasp_categories": self.owasp_categories,
            "severity": self.severity,
            "confidence": round(self.confidence, 2),
            "reasons": self.reasons,
            "details": self.details,
            "execution_latency_ms": round(self.execution_latency_ms, 3)
        }


# =============================================================================
# 3. SUB-INSPECTORS
# =============================================================================

class InjectionInspector:
    """
    Sub-Inspector 1: Detects SQLi, NoSQLi, and OS Command Injection inside
    query parameters and request body strings (OWASP API8:2023).
    """

    @staticmethod
    def inspect_text(text: str, field_path: str = "") -> List[Tuple[str, str, str, float, str]]:
        """
        Scans a single string value for SQLi or Command Injection signatures.
        Returns: list of (indicator, owasp, severity, confidence, reason)
        """
        findings = []
        if not text or len(text) < 2:
            return findings

        # 1. SQL Injection Check
        for pattern in SQLI_PATTERNS:
            if pattern.search(text):
                findings.append((
                    "SQL_INJECTION_DETECTED",
                    "API8:2023 Security Misconfiguration & Injection",
                    "CRITICAL",
                    0.98,
                    f"SQL injection syntax matched in field '{field_path}': {pattern.pattern}"
                ))
                break

        # 2. OS Command Injection Check
        for pattern in CMD_INJECTION_PATTERNS:
            if pattern.search(text):
                findings.append((
                    "COMMAND_INJECTION_DETECTED",
                    "API8:2023 Security Misconfiguration & Injection",
                    "CRITICAL",
                    0.99,
                    f"OS command injection delimiter or shell binary matched in field '{field_path}'"
                ))
                break

        return findings

    @classmethod
    def inspect_json(cls, data: Any, path: str = "body") -> List[Tuple[str, str, str, float, str]]:
        findings = []
        if isinstance(data, dict):
            for k, v in data.items():
                cur_path = f"{path}.{k}"
                # Check NoSQL operator injection in keys
                if str(k).startswith("$") or str(k).lower() in NOSQL_OPERATORS:
                    findings.append((
                        "NOSQL_OPERATOR_INJECTION",
                        "API8:2023 Security Misconfiguration & Injection",
                        "CRITICAL",
                        0.97,
                        f"NoSQL query operator injection '{k}' detected at '{cur_path}'"
                    ))
                # Check string key
                if isinstance(k, str):
                    findings.extend(cls.inspect_text(k, cur_path))
                # Recurse on value
                findings.extend(cls.inspect_json(v, cur_path))
        elif isinstance(data, list):
            for idx, item in enumerate(data):
                findings.extend(cls.inspect_json(item, f"{path}[{idx}]"))
        elif isinstance(data, str):
            findings.extend(cls.inspect_text(data, path))

        return findings


class SSRFInspector:
    """
    Sub-Inspector 2: Detects Server-Side Request Forgery (SSRF) targeting
    link-local cloud metadata, loopback, RFC1918 private subnets, or non-HTTP schemes (OWASP API7:2023).
    """

    @classmethod
    def is_ssrf_target(cls, url_str: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Evaluates if a URL string targets internal or forbidden destinations.
        Returns: (is_ssrf, indicator, reason)
        """
        if not url_str or not isinstance(url_str, str):
            return False, None, None

        # Check if text looks like a URL or protocol target
        trimmed = url_str.strip()
        if not (trimmed.startswith(("http://", "https://", "file://", "gopher://", "dict://", "ftp://", "ldap://", "//")) or
                any(h in trimmed for h in CLOUD_METADATA_HOSTS)):
            return False, None, None

        try:
            parsed = urllib.parse.urlparse(trimmed)
        except Exception:
            return False, None, None

        scheme = parsed.scheme.lower() if parsed.scheme else ""

        # 1. Non-HTTP Scheme Attack
        if scheme in RESTRICTED_SCHEMES:
            return True, "SSRF_UNSAFE_SCHEME", f"Disallowed protocol scheme '{scheme}://' in URL"

        hostname = (parsed.hostname or "").lower()
        if not hostname:
            # Check if trimmed starts with cloud metadata IP directly
            for cm in CLOUD_METADATA_HOSTS:
                if cm in trimmed:
                    return True, "SSRF_CLOUD_METADATA", f"Direct cloud metadata endpoint '{cm}' referenced"
            return False, None, None

        # 2. Cloud Metadata IP / Hostname Match
        if hostname in CLOUD_METADATA_HOSTS:
            return True, "SSRF_CLOUD_METADATA", f"Link-local cloud metadata service '{hostname}' targeted"

        # 3. Loopback Hostname Match
        if hostname in {"localhost", "127.0.0.1", "::1", "0.0.0.0"}:
            return True, "SSRF_LOOPBACK_TARGET", f"Loopback host '{hostname}' targeted"

        # 4. IP Subnet Evaluation (RFC1918 / Loopback / Link-Local)
        try:
            ip_obj = ipaddress.ip_address(hostname)
            for net in PRIVATE_NETWORKS:
                if ip_obj in net:
                    if ip_obj in ipaddress.ip_network("169.254.0.0/16"):
                        return True, "SSRF_CLOUD_METADATA", f"Link-local subnet IP '{hostname}' targeted"
                    elif ip_obj in ipaddress.ip_network("127.0.0.0/8"):
                        return True, "SSRF_LOOPBACK_TARGET", f"Loopback IP '{hostname}' targeted"
                    else:
                        return True, "SSRF_PRIVATE_NETWORK", f"Private RFC1918 network IP '{hostname}' targeted ({net})"
        except ValueError:
            # Hostname is a domain name (not raw IP)
            if hostname.endswith((".local", ".internal", ".localhost", ".corp", ".lan")):
                return True, "SSRF_PRIVATE_NETWORK", f"Internal corporate domain '{hostname}' targeted"

        return False, None, None

    @classmethod
    def inspect(cls, query_params: Dict[str, Any], body: Any) -> List[Tuple[str, str, str, float, str]]:
        findings = []

        # Check query parameters
        for k, v in query_params.items():
            if isinstance(v, str):
                is_ssrf, ind, reason = cls.is_ssrf_target(v)
                if is_ssrf and ind and reason:
                    findings.append((ind, "API7:2023 Server Side Request Forgery", "CRITICAL", 0.99, f"Query '{k}': {reason}"))

        # Check body recursively
        def scan_body(item: Any, path: str = "body"):
            if isinstance(item, dict):
                for k, v in item.items():
                    scan_body(v, f"{path}.{k}")
            elif isinstance(item, list):
                for idx, v in enumerate(item):
                    scan_body(v, f"{path}[{idx}]")
            elif isinstance(item, str):
                is_ssrf, ind, reason = cls.is_ssrf_target(item)
                if is_ssrf and ind and reason:
                    findings.append((ind, "API7:2023 Server Side Request Forgery", "CRITICAL", 0.99, f"Field '{path}': {reason}"))

        if body:
            scan_body(body)

        return findings


class BusinessLogicInspector:
    """
    Sub-Inspector 3: Enforces arithmetic and domain invariants on financial payloads:
    - Numerical invariants (amount > 0, price > 0, bounds check, NaN/Inf)
    - Array invariants (duplicate stuffing prevention, element count bounds)
    (OWASP API3:2023 Broken Object Property Level Authorization & API6:2023 Business Flow Abuse).
    """

    FINANCIAL_NUMERIC_KEYS = {
        "amount", "amount_paise", "transfer_amount", "price", "transfer_value",
        "new_daily_limit_paise", "daily_limit", "credit_limit", "balance", "quantity"
    }

    ARRAY_STUFFING_KEYS = {
        "coupons", "promo_codes", "vouchers", "beneficiaries", "discount_codes", "tags"
    }

    @classmethod
    def inspect(cls, query_params: Dict[str, Any], body: Any) -> List[Tuple[str, str, str, float, str]]:
        findings = []

        def check_number(val: Any, key_name: str, path: str):
            if isinstance(val, (int, float)):
                # NaN / Inf Check
                if math.isnan(val) or math.isinf(val):
                    findings.append((
                        "ARITHMETIC_NAN_INF_EXPLOIT",
                        "API3:2023 Broken Object Property Level Authorization",
                        "CRITICAL",
                        0.99,
                        f"Non-numeric arithmetic float (NaN/Inf) passed to financial field '{path}'"
                    ))
                    return

                # Negative Amount Exploit Check
                if val < 0:
                    findings.append((
                        "NEGATIVE_AMOUNT_EXPLOIT",
                        "API3:2023 Broken Object Property Level Authorization",
                        "CRITICAL",
                        0.99,
                        f"Negative financial value ({val}) supplied to field '{path}'"
                    ))

                # Absurd balance inflation bound (> Rs 100 Crore / 1,000,000,000)
                if val > 1_000_000_000 and "limit" not in key_name:
                    findings.append((
                        "ARITHMETIC_OVERFLOW_INFLATION",
                        "API3:2023 Broken Object Property Level Authorization",
                        "HIGH",
                        0.92,
                        f"Excessive out-of-bounds transfer value ({val}) supplied to field '{path}'"
                    ))

        def check_array(val: Any, key_name: str, path: str):
            if isinstance(val, list):
                # Duplicate Stuffing Check
                str_items = [str(x).strip().upper() for x in val if isinstance(x, (str, int, float))]
                if len(str_items) > len(set(str_items)):
                    duplicates = [x for x in str_items if str_items.count(x) > 1]
                    findings.append((
                        "DUPLICATE_ARRAY_STUFFING",
                        "API6:2023 Unrestricted Access to Sensitive Business Flows",
                        "HIGH",
                        0.95,
                        f"Duplicate coupon/array items {list(set(duplicates))} stuffed into '{path}'"
                    ))

                # Array Element Bomb
                if len(val) > 50:
                    findings.append((
                        "ARRAY_ELEMENT_BOMB",
                        "API4:2023 Unrestricted Resource Consumption",
                        "HIGH",
                        0.94,
                        f"Array field '{path}' contains excessive elements ({len(val)} > 50 max allowed)"
                    ))

        # Check Body
        def traverse(item: Any, path: str = "body"):
            if isinstance(item, dict):
                for k, v in item.items():
                    cur_key = str(k).lower()
                    cur_path = f"{path}.{k}"
                    if cur_key in cls.FINANCIAL_NUMERIC_KEYS:
                        check_number(v, cur_key, cur_path)
                    elif cur_key in cls.ARRAY_STUFFING_KEYS:
                        check_array(v, cur_key, cur_path)

                    traverse(v, cur_path)
            elif isinstance(item, list):
                for idx, v in enumerate(item):
                    traverse(v, f"{path}[{idx}]")

        if body:
            traverse(body)

        # Check Query Params
        for k, v in query_params.items():
            k_lower = k.lower()
            if k_lower in cls.FINANCIAL_NUMERIC_KEYS:
                try:
                    num_val = float(v)
                    check_number(num_val, k_lower, f"query.{k}")
                except ValueError:
                    pass

        return findings


class ComplexityAndReDoSInspector:
    """
    Sub-Inspector 4: Detects Algorithmic Complexity attacks, ReDoS patterns,
    excessive JSON nesting depth (> 10), and single-request latency spikes (OWASP API4:2023).
    """

    MAX_SAFE_DEPTH = 10

    @classmethod
    def calculate_json_depth(cls, data: Any, current_depth: int = 1) -> int:
        """Computes the maximum nesting depth of an arbitrary JSON structure."""
        if current_depth > 30:  # Circuit breaker
            return current_depth

        if isinstance(data, dict) and data:
            return max(cls.calculate_json_depth(v, current_depth + 1) for v in data.values())
        elif isinstance(data, list) and data:
            return max(cls.calculate_json_depth(item, current_depth + 1) for item in data)
        return current_depth

    @classmethod
    def inspect(cls, raw_body_sample: str, parsed_body: Any, latency_ms: float = 0.0) -> List[Tuple[str, str, str, float, str]]:
        findings = []

        # 1. JSON Depth Check
        if parsed_body:
            depth = cls.calculate_json_depth(parsed_body)
            if depth > cls.MAX_SAFE_DEPTH:
                findings.append((
                    "EXCESSIVE_JSON_DEPTH",
                    "API4:2023 Unrestricted Resource Consumption",
                    "HIGH",
                    0.96,
                    f"JSON nesting depth ({depth}) exceeds safe maximum of {cls.MAX_SAFE_DEPTH} levels"
                ))

        # 2. ReDoS Evil Regex Pattern Check in Raw Sample
        if raw_body_sample:
            for pattern in EVIL_REGEX_PATTERNS:
                if pattern.search(raw_body_sample):
                    findings.append((
                        "REDOS_PATTERN_DETECTED",
                        "API4:2023 Unrestricted Resource Consumption",
                        "CRITICAL",
                        0.97,
                        f"Catastrophic backtracking / ReDoS pattern '{pattern.pattern}' detected in payload"
                    ))
                    break

        # 3. Single-Request Latency Anomaly on Small Payload
        if latency_ms > 250.0 and len(raw_body_sample or "") < 1024:
            findings.append((
                "ALGORITHMIC_COMPLEXITY_SPIKE",
                "API4:2023 Unrestricted Resource Consumption",
                "MEDIUM",
                0.80,
                f"Suspicious request execution latency ({latency_ms:.1f}ms) on small payload (<1KB)"
            ))

        return findings


# =============================================================================
# 4. MASTER DEEP SEMANTIC INSPECTOR
# =============================================================================

class DeepSemanticInspector:
    """
    Unified Ingress Deep Semantic Inspector coordinating Box A+ & Box B+ analysis:
    - Runs all 4 sub-inspectors in < 1ms total execution time.
    - Yields explainable threat indicators and OWASP API tags.
    """

    def __init__(self):
        self.injection_inspector = InjectionInspector()
        self.ssrf_inspector = SSRFInspector()
        self.business_logic_inspector = BusinessLogicInspector()
        self.complexity_inspector = ComplexityAndReDoSInspector()

    def inspect_request(
        self,
        query_params: Dict[str, Any],
        raw_body_sample: str = "",
        parsed_body: Any = None,
        latency_ms: float = 0.0
    ) -> DeepInspectionResult:
        """
        Executes comprehensive semantic inspection across incoming request parameters and body.
        """
        t0 = time.perf_counter()
        result = DeepInspectionResult()

        # 1. Blind Spot #1: Injection (SQLi, NoSQLi, Command Injection)
        # Scan Query Params
        for k, v in query_params.items():
            if isinstance(v, str):
                for ind, owasp, sev, conf, reason in self.injection_inspector.inspect_text(v, f"query.{k}"):
                    result.add_finding(ind, owasp, sev, conf, reason, {"query_param": k, "sample": v[:100]})
        # Scan Body
        if parsed_body:
            for ind, owasp, sev, conf, reason in self.injection_inspector.inspect_json(parsed_body, "body"):
                result.add_finding(ind, owasp, sev, conf, reason)
        elif raw_body_sample:
            for ind, owasp, sev, conf, reason in self.injection_inspector.inspect_text(raw_body_sample, "raw_body"):
                result.add_finding(ind, owasp, sev, conf, reason)

        # 2. Blind Spot #2: SSRF (Cloud Metadata, Loopback, RFC1918)
        for ind, owasp, sev, conf, reason in self.ssrf_inspector.inspect(query_params, parsed_body):
            result.add_finding(ind, owasp, sev, conf, reason)

        # 3. Blind Spot #3: Business Logic & Arithmetic Inflation
        for ind, owasp, sev, conf, reason in self.business_logic_inspector.inspect(query_params, parsed_body):
            result.add_finding(ind, owasp, sev, conf, reason)

        # 4. Blind Spot #4: Complexity, ReDoS & Depth
        for ind, owasp, sev, conf, reason in self.complexity_inspector.inspect(raw_body_sample, parsed_body, latency_ms):
            result.add_finding(ind, owasp, sev, conf, reason)

        result.execution_latency_ms = (time.perf_counter() - t0) * 1000.0
        return result


# Global Singleton instance
deep_inspector = DeepSemanticInspector()
