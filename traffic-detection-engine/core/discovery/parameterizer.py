"""
Dynamic URL Parameterizer.
Converts dynamic runtime paths into generalized OpenAPI route schemas and extracts entity parameters.
Example:
    /api/v2/accounts/9841/balance -> /api/v2/accounts/{id}/balance
    extracted_params: {"id": "9841"}
"""

import re
from typing import Tuple, Dict

# Regex patterns for dynamic URL segments
UUID_REGEX = re.compile(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
MONGO_ID_REGEX = re.compile(r'^[0-9a-fA-F]{24}$')
INTEGER_ID_REGEX = re.compile(r'^\d+$')
FINTECH_PREFIXED_ID_REGEX = re.compile(r'^(ACC|TXN|USR|ORD|INV|CUST)[-_]\d+$', re.IGNORECASE)
HASH_TOKEN_REGEX = re.compile(r'^[0-9a-fA-F]{32,64}$')


class URLParameterizer:
    """
    Normalizes dynamic paths to canonical schemas and extracts variable resource IDs.
    """

    @classmethod
    def parameterize(cls, raw_path: str) -> Tuple[str, Dict[str, str]]:
        """
        Parses raw path into (parameterized_template, extracted_params).
        """
        if not raw_path:
            return "/", {}

        # Strip query strings if present
        path_only = raw_path.split("?")[0].strip()
        segments = [s for s in path_only.split("/") if s]
        
        parameterized_segments = []
        extracted_params: Dict[str, str] = {}
        
        param_counter = 0

        for i, seg in enumerate(segments):
            is_dynamic = False
            param_name = "id"
            
            # Check previous segment to name parameter contextually (e.g. /accounts/9841 -> account_id)
            prev_seg = segments[i - 1].lower() if i > 0 else ""
            if prev_seg.endswith("s") and len(prev_seg) > 2:
                # Plural noun (accounts -> id, users -> id)
                suggested_name = "id"
            else:
                suggested_name = "id"

            if INTEGER_ID_REGEX.match(seg):
                is_dynamic = True
            elif UUID_REGEX.match(seg):
                is_dynamic = True
            elif MONGO_ID_REGEX.match(seg):
                is_dynamic = True
            elif FINTECH_PREFIXED_ID_REGEX.match(seg):
                is_dynamic = True
            elif HASH_TOKEN_REGEX.match(seg):
                is_dynamic = True

            if is_dynamic:
                param_counter += 1
                assigned_name = suggested_name if param_counter == 1 else f"{suggested_name}_{param_counter}"
                parameterized_segments.append(f"{{{assigned_name}}}")
                extracted_params[assigned_name] = seg
            else:
                parameterized_segments.append(seg)

        parameterized_path = "/" + "/".join(parameterized_segments)
        return parameterized_path, extracted_params
