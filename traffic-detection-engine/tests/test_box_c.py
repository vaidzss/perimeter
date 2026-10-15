"""
Unit Tests for Box C: Explainable Risk Scorer.
"""

import unittest
from core.models import (
    TelemetryEvent,
    SpecDriftStatus,
    PIISeverity,
    PIIMatch,
    AbuseAlert,
    AbuseAlertType
)
from core.scoring.risk_scorer import RiskScorer


class TestBoxCRiskScorer(unittest.TestCase):

    def test_unauth_shadow_critical_pii(self):
        # Mirrored event without Authorization header
        event = TelemetryEvent(
            request_id="req-test-1",
            method="POST",
            path="/api/internal/debug/reset",
            headers={"host": "api.internal"}
        )

        pii_matches = [
            PIIMatch(
                entity_type="AADHAAR",
                count=1,
                sample_masked="********1234",
                severity=PIISeverity.CRITICAL
            )
        ]

        score = RiskScorer.calculate_score(
            event=event,
            parameterized_path="/api/internal/debug/reset",
            extracted_params={},
            spec_status=SpecDriftStatus.SHADOW,
            pii_matches=pii_matches,
            pii_severity=PIISeverity.CRITICAL,
            abuse_alerts=[]
        )

        # Expected: Exposure (+35) + PII (+25) + Shadow (+20) = 80
        self.assertEqual(score.risk_score, 80)
        self.assertEqual(score.severity, "HIGH")
        self.assertTrue(any("+35 Unauth" in r for r in score.reason_vector))
        self.assertTrue(any("+25 PII" in r for r in score.reason_vector))
        self.assertTrue(any("+20 Shadow" in r for r in score.reason_vector))

    def test_benign_authenticated_documented_traffic(self):
        event = TelemetryEvent(
            request_id="req-test-2",
            method="GET",
            path="/api/v2/accounts/9841/balance",
            headers={"authorization": "Bearer eyJhbGciOi..."}
        )

        score = RiskScorer.calculate_score(
            event=event,
            parameterized_path="/api/v2/accounts/{id}/balance",
            extracted_params={"id": "9841"},
            spec_status=SpecDriftStatus.DOCUMENTED,
            pii_matches=[],
            pii_severity=PIISeverity.NONE,
            abuse_alerts=[]
        )

        self.assertEqual(score.risk_score, 0)
        self.assertEqual(score.severity, "LOW")
        self.assertEqual(len(score.reason_vector), 0)

    def test_zombie_pii_leak(self):
        event = TelemetryEvent(
            request_id="req-test-3",
            method="GET",
            path="/api/v1/users/export-all",
            headers={"authorization": "Bearer eyJhbGciOi..."}
        )

        pii_matches = [
            PIIMatch(
                entity_type="PAN",
                count=1,
                sample_masked="ABCDE****F",
                severity=PIISeverity.CRITICAL
            )
        ]

        score = RiskScorer.calculate_score(
            event=event,
            parameterized_path="/api/v1/users/export-all",
            extracted_params={},
            spec_status=SpecDriftStatus.ZOMBIE,
            pii_matches=pii_matches,
            pii_severity=PIISeverity.CRITICAL,
            abuse_alerts=[]
        )

        # Expected: Auth (0) + PII (+25) + Zombie (+15) = 40
        self.assertEqual(score.risk_score, 40)
        self.assertEqual(score.severity, "MEDIUM")
        self.assertTrue(any("+15 Zombie" in r for r in score.reason_vector))
        self.assertTrue(any("+25 PII" in r for r in score.reason_vector))


if __name__ == "__main__":
    unittest.main()
