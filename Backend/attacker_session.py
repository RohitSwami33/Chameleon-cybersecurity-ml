"""
Attacker Session Model
Tracks the progressive journey of each unique attacker through the honeypot
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import hashlib
import random

class SessionHistory(BaseModel):
    """Individual attempt in the attacker's session"""
    timestamp: datetime
    raw_input: str
    stage: int
    response: str
    attack_type: str

class AttackerSession(BaseModel):
    """
    Tracks an attacker's progressive journey through the honeypot.
    Each session represents a unique attacker identified by fingerprint.
    """
    attacker_fingerprint: str = Field(..., description="Hash of IP + User-Agent")
    attempt_count: int = Field(default=0, description="Total number of attempts")
    attack_type: Optional[str] = Field(default=None, description="Primary attack vector (SQLi, XSS, etc.)")
    current_stage: int = Field(default=1, description="Current deception stage")
    db_type: str = Field(default="MySQL", description="Fake database type for consistency")
    guessed_table: Optional[str] = Field(default=None, description="Table name attacker 'discovered'")
    guessed_column: Optional[str] = Field(default=None, description="Column name attacker 'discovered'")
    history: List[SessionHistory] = Field(default_factory=list, description="Attack attempt history")
    first_seen: datetime = Field(default_factory=datetime.utcnow)
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "attacker_fingerprint": "a1b2c3d4e5f6",
                "attempt_count": 3,
                "attack_type": "SQLI",
                "current_stage": 2,
                "db_type": "MySQL",
                "guessed_table": "users",
                "guessed_column": None,
                "history": []
            }
        }

def generate_attacker_fingerprint(ip_address: str, user_agent: str) -> str:
    """
    Generate a unique fingerprint for an attacker based on IP and User-Agent.
    
    Args:
        ip_address: Attacker's IP address
        user_agent: Attacker's User-Agent string
        
    Returns:
        SHA256 hash of the combined identifiers
    """
    combined = f"{ip_address}:{user_agent or 'unknown'}"
    return hashlib.sha256(combined.encode()).hexdigest()

def initialize_session(fingerprint: str, attack_type: str) -> AttackerSession:
    """
    Initialize a new attacker session with random characteristics.
    
    Args:
        fingerprint: Unique attacker fingerprint
        attack_type: Type of attack detected
        
    Returns:
        New AttackerSession with randomized database type
    """
    # Randomly assign a database type for consistency in error messages
    db_types = ["MySQL", "PostgreSQL", "SQLite", "MariaDB"]
    
    return AttackerSession(
        attacker_fingerprint=fingerprint,
        attack_type=attack_type,
        db_type=random.choice(db_types),
        current_stage=1,
        attempt_count=0
    )

# In-memory session storage (in production, this would be MongoDB)
# Key: attacker_fingerprint, Value: AttackerSession
_session_store: Dict[str, AttackerSession] = {}

async def get_or_create_session(
    ip_address: str, 
    user_agent: str, 
    attack_type: str
) -> AttackerSession:
    """
    Retrieve existing session or create a new one for an attacker.
    
    Args:
        ip_address: Attacker's IP address
        user_agent: Attacker's User-Agent string
        attack_type: Type of attack detected
        
    Returns:
        AttackerSession for this attacker
    """
    fingerprint = generate_attacker_fingerprint(ip_address, user_agent)
    
    if fingerprint not in _session_store:
        _session_store[fingerprint] = initialize_session(fingerprint, attack_type)
    
    return _session_store[fingerprint]

async def update_session(
    session: AttackerSession,
    raw_input: str,
    response: str,
    attack_type: str
) -> AttackerSession:
    """
    Update session after an attack attempt.
    
    Args:
        session: Current attacker session
        raw_input: The attack payload
        response: The deceptive response sent
        attack_type: Type of attack
        
    Returns:
        Updated AttackerSession
    """
    # Increment attempt count
    session.attempt_count += 1
    session.last_seen = datetime.utcnow()
    
    # Add to history
    history_entry = SessionHistory(
        timestamp=datetime.utcnow(),
        raw_input=raw_input[:500],  # Limit size
        stage=session.current_stage,
        response=response,
        attack_type=attack_type
    )
    session.history.append(history_entry)
    
    # Keep only last 50 entries to prevent memory bloat
    if len(session.history) > 50:
        session.history = session.history[-50:]
    
    # Update session in store
    _session_store[session.attacker_fingerprint] = session
    
    return session

async def advance_session_stage(session: AttackerSession) -> AttackerSession:
    """
    Advance the attacker to the next deception stage.
    
    Args:
        session: Current attacker session
        
    Returns:
        Updated AttackerSession with incremented stage
    """
    # Maximum stage is 4 for SQLi, 3 for XSS
    max_stage = 4 if session.attack_type == "SQLI" else 3
    
    if session.current_stage < max_stage:
        session.current_stage += 1
    
    # Update in store
    _session_store[session.attacker_fingerprint] = session
    
    return session

async def get_session_stats() -> Dict[str, Any]:
    """
    Get statistics about all active sessions.
    
    Returns:
        Dictionary with session statistics
    """
    total_sessions = len(_session_store)
    
    # Count by attack type
    attack_types = {}
    stages = {1: 0, 2: 0, 3: 0, 4: 0}
    
    for session in _session_store.values():
        attack_type = session.attack_type or "UNKNOWN"
        attack_types[attack_type] = attack_types.get(attack_type, 0) + 1
        stages[session.current_stage] = stages.get(session.current_stage, 0) + 1
    
    return {
        "total_sessions": total_sessions,
        "attack_types": attack_types,
        "stage_distribution": stages
    }
