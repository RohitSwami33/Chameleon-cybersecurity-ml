from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.core.config import settings, redis_client, REDIS_AVAILABLE
import re
import secrets
import os
import uuid

USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_\-\.]{1,64}$')


def sanitise_username(username: str):
    """Validate and sanitise username to prevent template injection."""
    if not username or not USERNAME_PATTERN.match(username):
        return None
    return username


# Short-lived access tokens (15 minutes)
ACCESS_TOKEN_EXPIRE_MINUTES = 15


security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT with jti claim for revocation support."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({
        "jti": str(uuid.uuid4()),
        "exp": expire
    })
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm="HS256")


async def verify_not_revoked(jti: str) -> None:
    """Check if token jti has been revoked via Redis denylist."""
    if not REDIS_AVAILABLE or redis_client is None:
        return  # graceful fallback
    try:
        if await redis_client.get(f"revoked_jti:{jti}"):
            raise HTTPException(status_code=401, detail="Not authenticated")
    except HTTPException:
        raise
    except Exception:
        pass  # Redis error — fail open, log internally


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify JWT token and check revocation status."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"], options={"leeway": 30})
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # Check revocation
        jti = payload.get("jti")
        if jti:
            await verify_not_revoked(jti)
        return username
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_token_payload(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get full JWT payload including jti for logout revocation."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"], options={"leeway": 30})
        jti = payload.get("jti")
        exp = payload.get("exp")
        if jti:
            await verify_not_revoked(jti)
        return payload
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_credentials(username: str, password: str) -> bool:
    """Verify credentials using constant-time comparison."""
    safe_username = sanitise_username(username)
    if safe_username is None:
        return False
    try:
        admin_user = os.getenv("ADMIN_USERNAME", "")
        admin_pass = os.getenv("ADMIN_PASSWORD", "")
        username_ok = secrets.compare_digest(safe_username.encode(), admin_user.encode())
        password_ok = secrets.compare_digest(password.encode(), admin_pass.encode())
        return username_ok and password_ok
    except Exception:
        return False
