"""
Baseline Profiler using Welford's Algorithm.
Calculates online mean (μ) and standard deviation (σ) for request rates and payload byte sizes per route.
Guarantees numerical stability and O(1) time complexity per telemetry event.
"""

import math
from typing import Dict, Tuple, Optional


class WelfordAccumulator:
    """
    Maintains running mean, variance, and standard deviation using Welford's algorithm.
    """
    def __init__(self, initial_mean: float = 10.0, initial_std: float = 3.0):
        self.count = 0
        self.mean = initial_mean
        self.M2 = (initial_std ** 2) * max(1, self.count)
        self.min_val = float('inf')
        self.max_val = float('-inf')

    def update(self, val: float):
        self.count += 1
        delta = val - self.mean
        self.mean += delta / self.count
        delta2 = val - self.mean
        self.M2 += delta * delta2
        if val < self.min_val:
            self.min_val = val
        if val > self.max_val:
            self.max_val = val

    @property
    def variance(self) -> float:
        if self.count < 2:
            return 9.0  # default std=3.0, var=9.0
        return self.M2 / (self.count - 1)

    @property
    def std_dev(self) -> float:
        var = self.variance
        return math.sqrt(var) if var > 0.0001 else 1.0


class BaselineProfiler:
    """
    Per-route baseline profiling for:
    - Request rates (requests / minute)
    - Response byte sizes (bytes)
    """

    def __init__(self):
        # Key: "METHOD:ROUTE_TEMPLATE" -> WelfordAccumulator for rate
        self.rate_profiles: Dict[str, WelfordAccumulator] = {}
        # Key: "METHOD:ROUTE_TEMPLATE" -> WelfordAccumulator for bytes
        self.byte_profiles: Dict[str, WelfordAccumulator] = {}

    def get_or_create_rate(self, route_key: str) -> WelfordAccumulator:
        if route_key not in self.rate_profiles:
            self.rate_profiles[route_key] = WelfordAccumulator(initial_mean=10.0, initial_std=3.0)
        return self.rate_profiles[route_key]

    def get_or_create_bytes(self, route_key: str) -> WelfordAccumulator:
        if route_key not in self.byte_profiles:
            self.byte_profiles[route_key] = WelfordAccumulator(initial_mean=500.0, initial_std=150.0)
        return self.byte_profiles[route_key]

    def record_observation(self, route_key: str, current_rate: float, response_bytes: float):
        """
        Updates the running baseline with a new observation.
        """
        rate_acc = self.get_or_create_rate(route_key)
        rate_acc.update(current_rate)

        bytes_acc = self.get_or_create_bytes(route_key)
        bytes_acc.update(response_bytes)

    def calculate_rate_z_score(self, route_key: str, observed_rate: float) -> Tuple[float, float, float]:
        """
        Returns (z_score, mu, sigma) for the observed rate.
        Z = (X - μ) / σ
        """
        acc = self.get_or_create_rate(route_key)
        mu = acc.mean
        sigma = acc.std_dev
        z_score = (observed_rate - mu) / sigma
        return z_score, mu, sigma

    def is_byte_spike(self, route_key: str, observed_bytes: float, z_threshold: float = 3.0) -> Tuple[bool, float, float, float]:
        """
        Returns (is_spike, z_score, mu, sigma) for observed response bytes.
        """
        acc = self.get_or_create_bytes(route_key)
        mu = acc.mean
        sigma = acc.std_dev
        z_score = (observed_bytes - mu) / sigma
        is_spike = z_score > z_threshold or observed_bytes > (mu + 3 * sigma)
        return is_spike, z_score, mu, sigma
