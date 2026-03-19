"""
SQLAlchemy ORM Models for Chameleon Honeypot System
PostgreSQL Database Schema with Async Support

This module defines the database models for:
- Tenants: Multi-tenant API key management (simplified for single-tenant)
- HoneypotLogs: Attack logs with command/response tracking
- ReputationScores: IP reputation with Merkle Tree integrity
- BeaconEvents: Honeytoken exfiltration tracking (Canary Trap)
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import (
    String, Integer, Text, DateTime, Boolean, ForeignKey, Index, func
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class Tenant(Base):
    """
    Tenant model for API key management and credit tracking.
    
    In single-tenant mode, a default tenant is created on initialization.
    """
    __tablename__ = "tenants"
    
    # Primary key - UUID for distributed systems compatibility
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True
    )
    
    # API key for authentication (SHA-256 hashed in production)
    api_key: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
        comment="API key for tenant authentication"
    )
    
    # Contact email
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Tenant contact email"
    )
    
    # Credit balance for rate limiting/billing
    credit_balance: Mapped[int] = mapped_column(
        Integer,
        default=1000,
        nullable=False,
        comment="Available API credits"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationship to honeypot logs
    logs: Mapped[List["HoneypotLog"]] = relationship(
        "HoneypotLog",
        back_populates="tenant",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Tenant(id={self.id}, email={self.email})>"


class HoneypotLog(Base):
    """
    Honeypot log model for tracking attacker interactions.
    
    Stores command entered by attacker, deceptive response sent,
    and metadata including headers, fingerprints, and session info.
    """
    __tablename__ = "honeypot_logs"
    
    # Primary key
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True
    )
    
    # Foreign key to tenant
    tenant_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to tenant"
    )
    
    # Attacker information
    attacker_ip: Mapped[str] = mapped_column(
        String(45),  # IPv6 max length
        nullable=False,
        index=True,
        comment="Attacker's IP address (IPv4 or IPv6)"
    )
    
    # Command and response
    command_entered: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Command entered by attacker"
    )
    response_sent: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Deceptive response sent to attacker"
    )
    
    # Timestamp with index for time-based queries
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
        comment="When the attack was logged"
    )
    
    # JSONB for flexible metadata storage
    # Note: Python attribute is 'log_metadata' because 'metadata' is reserved by SQLAlchemy DeclarativeBase.
    # The actual database column is still named 'metadata'.
    log_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        "metadata",
        JSONB,
        nullable=True,
        comment="Additional metadata: headers, fingerprints, session info"
    )
    
    # Honeytoken exfiltration flag
    is_exfiltration_attempt: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        nullable=False,
        comment="True if this interaction triggered a honeytoken beacon"
    )
    
    # Relationship to tenant
    tenant: Mapped["Tenant"] = relationship(
        "Tenant",
        back_populates="logs"
    )
    
    # Composite indexes for common queries
    __table_args__ = (
        Index('ix_honeypot_logs_tenant_timestamp', 'tenant_id', 'timestamp'),
        Index('ix_honeypot_logs_ip_timestamp', 'attacker_ip', 'timestamp'),
    )
    
    def __repr__(self) -> str:
        return f"<HoneypotLog(id={self.id}, ip={self.attacker_ip})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for API responses."""
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "attacker_ip": self.attacker_ip,
            "command_entered": self.command_entered,
            "response_sent": self.response_sent,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "metadata": self.log_metadata
        }


class ReputationScore(Base):
    """
    Reputation score model for IP address tracking.
    
    Stores reputation scores, behavior hashes, and Merkle Tree roots
    for tamper-proof log integrity verification.
    """
    __tablename__ = "reputation_scores"
    
    # Primary key - IP address
    ip_address: Mapped[str] = mapped_column(
        String(45),  # IPv6 max length
        primary_key=True,
        comment="IP address (IPv4 or IPv6)"
    )
    
    # Reputation score (0-100, lower = more malicious)
    reputation_score: Mapped[int] = mapped_column(
        Integer,
        default=100,
        nullable=False,
        comment="Reputation score (0-100, lower = more malicious)"
    )
    
    # Hash of attacker's behavior pattern
    behavior_hash: Mapped[Optional[str]] = mapped_column(
        String(64),  # SHA-256 hex digest length
        nullable=True,
        comment="SHA-256 hash of attacker behavior pattern"
    )
    
    # Merkle root for log integrity
    merkle_root: Mapped[Optional[str]] = mapped_column(
        String(64),  # SHA-256 hex digest length
        nullable=True,
        comment="Merkle Tree root hash for log integrity verification"
    )
    
    # Timestamps
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Last time this record was updated"
    )
    
    # Additional data as JSONB
    attack_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Total number of attacks from this IP"
    )
    
    attack_types: Mapped[Optional[Dict[str, int]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Breakdown of attack types observed"
    )
    
    def __repr__(self) -> str:
        return f"<ReputationScore(ip={self.ip_address}, score={self.reputation_score})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for API responses."""
        return {
            "ip_address": self.ip_address,
            "reputation_score": self.reputation_score,
            "behavior_hash": self.behavior_hash,
            "merkle_root": self.merkle_root,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "attack_count": self.attack_count,
            "attack_types": self.attack_types
        }
    
    def is_malicious(self, threshold: int = 50) -> bool:
        """Check if IP is considered malicious based on threshold."""
        return self.reputation_score < threshold
    
    def decrement_score(self, amount: int = 10) -> int:
        """
        Decrement reputation score by specified amount.
        
        Returns:
            New reputation score (minimum 0)
        """
        self.reputation_score = max(0, self.reputation_score - amount)
        return self.reputation_score


class BeaconEvent(Base):
    """
    Honeytoken beacon event — tracks when an attacker accesses a
    canary URL embedded in fake exfiltrated files.
    
    Each beacon hit is a high-confidence indicator of data exfiltration,
    providing the attacker's external IP, user agent, and timing.
    """
    __tablename__ = "beacon_events"
    
    # Primary key
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True
    )
    
    # Session ID from the honeytoken URL (/api/beacon/{session_id})
    session_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
        comment="UUID session ID embedded in the honeytoken URL"
    )
    
    # Source IP of whoever triggered the beacon (attacker's external IP)
    source_ip: Mapped[str] = mapped_column(
        String(45),
        nullable=False,
        index=True,
        comment="IP address that accessed the beacon URL"
    )
    
    # User-Agent header from the beacon request
    user_agent: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="User-Agent string from the beacon request"
    )
    
    # Full request headers (for deep forensic analysis)
    request_headers: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="All HTTP headers from the beacon request"
    )
    
    # IP of the original attacker who received the honeytoken
    original_attacker_ip: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
        index=True,
        comment="Original attacker IP from the honeypot session"
    )
    
    # Timestamp
    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
        comment="When the beacon was triggered"
    )
    
    # Which honeytoken file was accessed
    honeytoken_file: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Name of the fake file containing the beacon URL"
    )
    
    # X-Forwarded-For chain (reveals proxy/VPN hops)
    forwarded_for: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="X-Forwarded-For header chain"
    )
    
    # Composite indexes
    __table_args__ = (
        Index('ix_beacon_events_session_triggered', 'session_id', 'triggered_at'),
        Index('ix_beacon_events_source_ip_triggered', 'source_ip', 'triggered_at'),
    )
    
    def __repr__(self) -> str:
        return f"<BeaconEvent(id={self.id}, session={self.session_id}, ip={self.source_ip})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "id": str(self.id),
            "session_id": self.session_id,
            "source_ip": self.source_ip,
            "user_agent": self.user_agent,
            "request_headers": self.request_headers,
            "original_attacker_ip": self.original_attacker_ip,
            "triggered_at": self.triggered_at.isoformat() if self.triggered_at else None,
            "honeytoken_file": self.honeytoken_file,
            "forwarded_for": self.forwarded_for,
        }


# Pydantic models for API validation (kept for request/response schemas)
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional


class AttackType(str, Enum):
    """Enumeration of attack types for classification."""
    BENIGN = "BENIGN"
    SQLI = "SQLI"
    XSS = "XSS"
    SSI = "SSI"
    BRUTE_FORCE = "BRUTE_FORCE"


class UserInput(BaseModel):
    """User input schema for trap endpoint."""
    input_text: str = Field(..., description="The input text from the attacker")
    ip_address: Optional[str] = Field(None, description="Optional IP address override")
    user_agent: Optional[str] = Field(None, description="Optional user agent override")


class GeoLocation(BaseModel):
    """Geographic location data for an IP address."""
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    isp: Optional[str] = None


class ClassificationResult(BaseModel):
    """ML classification result for an input."""
    attack_type: AttackType
    confidence: float = Field(..., ge=0.0, le=1.0)
    is_malicious: bool


class DeceptionResponse(BaseModel):
    """Deceptive response sent to attacker."""
    message: str
    delay_applied: float
    http_status: int


class AttackLogResponse(BaseModel):
    """Attack log response for API."""
    id: Optional[str] = None
    timestamp: datetime
    raw_input: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    geo_location: Optional[GeoLocation]
    classification: ClassificationResult
    deception_response: DeceptionResponse
    hash: Optional[str] = None
    previous_hash: Optional[str] = None


class DashboardStats(BaseModel):
    """Dashboard statistics response."""
    total_attempts: int
    malicious_attempts: int
    benign_attempts: int
    attack_distribution: Dict[str, int]
    top_attackers: List[Dict[str, Any]]
    geo_locations: List[Dict[str, Any]] = []
    flagged_ips_count: int = 0
    top_threats: List[Dict[str, Any]] = []
    merkle_root: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request schema."""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response schema."""
    access_token: str
    token_type: str = "bearer"


class TenantCreate(BaseModel):
    """Schema for creating a new tenant."""
    email: str
    api_key: Optional[str] = None


class TenantResponse(BaseModel):
    """Schema for tenant API response."""
    id: str
    email: str
    credit_balance: int
    created_at: datetime
    updated_at: datetime


class HoneypotLogCreate(BaseModel):
    """Schema for creating a honeypot log entry."""
    tenant_id: str
    attacker_ip: str
    command_entered: str
    response_sent: str
    metadata: Optional[Dict[str, Any]] = None


class ReputationScoreResponse(BaseModel):
    """Schema for reputation score API response."""
    ip_address: str
    reputation_score: int
    behavior_hash: Optional[str] = None
    merkle_root: Optional[str] = None
    last_updated: datetime
    attack_count: int
    attack_types: Optional[Dict[str, int]] = None