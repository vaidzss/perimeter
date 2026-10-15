"""
API & Server Integration Tests.
Verifies FastAPI REST endpoints and ingestion contract.
"""

import unittest
from fastapi.testclient import TestClient
from server import app


class TestServerEndpoints(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertTrue(data["spec_loaded"])

    def test_telemetry_ingestion_api(self):
        payload = {
            "request_id": "api-test-req-1",
            "method": "POST",
            "path": "/api/internal/debug/reset",
            "headers": {"host": "api.fintech.local"},
            "response_body": {"status": "debug mode on"},
            "response_size_bytes": 28,
            "ground_truth": "attack_shadow"
        }
        response = self.client.post("/api/telemetry", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "processed")
        self.assertEqual(data["spec_status"], "SHADOW")
        self.assertGreaterEqual(data["risk_score"], 40)
        self.assertIn("reason_vector", data)

    def test_inventory_endpoint(self):
        response = self.client.get("/api/inventory")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_confusion_matrix_endpoint(self):
        response = self.client.get("/api/metrics/confusion-matrix")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("tpr_percentage", data)
    def test_session_graph_endpoint(self):
        response = self.client.get("/api/session-graph/sess_test_123")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("nodes", data)
        self.assertIn("edges", data)
        self.assertEqual(data["session_id"], "sess_test_123")


if __name__ == "__main__":
    unittest.main()
