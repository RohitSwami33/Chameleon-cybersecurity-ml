"""
PostgreSQL Database Connection Module for Chameleon Honeypot System
Async SQLAlchemy with connection pooling and session management

This module provides:
- Async engine creation with connection pooling
- Async session factory
- Dependency injection for FastAPI endpoints
- Database initialization and health checks
"""

import os
import logging
from typing import AsyncGenerator, Optional, List, Dict, Any
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    AsyncAttrs
)
from sqlalchemy.orm import selectinload

from models_sqlalchemy import (
    Base,
    Tenant,
    HoneypotLog,
    ReputationScore,
    AttackType
)

# Configure logging
logger = logging.getLogger(__name__)


class DatabaseSettings:
    """Database connection settings."""
    
    def __init__(self):
        # Connection parameters
        self.POSTGRES_USER: str = os.getenv("POSTGRES_USER", "chameleon")
        self.POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "chameleon123")
        self.POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
        self.POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
        self.POSTGRES_DB: str = os.getenv("POSTGRES_DB", "chameleon_db")
        
        # Connection pool settings
        self.POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))
        self.MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
        self.POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
        self.POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "3600"))
        
        # Echo SQL for debugging (set to True in development)
        self.ECHO_SQL: bool = os.getenv("ECHO_SQL", "false").lower() == "true"
    
    @property
    def database_url(self) -> str:
        """Construct the async PostgreSQL connection URL."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    @property
    def sync_database_url(self) -> str:
        """Construct the sync PostgreSQL connection URL (for Alembic)."""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


# Global settings instance
db_settings = DatabaseSettings()


class Database:
    """
    Database manager class for connection and session handling.
    
    Provides async engine, session factory, and database operations.
    """
    
    engine: Optional[AsyncEngine] = None
    session_factory: Optional[async_sessionmaker[AsyncSession]] = None
    connected: bool = False
    
    async def connect(self) -> None:
        """
        Initialize database connection with connection pooling.
        
        Creates the async engine and session factory.
        """
        try:
            # Create async engine with connection pooling
            self.engine = create_async_engine(
                db_settings.database_url,
                echo=db_settings.ECHO_SQL,
                pool_size=db_settings.POOL_SIZE,
                max_overflow=db_settings.MAX_OVERFLOW,
                pool_timeout=db_settings.POOL_TIMEOUT,
                pool_recycle=db_settings.POOL_RECYCLE,
                pool_pre_ping=True,  # Verify connections before use
            )
            
            # Create session factory
            self.session_factory = async_sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False,
            )
            
            # Test connection
            async with self.engine.connect() as conn:
                await conn.execute(select(1))
            
            self.connected = True
            logger.info("Successfully connected to PostgreSQL database")
            print("Successfully connected to PostgreSQL database")
            
        except Exception as e:
            self.connected = False
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            print(f"Failed to connect to PostgreSQL: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close database connection and dispose of engine."""
        if self.engine:
            await self.engine.dispose()
            self.connected = False
            logger.info("Disconnected from PostgreSQL database")
            print("Disconnected from PostgreSQL database")
    
    async def create_tables(self) -> None:
        """Create all tables in the database."""
        if not self.engine:
            raise RuntimeError("Database not connected")
        
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database tables created successfully")
    
    async def drop_tables(self) -> None:
        """Drop all tables in the database (use with caution!)."""
        if not self.engine:
            raise RuntimeError("Database not connected")
        
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        
        logger.warning("All database tables dropped")


# Global database instance
db = Database()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database session injection.
    
    Yields an async session and ensures proper cleanup.
    
    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    if not db.session_factory:
        raise RuntimeError("Database not initialized. Call db.connect() first.")
    
    async with db.session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for database session (for use outside FastAPI).
    
    Usage:
        async with get_db_context() as session:
            result = await session.execute(select(Tenant))
    """
    if not db.session_factory:
        raise RuntimeError("Database not initialized. Call db.connect() first.")
    
    async with db.session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ============================================================
# Repository Functions for Tenant Operations
# ============================================================

async def create_tenant(
    session: AsyncSession,
    email: str,
    api_key: str,
    credit_balance: int = 1000
) -> Tenant:
    """
    Create a new tenant.
    
    Args:
        session: Database session
        email: Tenant email
        api_key: API key for authentication
        credit_balance: Initial credit balance
    
    Returns:
        Created Tenant instance
    """
    tenant = Tenant(
        email=email,
        api_key=api_key,
        credit_balance=credit_balance
    )
    session.add(tenant)
    await session.flush()
    await session.refresh(tenant)
    return tenant


async def get_tenant_by_api_key(session: AsyncSession, api_key: str) -> Optional[Tenant]:
    """Get tenant by API key."""
    result = await session.execute(
        select(Tenant).where(Tenant.api_key == api_key)
    )
    return result.scalar_one_or_none()


async def get_tenant_by_id(session: AsyncSession, tenant_id: str) -> Optional[Tenant]:
    """Get tenant by ID."""
    result = await session.execute(
        select(Tenant).where(Tenant.id == tenant_id)
    )
    return result.scalar_one_or_none()


async def get_default_tenant(session: AsyncSession) -> Optional[Tenant]:
    """Get the default tenant (first tenant in single-tenant mode)."""
    result = await session.execute(select(Tenant).limit(1))
    return result.scalar_one_or_none()


# ============================================================
# Repository Functions for HoneypotLog Operations
# ============================================================

async def save_honeypot_log(
    session: AsyncSession,
    tenant_id: str,
    attacker_ip: str,
    command_entered: str,
    response_sent: str,
    metadata: Optional[Dict[str, Any]] = None
) -> HoneypotLog:
    """
    Save a honeypot log entry.
    
    Args:
        session: Database session
        tenant_id: UUID of the tenant
        attacker_ip: IP address of the attacker
        command_entered: Command entered by attacker
        response_sent: Deceptive response sent
        metadata: Optional metadata dict
    
    Returns:
        Created HoneypotLog instance
    """
    log = HoneypotLog(
        tenant_id=tenant_id,
        attacker_ip=attacker_ip,
        command_entered=command_entered,
        response_sent=response_sent,
        log_metadata=metadata
    )
    session.add(log)
    await session.flush()
    await session.refresh(log)
    return log


async def get_honeypot_logs(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    tenant_id: Optional[str] = None,
    attacker_ip: Optional[str] = None
) -> List[HoneypotLog]:
    """
    Get honeypot logs with optional filtering.
    
    Args:
        session: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        tenant_id: Optional tenant filter
        attacker_ip: Optional IP filter
    
    Returns:
        List of HoneypotLog instances
    """
    query = select(HoneypotLog).order_by(HoneypotLog.timestamp.desc())
    
    if tenant_id:
        query = query.where(HoneypotLog.tenant_id == tenant_id)
    if attacker_ip:
        query = query.where(HoneypotLog.attacker_ip == attacker_ip)
    
    query = query.offset(skip).limit(limit)
    result = await session.execute(query)
    return result.scalars().all()


async def get_honeypot_log_by_id(
    session: AsyncSession,
    log_id: str
) -> Optional[HoneypotLog]:
    """Get a specific honeypot log by ID."""
    result = await session.execute(
        select(HoneypotLog).where(HoneypotLog.id == log_id)
    )
    return result.scalar_one_or_none()


async def get_logs_by_ip(
    session: AsyncSession,
    ip_address: str,
    limit: int = 100
) -> List[HoneypotLog]:
    """Get all logs for a specific IP address."""
    result = await session.execute(
        select(HoneypotLog)
        .where(HoneypotLog.attacker_ip == ip_address)
        .order_by(HoneypotLog.timestamp.desc())
        .limit(limit)
    )
    return result.scalars().all()


async def count_honeypot_logs(
    session: AsyncSession,
    tenant_id: Optional[str] = None
) -> int:
    """Count total honeypot logs."""
    query = select(func.count(HoneypotLog.id))
    if tenant_id:
        query = query.where(HoneypotLog.tenant_id == tenant_id)
    result = await session.execute(query)
    return result.scalar() or 0


# ============================================================
# Repository Functions for ReputationScore Operations
# ============================================================

async def get_or_create_reputation_score(
    session: AsyncSession,
    ip_address: str,
    initial_score: int = 100
) -> ReputationScore:
    """
    Get existing reputation score or create a new one.
    
    Args:
        session: Database session
        ip_address: IP address to look up
        initial_score: Initial reputation score for new entries
    
    Returns:
        ReputationScore instance
    """
    result = await session.execute(
        select(ReputationScore).where(ReputationScore.ip_address == ip_address)
    )
    score = result.scalar_one_or_none()
    
    if not score:
        score = ReputationScore(
            ip_address=ip_address,
            reputation_score=initial_score
        )
        session.add(score)
        await session.flush()
        await session.refresh(score)
    
    return score


async def update_reputation_score(
    session: AsyncSession,
    ip_address: str,
    score_delta: int = -10,
    attack_type: Optional[str] = None,
    merkle_root: Optional[str] = None
) -> ReputationScore:
    """
    Update reputation score for an IP address.
    
    Args:
        session: Database session
        ip_address: IP address to update
        score_delta: Amount to change score (negative for malicious)
        attack_type: Optional attack type to record
        merkle_root: Optional Merkle root for integrity
    
    Returns:
        Updated ReputationScore instance
    """
    score = await get_or_create_reputation_score(session, ip_address)
    
    # Update score
    score.reputation_score = max(0, min(100, score.reputation_score + score_delta))
    score.attack_count += 1
    
    # Update attack type breakdown
    if attack_type:
        if not score.attack_types:
            score.attack_types = {}
        score.attack_types[attack_type] = score.attack_types.get(attack_type, 0) + 1
    
    # Update Merkle root
    if merkle_root:
        score.merkle_root = merkle_root
    
    score.last_updated = datetime.utcnow()
    
    await session.flush()
    await session.refresh(score)
    return score


async def get_flagged_ips(
    session: AsyncSession,
    threshold: int = 50,
    limit: int = 100
) -> List[ReputationScore]:
    """
    Get IPs with reputation score below threshold.
    
    Args:
        session: Database session
        threshold: Maximum reputation score to include
        limit: Maximum number of results
    
    Returns:
        List of ReputationScore instances
    """
    result = await session.execute(
        select(ReputationScore)
        .where(ReputationScore.reputation_score < threshold)
        .order_by(ReputationScore.reputation_score.asc())
        .limit(limit)
    )
    return result.scalars().all()


async def get_top_threats(
    session: AsyncSession,
    limit: int = 10
) -> List[ReputationScore]:
    """
    Get top threat IPs (lowest reputation scores).
    
    Args:
        session: Database session
        limit: Maximum number of results
    
    Returns:
        List of ReputationScore instances
    """
    result = await session.execute(
        select(ReputationScore)
        .where(ReputationScore.attack_count > 0)
        .order_by(ReputationScore.reputation_score.asc())
        .limit(limit)
    )
    return result.scalars().all()


# ============================================================
# Dashboard Statistics Functions
# ============================================================

async def get_dashboard_stats(session: AsyncSession) -> Dict[str, Any]:
    """
    Get comprehensive dashboard statistics.
    
    Returns:
        Dictionary with attack statistics, top attackers, and geo data
    """
    # Total counts
    total_logs = await count_honeypot_logs(session)
    
    # Get recent logs for analysis
    recent_logs = await get_honeypot_logs(session, limit=1000)
    
    # Count malicious vs benign (based on metadata classification)
    malicious_count = 0
    benign_count = 0
    attack_distribution: Dict[str, int] = {}
    attacker_counts: Dict[str, int] = {}
    geo_locations: List[Dict[str, Any]] = []
    
    for log in recent_logs:
        # Extract classification from metadata
        metadata = log.log_metadata or {}
        classification = metadata.get("classification", {})
        is_malicious = classification.get("is_malicious", False)
        attack_type = classification.get("attack_type", "UNKNOWN")
        
        if is_malicious:
            malicious_count += 1
            attack_distribution[attack_type] = attack_distribution.get(attack_type, 0) + 1
        else:
            benign_count += 1
        
        # Count attacks per IP
        attacker_counts[log.attacker_ip] = attacker_counts.get(log.attacker_ip, 0) + 1
        
        # Extract geo data
        geo = metadata.get("geo_location")
        if geo and geo.get("country"):
            geo_locations.append({
                "country": geo.get("country"),
                "city": geo.get("city"),
                "latitude": geo.get("latitude"),
                "longitude": geo.get("longitude"),
                "count": 1
            })
    
    # Top attackers
    top_attackers = [
        {"ip": ip, "count": count}
        for ip, count in sorted(
            attacker_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
    ]
    
    # Get flagged IPs count
    flagged = await get_flagged_ips(session, threshold=50, limit=1000)
    
    # Get top threats
    top_threats = await get_top_threats(session, limit=5)
    
    return {
        "total_attempts": total_logs,
        "malicious_attempts": malicious_count,
        "benign_attempts": benign_count,
        "attack_distribution": attack_distribution,
        "top_attackers": top_attackers,
        "geo_locations": geo_locations[:50],
        "flagged_ips_count": len(flagged),
        "top_threats": [
            {
                "ip": t.ip_address,
                "score": t.reputation_score,
                "attack_count": t.attack_count
            }
            for t in top_threats
        ]
    }


# ============================================================
# Database Initialization
# ============================================================

async def init_database() -> None:
    """
    Initialize database connection and create tables.
    
    This should be called during application startup.
    """
    await db.connect()
    await db.create_tables()
    
    # Create default tenant if not exists (for single-tenant mode)
    async with get_db_context() as session:
        existing = await get_default_tenant(session)
        if not existing:
            import secrets
            default_api_key = secrets.token_hex(32)
            await create_tenant(
                session,
                email="admin@chameleon.local",
                api_key=default_api_key,
                credit_balance=10000
            )
            logger.info(f"Created default tenant with API key: {default_api_key[:16]}...")
            print(f"Created default tenant with API key: {default_api_key[:16]}...")


async def close_database() -> None:
    """Close database connection during application shutdown."""
    await db.disconnect()