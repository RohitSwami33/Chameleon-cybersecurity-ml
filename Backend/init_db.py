"""
Database Initializer — Create all tables in PostgreSQL
=======================================================

Creates the following tables (idempotent — safe to run multiple times):
  • tenants
  • honeypot_logs       (+ is_exfiltration_attempt column)
  • reputation_scores
  • beacon_events       (NEW — honeytoken telemetry)

Usage:
    python init_db.py
"""

import asyncio
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


async def init():
    """Connect to PostgreSQL and create all SQLAlchemy tables."""
    from database_postgres import db

    logger.info("Connecting to PostgreSQL...")
    await db.connect()

    logger.info("Creating tables (if not exist)...")
    await db.create_tables()

    # Verify critical tables
    from sqlalchemy import inspect, text
    async with db.engine.connect() as conn:
        def _check(connection):
            inspector = inspect(connection)
            tables = inspector.get_table_names()
            return tables

        tables = await conn.run_sync(_check)

    expected = ["tenants", "honeypot_logs", "reputation_scores", "beacon_events"]
    missing = [t for t in expected if t not in tables]

    if missing:
        logger.error("❌ Missing tables: %s", missing)
        sys.exit(1)
    else:
        logger.info("✅ All tables verified: %s", expected)

    # Check is_exfiltration_attempt column on honeypot_logs
    async with db.engine.connect() as conn:
        def _check_column(connection):
            inspector = inspect(connection)
            columns = [c["name"] for c in inspector.get_columns("honeypot_logs")]
            return columns

        cols = await conn.run_sync(_check_column)

    if "is_exfiltration_attempt" in cols:
        logger.info("✅ honeypot_logs.is_exfiltration_attempt column present")
    else:
        logger.error("❌ honeypot_logs.is_exfiltration_attempt column MISSING")
        sys.exit(1)

    # Check beacon_events columns
    async with db.engine.connect() as conn:
        def _check_beacon(connection):
            inspector = inspect(connection)
            return [c["name"] for c in inspector.get_columns("beacon_events")]

        beacon_cols = await conn.run_sync(_check_beacon)

    required_beacon = ["id", "session_id", "source_ip", "user_agent", "triggered_at"]
    missing_beacon = [c for c in required_beacon if c not in beacon_cols]
    if missing_beacon:
        logger.error("❌ beacon_events missing columns: %s", missing_beacon)
        sys.exit(1)
    else:
        logger.info("✅ beacon_events columns verified: %s", beacon_cols)

    await db.disconnect()
    logger.info("🎉 Database initialization complete!")


if __name__ == "__main__":
    asyncio.run(init())
