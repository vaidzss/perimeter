"""
Unit Tests for Box B: Runtime Behavior & Abuse Detector.
"""

import unittest
import time
from core.abuse.baseline import BaselineProfiler, WelfordAccumulator
from core.abuse.bola_detector import BOLADetector
from core.abuse.scraping_detector import ScrapingDetector
from core.abuse.replay_detector import TokenReplayDetector
from core.models import AbuseAlertType


class TestBoxBAbuse(unittest.TestCase):

    def test_welford_accumulator(self):
        acc = WelfordAccumulator(initial_mean=10.0, initial_std=2.0)
        # Feed known values [10, 12, 14, 16, 18]
        for v in [10.0, 12.0, 14.0, 16.0, 18.0]:
            acc.update(v)
        self.assertAlmostEqual(acc.mean, 14.0, places=1)
        self.assertGreater(acc.std_dev, 0.5)

    def test_bola_detector(self):
        detector = BOLADetector(window_seconds=60.0, unique_id_threshold=5)
        now = time.time()

        # 1. Benign: user accesses only their own account (acc_123)
        for i in range(5):
            alert = detector.inspect(
                jwt_sub="usr_garv",
                extracted_params={"id": "acc_123"},
                route="/api/v2/accounts/{id}/balance",
                timestamp=now + i
            )
            self.assertIsNone(alert)

        # 2. BOLA Attack: user enumerates multiple foreign IDs (acc_101, acc_102, acc_103, ...)
        alerts = []
        for i in range(1, 7):
            alert = detector.inspect(
                jwt_sub="usr_attacker",
                extracted_params={"id": f"acc_{100 + i}"},
                route="/api/v2/accounts/{id}/balance",
                timestamp=now + i
            )
            if alert:
                alerts.append(alert)

        self.assertTrue(len(alerts) > 0)
        self.assertEqual(alerts[-1].alert_type, AbuseAlertType.BOLA_IDOR)
        self.assertIn("usr_attacker", alerts[-1].reason)

    def test_scraping_detector(self):
        profiler = BaselineProfiler()
        detector = ScrapingDetector(profiler, window_seconds=60.0)
        now = time.time()
        route = "GET:/api/v2/accounts/{id}/balance"

        # Prime baseline with normal requests (10 req/min, 200 bytes)
        for i in range(10):
            profiler.record_observation(route, 10.0, 200.0)

        # Normal request within baseline
        normal_alert = detector.inspect("ip_user", route, response_bytes=250, timestamp=now)
        self.assertIsNone(normal_alert)

        # High-velocity scraping attack: 25 requests in 5 seconds
        alert = None
        for i in range(25):
            alert = detector.inspect("ip_scraper", route, response_bytes=300, timestamp=now + i * 0.1)

        self.assertIsNotNone(alert)
        self.assertEqual(alert.alert_type, AbuseAlertType.DATA_SCRAPING)

    def test_token_replay_detector(self):
        detector = TokenReplayDetector(window_seconds=60.0)
        now = time.time()

        # 1. Normal usage from single device/IP
        alert1 = detector.inspect(
            jwt_jti="jti-token-abc",
            jwt_sub="usr_123",
            client_ip="192.168.1.5",
            user_agent="Mozilla/5.0 Chrome",
            timestamp=now
        )
        self.assertIsNone(alert1)

        # 2. Token Replay / Concurrent use from second conflicting IP
        alert2 = detector.inspect(
            jwt_jti="jti-token-abc",
            jwt_sub="usr_123",
            client_ip="203.0.113.88",
            user_agent="curl/7.68.0",
            timestamp=now + 2.0
        )
        self.assertIsNotNone(alert2)
        self.assertEqual(alert2.alert_type, AbuseAlertType.TOKEN_REPLAY)
        self.assertIn("divergent client fingerprints", alert2.reason)


if __name__ == "__main__":
    unittest.main()
