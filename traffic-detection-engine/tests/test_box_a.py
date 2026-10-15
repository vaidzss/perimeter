"""
Unit Tests for Box A: API Discovery & Shadow Diff Engine.
"""

import unittest
import os
import json
from core.discovery.parameterizer import URLParameterizer
from core.discovery.pii_classifier import PIIClassifier, validate_verhoeff, generate_verhoeff_checksum
from core.discovery.spec_comparator import OpenAPISpecComparator
from core.models import SpecDriftStatus, PIISeverity


class TestBoxADiscovery(unittest.TestCase):

    def test_url_parameterization(self):
        # Numeric ID
        path, params = URLParameterizer.parameterize("/api/v2/accounts/9841/balance")
        self.assertEqual(path, "/api/v2/accounts/{id}/balance")
        self.assertEqual(params, {"id": "9841"})

        # UUID
        path, params = URLParameterizer.parameterize("/api/v1/users/550e8400-e29b-41d4-a716-446655440000/profile")
        self.assertEqual(path, "/api/v1/users/{id}/profile")
        self.assertEqual(params, {"id": "550e8400-e29b-41d4-a716-446655440000"})

        # FinTech Prefixed ID
        path, params = URLParameterizer.parameterize("/api/v2/transactions/TXN-90214/receipt")
        self.assertEqual(path, "/api/v2/transactions/{id}/receipt")
        self.assertEqual(params, {"id": "TXN-90214"})

    def test_verhoeff_algorithm_accuracy(self):
        # Generate a mathematically valid 12-digit Aadhaar number
        prefix_11 = "28475928371"
        check_digit = generate_verhoeff_checksum(prefix_11)
        valid_aadhaar = prefix_11 + check_digit

        # Verify it validates
        self.assertTrue(validate_verhoeff(valid_aadhaar))

        # Intentionally tamper with one digit - must immediately fail
        tampered = prefix_11 + str((int(check_digit) + 1) % 10)
        self.assertFalse(validate_verhoeff(tampered))

        # A random 12-digit timestamp/number should fail
        self.assertFalse(validate_verhoeff("123456789012"))

    def test_pii_classifier(self):
        # 1. PAN Card
        payload = {"user": "Garv", "pan": "ABCDE1234F"}
        matches, severity = PIIClassifier.classify_payload(payload)
        self.assertEqual(severity, PIISeverity.CRITICAL)
        self.assertTrue(any(m.entity_type == "PAN" for m in matches))

        # 2. Valid Aadhaar vs Invalid 12-digit number
        valid_aadhaar = "28475928371" + generate_verhoeff_checksum("28475928371")
        payload = {"notes": f"Identity record: {valid_aadhaar}, random counter: 999988887777"}
        matches, severity = PIIClassifier.classify_payload(payload)
        self.assertEqual(severity, PIISeverity.CRITICAL)
        aadhaar_matches = [m for m in matches if m.entity_type == "AADHAAR"]
        self.assertEqual(len(aadhaar_matches), 1)

        # 3. UPI ID
        payload = {"status": "SUCCESS", "vpa": "merchant@okaxis"}
        matches, severity = PIIClassifier.classify_payload(payload)
        self.assertEqual(severity, PIISeverity.SENSITIVE)
        self.assertTrue(any(m.entity_type == "UPI_VPA" for m in matches))

    def test_openapi_spec_comparator(self):
        spec_dict = {
            "openapi": "3.0.0",
            "paths": {
                "/api/v2/accounts/{id}/balance": {
                    "get": {"summary": "balance"}
                },
                "/api/v1/users/export-all": {
                    "get": {"summary": "deprecated export", "deprecated": True}
                }
            }
        }
        comparator = OpenAPISpecComparator(spec_dict)

        # 1. Documented endpoint
        status, template, _ = comparator.compare("GET", "/api/v2/accounts/9841/balance")
        self.assertEqual(status, SpecDriftStatus.DOCUMENTED)
        self.assertEqual(template, "/api/v2/accounts/{id}/balance")

        # 2. Zombie v1 deprecated endpoint
        status, template, _ = comparator.compare("GET", "/api/v1/users/export-all")
        self.assertEqual(status, SpecDriftStatus.ZOMBIE)

        # 3. Shadow undocumented endpoint
        status, template, _ = comparator.compare("POST", "/api/internal/debug/reset")
        self.assertEqual(status, SpecDriftStatus.SHADOW)
        self.assertIsNone(template)


if __name__ == "__main__":
    unittest.main()
