"""
BOLA / IDOR Sequence Detector.
Tracks unique {id} entropy and access cardinality per JWT 'sub' in a 60-second sliding window.
Identifies unauthorized resource enumeration (OWASP API Security #1).
"""

import time
from collections import deque
from typing import Dict, Deque, Tuple, Optional, List
from core.models import AbuseAlert, AbuseAlertType, OWASPCategory


class BOLADetector:
    """
    Stateful detector tracking object access entropy per authenticated user.
    """

    def __init__(self, window_seconds: float = 60.0, unique_id_threshold: int = 5):
        self.window_seconds = window_seconds
        self.unique_id_threshold = unique_id_threshold
        # Key: jwt_sub -> Deque[(timestamp, object_id, route)]
        self.user_history: Dict[str, Deque[Tuple[float, str, str]]] = {}

    def _purge_old_entries(self, sub: str, current_time: float):
        cutoff = current_time - self.window_seconds
        history = self.user_history.get(sub)
        if history:
            while history and history[0][0] < cutoff:
                history.popleft()
            if not history:
                del self.user_history[sub]

    def inspect(self, 
                jwt_sub: Optional[str], 
                extracted_params: Dict[str, str], 
                route: str, 
                timestamp: Optional[float] = None) -> Optional[AbuseAlert]:
        """
        Inspects incoming request for BOLA/IDOR behavior.
        Returns AbuseAlert if anomalous object enumeration is detected.
        """
        # BOLA requires an authenticated identity accessing variable object IDs
        if not jwt_sub or not extracted_params:
            return None

        now = timestamp if timestamp is not None else time.time()
        self._purge_old_entries(jwt_sub, now)

        # Primary object identifier (e.g., id, account_id, user_id)
        primary_id = None
        for k, v in extracted_params.items():
            if "id" in k.lower():
                primary_id = v
                break
        if not primary_id:
            # Fall back to first extracted param
            primary_id = next(iter(extracted_params.values()))

        if jwt_sub not in self.user_history:
            self.user_history[jwt_sub] = deque()

        self.user_history[jwt_sub].append((now, str(primary_id), route))

        # Calculate metrics in the 60s sliding window
        window_events = self.user_history[jwt_sub]
        unique_ids = set(item[1] for item in window_events)
        total_requests = len(window_events)
        unique_count = len(unique_ids)

        # Check sequential enumeration heuristic (e.g. 101, 102, 103, 104)
        is_sequential = False
        try:
            numeric_ids = [int(item[1]) for item in window_events if item[1].isdigit()]
            if len(numeric_ids) >= 3:
                diffs = [numeric_ids[i+1] - numeric_ids[i] for i in range(len(numeric_ids)-1)]
                if all(d == 1 for d in diffs[-3:]) or all(d == -1 for d in diffs[-3:]):
                    is_sequential = True
        except Exception:
            pass

        # Trigger if unique objects exceed threshold in 60s or sequential enumeration is observed
        if unique_count >= self.unique_id_threshold or (is_sequential and unique_count >= 3):
            confidence = 0.99 if is_sequential else min(1.0, 0.7 + (unique_count / 10.0) * 0.3)
            return AbuseAlert(
                alert_type=AbuseAlertType.BOLA_IDOR,
                owasp_category=OWASPCategory.API1_BOLA,
                severity="CRITICAL" if unique_count >= 8 or is_sequential else "HIGH",
                confidence=round(confidence, 2),
                reason=f"User '{jwt_sub}' accessed {unique_count} distinct object IDs in 60s sliding window "
                       f"({'Sequential enumeration detected' if is_sequential else 'High ID cardinality'})",
                details={
                    "jwt_sub": jwt_sub,
                    "unique_ids_accessed": list(unique_ids)[-10:],
                    "unique_count": unique_count,
                    "total_requests_in_window": total_requests,
                    "is_sequential": is_sequential,
                    "window_seconds": self.window_seconds
                },
                timestamp=now
            )

        return None
