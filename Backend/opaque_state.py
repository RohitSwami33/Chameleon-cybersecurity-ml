"""
OpaqueStateVM — State Obfuscation Virtual Machine
====================================================

Encodes internal state values (stage numbers, IDs) into opaque tokens
before they appear in any response. Prevents attackers from reasoning
about internal honeypot state progression.

Encoding:
  (stage XOR register[0]) * register[1] % register[2]
  where registers are derived from HMAC(secret, session_id)

Decoding reverses the operation using modular inverse.
"""

import hashlib
import hmac
import logging
import os
from typing import Tuple

logger = logging.getLogger(__name__)

SESSION_SECRET = os.getenv("SESSION_SECRET", "chameleon-default-session-secret-change-me")


class OpaqueStateVM:
    """
    Encodes and decodes internal state values using session-specific registers.

    Each session gets unique registers derived from HMAC(secret, session_id),
    making the encoding opaque and session-specific.
    """

    @staticmethod
    def _derive_registers(session_id: str) -> Tuple[int, int, int]:
        """
        Derive three encoding registers from HMAC of session_id.

        Returns:
            Tuple of (reg0: XOR key, reg1: multiplier, reg2: modulus)
        """
        digest = hmac.new(
            SESSION_SECRET.encode(),
            session_id.encode(),
            hashlib.sha256,
        ).hexdigest()

        reg0 = int(digest[:8], 16) % 256       # XOR key (0-255)
        reg1 = int(digest[8:16], 16) % 997 + 2  # Multiplier (2-998) — avoid 0,1
        reg2 = int(digest[16:24], 16) % 9973 + 1000  # Modulus (1000-10972) — large prime-ish

        return reg0, reg1, reg2

    @classmethod
    def encode_stage(cls, stage: int, session_id: str) -> str:
        """
        Encode a stage number into an opaque token.

        Formula: (stage XOR reg0) * reg1 % reg2

        Args:
            stage: The integer stage number to encode
            session_id: Session identifier for register derivation

        Returns:
            Hex string opaque token
        """
        try:
            reg0, reg1, reg2 = cls._derive_registers(session_id)
            encoded = ((stage ^ reg0) * reg1) % reg2
            return format(encoded, "x")
        except Exception as e:
            logger.warning(f"OpaqueStateVM: encode error: {e}")
            # Fallback: return a hash-based opaque value
            return hashlib.md5(f"{stage}:{session_id}".encode()).hexdigest()[:8]

    @classmethod
    def decode_stage(cls, opaque_token: str, session_id: str) -> int:
        """
        Decode an opaque token back to a stage number.

        Uses modular multiplicative inverse of reg1 mod reg2.

        Args:
            opaque_token: Hex string opaque token
            session_id: Session identifier for register derivation

        Returns:
            Integer stage number
        """
        try:
            reg0, reg1, reg2 = cls._derive_registers(session_id)
            encoded = int(opaque_token, 16)

            # Modular multiplicative inverse of reg1 mod reg2
            inv = cls._mod_inverse(reg1, reg2)
            if inv is None:
                logger.warning("OpaqueStateVM: no modular inverse, falling back")
                return 1

            decoded = (encoded * inv) % reg2
            stage = decoded ^ reg0

            # Sanity check — stages should be small integers
            if 0 <= stage <= 100:
                return stage
            else:
                logger.warning(f"OpaqueStateVM: decoded stage {stage} out of range")
                return 1
        except Exception as e:
            logger.warning(f"OpaqueStateVM: decode error: {e}")
            return 1

    @staticmethod
    def _mod_inverse(a: int, m: int) -> int:
        """
        Compute modular multiplicative inverse of a mod m using
        extended Euclidean algorithm.

        Returns None if inverse doesn't exist.
        """
        def _extended_gcd(a, b):
            if a == 0:
                return b, 0, 1
            gcd, x1, y1 = _extended_gcd(b % a, a)
            x = y1 - (b // a) * x1
            y = x1
            return gcd, x, y

        gcd, x, _ = _extended_gcd(a % m, m)
        if gcd != 1:
            return None  # Inverse doesn't exist
        return (x % m + m) % m

    @classmethod
    def encode_value(cls, value: int, session_id: str) -> str:
        """Generic integer value encoder (same algorithm as encode_stage)."""
        return cls.encode_stage(value, session_id)

    @classmethod
    def decode_value(cls, opaque_token: str, session_id: str) -> int:
        """Generic integer value decoder."""
        return cls.decode_stage(opaque_token, session_id)


# Global singleton (stateless, so a class reference would also work)
opaque_vm = OpaqueStateVM()
