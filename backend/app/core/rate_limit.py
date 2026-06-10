import time
from collections import defaultdict
from threading import Lock


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._hits: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def allow(self, key: str, limit: int, window_seconds: int) -> bool:
        now = time.monotonic()
        cutoff = now - window_seconds

        with self._lock:
            bucket = [timestamp for timestamp in self._hits[key] if timestamp > cutoff]
            if len(bucket) >= limit:
                self._hits[key] = bucket
                return False

            bucket.append(now)
            self._hits[key] = bucket
            return True

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


_limiter = InMemoryRateLimiter()


def get_rate_limiter() -> InMemoryRateLimiter:
    return _limiter
