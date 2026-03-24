from __future__ import annotations

import time
from dataclasses import dataclass
from threading import Lock
from typing import Any, Dict, Optional, Tuple


@dataclass
class CacheEntry:
    value: Any
    expires_at: float


class TTLCache:
    """Very small in-memory TTL cache (single-process)."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._data: Dict[str, CacheEntry] = {}

    def get(self, key: str) -> Optional[Any]:
        now = time.time()
        with self._lock:
            entry = self._data.get(key)
            if not entry:
                return None
            if entry.expires_at <= now:
                self._data.pop(key, None)
                return None
            return entry.value

    def set(self, key: str, value: Any, ttl_s: int) -> None:
        with self._lock:
            self._data[key] = CacheEntry(value=value, expires_at=time.time() + ttl_s)

    def clear(self) -> None:
        with self._lock:
            self._data.clear()


class SimpleRateLimiter:
    """
    Simple per-key fixed-window rate limiter (single-process).
    Used to avoid hammering API-Football / NewsAPI.
    """

    def __init__(self) -> None:
        self._lock = Lock()
        self._window: Dict[str, Tuple[float, int]] = {}

    def allow(self, key: str, window_s: int, max_requests: int) -> bool:
        now = time.time()
        with self._lock:
            window_start, count = self._window.get(key, (now, 0))
            if now - window_start >= window_s:
                window_start, count = now, 0
            if count >= max_requests:
                self._window[key] = (window_start, count)
                return False
            self._window[key] = (window_start, count + 1)
            return True
