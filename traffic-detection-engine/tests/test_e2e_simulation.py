"""
End-to-End Simulation & Verification Test Suite.
Simulates normal and attack traffic, measuring TPR, FPR, and <0.5ms non-blocking latency.
"""

import unittest
import os
import time
import random
from pipeline import CoreDetectionEngine
from core.models import TelemetryEvent, SpecDriftStatus


class TestE2ESimulation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        spec_path = os.path.join(base_dir, "config", "openapi.json")
        # Use in-memory SQLite for testing isolation
        cls.engine = CoreDetectionEngine(openapi_spec_path=spec_path, db_path=":memory:")

    def test_end_to_end_simulation(self):
        latencies = []
        events_count = 0
        now = time.time()

        # -------------------------------------------------------------
        # 1. 50 Benign Requests (Valid JWT, standard rate, Documented)
        # -------------------------------------------------------------
        for i in range(50):
            user_idx = i % 10
            event = TelemetryEvent(
                request_id=f"benign-{i}",
                timestamp=now + (i * 0.1),
                method="GET",
                path=f"/api/v2/accounts/{9800 + user_idx}/balance",
                headers={
                    "authorization": "Bearer valid.jwt.token",
                    "user-agent": "Mozilla/5.0 Chrome",
                    "x-forwarded-for": f"10.0.0.{user_idx}",
                    "x-truth": "benign"
                },
                response_body={"account_id": str(9800 + user_idx), "balance": 150000},
                response_size_bytes=45,
                client_ip=f"10.0.0.{user_idx}",
                user_agent="Mozilla/5.0 Chrome",
                jwt_sub=f"user_{9800 + user_idx}",
                jwt_jti=f"jti-benign-{9800 + user_idx}",
                ground_truth="benign"
            )
            score, latency_ms = self.engine.process_telemetry(event)
            latencies.append(latency_ms)
            events_count += 1
            self.assertEqual(score.spec_status, SpecDriftStatus.DOCUMENTED)

        # -------------------------------------------------------------
        # 2. 20 BOLA Attack Requests (One user enumerating distinct IDs)
        # -------------------------------------------------------------
        for i in range(20):
            event = TelemetryEvent(
                request_id=f"bola-{i}",
                timestamp=now + 5.0 + (i * 0.05),
                method="GET",
                path=f"/api/v2/accounts/{5000 + i}/balance",
                headers={
                    "authorization": "Bearer attacker.jwt.token",
                    "user-agent": "Python-requests/2.28",
                    "x-forwarded-for": "198.51.100.99",
                    "x-truth": "attack_bola"
                },
                response_body={"account_id": str(5000 + i), "balance": 12000},
                response_size_bytes=42,
                client_ip="198.51.100.99",
                user_agent="Python-requests/2.28",
                jwt_sub="attacker_bob",
                jwt_jti="jti-attacker",
                ground_truth="attack_bola"
            )
            score, latency_ms = self.engine.process_telemetry(event)
            latencies.append(latency_ms)
            events_count += 1

        # -------------------------------------------------------------
        # 3. 25 Scraping Attack Requests (High-velocity crawl)
        # -------------------------------------------------------------
        for i in range(25):
            event = TelemetryEvent(
                request_id=f"scraping-{i}",
                timestamp=now + 10.0 + (i * 0.02),
                method="GET",
                path=f"/api/v2/users/{100 + i}/profile",
                headers={
                    "authorization": "Bearer valid.jwt.token",
                    "user-agent": "Scrapy/2.11",
                    "x-forwarded-for": "203.0.113.15",
                    "x-truth": "attack_scraping"
                },
                response_body={"user_id": str(100 + i), "name": "Test User"},
                response_size_bytes=60,
                client_ip="203.0.113.15",
                user_agent="Scrapy/2.11",
                jwt_sub="scraper_bot",
                jwt_jti="jti-scraper",
                ground_truth="attack_scraping"
            )
            score, latency_ms = self.engine.process_telemetry(event)
            latencies.append(latency_ms)
            events_count += 1

        # -------------------------------------------------------------
        # 4. 15 Token Replay Requests (Same JTI across multiple IPs)
        # -------------------------------------------------------------
        for i in range(15):
            ip = f"185.220.101.{i % 5}"
            ua = f"Browser-{i % 3}"
            event = TelemetryEvent(
                request_id=f"replay-{i}",
                timestamp=now + 15.0 + (i * 0.1),
                method="GET",
                path="/api/v2/accounts/9841/balance",
                headers={
                    "authorization": "Bearer stolen.jwt.token",
                    "user-agent": ua,
                    "x-forwarded-for": ip,
                    "x-truth": "attack_replay"
                },
                response_body={"account_id": "9841", "balance": 150000},
                response_size_bytes=45,
                client_ip=ip,
                user_agent=ua,
                jwt_sub="victim_user",
                jwt_jti="jti-stolen-token-xyz",
                ground_truth="attack_replay"
            )
            score, latency_ms = self.engine.process_telemetry(event)
            latencies.append(latency_ms)
            events_count += 1

        # -------------------------------------------------------------
        # 5. 15 Zombie API Leaks (Deprecated /api/v1/users/export-all)
        # -------------------------------------------------------------
        for i in range(15):
            event = TelemetryEvent(
                request_id=f"zombie-{i}",
                timestamp=now + 20.0 + (i * 0.1),
                method="GET",
                path="/api/v1/users/export-all",
                headers={
                    "authorization": "Bearer user.jwt",
                    "x-truth": "attack_zombie"
                },
                response_body={"export": [{"pan": "ABCDE1234F", "phone": "9876543210"}]},
                response_size_bytes=12000,
                client_ip="10.0.0.50",
                ground_truth="attack_zombie"
            )
            score, latency_ms = self.engine.process_telemetry(event)
            latencies.append(latency_ms)
            events_count += 1
            self.assertEqual(score.spec_status, SpecDriftStatus.ZOMBIE)

        # -------------------------------------------------------------
        # 6. 15 Shadow API Access (Undocumented /api/internal/debug/reset)
        # -------------------------------------------------------------
        for i in range(15):
            event = TelemetryEvent(
                request_id=f"shadow-{i}",
                timestamp=now + 25.0 + (i * 0.1),
                method="POST",
                path="/api/internal/debug/reset",
                headers={
                    "x-truth": "attack_shadow"
                },
                response_body={"status": "debug mode reset executed"},
                response_size_bytes=35,
                client_ip="192.168.1.100",
                ground_truth="attack_shadow"
            )
            score, latency_ms = self.engine.process_telemetry(event)
            latencies.append(latency_ms)
            events_count += 1
            self.assertEqual(score.spec_status, SpecDriftStatus.SHADOW)

        # -------------------------------------------------------------
        # Performance & Metrics Evaluation
        # -------------------------------------------------------------
        avg_latency = sum(latencies) / len(latencies)
        print(f"\n[BENCHMARK] Total Events Processed: {events_count}")
        print(f"[BENCHMARK] Average Latency per Request: {avg_latency:.3f} ms")

        # Must meet the blueprint SLA (< 0.5ms average latency)
        self.assertLess(avg_latency, 0.5, f"Engine latency {avg_latency:.3f}ms exceeded 0.5ms SLA!")

        # Check API Inventory
        inventory = self.engine.get_inventory()
        self.assertTrue(len(inventory) >= 3)
        statuses = set(item["spec_status"] for item in inventory)
        self.assertIn("DOCUMENTED", statuses)
        self.assertIn("ZOMBIE", statuses)
        self.assertIn("SHADOW", statuses)

        # Check Confusion Matrix
        cm = self.engine.get_confusion_matrix()
        print(f"[METRICS] Live Confusion Matrix:")
        print(f"  TP: {cm['tp']} | FP: {cm['fp']} | TN: {cm['tn']} | FN: {cm['fn']}")
        print(f"  TPR (True Positive Rate): {cm['tpr_percentage']}%")
        print(f"  FPR (False Positive Rate): {cm['fpr_percentage']}%")

        self.assertGreaterEqual(cm['tpr_percentage'], 90.0, "TPR should be >= 90%")
        self.assertLessEqual(cm['fpr_percentage'], 5.0, "FPR should be <= 5%")


if __name__ == "__main__":
    unittest.main()
