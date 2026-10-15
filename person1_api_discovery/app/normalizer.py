"""
Path Normalization & PII Classification Engine for Person 1:
1. Dynamic URL Path Parameterizer:
   - Matches raw paths against known OpenAPI templates (/api/v2/accounts/1004 -> /api/v2/accounts/{account_id})
   - Falls back to structural collapse for uncataloged Shadow routes (/api/v1/accounts/1004/passbook-dump -> /api/v1/accounts/{id}/passbook-dump)
2. Response Payload PII Classifier:
   - Compiled regexes detecting PAN, GOVT_ID_LIKE, PHONE, UPI_VPA, EMAIL
"""

import os
import re
import json
from typing import List, Tuple, Dict, Any, Optional

# Segment pattern matchers
NUMERIC_SEGMENT_REGEX = re.compile(r"^\d+$")
TXN_SEGMENT_REGEX = re.compile(r"^TXN\d+$", re.IGNORECASE)
IFSC_SEGMENT_REGEX = re.compile(r"^[A-Z]{4}0[A-Z0-9]{6}$", re.IGNORECASE)
UUID_SEGMENT_REGEX = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE)

# Fast compiled Indian PII regexes
PII_PATTERNS = {
    "PAN": re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"),
    "GOVT_ID_LIKE": re.compile(r"(\[GOVT-ID-[A-Z0-9-]+\]|GOVT-ID-XXXX-[0-9]{4}|AADHAAR-[A-Z0-9-]+|VOTER-ID-[A-Z0-9-]+)"),
    "PHONE": re.compile(r"(\+91-?[6-9]\d{9}|\+91-\d{10})"),
    "UPI_VPA": re.compile(r"\b[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}\b"),
    "EMAIL": re.compile(r"\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b")
}


def load_spec_templates(spec_path: Optional[str] = None) -> List[str]:
    """Load documented route templates from openapi_partial.json."""
    if not spec_path:
        spec_path = os.path.join(os.path.dirname(__file__), "..", "specs", "openapi_partial.json")
    if os.path.exists(spec_path):
        try:
            with open(spec_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return list(data.get("paths", {}).keys())
        except Exception:
            pass
    return []


def match_template(raw_segments: List[str], template_segments: List[str]) -> Optional[Dict[str, str]]:
    """Checks if raw_segments match template_segments and extracts named parameters."""
    if len(raw_segments) != len(template_segments):
        return None
    extracted = {}
    for r_seg, t_seg in zip(raw_segments, template_segments):
        if t_seg.startswith("{") and t_seg.endswith("}"):
            param_name = t_seg[1:-1]
            extracted[param_name] = r_seg
        elif r_seg.lower() != t_seg.lower():
            return None
    return extracted


def normalize_path(raw_path: str, known_spec_templates: Optional[List[str]] = None) -> Tuple[str, Dict[str, str]]:
    """
    Normalizes raw request path to template format.
    1. First attempts structural match against known OpenAPI spec templates.
    2. If no template matches (Shadow route), collapses dynamic numeric, UUID, TXN, and IFSC segments.
    """
    clean_raw = "/" + raw_path.strip("/")
    raw_segments = clean_raw.split("/")

    # Check known templates first
    if known_spec_templates is None:
        known_spec_templates = load_spec_templates()

    # 1. Check exact static matches first
    for tmpl in known_spec_templates:
        tmpl_clean = "/" + tmpl.strip("/")
        if clean_raw.lower() == tmpl_clean.lower():
            return tmpl_clean, {}

    # 2. Sort templates so more specific templates (fewer parameters) match first
    sorted_templates = sorted(
        known_spec_templates,
        key=lambda t: (t.count("{"), -len(t))
    )

    for tmpl in sorted_templates:
        tmpl_clean = "/" + tmpl.strip("/")
        tmpl_segments = tmpl_clean.split("/")
        extracted = match_template(raw_segments, tmpl_segments)
        if extracted is not None:
            return tmpl_clean, extracted

    # Fallback: Dynamic parameterization for Shadow routes
    normalized_parts = []
    extracted_params: Dict[str, str] = {}
    param_idx = 1

    for seg in raw_segments:
        if not seg:
            continue
        if NUMERIC_SEGMENT_REGEX.match(seg):
            param_name = "account_id" if "account" in clean_raw else ("id" if param_idx == 1 else f"id_{param_idx}")
            normalized_parts.append(f"{{{param_name}}}")
            extracted_params[param_name] = seg
            param_idx += 1
        elif TXN_SEGMENT_REGEX.match(seg):
            param_name = "txn_id"
            normalized_parts.append(f"{{{param_name}}}")
            extracted_params[param_name] = seg
        elif IFSC_SEGMENT_REGEX.match(seg):
            param_name = "ifsc_code"
            normalized_parts.append(f"{{{param_name}}}")
            extracted_params[param_name] = seg
        elif UUID_SEGMENT_REGEX.match(seg):
            param_name = f"uuid_{param_idx}"
            normalized_parts.append(f"{{{param_name}}}")
            extracted_params[param_name] = seg
            param_idx += 1
        else:
            normalized_parts.append(seg)

    normalized_path = "/" + "/".join(normalized_parts)
    return normalized_path, extracted_params


def scan_pii_fields(text_content: str) -> List[str]:
    """Scans text for sensitive Indian PII patterns."""
    detected = []
    if not text_content:
        return detected
    for pii_type, pattern in PII_PATTERNS.items():
        if pattern.search(text_content):
            detected.append(pii_type)
    return detected
