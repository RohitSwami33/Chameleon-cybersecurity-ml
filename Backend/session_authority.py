"""
SingleSourceSessionAuthority — HMAC-Seeded Deterministic Session Ledger
=======================================================================

PostgreSQL-backed session authority that replaces the in-memory _session_store dict.
All session fields are deterministically derived from HMAC-SHA256(SECRET, fingerprint).
Stage advances are wrapped in DB transactions with per-fingerprint threading locks.
Every state mutation appends an HMAC-signed entry to a session_audit_log table.

Fallback: If PostgreSQL is unreachable, degrades to in-memory dict for that request.
"""

import hashlib
import hmac
import json
import logging
import os
import threading
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# ── Environment ──────────────────────────────────────────────────────────
SESSION_SECRET = os.getenv("SESSION_SECRET", "chameleon-default-session-secret-change-me")
DATABASE_URL = os.getenv("DATABASE_URL", "")

# ── Deterministic field derivation ────────────────────────────────────────

_DB_TYPES = ["MySQL", "PostgreSQL", "SQLite", "MariaDB"]
_TABLE_NAMES = [
    "users", "admin", "accounts", "members", "customers",
    "login", "user_data", "profiles", "sessions", "auth",
]
_COLUMN_NAMES = [
    "password", "passwd", "pwd", "pass", "username", "user",
    "email", "id", "admin", "role", "token", "hash", "salt",
]


def _hmac_digest(key: str, data: str) -> str:
    """Compute HMAC-SHA256 hex digest."""
    return hmac.new(key.encode(), data.encode(), hashlib.sha256).hexdigest()


def compute_deterministic_fields(fingerprint: str) -> Dict[str, Any]:
    """
    Derive session fields deterministically from the fingerprint.

    Uses HMAC-SHA256(SESSION_SECRET, fingerprint) to produce a digest,
    then slices it to select db_type, table_name, and columns.
    """
    digest = _hmac_digest(SESSION_SECRET, fingerprint)
    # Use different sections of the hash for each field
    db_index = int(digest[:8], 16) % len(_DB_TYPES)
    table_index = int(digest[8:16], 16) % len(_TABLE_NAMES)
    col_index = int(digest[16:24], 16) % len(_COLUMN_NAMES)

    return {
        "db_type": _DB_TYPES[db_index],
        "table_name": _TABLE_NAMES[table_index],
        "column_name": _COLUMN_NAMES[col_index],
    }


def sign_state(session_data: dict) -> str:
    """Create HMAC-SHA256 signature of session state for audit log."""
    canonical = json.dumps(session_data, sort_keys=True, default=str)
    return _hmac_digest(SESSION_SECRET, canonical)


# ── Per-fingerprint lock registry ─────────────────────────────────────────

class _LockRegistry:
    """Thread-safe per-fingerprint lock manager."""

    def __init__(self):
        self._locks: Dict[str, threading.Lock] = {}
        self._master = threading.Lock()

    def get(self, fingerprint: str) -> threading.Lock:
        with self._master:
            if fingerprint not in self._locks:
                self._locks[fingerprint] = threading.Lock()
            return self._locks[fingerprint]


_lock_registry = _LockRegistry()


# ── In-memory fallback store ─────────────────────────────────────────────

_fallback_store: Dict[str, Dict[str, Any]] = {}


# ── SingleSourceSessionAuthority ──────────────────────────────────────────

class SingleSourceSessionAuthority:
    """
    Centralised session authority.

    Primary: PostgreSQL (via SQLAlchemy async session from database_postgres).
    Fallback: In-memory dict when DB is unavailable.

    All public methods are synchronous so they can be called from both sync
    and async contexts. The caller (attacker_session.py) wraps them as needed.
    """

    # ── PostgreSQL helpers (lazy import to avoid circular imports) ──────

    @staticmethod
    def _get_pg_session_data(fingerprint: str) -> Optional[Dict[str, Any]]:
        """
        Synchronous best-effort fetch from PostgreSQL via a new connection.

        Returns None if DB is unavailable or session not found.
        """
        try:
            from sqlalchemy import create_engine, text

            db_url = DATABASE_URL
            if not db_url:
                # Build from individual settings
                pg_user = os.getenv("POSTGRES_USER", "chameleon")
                pg_pass = os.getenv("POSTGRES_PASSWORD", "chameleon123")
                pg_host = os.getenv("POSTGRES_HOST", "localhost")
                pg_port = os.getenv("POSTGRES_PORT", "5432")
                pg_db = os.getenv("POSTGRES_DB", "chameleon_db")
                db_url = f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"

            engine = create_engine(db_url, pool_pre_ping=True, pool_size=1, max_overflow=0)

            # Ensure session_ledger table exists
            with engine.begin() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS session_ledger (
                        fingerprint VARCHAR(128) PRIMARY KEY,
                        db_type VARCHAR(32) NOT NULL,
                        table_name VARCHAR(64) NOT NULL,
                        column_name VARCHAR(64) NOT NULL,
                        current_stage INTEGER NOT NULL DEFAULT 1,
                        attack_type VARCHAR(32),
                        attempt_count INTEGER NOT NULL DEFAULT 0,
                        first_seen TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        last_seen TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        session_data JSONB DEFAULT '{}'
                    )
                """))
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS session_audit_log (
                        id SERIAL PRIMARY KEY,
                        fingerprint VARCHAR(128) NOT NULL,
                        action VARCHAR(64) NOT NULL,
                        old_state JSONB,
                        new_state JSONB,
                        hmac_signature VARCHAR(128) NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                """))

            with engine.connect() as conn:
                row = conn.execute(
                    text("SELECT * FROM session_ledger WHERE fingerprint = :fp"),
                    {"fp": fingerprint},
                ).mappings().first()

                if row:
                    return dict(row)
            engine.dispose()
            return None
        except Exception as e:
            logger.debug(f"SessionAuthority: PG fetch failed (non-fatal): {e}")
            return None

    @staticmethod
    def _pg_upsert(fingerprint: str, data: Dict[str, Any]) -> bool:
        """Upsert session into PostgreSQL. Returns True on success."""
        try:
            from sqlalchemy import create_engine, text

            db_url = DATABASE_URL
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
                    INSERT INTO session_ledger
                        (fingerprint, db_type, table_name, column_name, current_stage,
                         attack_type, attempt_count, last_seen, session_data)
                    VALUES
                        (:fp, :db_type, :table_name, :column_name, :stage,
                         :attack_type, :attempts, NOW(), :sdata)
                    ON CONFLICT (fingerprint) DO UPDATE SET
                        current_stage = :stage,
                        attack_type = :attack_type,
                        attempt_count = :attempts,
                        last_seen = NOW(),
                        session_data = :sdata
                """), {
                    "fp": fingerprint,
                    "db_type": data.get("db_type", "MySQL"),
                    "table_name": data.get("table_name", "users"),
                    "column_name": data.get("column_name", "password"),
                    "stage": data.get("current_stage", 1),
                    "attack_type": data.get("attack_type"),
                    "attempts": data.get("attempt_count", 0),
                    "sdata": json.dumps(data.get("session_data", {})),
                })
            engine.dispose()
            return True
        except Exception as e:
            logger.debug(f"SessionAuthority: PG upsert failed (non-fatal): {e}")
            return False

    @staticmethod
    def _pg_append_audit(fingerprint: str, action: str,
                         old_state: dict, new_state: dict) -> bool:
        """Append HMAC-signed entry to session_audit_log."""
        try:
            from sqlalchemy import create_engine, text

            db_url = DATABASE_URL
            if not db_url:
                pg_user = os.getenv("POSTGRES_USER", "chameleon")
                pg_pass = os.getenv("POSTGRES_PASSWORD", "chameleon123")
                pg_host = os.getenv("POSTGRES_HOST", "localhost")
                pg_port = os.getenv("POSTGRES_PORT", "5432")
                pg_db = os.getenv("POSTGRES_DB", "chameleon_db")
                db_url = f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"

            sig = sign_state({"fingerprint": fingerprint, "action": action, "new": new_state})
            engine = create_engine(db_url, pool_pre_ping=True, pool_size=1, max_overflow=0)
            with engine.begin() as conn:
                conn.execute(text("""
                    INSERT INTO session_audit_log
                        (fingerprint, action, old_state, new_state, hmac_signature)
                    VALUES (:fp, :action, :old, :new, :sig)
                """), {
                    "fp": fingerprint,
                    "action": action,
                    "old": json.dumps(old_state, default=str),
                    "new": json.dumps(new_state, default=str),
                    "sig": sig,
                })
            engine.dispose()
            return True
        except Exception as e:
            logger.debug(f"SessionAuthority: audit log failed (non-fatal): {e}")
            return False

    # ── Public API ─────────────────────────────────────────────────────

    @classmethod
    def get_or_create(cls, fingerprint: str, attack_type: str = None) -> Dict[str, Any]:
        """
        Load session from PostgreSQL first; fall back to creating a new one.
        Returns a plain dict with all session fields.
        """
        lock = _lock_registry.get(fingerprint)
        with lock:
            # Try PostgreSQL first
            pg_data = cls._get_pg_session_data(fingerprint)
            if pg_data is not None:
                # Also cache in fallback store
                _fallback_store[fingerprint] = pg_data
                return pg_data

            # Check in-memory fallback
            if fingerprint in _fallback_store:
                return _fallback_store[fingerprint]

            # Create new session with deterministic fields
            fields = compute_deterministic_fields(fingerprint)
            session_data = {
                "fingerprint": fingerprint,
                "db_type": fields["db_type"],
                "table_name": fields["table_name"],
                "column_name": fields["column_name"],
                "current_stage": 1,
                "attack_type": attack_type,
                "attempt_count": 0,
                "first_seen": datetime.utcnow().isoformat(),
                "last_seen": datetime.utcnow().isoformat(),
                "session_data": {},
            }

            # Persist to PostgreSQL (best-effort)
            cls._pg_upsert(fingerprint, session_data)

            # Audit
            cls._pg_append_audit(fingerprint, "SESSION_CREATED", {}, session_data)

            # Always cache locally
            _fallback_store[fingerprint] = session_data
            logger.info(f"SessionAuthority: Created new session for {fingerprint[:12]}...")
            return session_data

    @classmethod
    def get_session(cls, fingerprint: str) -> Optional[Dict[str, Any]]:
        """Get session by fingerprint. Returns None if not found."""
        lock = _lock_registry.get(fingerprint)
        with lock:
            pg_data = cls._get_pg_session_data(fingerprint)
            if pg_data is not None:
                _fallback_store[fingerprint] = pg_data
                return pg_data
            return _fallback_store.get(fingerprint)

    @classmethod
    def advance_stage(cls, fingerprint: str, max_stage: int = 4) -> int:
        """
        Advance session stage within a locked transaction.
        Returns the new stage number.
        """
        lock = _lock_registry.get(fingerprint)
        with lock:
            session = _fallback_store.get(fingerprint)
            if not session:
                session = cls._get_pg_session_data(fingerprint)
            if not session:
                return 1

            old_stage = session.get("current_stage", 1)
            new_stage = min(old_stage + 1, max_stage)

            old_state = {"current_stage": old_stage}
            session["current_stage"] = new_stage
            session["last_seen"] = datetime.utcnow().isoformat()
            new_state = {"current_stage": new_stage}

            # Persist
            cls._pg_upsert(fingerprint, session)
            cls._pg_append_audit(fingerprint, "STAGE_ADVANCE", old_state, new_state)

            _fallback_store[fingerprint] = session
            return new_stage

    @classmethod
    def update_session(cls, fingerprint: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update arbitrary session fields."""
        lock = _lock_registry.get(fingerprint)
        with lock:
            session = _fallback_store.get(fingerprint)
            if not session:
                session = cls._get_pg_session_data(fingerprint) or {}

            old_state = dict(session)
            session.update(updates)
            session["last_seen"] = datetime.utcnow().isoformat()

            cls._pg_upsert(fingerprint, session)
            cls._pg_append_audit(fingerprint, "SESSION_UPDATE", old_state, session)

            _fallback_store[fingerprint] = session
            return session

    @classmethod
    def get_all_sessions(cls) -> Dict[str, Dict[str, Any]]:
        """Return all cached sessions (for stats)."""
        return dict(_fallback_store)
