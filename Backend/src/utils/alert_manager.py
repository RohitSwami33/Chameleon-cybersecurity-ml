"""
Alert Manager — Chameleon Adaptive Honeypot System
===================================================
EC-033/034/035/036/037: Full Alerting System Hardening

Features:
- EC-033: Fire-and-forget webhook with 5s timeout
- EC-034: Fallback to stderr/logging when WEBHOOK_URL absent
- EC-035: Exponential backoff [1,2,4]s on 429 rate limiting
- EC-036: SWAD — Sliding-Window Alert Deduplication (Novel Algorithm)
- EC-037: ChameleonEncoder for safe JSON serialization
"""
import asyncio
import json
import logging
import os
import random
import threading
import time
from datetime import datetime

logger = logging.getLogger("chameleon.alerts")


# ============================================================
# EC-037: ChameleonEncoder — Custom JSON Encoder
# ============================================================

class ChameleonEncoder(json.JSONEncoder):
    """
    EC-037: Safe JSON encoder for non-serializable types.
    Handles numpy arrays, tensors, datetimes, UUIDs, and custom objects.
    """
    def default(self, obj):
        # Tensor/numpy scalar
        if hasattr(obj, 'item'):
            return obj.item()
        # Numpy array
        if hasattr(obj, 'tolist'):
            return obj.tolist()
        # Datetime
        if isinstance(obj, datetime):
            return obj.isoformat()
        # Numpy dtype
        if hasattr(obj, 'dtype'):
            return obj.item() if hasattr(obj, 'item') else str(obj)
        # UUID/hex objects
        if hasattr(obj, 'hex'):
            return str(obj)
        # Fallback to string
        return str(obj)


def safe_json_dumps(payload: dict) -> str:
    """
    EC-037: Safely serialize payload to JSON using ChameleonEncoder.
    Prevents TypeError from non-serializable objects.
    """
    return json.dumps(payload, cls=ChameleonEncoder)


# ============================================================
# EC-033/035: Fire-and-Forget Webhook with Exponential Backoff
# ============================================================

async def _send_webhook_inner(url: str, payload: dict) -> None:
    """
    EC-033: Send webhook with 5s timeout.
    EC-035: Exponential backoff [1,2,4]s on 429 rate limiting.
    Abandons after 3 attempts to prevent blocking.
    """
    import httpx
    
    delays = [1.0, 2.0, 4.0]  # EC-035: Exponential backoff
    
    for attempt, base_delay in enumerate(delays):
        try:
            async with httpx.AsyncClient() as client:
                response = await asyncio.wait_for(
                    client.post(
                        url,
                        content=safe_json_dumps(payload),
                        headers={"Content-Type": "application/json"}
                    ),
                    timeout=5.0  # EC-033: 5s timeout
                )
                
                if response.status_code == 429:
                    # EC-035: Rate limited — apply backoff with jitter
                    wait = base_delay + random.uniform(-0.3, 0.3)
                    await asyncio.sleep(max(0.1, wait))
                    continue
                    
                return  # Success or non-retryable error
                
        except asyncio.TimeoutError:
            logger.debug("Webhook timeout attempt %d", attempt + 1)
        except Exception as e:
            logger.debug("Webhook error attempt %d: %s", attempt + 1, e)
    
    logger.warning("Webhook abandoned after 3 attempts")


def _dispatch_alert(message: str) -> None:
    """
    EC-034: Dispatch alert via webhook or fallback to stderr logging.
    Non-blocking fire-and-forget execution.
    """
    url = os.getenv("WEBHOOK_URL")
    
    if url:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Fire-and-forget: don't await
                loop.create_task(_send_webhook_inner(url, {"text": message}))
            else:
                # No running loop — log to stderr
                logger.warning("[ALERT] %s", message)
        except Exception:
            # No event loop — log to stderr
            logger.warning("[ALERT-NO-LOOP] %s", message)
    else:
        # EC-034: No webhook configured — fallback to stderr
        logger.warning("[ALERT-NO-WEBHOOK] %s", message)


# ============================================================
# EC-036: SWAD — Sliding-Window Alert Deduplication (Novel)
# ============================================================

class SWADBuffer:
    """
    EC-036: SWAD (Sliding-Window Alert Deduplication) Buffer.
    Novel algorithm: Aggregates alerts within a time window to prevent flooding.
    
    When burst threshold is exceeded, sends a digest instead of individual alerts.
    """
    
    def __init__(self, window_seconds: float = 60.0, min_burst: int = 10):
        """
        Initialize SWAD buffer.
        
        Args:
            window_seconds: Time window for aggregation (default 60s)
            min_burst: Minimum alerts before deduplication kicks in (default 10)
        """
        self._window = window_seconds
        self._min_burst = min_burst
        self._buffer: dict = {}  # {alert_type: count}
        self._last_flush = time.monotonic()
        self._lock = threading.Lock()

    def push(self, alert_type: str, count: int = 1) -> str:
        """
        Push alert to buffer. Returns digest if flush triggered, None otherwise.
        
        Args:
            alert_type: Type of alert (e.g., "WARNING:SQLi")
            count: Number of alerts to add
            
        Returns:
            Digest string if flushed, None otherwise
        """
        with self._lock:
            self._buffer[alert_type] = self._buffer.get(alert_type, 0) + count
            total = sum(self._buffer.values())
            now = time.monotonic()
            
            # Flush if window expired
            if now - self._last_flush >= self._window:
                return self._flush()
            
            # Below burst threshold — don't aggregate, return None (no send)
            if total < self._min_burst:
                return None
                
            # At or above burst — flush and send digest
            return self._flush()

    def _flush(self) -> str:
        """Flush buffer and return digest."""
        if not self._buffer:
            self._last_flush = time.monotonic()
            return None
        
        # Create digest: sorted by count descending
        parts = [
            f"{k}x{v}"
            for k, v in sorted(self._buffer.items(), key=lambda x: -x[1])
        ]
        digest = f"[Digest {self._window:.0f}s] " + ", ".join(parts)
        
        self._buffer.clear()
        self._last_flush = time.monotonic()
        return digest

    def force_flush(self) -> str:
        """Force flush regardless of window/burst."""
        with self._lock:
            return self._flush()


# Global SWAD instance
_swad = SWADBuffer(window_seconds=60.0, min_burst=10)


# ============================================================
# Public API
# ============================================================

def alert(message: str, alert_type: str = "general", level: str = "WARNING") -> None:
    """
    Unified alert dispatcher.
    Uses SWAD deduplication + fire-and-forget dispatch.
    
    Args:
        message: Alert message
        alert_type: Type of alert for deduplication
        level: Alert level (WARNING, CRITICAL, etc.)
    """
    # Push to SWAD buffer for deduplication
    digest = _swad.push(f"{level}:{alert_type}")
    
    if digest:
        # Send digest instead of individual alert
        _dispatch_alert(digest)


async def swad_flush_loop() -> None:
    """
    Background task: Periodically flush SWAD buffer.
    Call once from FastAPI lifespan.
    """
    while True:
        await asyncio.sleep(60)
        digest = _swad.force_flush()
        if digest:
            _dispatch_alert(digest)


# ============================================================
# Legacy Compatibility (deprecated but kept for backward compat)
# ============================================================

class AlertManager:
    """Legacy AlertManager — deprecated. Use alert() function instead."""
    
    def __init__(self):
        self.slack_webhook_url = None
        self.discord_webhook_url = None
        logger.warning("AlertManager class is deprecated. Use alert() function instead.")

    async def trigger_critical_attack_alert(
        self,
        ip_address: str,
        command: str,
        score: float,
        session_id: str = None
    ) -> None:
        """Legacy method — redirects to alert() function."""
        message = f"CRITICAL ATTACK | IP={ip_address} | CMD={command[:50]} | SCORE={score}"
        alert(message, alert_type="CRITICAL_ATTACK", level="CRITICAL")

    async def trigger_beacon_exfiltration_alert(
        self,
        session_id: str,
        ip_address: str,
        user_agent: str
    ) -> None:
        """Legacy method — redirects to alert() function."""
        message = f"BEACON EXFILTRATION | SESSION={session_id} | IP={ip_address}"
        alert(message, alert_type="BEACON_EXFIL", level="CRITICAL")


# Singleton for backward compatibility
alert_manager = AlertManager()
