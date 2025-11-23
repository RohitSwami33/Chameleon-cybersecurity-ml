from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class AttackType(str, Enum):
    BENIGN = "BENIGN"
    SQLI = "SQLI"
    XSS = "XSS"
    SSI = "SSI"
    BRUTE_FORCE = "BRUTE_FORCE"

class UserInput(BaseModel):
    input_text: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class GeoLocation(BaseModel):
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    isp: Optional[str] = None

class ClassificationResult(BaseModel):
    attack_type: AttackType
    confidence: float
    is_malicious: bool

class DeceptionResponse(BaseModel):
    message: str
    delay_applied: float
    http_status: int

class AttackLog(BaseModel):
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
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class DashboardStats(BaseModel):
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
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
