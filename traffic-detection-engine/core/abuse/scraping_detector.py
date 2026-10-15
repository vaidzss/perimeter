"""
Data Scraping & Harvesting Detector.
Identifies high-velocity crawlers and automated scrapers by evaluating:
1. Dynamic Rate Z-Score > 3.0 (Rate > μ + 3σ req/min)
2. Response Byte Volume Spikes (bulk data exfiltration)
"""

import time
from collections import deque
from typing import Dict, Deque, Optional, Tuple
from core.models import AbuseAlert, AbuseAlertType, OWASPCategory
from core.abuse.baseline import BaselineProfiler


class ScrapingDetector:
    """
    Evaluates client and route traffic velocity against dynamic baseline profiles.
    """

    def __init__(self, baseline_profiler: BaselineProfiler, window_seconds: float = 60.0):
        self.baseline = baseline_profiler
        self.window_seconds = window_seconds
        # Key: "client_id:route_key" -> Deque of timestamps
        self.client_windows: Dict[str, Deque[float]] = {}

    def _purge_old_timestamps(self, key: str, current_time: float):
        cutoff = current_time - self.window_seconds
        q = self.client_windows.get(key)
        if q:
            while q and q[0] < cutoff:
                q.popleft()
            if not q:
                del self.client_windows[key]

    def inspect(self,
                client_id: str,
                route_key: str,
                response_bytes: int,
                timestamp: Optional[float] = None) -> Optional[AbuseAlert]:
        """
        Inspects incoming event for scraping or harvesting behavior.
        """
        now = timestamp if timestamp is not None else time.time()
        window_key = f"{client_id}:{route_key}"
        self._purge_old_timestamps(window_key, now)

        if window_key not in self.client_windows:
            self.client_windows[window_key] = deque()

        self.client_windows[window_key].append(now)
        current_window_rate = float(len(self.client_windows[window_key]))

        # Calculate Z-score for request rate against baseline
        z_rate, mu_rate, sigma_rate = self.baseline.calculate_rate_z_score(route_key, current_window_rate)

        # Check response byte spike against baseline
        is_byte_spike, z_bytes, mu_bytes, sigma_bytes = self.baseline.is_byte_spike(route_key, float(response_bytes))

        # Check condition: Rate > (μ + 3σ) OR Response Byte Spike
        rate_threshold = mu_rate + (3.0 * sigma_rate)
        rate_violation = (current_window_rate > rate_threshold and current_window_rate >= 15.0) or (z_rate > 3.0 and current_window_rate >= 15.0)
        byte_violation = (is_byte_spike and response_bytes > 5000)

        # Only update baseline for stable, non-anomalous observations (|Z| <= 1.5)
        if abs(z_rate) <= 1.5 and not is_byte_spike:
            self.baseline.record_observation(route_key, current_window_rate, float(response_bytes))

        if rate_violation or byte_violation:
            reasons = []
            if rate_violation:
                reasons.append(f"Request rate {current_window_rate:.1f} req/min exceeds dynamic threshold (μ={mu_rate:.1f}, σ={sigma_rate:.1f}, Z={z_rate:.2f})")
            if byte_violation:
                reasons.append(f"Response payload {response_bytes} bytes exceeds normal baseline (μ={mu_bytes:.1f}, σ={sigma_bytes:.1f}, Z={z_bytes:.2f})")

            alert_type = AbuseAlertType.BYTE_SPIKE if (byte_violation and not rate_violation) else AbuseAlertType.DATA_SCRAPING
            
            return AbuseAlert(
                alert_type=alert_type,
                owasp_category=OWASPCategory.API4_UNRESTRICTED_RESOURCE,
                severity="CRITICAL" if (rate_violation and byte_violation) else "HIGH",
                confidence=round(min(1.0, 0.75 + (max(z_rate, z_bytes) / 10.0) * 0.25), 2),
                reason=" | ".join(reasons),
                details={
                    "client_id": client_id,
                    "route_key": route_key,
                    "current_rate_per_min": current_window_rate,
                    "baseline_rate_mu": round(mu_rate, 2),
                    "baseline_rate_sigma": round(sigma_rate, 2),
                    "rate_z_score": round(z_rate, 2),
                    "response_bytes": response_bytes,
                    "baseline_bytes_mu": round(mu_bytes, 2),
                    "baseline_bytes_sigma": round(sigma_bytes, 2),
                    "bytes_z_score": round(z_bytes, 2)
                },
                timestamp=now
            )

        return None
