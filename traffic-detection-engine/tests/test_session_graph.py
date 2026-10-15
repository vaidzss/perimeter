"""
Unit Tests for Context-Aware Session Graphing Engine.
Tests stateful workflow validation and random-walk graph entropy analysis (OWASP API6:2023).
"""

import unittest
import time
from core.graph.session_graph import SessionGraphEngine
from core.models import AbuseAlertType, OWASPCategory


class TestSessionGraphEngine(unittest.TestCase):

    def setUp(self):
        self.engine = SessionGraphEngine(session_ttl=60.0)

    def test_benign_session_graph(self):
        now = time.time()
        sid = "sess_legit_user"

        # Legitimate sequence: login -> profile -> balance -> transfer
        steps = [
            "POST:/api/v2/auth/login",
            "GET:/api/v2/users/{id}/profile",
            "GET:/api/v2/accounts/{id}/balance",
            "POST:/api/v2/payments/transfer"
        ]

        alerts = []
        for i, step in enumerate(steps):
            alert, graph = self.engine.record_transition(sid, step, timestamp=now + i)
            if alert:
                alerts.append(alert)

        # Normal sequential workflow should NOT alert
        self.assertEqual(len(alerts), 0)
        self.assertEqual(graph["total_steps"], 4)
        self.assertEqual(len(graph["nodes"]), 4)
        self.assertEqual(len(graph["edges"]), 3)

    def test_skip_step_workflow_violation(self):
        now = time.time()
        sid = "sess_direct_bypass"

        # Direct attempt to invoke financial transfer without any prerequisite history
        alert, graph = self.engine.record_transition(sid, "POST:/api/v2/payments/transfer", timestamp=now)

        self.assertIsNotNone(alert)
        self.assertEqual(alert.alert_type, AbuseAlertType.WORKFLOW_VIOLATION)
        self.assertEqual(alert.owasp_category, OWASPCategory.API6_BUSINESS_FLOW)
        self.assertIn("invoked directly without preceding", alert.reason)

    def test_random_walk_reconnaissance(self):
        now = time.time()
        sid = "sess_bot_recon"

        # Bot crawls 7 distinct unlinked routes
        scanned_routes = [
            "GET:/api/v2/users/{id}/profile",
            "GET:/api/v2/admin/status",
            "GET:/api/v2/config/env",
            "GET:/api/v2/metrics/dump",
            "GET:/api/v2/system/health",
            "GET:/api/v2/auth/providers",
            "GET:/api/v2/logs/stream"
        ]

        alerts = []
        for i, route in enumerate(scanned_routes):
            alert, graph = self.engine.record_transition(sid, route, timestamp=now + i)
            if alert:
                alerts.append(alert)

        # High-entropy random walk should trigger API6:2023 reconnaissance alert
        self.assertTrue(len(alerts) > 0)
        recon_alert = alerts[-1]
        self.assertEqual(recon_alert.alert_type, AbuseAlertType.WORKFLOW_VIOLATION)
        self.assertEqual(recon_alert.owasp_category, OWASPCategory.API6_BUSINESS_FLOW)
        self.assertIn("high-entropy API graph traversal", recon_alert.reason)


if __name__ == "__main__":
    unittest.main()
