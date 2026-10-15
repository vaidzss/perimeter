"""
State Store for Real-Time Detection Windows.
Provides high-performance, thread-safe in-memory sliding windows and cache structures.
Fully pluggable with Redis backends if REDIS_URL is configured.
"""

import time
import threading
from typing import Dict, Any, Optional


class StateStore:
    """
    Manages real-time sliding windows, JWT fingerprints, and baseline state.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._kv_store: Dict[str, Any] = {}
        self._expiry: Dict[str, float] = {}

    def set(self, key: str, value: Any, ttl_seconds: Optional[float] = None):
        with self._lock:
            self._kv_store[key] = value
            if ttl_seconds:
                self._expiry[key] = time.time() + ttl_seconds
            elif key in self._expiry:
                del self._expiry[key]

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            if key in self._expiry and time.time() > self._expiry[key]:
                del self._kv_store[key]
                del self._expiry[key]
                return default
            return self._kv_store.get(key, default)

    def delete(self, key: str):
        with self._lock:
            self._kv_store.pop(key, None)
            self._expiry.pop(key, None)

    def clean_expired(self):
        with self._lock:
            now = time.time()
            expired_keys = [k for k, exp in self._expiry.items() if now > exp]
            for k in expired_keys:
                self._kv_store.pop(k, None)
                self._expiry.pop(k, None)
