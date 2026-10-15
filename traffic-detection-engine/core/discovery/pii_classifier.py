"""
Response Payload PII Classifier (Regex + Verhoeff Mathematical Validation).
Detects Indian DPI & FinTech identifiers:
- PAN Card
- Aadhaar (with UIDAI-compliant Verhoeff dihedral group D5 checksum)
- UPI VPA ID
- Indian Phone Numbers
- Email Addresses
- Bearer / JWT Secret Reflection
"""

import re
import json
from typing import List, Tuple, Dict, Any, Union
from core.models import PIIMatch, PIISeverity

# Regex patterns
PAN_REGEX = re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b')
# Aadhaar candidate: 12 digits, optional hyphen or space, first digit cannot be 0 or 1
AADHAAR_CANDIDATE_REGEX = re.compile(r'\b([2-9][0-9]{3}[-\s]?[0-9]{4}[-\s]?[0-9]{4})\b')
# UPI ID / VPA
UPI_REGEX = re.compile(r'\b[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}\b')
# Indian Mobile Phone (10 digits starting with 6,7,8,9, optional +91, 91, 0)
PHONE_REGEX = re.compile(r'(?:\+91|91|0)?\s*([6-9]\d{9})\b')
# Email RFC 5322 simplified
EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')
# Exposed JWT or Bearer in body
BEARER_REGEX = re.compile(r'\bBearer\s+(eyJ[a-zA-Z0-9_\-\.]+\.[a-zA-Z0-9_\-\.]+)\b|\b(eyJ[a-zA-Z0-9_\-]{10,}\.[a-zA-Z0-9_\-]{10,}\.[a-zA-Z0-9_\-]{10,})\b')

# Verhoeff Multiplication Table (d)
_VERHOEFF_D = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
    [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
    [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
    [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
    [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
    [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
    [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
    [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
    [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
]

# Verhoeff Permutation Table (p)
_VERHOEFF_P = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
    [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
    [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
    [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
    [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
    [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
    [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]
]

# Verhoeff Inverse Table (inv)
_VERHOEFF_INV = [0, 4, 3, 2, 1, 5, 6, 7, 8, 9]


def validate_verhoeff(num_str: str) -> bool:
    """Validates a number string using the Verhoeff algorithm."""
    if not num_str.isdigit():
        return False
    c = 0
    inverted = [int(x) for x in reversed(num_str)]
    for i, digit in enumerate(inverted):
        c = _VERHOEFF_D[c][_VERHOEFF_P[i % 8][digit]]
    return c == 0


def generate_verhoeff_checksum(num_str_11_or_more: str) -> str:
    """Generates the single check digit to append to make num_str valid."""
    c = 0
    inverted = [int(x) for x in reversed(num_str_11_or_more)]
    for i, digit in enumerate(inverted):
        c = _VERHOEFF_D[c][_VERHOEFF_P[(i + 1) % 8][digit]]
    return str(_VERHOEFF_INV[c])


class PIIClassifier:
    """
    Scans HTTP payloads for sensitive PII and generates structured matches.
    """

    @classmethod
    def _mask(cls, text: str, entity_type: str) -> str:
        if entity_type == "PAN":
            return text[:4] + "****" + text[-2:]
        elif entity_type == "AADHAAR":
            clean = re.sub(r'[-\s]', '', text)
            return "********" + clean[-4:]
        elif entity_type == "PHONE":
            return text[:3] + "****" + text[-2:]
        elif entity_type == "EMAIL":
            parts = text.split("@")
            return parts[0][:2] + "***@" + parts[1]
        elif entity_type == "UPI_VPA":
            parts = text.split("@")
            return parts[0][:2] + "***@" + parts[1]
        elif entity_type == "BEARER_TOKEN":
            return text[:10] + "..."
        return "***"

    @classmethod
    def classify_payload(cls, payload: Union[str, Dict, List, None]) -> Tuple[List[PIIMatch], PIISeverity]:
        if not payload:
            return [], PIISeverity.NONE

        if isinstance(payload, (dict, list)):
            text = json.dumps(payload)
        else:
            text = str(payload)

        matches: List[PIIMatch] = []
        has_critical = False
        has_sensitive = False

        # 1. Check PAN Card
        pan_matches = PAN_REGEX.findall(text)
        if pan_matches:
            has_critical = True
            matches.append(PIIMatch(
                entity_type="PAN",
                count=len(pan_matches),
                sample_masked=cls._mask(pan_matches[0], "PAN"),
                severity=PIISeverity.CRITICAL
            ))

        # 2. Check Aadhaar with Verhoeff Checksum
        aadhaar_candidates = AADHAAR_CANDIDATE_REGEX.findall(text)
        valid_aadhaar = []
        for cand in aadhaar_candidates:
            clean_digits = re.sub(r'[-\s]', '', cand)
            if len(clean_digits) == 12 and validate_verhoeff(clean_digits):
                valid_aadhaar.append(cand)

        if valid_aadhaar:
            has_critical = True
            matches.append(PIIMatch(
                entity_type="AADHAAR",
                count=len(valid_aadhaar),
                sample_masked=cls._mask(valid_aadhaar[0], "AADHAAR"),
                severity=PIISeverity.CRITICAL
            ))

        # 3. Check UPI VPA
        upi_matches = UPI_REGEX.findall(text)
        # Filter out common false positives like email addresses
        upi_filtered = [u for u in upi_matches if not re.search(r'\.(com|org|net|io|co|in)$', u.split('@')[-1])]
        if upi_filtered:
            has_sensitive = True
            matches.append(PIIMatch(
                entity_type="UPI_VPA",
                count=len(upi_filtered),
                sample_masked=cls._mask(upi_filtered[0], "UPI_VPA"),
                severity=PIISeverity.SENSITIVE
            ))

        # 4. Check Phone Numbers
        phone_matches = PHONE_REGEX.findall(text)
        if phone_matches:
            has_sensitive = True
            matches.append(PIIMatch(
                entity_type="PHONE",
                count=len(phone_matches),
                sample_masked=cls._mask(phone_matches[0], "PHONE"),
                severity=PIISeverity.SENSITIVE
            ))

        # 5. Check Email Addresses
        email_matches = EMAIL_REGEX.findall(text)
        if email_matches:
            has_sensitive = True
            matches.append(PIIMatch(
                entity_type="EMAIL",
                count=len(email_matches),
                sample_masked=cls._mask(email_matches[0], "EMAIL"),
                severity=PIISeverity.SENSITIVE
            ))

        # 6. Check Bearer / JWT token leaks
        bearer_matches = BEARER_REGEX.findall(text)
        if bearer_matches:
            flat_tokens = [m[0] or m[1] for m in bearer_matches if (m[0] or m[1])]
            if flat_tokens:
                has_critical = True
                matches.append(PIIMatch(
                    entity_type="BEARER_TOKEN",
                    count=len(flat_tokens),
                    sample_masked=cls._mask(flat_tokens[0], "BEARER_TOKEN"),
                    severity=PIISeverity.CRITICAL
                ))

        # Overall severity
        if has_critical:
            overall_severity = PIISeverity.CRITICAL
        elif has_sensitive:
            overall_severity = PIISeverity.SENSITIVE
        else:
            overall_severity = PIISeverity.NONE

        return matches, overall_severity
