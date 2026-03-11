"""
CanaryTrapSystem — Embedded Attacker Canary (EAC) Tracking
===========================================================

Plants unique trackable tokens (canary IDs) into deception responses:
  - Fake SQL dump entries
  - File paths
  - API keys
  - JWT tokens

Each canary is registered in PostgreSQL with the session fingerprint.
Incoming requests are scanned for previously planted canary IDs.
If found → escalate threat level and re-bind to original session.

Fallback: In-memory registry if PostgreSQL is unavailable.
"""

import hashlib
import json
import logging
import os
import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class CanaryTrapSystem:
    """
    Plants and detects canary tokens in deception responses.

    Each canary is a unique, short, plausible-looking token embedded into
    fake data served to attackers. If the attacker replays data containing
    a canary, we detect it and re-bind them to their original session.
    """

    # Characters for generating canary tokens that look like real credentials
    _CANARY_PREFIX = "CHML"  # Chameleon marker (looks like AWS key prefix)

    def __init__(self):
        # In-memory registry: canary_id → metadata
        self._registry: Dict[str, Dict[str, Any]] = {}
        # Quick lookup: fingerprint → list of canary_ids
        self._by_fingerprint: Dict[str, List[str]] = {}

    def _generate_canary_id(self) -> str:
        """Generate a unique canary ID that looks like a credential fragment."""
        raw = uuid.uuid4().hex[:16].upper()
        return f"{self._CANARY_PREFIX}{raw}"

    def plant_canary(
        self,
        response: str,
        session_fingerprint: str,
        canary_type: str = "generic",
    ) -> Tuple[str, str]:
        """
        Embed a unique canary token into a deception response.

        Args:
            response: The deception response text
            session_fingerprint: The attacker's session fingerprint
            canary_type: Type of canary (api_key, jwt, sql_dump, file_path)

        Returns:
            Tuple of (response_with_canary, canary_id)
        """
        canary_id = self._generate_canary_id()

        # Register the canary
        canary_meta = {
            "canary_id": canary_id,
            "session_fingerprint": session_fingerprint,
            "canary_type": canary_type,
            "planted_at": datetime.utcnow().isoformat(),
            "detected": False,
            "detected_at": None,
        }
        self._registry[canary_id] = canary_meta

        if session_fingerprint not in self._by_fingerprint:
            self._by_fingerprint[session_fingerprint] = []
        self._by_fingerprint[session_fingerprint].append(canary_id)

        # Persist to PostgreSQL (best-effort)
        self._pg_store_canary(canary_meta)

        # Embed canary into response
        response_with_canary = self._embed_canary(response, canary_id, canary_type)

        logger.debug(
            f"CanaryTrap: Planted {canary_type} canary {canary_id[:12]}... "
            f"for fingerprint {session_fingerprint[:12]}..."
        )

        return response_with_canary, canary_id

    def check_incoming(self, request_data: str) -> Optional[Dict[str, Any]]:
        """
        Scan incoming request data for previously planted canary IDs.

        Args:
            request_data: Full request string (URL + headers + body)

        Returns:
            Canary match metadata if found, else None
        """
        if not request_data or not self._registry:
            return None

        for canary_id, meta in self._registry.items():
            if canary_id in request_data:
                logger.warning(
                    f"🚨 CANARY DETECTED | ID={canary_id[:12]}... | "
                    f"Original fingerprint={meta['session_fingerprint'][:12]}..."
                )
                meta["detected"] = True
                meta["detected_at"] = datetime.utcnow().isoformat()

                # Update in PG
                self._pg_mark_detected(canary_id)

                return meta

        return None

    def get_canaries_for_session(self, fingerprint: str) -> List[Dict[str, Any]]:
        """Get all canaries planted for a given session."""
        canary_ids = self._by_fingerprint.get(fingerprint, [])
        return [self._registry[cid] for cid in canary_ids if cid in self._registry]

    # ── Embedding strategies ──────────────────────────────────────────

    def _embed_canary(self, response: str, canary_id: str, canary_type: str) -> str:
        """Embed canary into response based on type."""
        try:
            if canary_type == "api_key":
                # Embed as a fake API key
                fake_key = f"sk_live_{canary_id}"
                return f"{response}\n# API Key: {fake_key}"

            elif canary_type == "jwt":
                # Embed as a fake JWT fragment
                fake_jwt = f"eyJhbGciOiJIUzI1NiJ9.{canary_id}.fake_signature"
                return f"{response}\n# Token: {fake_jwt}"

            elif canary_type == "sql_dump":
                # Embed as a comment in SQL-like output
                return f"{response}\n-- Backup ID: {canary_id}"

            elif canary_type == "file_path":
                # Embed as a file path reference
                return f"{response}\n# See also: /var/backups/{canary_id}.tar.gz"

            else:
                # Generic: embed as a trace ID in the response
                return f"{response}\n# Trace: {canary_id}"

        except Exception:
            return response

    # ── PostgreSQL persistence (best-effort) ──────────────────────────

    @staticmethod
    def _pg_store_canary(meta: Dict[str, Any]) -> bool:
        """Store canary in PostgreSQL."""
        try:
            from sqlalchemy import create_engine, text

            db_url = os.getenv("DATABASE_URL", "")
            if not db_url:
                pg_user = os.getenv("POSTGRES_USER", "chameleon")
                pg_pass = os.getenv("POSTGRES_PASSWORD", "chameleon123")
                pg_host = os.getenv("POSTGRES_HOST", "localhost")
                pg_port = os.getenv("POSTGRES_PORT", "5432")
                pg_db = os.getenv("POSTGRES_DB", "chameleon_db")
                db_url = f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"

            engine = create_engine(db_url, pool_pre_ping=True, pool_size=1, max_overflow=0)
            with engine.begin() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS canary_registry (
                        canary_id VARCHAR(64) PRIMARY KEY,
                        session_fingerprint VARCHAR(128) NOT NULL,
                        canary_type VARCHAR(32) NOT NULL,
                        planted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        detected BOOLEAN NOT NULL DEFAULT FALSE,
                        detected_at TIMESTAMPTZ
                    )
                """))
                conn.execute(text("""
                    INSERT INTO canary_registry
                        (canary_id, session_fingerprint, canary_type, planted_at)
                    VALUES (:cid, :fp, :ctype, :planted)
                    ON CONFLICT (canary_id) DO NOTHING
                """), {
                    "cid": meta["canary_id"],
                    "fp": meta["session_fingerprint"],
                    "ctype": meta["canary_type"],
                    "planted": meta["planted_at"],
                })
            engine.dispose()
            return True
        except Exception as e:
            logger.debug(f"CanaryTrap: PG store failed (non-fatal): {e}")
            return False

    @staticmethod
    def _pg_mark_detected(canary_id: str) -> bool:
        """Mark canary as detected in PostgreSQL."""
        try:
            from sqlalchemy import create_engine, text

            db_url = os.getenv("DATABASE_URL", "")
            if not db_url:
                pg_user = os.getenv("POSTGRES_USER", "chameleon")
                pg_pass = os.getenv("POSTGRES_PASSWORD", "chameleon123")
                pg_host = os.getenv("POSTGRES_HOST", "localhost")
                pg_port = os.getenv("POSTGRES_PORT", "5432")
                pg_db = os.getenv("POSTGRES_DB", "chameleon_db")
                db_url = f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"

            engine = create_engine(db_url, pool_pre_ping=True, pool_size=1, max_overflow=0)
            with engine.begin() as conn:
                conn.execute(text("""
                    UPDATE canary_registry
                    SET detected = TRUE, detected_at = NOW()
                    WHERE canary_id = :cid
                """), {"cid": canary_id})
            engine.dispose()
            return True
        except Exception as e:
            logger.debug(f"CanaryTrap: PG mark-detected failed (non-fatal): {e}")
            return False


# Global singleton
canary_system = CanaryTrapSystem()
