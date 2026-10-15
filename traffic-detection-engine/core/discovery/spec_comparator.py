"""
OpenAPI 3.0 / Swagger Diff Comparator.
Compares live parameterized traffic against loaded OpenAPI specifications to flag:
- DOCUMENTED: Active, valid route in official spec.
- SHADOW: Live route observed in traffic, but absent from OpenAPI spec.
- ZOMBIE (v1): Legacy/deprecated route still receiving traffic or leaking PII.
"""

import json
import re
from typing import Dict, Any, Optional, Tuple, Set
from core.models import SpecDriftStatus


class OpenAPISpecComparator:
    """
    Parses and indexes an OpenAPI 3.0 specification into a parameterized route matcher.
    """

    def __init__(self, spec_dict: Optional[Dict[str, Any]] = None):
        self.spec_routes: Dict[str, Dict[str, Any]] = {}
        self.compiled_routes = []
        if spec_dict:
            self.load_spec(spec_dict)

    def load_spec_from_file(self, file_path: str):
        with open(file_path, "r", encoding="utf-8") as f:
            spec = json.load(f)
        self.load_spec(spec)

    def load_spec(self, spec: Dict[str, Any]):
        self.spec_routes.clear()
        self.compiled_routes.clear()

        paths = spec.get("paths", {})
        for path_template, path_item in paths.items():
            # Build regex pattern from path template
            # e.g., /api/v2/accounts/{id}/balance -> ^/api/v2/accounts/[^/]+/balance$
            regex_str = "^" + re.sub(r'\{[^}]+\}', r'[^/]+', path_template) + "$"
            compiled_regex = re.compile(regex_str, re.IGNORECASE)

            # Store operations (get, post, put, delete, etc.)
            methods: Dict[str, Dict[str, Any]] = {}
            for method, op_data in path_item.items():
                if method.lower() in ("get", "post", "put", "delete", "patch", "options", "head"):
                    methods[method.upper()] = op_data if isinstance(op_data, dict) else {}

            self.compiled_routes.append({
                "template": path_template,
                "regex": compiled_regex,
                "methods": methods
            })

    def compare(self, method: str, raw_path: str) -> Tuple[SpecDriftStatus, Optional[str], Optional[Dict[str, Any]]]:
        """
        Matches incoming request against spec.
        Returns: (SpecDriftStatus, matched_template, matched_operation_data)
        """
        method_upper = method.upper()
        clean_path = raw_path.split("?")[0].strip()

        for route_entry in self.compiled_routes:
            if route_entry["regex"].match(clean_path):
                methods = route_entry["methods"]
                if method_upper in methods:
                    op_data = methods[method_upper]
                    # Check if deprecated or zombie v1
                    is_deprecated = op_data.get("deprecated", False)
                    is_legacy_v1 = clean_path.startswith("/api/v1/") or "/v1/" in clean_path

                    if is_deprecated or is_legacy_v1:
                        return SpecDriftStatus.ZOMBIE, route_entry["template"], op_data
                    return SpecDriftStatus.DOCUMENTED, route_entry["template"], op_data

        # If no route or method matched, it is a SHADOW route
        return SpecDriftStatus.SHADOW, None, None
