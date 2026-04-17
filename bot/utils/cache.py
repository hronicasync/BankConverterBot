from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class _Entry:
    value: Any
    stored_at: float = field(default_factory=time.monotonic)


class TTLCache:
    def __init__(self, ttl_seconds: int) -> None:
        self.ttl = ttl_seconds
        self._store: dict[str, _Entry] = {}

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        if time.monotonic() - entry.stored_at > self.ttl:
            return None
        return entry.value

    def set(self, key: str, value: Any) -> None:
        self._store[key] = _Entry(value=value)

    def invalidate(self, key: str) -> None:
        self._store.pop(key, None)

    def get_stale(self, key: str) -> Any | None:
        entry = self._store.get(key)
        return entry.value if entry else None

    def age_seconds(self, key: str) -> float | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        return time.monotonic() - entry.stored_at


_ttl = int(os.getenv("RATES_CACHE_TTL", "1800"))
rates_cache = TTLCache(ttl_seconds=_ttl)
