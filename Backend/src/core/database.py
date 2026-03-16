"""
Database layer — reads from PostgreSQL via database_postgres.py.

Every dashboard endpoint (get_attack_logs, get_dashboard_stats …) now queries
the real `honeypot_logs` table instead of falling back to mock_database.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy import select, func, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from database_postgres import db              # singleton Database instance
from models_sqlalchemy import HoneypotLog

logger = logging.getLogger(__name__)

# ── helpers ──────────────────────────────────────────────────────────

def _row_to_dashboard_dict(row: HoneypotLog) -> dict:
    """
    Convert a HoneypotLog ORM row → dict matching the AttackLog
    Pydantic model the frontend expects.
    """
    meta = row.log_metadata or {}

    classification = meta.get("classification")
    if not classification:
        classification = {
            "attack_type": "BENIGN",
            "confidence": 0.0,
            "is_malicious": False,
        }

    deception_response = meta.get("deception_response")
    if not deception_response:
        deception_response = {
            "message": row.response_sent or "",
            "delay_applied": 0.0,
            "http_status": 200,
        }

    geo_location = meta.get("geo_location")

    return {
        "id": str(row.id),
        "timestamp": row.timestamp,
        "raw_input": row.command_entered or "",
        "ip_address": row.attacker_ip,
        "user_agent": meta.get("user_agent", ""),
        "geo_location": geo_location,
        "classification": classification,
        "deception_response": deception_response,
    }


# ── CRUD used by main.py endpoints ──────────────────────────────────

async def save_attack_log(log_data: dict) -> str:
    """Save an attack log dict into PostgreSQL honeypot_logs."""
    if not db.connected or not db.session_factory:
        logger.warning("PostgreSQL not connected — cannot save attack log")
        return ""

    try:
        from database_postgres import get_default_tenant
        from threat_score import threat_score_system

        # Update the blockchain/threat score before saving to DB
        ip_addr = log_data.get("ip_address", "0.0.0.0")
        classification_data = log_data.get("classification", {})
        attack_type = classification_data.get("attack_type", "UNKNOWN")
        is_malicious = classification_data.get("is_malicious", False)
        threat_score_system.calculate_threat_score(ip_addr, attack_type, is_malicious)

        async with db.session_factory() as session:
            tenant_id = log_data.get("tenant_id")
            if not tenant_id:
                tenant = await get_default_tenant(session)
                tenant_id = str(tenant.id) if tenant else str(uuid4())
                
        # Parse timestamp if it's a string
        ts = log_data.get("timestamp", datetime.utcnow())
        if isinstance(ts, str):
            try:
                # Handle possible 'Z' suffix or other iso formats
                ts = datetime.fromisoformat(ts.replace('Z', '+00:00'))
            except:
                ts = datetime.utcnow()
                
        async with db.session_factory() as session:
            tenant_id = log_data.get("tenant_id")
            if not tenant_id:
                tenant = await get_default_tenant(session)
                tenant_id = str(tenant.id) if tenant else str(uuid4())
                
            row = HoneypotLog(
                id=uuid4(),
                tenant_id=tenant_id,
                attacker_ip=ip_addr,
                command_entered=log_data.get("raw_input", ""),
                response_sent=log_data.get("deception_response", {}).get("message", ""),
                timestamp=ts,
                log_metadata={
                    "classification": classification_data,
                    "deception_response": log_data.get("deception_response"),
                    "geo_location": log_data.get("geo_location"),
                    "user_agent": log_data.get("user_agent", ""),
                },
            )
            session.add(row)
            await session.commit()
            return str(row.id)
    except Exception as e:
        logger.error(f"Error saving attack log: {e}")
        return ""


async def get_attack_logs(skip: int = 0, limit: int = 50) -> List[dict]:
    """Return paginated attack logs from PostgreSQL (newest first)."""
    if not db.connected or not db.session_factory:
        logger.warning("PostgreSQL not connected — returning empty logs")
        return []

    try:
        async with db.session_factory() as session:
            stmt = (
                select(HoneypotLog)
                .order_by(desc(HoneypotLog.timestamp))
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            rows = result.scalars().all()
            return [_row_to_dashboard_dict(r) for r in rows]
    except Exception as e:
        logger.error(f"Error fetching attack logs: {e}")
        return []


async def get_attack_by_id(log_id: str) -> Optional[dict]:
    """Get a single attack log by UUID."""
    if not db.connected or not db.session_factory:
        return None

    try:
        from uuid import UUID as _UUID
        async with db.session_factory() as session:
            stmt = select(HoneypotLog).where(HoneypotLog.id == _UUID(log_id))
            result = await session.execute(stmt)
            row = result.scalar_one_or_none()
            return _row_to_dashboard_dict(row) if row else None
    except Exception as e:
        logger.error(f"Error fetching attack by ID: {e}")
        return None


async def get_dashboard_stats() -> dict:
    """Compute live dashboard statistics from PostgreSQL."""
    empty = {
        "total_attempts": 0,
        "malicious_attempts": 0,
        "benign_attempts": 0,
        "attack_distribution": {},
        "top_attackers": [],
        "geo_locations": [],
    }

    if not db.connected or not db.session_factory:
        return empty

    try:
        async with db.session_factory() as session:
            # Total rows
            total = (await session.execute(
                select(func.count()).select_from(HoneypotLog)
            )).scalar() or 0

            # Fetch all rows (small dataset) to compute stats from metadata
            stmt = select(HoneypotLog).order_by(desc(HoneypotLog.timestamp))
            result = await session.execute(stmt)
            rows = result.scalars().all()

            malicious = 0
            benign = 0
            attack_dist: Dict[str, int] = {}
            ip_counts: Dict[str, int] = {}
            ip_last_seen: Dict[str, datetime] = {}
            geo_counts: Dict[str, dict] = {}

            for row in rows:
                meta = row.log_metadata or {}
                classification = meta.get("classification", {})
                attack_type = classification.get("attack_type", "BENIGN")
                is_mal = classification.get("is_malicious", False)

                if is_mal:
                    malicious += 1
                else:
                    benign += 1

                attack_dist[attack_type] = attack_dist.get(attack_type, 0) + 1

                # Top attackers
                if is_mal:
                    ip = row.attacker_ip
                    ip_counts[ip] = ip_counts.get(ip, 0) + 1
                    if ip not in ip_last_seen or row.timestamp > ip_last_seen[ip]:
                        ip_last_seen[ip] = row.timestamp

                # Geo
                geo = meta.get("geo_location")
                if geo and is_mal:
                    key = f"{geo.get('country', '')}_{geo.get('city', '')}"
                    if key not in geo_counts:
                        geo_counts[key] = {
                            "country": geo.get("country"),
                            "city": geo.get("city"),
                            "latitude": geo.get("latitude"),
                            "longitude": geo.get("longitude"),
                            "count": 0,
                        }
                    geo_counts[key]["count"] += 1

            top_attackers = sorted(
                [{"ip": ip, "count": c, "last_seen": ip_last_seen[ip]}
                 for ip, c in ip_counts.items()],
                key=lambda x: x["count"], reverse=True
            )[:10]

            geo_locations = sorted(
                geo_counts.values(), key=lambda x: x["count"], reverse=True
            )[:50]

            return {
                "total_attempts": total,
                "malicious_attempts": malicious,
                "benign_attempts": benign,
                "attack_distribution": attack_dist,
                "top_attackers": top_attackers,
                "geo_locations": geo_locations,
            }

    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {e}")
        return empty


async def get_logs_by_ip(ip_address: str) -> List[dict]:
    """Get all logs for a specific IP address."""
    if not db.connected or not db.session_factory:
        return []

    try:
        async with db.session_factory() as session:
            stmt = (
                select(HoneypotLog)
                .where(HoneypotLog.attacker_ip == ip_address)
                .order_by(desc(HoneypotLog.timestamp))
            )
            result = await session.execute(stmt)
            rows = result.scalars().all()
            return [_row_to_dashboard_dict(r) for r in rows]
    except Exception as e:
        logger.error(f"Error fetching logs by IP: {e}")
        return []


# ── Legacy MongoDB stubs (no-op) ────────────────────────────────────

async def connect_to_mongo():
    """No-op — we use PostgreSQL now."""
    logger.info("MongoDB disabled — using PostgreSQL for all data")

async def close_mongo_connection():
    """No-op."""
    pass
