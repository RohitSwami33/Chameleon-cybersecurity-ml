import time
import threading


class TrapTokenBucket:
    """Per-IP token bucket. Rate: 5/s, Burst: 20. Returns False when exhausted."""
    def __init__(self, rate: float = 5.0, burst: int = 20):
        self._rate = rate
        self._burst = burst
        self._buckets: dict = {}
        self._lock = threading.Lock()

    def consume(self, ip: str) -> bool:
        now = time.monotonic()
        with self._lock:
            tokens, last = self._buckets.get(ip, (float(self._burst), now))
            tokens = min(self._burst, tokens + (now - last) * self._rate)
            if tokens < 1.0:
                self._buckets[ip] = (tokens, now)
                return False
            self._buckets[ip] = (tokens - 1.0, now)
            return True

    def cleanup(self, max_age: float = 3600.0):
        now = time.monotonic()
        with self._lock:
            stale = [ip for ip, (_, last) in self._buckets.items() if now - last > max_age]
            for ip in stale:
                del self._buckets[ip]


# Global instance
trap_limiter = TrapTokenBucket(rate=5.0, burst=20)
