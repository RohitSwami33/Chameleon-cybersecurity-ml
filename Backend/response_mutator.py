"""
ResponseMutationEngine — Deterministic Response Mutation
=========================================================

Applies deterministic micro-mutations to deception responses so that:
  - Same session + same request_count = always same mutation
  - Different sessions = different mutations

This breaks cross-session signature comparison by automated tools.

Mutation rules:
  - Whitespace variation
  - Punctuation alternatives
  - Timestamp shifting (±30s)
  - Error code micro-variation (±1)
  - Word order shuffle on safe tokens
"""

import hashlib
import logging
import random
import re
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


class ResponseMutationEngine:
    """
    Deterministic response mutator.

    Mutations are seeded from hash(session_id:request_count) so they are
    reproducible for the same session/count but different across sessions.
    """

    # Safe tokens that can be reordered in comma-separated lists
    _SAFE_REORDER_PATTERN = re.compile(r"(\w+(?:,\s*\w+){2,})")

    # Timestamp patterns (ISO-like and common log formats)
    _TIMESTAMP_PATTERN = re.compile(
        r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}"
    )

    # Error code patterns (Error NNNN or error code NNNN)
    _ERROR_CODE_PATTERN = re.compile(r"(Error\s+)(\d{3,5})", re.IGNORECASE)

    def mutate(
        self,
        base_response: str,
        session_id: str,
        request_count: int,
    ) -> str:
        """
        Apply deterministic mutations to a response.

        Args:
            base_response: Original response text
            session_id: Attacker session identifier
            request_count: Number of requests in this session

        Returns:
            Mutated response (deterministic for same session+count)
        """
        if not base_response:
            return base_response

        try:
            # Seed RNG deterministically
            seed_str = f"{session_id}:{request_count}"
            seed_int = int(hashlib.sha256(seed_str.encode()).hexdigest()[:8], 16)
            rng = random.Random(seed_int)

            result = base_response

            # Apply mutations in sequence
            result = self._mutate_whitespace(result, rng)
            result = self._mutate_punctuation(result, rng)
            result = self._mutate_timestamps(result, rng)
            result = self._mutate_error_codes(result, rng)
            result = self._mutate_word_order(result, rng)

            if result != base_response:
                logger.debug(
                    f"ResponseMutator: applied mutations for "
                    f"session={session_id[:8]}... count={request_count}"
                )

            return result

        except Exception as e:
            logger.warning(f"ResponseMutator: error during mutation: {e}")
            return base_response

    # ── Mutation strategies ────────────────────────────────────────────

    @staticmethod
    def _mutate_whitespace(text: str, rng: random.Random) -> str:
        """Add subtle whitespace variations."""
        # Randomly add trailing spaces to some lines
        lines = text.split("\n")
        for i in range(len(lines)):
            if rng.random() < 0.15:  # 15% chance per line
                lines[i] += " " * rng.randint(1, 3)
        return "\n".join(lines)

    @staticmethod
    def _mutate_punctuation(text: str, rng: random.Random) -> str:
        """Swap equivalent punctuation marks."""
        if rng.random() < 0.2:  # 20% chance
            # Swap smart quotes with straight quotes
            text = text.replace("'", "'") if rng.random() < 0.5 else text
        if rng.random() < 0.15:  # 15% chance
            # Add or remove trailing period
            if text.endswith("."):
                text = text[:-1]
            elif not text.endswith((".", "!", "?", "\n")):
                text += "."
        return text

    @classmethod
    def _mutate_timestamps(cls, text: str, rng: random.Random) -> str:
        """Shift embedded timestamps by ±30 seconds."""
        def _shift(match):
            try:
                ts_str = match.group()
                # Try to parse
                for fmt in ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]:
                    try:
                        dt = datetime.strptime(ts_str, fmt)
                        delta = rng.randint(-30, 30)
                        dt += timedelta(seconds=delta)
                        return dt.strftime(fmt)
                    except ValueError:
                        continue
                return ts_str
            except Exception:
                return match.group()

        return cls._TIMESTAMP_PATTERN.sub(_shift, text)

    @classmethod
    def _mutate_error_codes(cls, text: str, rng: random.Random) -> str:
        """Apply micro-variation to error codes (±1)."""
        def _vary(match):
            prefix = match.group(1)
            code = int(match.group(2))
            if rng.random() < 0.3:  # 30% chance
                code += rng.choice([-1, 1])
                code = max(100, code)  # Don't go below 100
            return f"{prefix}{code}"

        return cls._ERROR_CODE_PATTERN.sub(_vary, text)

    @classmethod
    def _mutate_word_order(cls, text: str, rng: random.Random) -> str:
        """Shuffle word order in comma-separated safe token lists."""
        def _shuffle(match):
            tokens = [t.strip() for t in match.group().split(",")]
            if len(tokens) < 3:
                return match.group()
            if rng.random() < 0.25:  # 25% chance
                rng.shuffle(tokens)
                return ", ".join(tokens)
            return match.group()

        return cls._SAFE_REORDER_PATTERN.sub(_shuffle, text)


# Global singleton
response_mutator = ResponseMutationEngine()
