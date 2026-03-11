"""
AdaptiveTimingMask — Response Timing Normalisation
====================================================

Normalises response timing across all paths (benign, cached, LLM, static
fallback) to a consistent distribution, preventing attackers from using
response time as a side-channel to distinguish cache hits from LLM calls.

Target distribution: Normal(mean=0.4, std=0.15) clipped to [0.1, 2.5]
Payload length adds up to 10% influence on delay.
Minimum delay: 100ms even for cache hits.

PSO-calculated delay is consumed as input (not replaced) — the timing
mask pads the actual processing time to the target.
"""

import asyncio
import logging
import random
import time
from typing import Optional

logger = logging.getLogger(__name__)


class AdaptiveTimingMask:
    """
    Makes all response times look similar regardless of processing path.
    """

    # Target distribution parameters
    MEAN_DELAY = 0.4       # seconds
    STD_DELAY = 0.15       # seconds
    MIN_DELAY = 0.1        # seconds (100ms floor)
    MAX_DELAY = 2.5        # seconds (ceiling)
    PAYLOAD_INFLUENCE = 0.10  # max 10% added by payload length

    def __init__(self):
        self._rng = random.Random()

    def sample_delay(
        self,
        payload_length: int = 0,
        is_cached: bool = False,
        is_llm_call: bool = False,
        pso_delay: float = 0.0,
    ) -> float:
        """
        Sample a delay from the target distribution.

        Args:
            payload_length: Length of the request payload
            is_cached: Whether the response came from cache
            is_llm_call: Whether an LLM API call was made
            pso_delay: PSO-optimised delay (consumed as input, not replaced)

        Returns:
            Target total response time in seconds
        """
        # Base delay from normal distribution
        base = self._rng.gauss(self.MEAN_DELAY, self.STD_DELAY)

        # Payload length influence (longer payloads → slightly longer delay)
        if payload_length > 0:
            length_factor = min(payload_length / 1000.0, 1.0) * self.PAYLOAD_INFLUENCE
            base += length_factor

        # Add PSO delay as additional factor (not replacement)
        if pso_delay > 0:
            base += pso_delay * 0.1  # 10% of PSO delay contributes

        # Clip to bounds
        return max(self.MIN_DELAY, min(base, self.MAX_DELAY))

    async def serve_with_mask(
        self,
        response_content: str,
        payload_length: int = 0,
        processing_start: Optional[float] = None,
        is_cached: bool = False,
        is_llm_call: bool = False,
        pso_delay: float = 0.0,
    ) -> str:
        """
        Pad actual processing time to sampled target.

        Args:
            response_content: The response string to return
            payload_length: Length of the request payload
            processing_start: time.time() when processing began
            is_cached: Whether response was from cache
            is_llm_call: Whether an LLM call was made
            pso_delay: PSO delay that was already applied

        Returns:
            The same response_content (after appropriate delay)
        """
        target_delay = self.sample_delay(
            payload_length=payload_length,
            is_cached=is_cached,
            is_llm_call=is_llm_call,
            pso_delay=pso_delay,
        )

        if processing_start is not None:
            elapsed = time.time() - processing_start
            remaining = target_delay - elapsed
        else:
            remaining = target_delay

        if remaining > 0:
            await asyncio.sleep(remaining)
            logger.debug(
                f"TimingMask: padded {remaining:.3f}s "
                f"(target={target_delay:.3f}s, cached={is_cached})"
            )

        return response_content


# Global singleton
timing_mask = AdaptiveTimingMask()
