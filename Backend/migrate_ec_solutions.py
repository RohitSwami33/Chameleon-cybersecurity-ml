#!/usr/bin/env python3
"""
Chameleon EC Solutions Database Migration Runner
=================================================
Execute database migrations for the EC security hardening fixes.

Usage:
    python migrate_ec_solutions.py

Prerequisites:
    - PostgreSQL must be running
    - Environment variables must be set (POSTGRES_USER, POSTGRES_PASSWORD, etc.)
    - Or .env file must exist with database configuration
"""
import asyncio
import sys
from sqlalchemy import text

# Add Backend to path
sys.path.insert(0, '.')

from src.core.database_postgres import db


MIGRATIONS = [
    # (EC Number, Description, SQL)
    (
        "EC-005",
        "Resize user_agent column to VARCHAR(512)",
        "ALTER TABLE beacon_events ALTER COLUMN user_agent TYPE VARCHAR(512)"
    ),
    (
        "EC-019",
        "Add NaN check constraint on reputation_score",
        "ALTER TABLE reputation_scores ADD CONSTRAINT IF NOT EXISTS reputation_score_valid "
        "CHECK (reputation_score >= 0 AND reputation_score <= 100)"
    ),
    (
        "EC-024",
        "Add covering index for timestamp queries",
        "CREATE INDEX IF NOT EXISTS idx_honeypot_logs_timestamp_desc "
        "ON honeypot_logs(timestamp DESC)"
    ),
    (
        "EC-024",
        "Add covering index for IP queries",
        "CREATE INDEX IF NOT EXISTS idx_honeypot_logs_attacker_ip "
        "ON honeypot_logs(attacker_ip)"
    ),
    (
        "EC-024",
        "Add composite index for tenant queries",
        "CREATE INDEX IF NOT EXISTS idx_honeypot_logs_tenant_timestamp "
        "ON honeypot_logs(tenant_id, timestamp DESC)"
    ),
    (
        "EC-038",
        "Add index for tenant email lookups",
        "CREATE INDEX IF NOT EXISTS idx_tenants_email ON tenants(email)"
    ),
    (
        "EC-038",
        "Add index for API key lookups",
        "CREATE INDEX IF NOT EXISTS idx_tenants_api_key ON tenants(api_key)"
    ),
    (
        "EC-040",
        "Add index for beacon session queries",
        "CREATE INDEX IF NOT EXISTS idx_beacon_events_session "
        "ON beacon_events(session_id, triggered_at DESC)"
    ),
]


async def run_migrations():
    """Execute all EC solution migrations."""
    print("=" * 60)
    print("Chameleon EC Solutions Database Migrations")
    print("=" * 60)
    
    # Connect to database
    try:
        print("\nConnecting to database...")
        await db.connect()
        print("✓ Connected successfully")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        print("\nEnsure PostgreSQL is running and environment variables are set:")
        print("  - POSTGRES_USER")
        print("  - POSTGRES_PASSWORD")
        print("  - POSTGRES_HOST")
        print("  - POSTGRES_PORT")
        print("  - POSTGRES_DB")
        return False
    
    success_count = 0
    skip_count = 0
    error_count = 0
    
    async with db.engine.begin() as conn:
        for ec_num, description, sql in MIGRATIONS:
            try:
                await conn.execute(text(sql))
                print(f"✓ {ec_num}: {description}")
                success_count += 1
            except Exception as e:
                error_msg = str(e)[:60]
                if "already exists" in error_msg.lower() or "if not exists" in sql.lower():
                    print(f"○ {ec_num}: {description} (already exists)")
                    skip_count += 1
                else:
                    print(f"✗ {ec_num}: {description} - {error_msg}")
                    error_count += 1
        
        await conn.commit()
    
    await db.disconnect()
    
    print("\n" + "=" * 60)
    print(f"Results: {success_count} applied, {skip_count} skipped, {error_count} errors")
    print("=" * 60)
    
    if error_count == 0:
        print("\n✓ MIGRATIONS COMPLETE")
        return True
    else:
        print(f"\n✗ MIGRATIONS FAILED ({error_count} errors)")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_migrations())
    sys.exit(0 if success else 1)
