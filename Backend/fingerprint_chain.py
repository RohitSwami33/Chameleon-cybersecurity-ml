"""
FingerprintChain — Deep Attacker Binding via Multi-Signal Fingerprinting
=========================================================================

Collects rich attacker signals beyond IP+UA and uses weighted cosine
similarity to match returning attackers even if they rotate IPs or proxies.

Signals:
  - IP address
  - User-Agent
  - Accept-Language
  - Accept-Encoding
  - JA3 hash (TLS fingerprint, if available)
  - Cookie presence
  - Payload writing style (quote preference, avg length, spacing)

match_existing_session() threshold = 0.65 cosine similarity.
"""

import hashlib
import logging
import math
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class FingerprintChain:
    """
    Multi-signal fingerprint generator and matcher.

    Maintains a registry of known fingerprint vectors and can match
    incoming connections to existing sessions via cosine similarity.
    """

    # Signal weights for similarity computation
    WEIGHTS = {
        "user_agent": 0.25,
        "accept_language": 0.15,
        "accept_encoding": 0.10,
        "ja3_hash": 0.20,
        "cookie_presence": 0.05,
        "quote_preference": 0.10,
        "avg_payload_length": 0.05,
        "spacing_style": 0.10,
    }

    MATCH_THRESHOLD = 0.65

    def __init__(self):
        # fingerprint → signal vector (dict of signal_name → hashed value)
        self._registry: Dict[str, Dict[str, float]] = {}
        # fingerprint → raw signals for debugging/logging
        self._raw_signals: Dict[str, Dict[str, Any]] = {}

    def compute_fingerprint(self, signals: Dict[str, Any]) -> str:
        """
        Compute a weighted hash fingerprint from collected signals.

        Args:
            signals: Dict with keys matching WEIGHTS keys plus 'ip_address'

        Returns:
            SHA256 hex digest fingerprint
        """
        # Canonical signal string
        parts = []
        for key in sorted(signals.keys()):
            parts.append(f"{key}={signals.get(key, '')}")
        combined = "|".join(parts)
        return hashlib.sha256(combined.encode()).hexdigest()

    def _vectorise(self, signals: Dict[str, Any]) -> Dict[str, float]:
        """
        Convert raw signals into a numerical vector for similarity comparison.

        Each signal is hashed to a float in [0, 1] for distance computation.
        """
        vector = {}
        for signal_name in self.WEIGHTS:
            value = signals.get(signal_name, "")
            if value is None:
                value = ""
            # Hash the string value to a float in [0, 1]
            h = int(hashlib.md5(str(value).encode()).hexdigest()[:8], 16)
            vector[signal_name] = h / 0xFFFFFFFF
        return vector

    def register(self, fingerprint: str, signals: Dict[str, Any]) -> None:
        """Register a fingerprint with its signal vector."""
        self._registry[fingerprint] = self._vectorise(signals)
        self._raw_signals[fingerprint] = dict(signals)

    def match_existing_session(
        self, signals: Dict[str, Any], threshold: float = None
    ) -> Optional[str]:
        """
        Attempt to match incoming signals to an existing session.

        Args:
            signals: Current request signals
            threshold: Similarity threshold (default = MATCH_THRESHOLD)

        Returns:
            Matching fingerprint if similarity > threshold, else None
        """
        if threshold is None:
            threshold = self.MATCH_THRESHOLD

        if not self._registry:
            return None

        new_vector = self._vectorise(signals)
        best_match: Optional[str] = None
        best_score: float = 0.0

        for fp, vec in self._registry.items():
            score = self._weighted_cosine_similarity(new_vector, vec)
            if score > best_score:
                best_score = score
                best_match = fp

        if best_score >= threshold:
            logger.info(
                f"FingerprintChain: Matched existing session "
                f"{best_match[:12]}... (similarity={best_score:.3f})"
            )
            return best_match

        return None

    def _weighted_cosine_similarity(
        self, vec_a: Dict[str, float], vec_b: Dict[str, float]
    ) -> float:
        """
        Compute weighted cosine similarity between two signal vectors.

        Weights are taken from self.WEIGHTS.
        """
        dot = 0.0
        mag_a = 0.0
        mag_b = 0.0

        for key, weight in self.WEIGHTS.items():
            a = vec_a.get(key, 0.0) * weight
            b = vec_b.get(key, 0.0) * weight
            dot += a * b
            mag_a += a * a
            mag_b += b * b

        if mag_a == 0 or mag_b == 0:
            return 0.0

        return dot / (math.sqrt(mag_a) * math.sqrt(mag_b))

    @staticmethod
    def collect_signals(request) -> Dict[str, Any]:
        """
        Collect fingerprint signals from a FastAPI Request object.

        This is a convenience method for use in main.py endpoints.
        """
        try:
            headers = request.headers if hasattr(request, 'headers') else {}

            # Payload writing style signals (basic — updated per request by pipeline)
            return {
                "ip_address": (
                    request.client.host if hasattr(request, 'client') and request.client else "unknown"
                ),
                "user_agent": headers.get("user-agent", ""),
                "accept_language": headers.get("accept-language", ""),
                "accept_encoding": headers.get("accept-encoding", ""),
                "ja3_hash": headers.get("x-ja3-hash", ""),  # Requires TLS middleware
                "cookie_presence": "1" if headers.get("cookie") else "0",
                "quote_preference": "",  # Updated per payload
                "avg_payload_length": "",
                "spacing_style": "",
            }
        except Exception as e:
            logger.debug(f"FingerprintChain: signal collection error: {e}")
            return {}

    @staticmethod
    def update_payload_signals(
        signals: Dict[str, Any], payload: str
    ) -> Dict[str, Any]:
        """Update payload-derived signals (writing style analysis)."""
        if not payload:
            return signals

        # Quote preference: single vs double
        single = payload.count("'")
        double = payload.count('"')
        if single > double:
            signals["quote_preference"] = "single"
        elif double > single:
            signals["quote_preference"] = "double"
        else:
            signals["quote_preference"] = "mixed"

        # Average payload length (this payload)
        signals["avg_payload_length"] = str(len(payload))

        # Spacing style: tabs vs spaces
        tabs = payload.count("\t")
        spaces = payload.count(" ")
        if tabs > spaces:
            signals["spacing_style"] = "tabs"
        else:
            signals["spacing_style"] = "spaces"

        return signals


# Global singleton
fingerprint_chain = FingerprintChain()
