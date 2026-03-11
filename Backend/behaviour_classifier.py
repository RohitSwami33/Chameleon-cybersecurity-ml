"""
BehaviourClassifier — Velocity/Entropy/Variance Attacker Classification
=========================================================================

Classifies incoming traffic as HUMAN, FUZZER, or SCANNER based on
behavioural signals:

- Requests per minute (velocity)
- Payload entropy (Shannon)
- Think-time variance (inter-request timing)
- Unique payload ratio

Routing:
  SCANNER → infinite stage-1 loop (never advance stage)
  FUZZER  → deterministic junk responses, never call Qwen
  HUMAN   → full pipeline as normal
"""

import logging
import math
import time
from collections import defaultdict
from enum import Enum
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class AttackerClass(str, Enum):
    HUMAN = "HUMAN"
    FUZZER = "FUZZER"
    SCANNER = "SCANNER"


class _IPHistory:
    """Per-IP request history for behaviour analysis."""

    __slots__ = ("timestamps", "payloads", "total_requests")

    def __init__(self):
        self.timestamps: List[float] = []
        self.payloads: List[str] = []
        self.total_requests: int = 0


class BehaviourClassifier:
    """
    Classify attacker traffic into HUMAN / FUZZER / SCANNER.

    Thresholds are intentionally conservative — if in doubt, classify as HUMAN
    so real attackers get the full deception pipeline.
    """

    # ── Thresholds ────────────────────────────────────────────────────
    SCANNER_RPM_THRESHOLD = 60           # > 60 req/min → scanner
    FUZZER_RPM_THRESHOLD = 30            # 30-60 req/min with high entropy → fuzzer
    FUZZER_ENTROPY_THRESHOLD = 4.5       # Shannon entropy > 4.5 → fuzzer-like
    SCANNER_UNIQUE_RATIO_THRESHOLD = 0.3 # < 30 % unique payloads → scanner
    THINK_TIME_VARIANCE_THRESHOLD = 0.01 # Very low variance (machine-like) → not human

    # Time window for analysis
    WINDOW_SECONDS = 60.0

    def __init__(self):
        self._histories: Dict[str, _IPHistory] = defaultdict(_IPHistory)

    def record_request(self, ip_address: str, payload: str) -> None:
        """Record an incoming request for behavioural analysis."""
        history = self._histories[ip_address]
        now = time.time()
        history.timestamps.append(now)
        history.payloads.append(payload)
        history.total_requests += 1

        # Trim old entries outside window
        cutoff = now - self.WINDOW_SECONDS
        while history.timestamps and history.timestamps[0] < cutoff:
            history.timestamps.pop(0)
            if history.payloads:
                history.payloads.pop(0)

    def classify(self, ip_address: str, payload: str) -> AttackerClass:
        """
        Classify an attacker IP based on accumulated behaviour.

        Args:
            ip_address: The attacker's IP
            payload: Current request payload

        Returns:
            AttackerClass enum: HUMAN, FUZZER, or SCANNER
        """
        self.record_request(ip_address, payload)
        history = self._histories[ip_address]

        # Need at least 5 data points for meaningful classification
        if len(history.timestamps) < 5:
            return AttackerClass.HUMAN

        # ── Signal 1: Requests per minute ─────────────────────────
        rpm = self._compute_rpm(history)

        # ── Signal 2: Payload entropy (Shannon) ──────────────────
        entropy = self._compute_entropy(payload)

        # ── Signal 3: Think-time variance ─────────────────────────
        ttv = self._compute_think_time_variance(history)

        # ── Signal 4: Unique payload ratio ────────────────────────
        upr = self._compute_unique_payload_ratio(history)

        logger.debug(
            f"BehaviourClassifier [{ip_address}]: "
            f"RPM={rpm:.1f}, entropy={entropy:.2f}, "
            f"TTV={ttv:.4f}, UPR={upr:.2f}"
        )

        # ── Decision logic ────────────────────────────────────────
        # SCANNER: high RPM + low unique ratio + low think-time variance
        if rpm > self.SCANNER_RPM_THRESHOLD and upr < self.SCANNER_UNIQUE_RATIO_THRESHOLD:
            logger.info(f"BehaviourClassifier: {ip_address} classified as SCANNER")
            return AttackerClass.SCANNER

        # FUZZER: moderate-high RPM + high entropy + low think-time variance
        if (rpm > self.FUZZER_RPM_THRESHOLD
                and entropy > self.FUZZER_ENTROPY_THRESHOLD
                and ttv < self.THINK_TIME_VARIANCE_THRESHOLD):
            logger.info(f"BehaviourClassifier: {ip_address} classified as FUZZER")
            return AttackerClass.FUZZER

        # SCANNER fallback: very high RPM regardless of other signals
        if rpm > self.SCANNER_RPM_THRESHOLD * 2:
            logger.info(f"BehaviourClassifier: {ip_address} classified as SCANNER (high RPM)")
            return AttackerClass.SCANNER

        return AttackerClass.HUMAN

    # ── Signal computations ────────────────────────────────────────

    @staticmethod
    def _compute_rpm(history: _IPHistory) -> float:
        """Compute requests per minute from timestamps."""
        if len(history.timestamps) < 2:
            return 0.0
        time_span = history.timestamps[-1] - history.timestamps[0]
        if time_span <= 0:
            return float('inf')
        return (len(history.timestamps) / time_span) * 60.0

    @staticmethod
    def _compute_entropy(payload: str) -> float:
        """Compute Shannon entropy of a payload string."""
        if not payload:
            return 0.0
        freq: Dict[str, int] = {}
        for char in payload:
            freq[char] = freq.get(char, 0) + 1
        length = len(payload)
        entropy = 0.0
        for count in freq.values():
            p = count / length
            if p > 0:
                entropy -= p * math.log2(p)
        return entropy

    @staticmethod
    def _compute_think_time_variance(history: _IPHistory) -> float:
        """Compute variance of inter-request intervals."""
        if len(history.timestamps) < 3:
            return 1.0  # Default high variance (human-like)
        intervals = [
            history.timestamps[i + 1] - history.timestamps[i]
            for i in range(len(history.timestamps) - 1)
        ]
        if not intervals:
            return 1.0
        mean = sum(intervals) / len(intervals)
        variance = sum((x - mean) ** 2 for x in intervals) / len(intervals)
        return variance

    @staticmethod
    def _compute_unique_payload_ratio(history: _IPHistory) -> float:
        """Compute ratio of unique payloads to total payloads."""
        if not history.payloads:
            return 1.0
        unique = len(set(history.payloads))
        return unique / len(history.payloads)

    def get_junk_response(self, payload: str) -> str:
        """Generate deterministic junk response for fuzzers."""
        # Deterministic based on payload hash
        h = hash(payload) % 5
        junk_responses = [
            "Error: Invalid syntax near ''",
            "ERROR 1064 (42000): Query error",
            "bash: command not found",
            "HTTP/1.1 500 Internal Server Error",
            "Access denied for user 'guest'@'localhost'",
        ]
        return junk_responses[h]


# Global singleton
behaviour_classifier = BehaviourClassifier()
