"""
Token Misuse & Replay Detector.
Detects concurrent JWT JTI usage across distinct IP addresses and User-Agent fingerprints
within a 60-second sliding window (Token Replay / Session Hijacking).
"""

import time
from collections import deque
from typing import Dict, Deque, Tuple, Optional, Set
from core.models import AbuseAlert, AbuseAlertType, OWASPCategory


class TokenReplayDetector:
    """
    Tracks token fingerprint stability (IP, User-Agent) across time windows.
    """

    def __init__(self, window_seconds: float = 60.0):
        self.window_seconds = window_seconds
        # Key: jti -> Deque of (timestamp, client_ip, user_agent)
        self.jti_fingerprints: Dict[str, Deque[Tuple[float, str, str]]] = {}

    def _purge_old_entries(self, jti: str, current_time: float):
        cutoff = current_time - self.window_seconds
        q = self.jti_fingerprints.get(jti)
        if q:
            while q and q[0][0] < cutoff:
                q.popleft()
            if not q:
                del self.jti_fingerprints[jti]

    def inspect(self,
                jwt_jti: Optional[str],
                jwt_sub: Optional[str],
                client_ip: Optional[str],
                user_agent: Optional[str],
                timestamp: Optional[float] = None) -> Optional[AbuseAlert]:
        """
        Inspects token usage for concurrent fingerprint drift across IPs or User-Agents.
        """
        if not jwt_jti:
            return None

        now = timestamp if timestamp is not None else time.time()
        ip = client_ip or "UNKNOWN_IP"
        ua = user_agent or "UNKNOWN_UA"

        self._purge_old_entries(jwt_jti, now)

        if jwt_jti not in self.jti_fingerprints:
            self.jti_fingerprints[jwt_jti] = deque()

        history = self.jti_fingerprints[jwt_jti]
        
        # Check existing entries in the window for conflicting IP or User-Agent
        conflicting_ips: Set[str] = set()
        conflicting_uas: Set[str] = set()

        for t, prev_ip, prev_ua in history:
            if prev_ip != ip and prev_ip != "UNKNOWN_IP" and ip != "UNKNOWN_IP":
                conflicting_ips.add(prev_ip)
            if prev_ua != ua and prev_ua != "UNKNOWN_UA" and ua != "UNKNOWN_UA":
                conflicting_uas.add(prev_ua)

        history.append((now, ip, ua))

        if conflicting_ips or conflicting_uas:
            violations = []
            if conflicting_ips:
                violations.append(f"Concurrent IPs: {list(conflicting_ips)} vs {ip}")
            if conflicting_uas:
                violations.append(f"Conflicting User-Agents detected in 60s")

            return AbuseAlert(
                alert_type=AbuseAlertType.TOKEN_REPLAY,
                owasp_category=OWASPCategory.API2_BROKEN_AUTH,
                severity="CRITICAL",
                confidence=0.98,
                reason=f"Token JTI '{jwt_jti}' reused concurrently across divergent client fingerprints: " + ", ".join(violations),
                details={
                    "jwt_jti": jwt_jti,
                    "jwt_sub": jwt_sub,
                    "current_ip": ip,
                    "conflicting_ips": list(conflicting_ips),
                    "current_ua": ua,
                    "conflicting_uas": list(conflicting_uas),
                    "window_seconds": self.window_seconds
                },
                timestamp=now
            )

        return None
