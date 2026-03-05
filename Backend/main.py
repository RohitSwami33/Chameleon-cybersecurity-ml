"""
Chameleon Adaptive Deception System — FastAPI Application
==========================================================

Core API pipeline connecting:
  • ChameleonPredictor  → BiLSTM inference  (ml_inference.py)
  • DeepSeek LLM        → Deception engine  (llm_controller.py)
  • SHA-256 hashing     → Integrity check   (integrity.py)
  • Async PostgreSQL    → Persistent logs   (database_postgres.py)

Primary new endpoint:  POST /trap/execute
"""

from fastapi import (
    FastAPI, Request, BackgroundTasks, HTTPException,
    Query, Depends,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
import httpx
from datetime import datetime
from typing import List, Optional, Dict, Any
from io import BytesIO
import asyncio
import logging

from pydantic import BaseModel, Field

from config import settings
from alert_manager import alert_manager

# ── ORM & Pydantic models ───────────────────────────────────────────────
from models import (
    UserInput, AttackLog, GeoLocation, ClassificationResult,
    DeceptionResponse, DashboardStats, LoginRequest, LoginResponse,
    AttackType,
)
from models_sqlalchemy import HoneypotLog, BeaconEvent

# ── Auth ─────────────────────────────────────────────────────────────────
from auth import create_access_token, verify_token, verify_credentials

# ── Async PostgreSQL (new) ──────────────────────────────────────────────
from database_postgres import (
    get_db,                   # FastAPI Depends() → yields AsyncSession
    db,                       # Database singleton (.connect / .disconnect)
    save_honeypot_log,        # (session, tenant_id, ip, cmd, resp, meta)
    get_default_tenant,       # (session) → Tenant | None
)

# ── Legacy MongoDB (existing endpoints) ─────────────────────────────────
from database import (
    connect_to_mongo, close_mongo_connection, save_attack_log,
    get_attack_logs, get_attack_by_id, get_dashboard_stats,
    get_logs_by_ip,
)

# ── ML Inference (Local MLX Model) ──────────────────────────────────────────
from local_inference import mlx_model
from pipeline import evaluate_payload

# ── LLM Deception Engine (DeepSeek API) ─────────────────────────────────
from llm_controller import generate_deceptive_response

# ── Integrity Hashing ──────────────────────────────────────────────────
from integrity import hash_log_entry as calculate_hash

# ── Other Services ──────────────────────────────────────────────────────
from ml_classifier import classifier
from deception_engine import deception_engine
from deception_engine_v2 import progressive_deception_engine
from attacker_session import (
    get_or_create_session, update_session,
    generate_attacker_fingerprint, get_session_stats,
)
from tarpit_manager import tarpit_manager
from blockchain_logger import blockchain_logger
from report_generator import report_generator
from login_rate_limiter import login_limiter
from threat_score import threat_score_system
from threat_intel_service import threat_intel_service
from chatbot_service import get_chatbot
from utils import get_current_time

# ── SIEM Export ────────────────────────────────────────────────────────
from api.export.stix import stix_router

logger = logging.getLogger(__name__)

# ========================================================================
# Deception Handler
# ========================================================================
async def handle_deception_layer(payload: str, request_data: dict, request: Request = None, additional_data: dict = None):
    """
    Called when a payload is flagged as BLOCK by the security pipeline.
    Routes the attacker into the 'Deception Layer', storing telemetry
    and returning a superficially valid 200 OK success response.
    """
    logger.warning(f"🚨 [DECEPTION LAYER TRIGGERED] Payload: {payload[:100]}")
    
    # Store telemetry data locally or to DB to track their behavior
    ip = request_data.get("ip_address", "Unknown")
    # Using the existing log_attack function for MongoDB logging
    await log_attack(
        {
            "timestamp": datetime.now().isoformat(),
            "ip_address": ip,
            "raw_input": payload,
            "classification": {
                "attack_type": AttackType.SSI.value, # Abstract generic type
                "confidence": 0.99,
                "is_malicious": True
            },
            "deception_response": {
                "message": "Routed to deception layer",
                "delay_applied": 0,
                "http_status": 200
            }
        }
    )

    try:
        # Flag in DB as deeply anomalous / trapped
        # This part assumes a `store_attack_log` function which is not defined.
        # Using save_honeypot_log for PostgreSQL logging.
        async with db.session_factory() as session:
            tenant = await get_default_tenant(session)
            tenant_id = str(tenant.id) if tenant else "00000000-0000-0000-0000-000000000000"
            log_meta = {
                "honeypot_event": "DECEPTION_LAYER_TRIGGERED",
                "fingerprint_data": request_data,
                "user_agent": request.headers.get("user-agent", "") if request else "",
                "referer": request.headers.get("referer", "") if request else "",
                "classification": {
                    "attack_type": "ATTACKER_IN_DECEPTION",
                    "confidence": 0.99,
                    "is_malicious": True,
                },
                "session_id": "DECEPTION_SESSION",
            }
            log = HoneypotLog(
                tenant_id=tenant_id,
                attacker_ip=ip,
                command_entered=f"[DECEPTION] {payload}",
                response_sent="Routed to deception layer",
                log_metadata=log_meta,
            )
            session.add(log)
            await session.commit()
    except Exception as e:
        logger.error(f"Failed to flag attacker in DB: {e}")

    # The deception response is tailored conceptually based on the action
    action = request_data.get("action", "generic")
    
    if action == "login":
        return JSONResponse(content={"status": "success", "session_id": "fake_token_123_abc", "message": "Login successful"}, status_code=200)
    elif action == "execute":
        # Simulate an empty terminal prompt or generic success for a command
        return JSONResponse(content={
            "status": "success",
            "output": f"bash: {payload[:20]} command not found\nroot@target:/# ",
            "execution_time_ms": 12
        }, status_code=200)
    else:
        return JSONResponse(content={"status": "success", "data": "Request accepted for processing."}, status_code=200)

# ========================================================================
# Pydantic Request / Response Models
# ========================================================================

class TrapExecuteRequest(BaseModel):
    """JSON payload for POST /trap/execute."""
    command: str = Field(..., description="Raw shell command from the attacker")
    ip_address: Optional[str] = Field(None, description="Override attacker IP")


class TrapExecuteResponse(BaseModel):
    """JSON response from POST /trap/execute."""
    response: str = Field(..., description="Deceptive terminal output")
    prediction_score: float = Field(..., ge=0.0, le=1.0)
    is_malicious: bool
    hash: str
    session_id: Optional[str] = Field(None, description="Honeytoken beacon session UUID")


class ChatMessage(BaseModel):
    message: str
    use_search: bool = False
    context: Optional[dict] = None


class ChatResponse(BaseModel):
    success: bool
    response: str
    search_results: List[dict] = []
    timestamp: str
    error: Optional[str] = None


# ========================================================================
# ML Predictor — local MLX model is loaded inside its own module
# ========================================================================


# ========================================================================
# Application Lifecycle
# ========================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start both database connections on startup; tear down on shutdown."""
    await connect_to_mongo()          # Legacy endpoints (no-op now)
    await db.connect()                # Async PostgreSQL for /trap/execute
    await db.create_tables()          # Ensure all tables exist
    logger.info("✅ All databases connected")
    yield
    await close_mongo_connection()
    await db.disconnect()
    logger.info("🛑 All databases disconnected")


app = FastAPI(
    title="Chameleon Adaptive Deception System",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:3000",
        "https://*.onrender.com",
        "https://chameleon-frontend.onrender.com",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Register routers
app.include_router(stix_router, prefix="/api/export", tags=["SIEM Export"])


# ========================================================================
# Helpers
# ========================================================================

def get_client_ip(request: Request) -> str:
    """Extract the real client IP, respecting X-Forwarded-For."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host


async def fetch_geo_location(ip: str) -> Optional[GeoLocation]:
    """Fetch geolocation for a public IP address."""
    if ip in ("127.0.0.1", "localhost", "::1"):
        return None
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{settings.GEOIP_API_URL}{ip}")
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "success":
                    return GeoLocation(
                        country=data.get("country"),
                        region=data.get("regionName"),
                        city=data.get("city"),
                        latitude=data.get("lat"),
                        longitude=data.get("lon"),
                        isp=data.get("isp"),
                    )
    except Exception as e:
        logger.warning("GeoIP lookup failed: %s", e)
    return None


async def log_attack(log_data: dict):
    """Legacy background logging → blockchain + MongoDB."""
    block_info = blockchain_logger.add_block(log_data)
    log_data["hash"] = block_info["hash"]
    log_data["previous_hash"] = block_info["previous_hash"]
    await save_attack_log(log_data)


def _static_fallback(command: str) -> str:
    """
    Cheap static bash response for low-confidence commands.
    Saves DeepSeek API costs when the model isn't confident
    enough that the command is truly malicious.
    """
    cmd = command.strip()
    cmd_lower = cmd.lower()

    # Common benign commands → realistic-looking output
    if cmd_lower in ("ls", "ls -la", "ls -al", "dir"):
        return (
            "total 0\n"
            "drwxr-xr-x  2 root root  40 Feb 28 02:00 .\n"
            "drwxr-xr-x  3 root root  60 Feb 28 01:55 ..\n"
        )
    if cmd_lower == "whoami":
        return "root"
    if cmd_lower == "id":
        return "uid=0(root) gid=0(root) groups=0(root)"
    if cmd_lower == "pwd":
        return "/root"
    if cmd_lower == "uname -a":
        return "Linux honeypot 5.15.0-91-generic #101-Ubuntu SMP x86_64 GNU/Linux"
    if cmd_lower.startswith("cat "):
        return f"cat: {cmd.split()[-1]}: Permission denied"
    if cmd_lower.startswith("cd "):
        return ""

    # Default → command not found
    first_word = cmd.split()[0] if cmd else cmd
    return f"bash: {first_word}: command not found"


# ========================================================================
# ★  POST /trap/execute  — Primary Honeypot Endpoint
# ========================================================================

@app.post("/trap/execute", response_model=TrapExecuteResponse)
async def trap_execute(
    payload: TrapExecuteRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db),
):
    """
    Core honeypot pipeline (fully async, non-blocking):

    1. Receive JSON  →  { "command": "...", "ip_address": "..." }
    2. BiLSTM prediction  →  ChameleonPredictor.predict(command)
    3. Threshold gate:
       • score > 0.85  →  DeepSeek LLM generates fake terminal output
       • score ≤ 0.85  →  static 'command not found' (saves API $)
    4. SHA-256 hash  →  calculate_hash(ip + command + response + score)
    5. PostgreSQL save  →  HoneypotLog with score + hash in JSONB metadata
    6. Return deceptive text to the attacker
    """
    ip_address = payload.ip_address or get_client_ip(request)
    command = payload.command

    # ── Step 1: ML Prediction via Two-Stage Pipeline ─────────────────────
    verdict = await evaluate_payload(command)
    is_malicious: bool = (verdict == "BLOCK")
    prediction_score: float = 0.99 if is_malicious else 0.01

    # ── Step 2: Deceptive Response (threshold gate) ─────────────────────
    DECEPTION_THRESHOLD = 0.85

    if prediction_score > DECEPTION_THRESHOLD:
        # High-confidence attack → call DeepSeek LLM for realistic fake output
        try:
            response_text, honeytoken_session_id = await generate_deceptive_response(
                command=command,
                ip_address=ip_address,
            )
        except Exception as e:
            logger.error("DeepSeek LLM call failed, falling back to static: %s", e)
            response_text = _static_fallback(command)
            honeytoken_session_id = None
    else:
        # Low/medium confidence → cheap static reply to save API costs
        response_text = _static_fallback(command)
        honeytoken_session_id = None

    # ── Step 3: Cryptographic Hash ──────────────────────────────────────
    #    Hash of (ip_address + command + response + prediction_score)
    hash_input: Dict[str, Any] = {
        "ip_address": ip_address,
        "command": command,
        "response": response_text,
        "prediction_score": round(prediction_score, 6),
    }
    interaction_hash: str = calculate_hash(hash_input)

    # ── Step 4: Save to PostgreSQL (inline async — non-blocking) ────────
    #    Prediction score + hash stored in the JSONB metadata column
    metadata: Dict[str, Any] = {
        "prediction_score": round(prediction_score, 6),
        "is_malicious": is_malicious,
        "hash": interaction_hash,
        "user_agent": request.headers.get("User-Agent"),
        "model": "chameleon_lstm_m4_50k",
        "honeytoken_session_id": honeytoken_session_id,
    }

    # Resolve tenant (single-tenant mode → first tenant in DB)
    tenant = await get_default_tenant(session)
    tenant_id = str(tenant.id) if tenant else "00000000-0000-0000-0000-000000000000"

    await save_honeypot_log(
        session=session,
        tenant_id=tenant_id,
        attacker_ip=ip_address,
        command_entered=command,
        response_sent=response_text,
        metadata=metadata,
    )
    # get_db dependency auto-commits on successful return

    # ── Step 4.5: Trigger Webhook Alert for Critical Attacks ────────────
    if prediction_score > DECEPTION_THRESHOLD:
        background_tasks.add_task(
            alert_manager.trigger_critical_attack_alert,
            ip_address=ip_address,
            command=command,
            score=prediction_score,
            session_id=honeytoken_session_id
        )

    # ── Step 5: Return Response ─────────────────────────────────────────
    return TrapExecuteResponse(
        response=response_text,
        prediction_score=round(prediction_score, 6),
        is_malicious=is_malicious,
        hash=interaction_hash,
        session_id=honeytoken_session_id,
    )


# ========================================================================
# ★  GET /api/beacon/{session_id}  — Honeytoken Tripwire
# ========================================================================
# 1x1 transparent PNG pixel — looks like a dead link / tracking pixel
TRANSPARENT_PIXEL = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
    b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4"
    b"\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05"
    b"\x00\x01\r\n\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)


@app.get("/api/beacon/{session_id}")
async def beacon_tripwire(
    session_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db),
):
    """
    Honeytoken tripwire — triggered when an attacker accesses a URL
    embedded in fake exfiltrated files (aws_production_keys.csv, .env.backup).

    Appears as a 1x1 transparent pixel (dead link) but silently logs
    high-fidelity telemetry about the requester:
      • Source IP (direct + X-Forwarded-For chain)
      • User-Agent
      • Full request headers

    This is a HIGH-CONFIDENCE indicator of data exfiltration.
    """
    # ── Capture telemetry ────────────────────────────────────────────────
    source_ip = request.client.host if request.client else "unknown"
    forwarded_for = request.headers.get("X-Forwarded-For")
    user_agent = request.headers.get("User-Agent", "unknown")
    
    # Capture all request headers for forensic analysis
    all_headers = dict(request.headers)
    
    logger.warning(
        "🚨 HONEYTOKEN BEACON TRIGGERED | session=%s | ip=%s | xff=%s | ua=%s",
        session_id, source_ip, forwarded_for, user_agent
    )

    # ── Persist to BeaconEvent table ─────────────────────────────────────
    # Look up original attacker IP from HoneypotLog metadata
    from sqlalchemy import select, cast, String
    stmt = (
        select(HoneypotLog.attacker_ip)
        .where(
            HoneypotLog.log_metadata["honeytoken_session_id"].astext == session_id
        )
        .order_by(HoneypotLog.timestamp.desc())
        .limit(1)
    )
    result = await session.execute(stmt)
    original_ip_row = result.scalar_one_or_none()
    original_attacker_ip = original_ip_row if original_ip_row else None

    beacon_event = BeaconEvent(
        session_id=session_id,
        source_ip=source_ip,
        user_agent=user_agent,
        request_headers=all_headers,
        original_attacker_ip=original_attacker_ip,
        honeytoken_file="aws_production_keys.csv / .env.backup",
        forwarded_for=forwarded_for,
    )
    session.add(beacon_event)

    # Also flag the original HoneypotLog as exfiltration attempt
    if original_attacker_ip:
        from sqlalchemy import update
        update_stmt = (
            update(HoneypotLog)
            .where(
                HoneypotLog.log_metadata["honeytoken_session_id"].astext == session_id
            )
            .values(is_exfiltration_attempt=True)
        )
        await session.execute(update_stmt)

    # get_db auto-commits on return

    # Trigger async webhook alert for exfiltration
    background_tasks.add_task(
        alert_manager.trigger_beacon_exfiltration_alert,
        session_id=session_id,
        ip_address=source_ip,
        user_agent=user_agent
    )

    # ── Return 1x1 transparent pixel (appear as dead link) ──────────────
    return Response(
        content=TRANSPARENT_PIXEL,
        media_type="image/png",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


# ========================================================================
# Legacy /api/trap/submit (existing progressive deception pipeline)
# ========================================================================

@app.post("/api/trap/submit")
async def submit_trap(
    user_input: UserInput,
    request: Request,
    background_tasks: BackgroundTasks,
):
    ip = user_input.ip_address or get_client_ip(request)
    user_agent = user_input.user_agent or request.headers.get("User-Agent")

    # Tarpit
    if tarpit_manager.is_blocked(ip):
        pass
    is_tarpit, delay = tarpit_manager.record_request(ip)
    if is_tarpit and delay > 0:
        await asyncio.sleep(delay)

    # Classification (Local MLX model + old ML classifier for attack type mapping)
    verdict = await evaluate_payload(user_input.input_text)
    classification = classifier.classify(user_input.input_text)
    
    is_malicious = (verdict == "BLOCK")
    classification.is_malicious = is_malicious
    classification.confidence = 0.99 if is_malicious else 0.01
    
    if is_malicious and classification.attack_type == AttackType.BENIGN:
        classification.attack_type = AttackType.SSI  # Default fallback attack type
        
    geo_location = await fetch_geo_location(ip)

    # Record the submission in local JSON logs
    await log_attack(
        {
            "timestamp": datetime.now().isoformat(),
            "ip_address": ip,
            "raw_input": user_input.input_text,
            "classification": {
                "attack_type": classification.attack_type.value,
                "confidence": classification.confidence,
                "is_malicious": classification.is_malicious
            },
            "deception_response": None  # will be handled by UI or later
        }
    )
    
    # Send the log asynchronously to the DB (MongoDB)
    # The original `save_attack_log` is already async and adds to blockchain.
    # The snippet provided `store_attack_log` is not defined.
    # The instruction implies using `handle_deception_layer` for malicious inputs.
    # So, if malicious, we route to deception layer and return a fake 200.
    if is_malicious:
        # Route to Deception Layer to feign success
        request_context = {"ip_address": ip, "action": "generic", "geo_location": geo_location.model_dump() if geo_location else {}}
        return await handle_deception_layer(user_input.input_text, request_context, request)

    # Progressive deception engine v2
    atk_session = await get_or_create_session(
        ip, user_agent, classification.attack_type.value,
    )
    progressive_message = await progressive_deception_engine.generate_progressive_response(
        classification.attack_type, user_input.input_text, atk_session,
    )

    http_status = 200
    if classification.attack_type == AttackType.SQLI:
        http_status = 500
    elif classification.attack_type == AttackType.SSI:
        http_status = 403
    elif classification.attack_type == AttackType.BRUTE_FORCE:
        http_status = 401

    deception = DeceptionResponse(
        message=progressive_message,
        delay_applied=delay,
        http_status=http_status,
    )

    await update_session(
        atk_session, user_input.input_text,
        progressive_message, classification.attack_type.value,
    )

    threat_score_system.calculate_threat_score(
        ip, classification.attack_type, classification.is_malicious,
    )

    log_entry = AttackLog(
        timestamp=get_current_time(),
        raw_input=user_input.input_text,
        ip_address=ip,
        user_agent=user_agent,
        geo_location=geo_location,
        classification=classification,
        deception_response=deception,
    )
    log_dict = log_entry.model_dump()

    # Threat intelligence
    if classification.is_malicious and threat_intel_service.is_novel_attack(
        user_input.input_text, classification.attack_type,
    ):
        threat_report = threat_intel_service.create_threat_report(
            user_input.input_text, classification.attack_type,
            ip, classification.confidence,
        )
        if threat_report:
            logger.info("Novel attack detected! Report: %s", threat_report["pattern_hash"][:16])

    background_tasks.add_task(log_attack, log_dict)

    if classification.is_malicious and classification.attack_type in (
        AttackType.SQLI, AttackType.XSS,
    ):
        if threat_intel_service.is_novel_attack(user_input.input_text, classification.attack_type):
            threat_intel_service.create_threat_intel_report(
                attack_type=classification.attack_type.value,
                payload=user_input.input_text,
                confidence=classification.confidence,
                timestamp=log_entry.timestamp,
            )

    return JSONResponse(content=deception.model_dump(), status_code=deception.http_status)


# ========================================================================
# Auth
# ========================================================================

@app.post("/api/auth/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    request: Request,
    background_tasks: BackgroundTasks,
):
    ip = get_client_ip(request)
    user_agent = request.headers.get("User-Agent")

    # ── 1. Check if the username or password itself is a malicious payload ──
    combined_input = f"{login_data.username} {login_data.password}"
    verdict = await evaluate_payload(combined_input)
    classification = classifier.classify(combined_input)
    
    is_malicious = (verdict == "BLOCK")
    classification.is_malicious = is_malicious
    classification.confidence = 0.99 if is_malicious else 0.01
    
    if is_malicious and classification.attack_type == AttackType.BENIGN:
        classification.attack_type = AttackType.BRUTE_FORCE
        
    if is_malicious:
        # Route to Deception Layer instead of HTTP 401
        request_context = {"ip_address": ip, "action": "login"}
        return await handle_deception_layer(combined_input, request_context, request)


    # ── 2. Check for Brute Force (Rate Limiting) ──
    if login_limiter.is_rate_limited(ip):
        log_entry = AttackLog(
            timestamp=get_current_time(),
            raw_input=f"Blocked login attempt - Username: {login_data.username}",
            ip_address=ip, user_agent=user_agent, geo_location=None,
            classification=ClassificationResult(
                attack_type="BRUTE_FORCE", confidence=1.0, is_malicious=True,
            ),
            deception_response=DeceptionResponse(
                message="Too many login attempts. Account temporarily locked.",
                delay_applied=0, http_status=429,
            ),
        )
        background_tasks.add_task(log_attack, log_entry.model_dump())
        return JSONResponse(status_code=429, content={"detail": "Too many login attempts. Please try again later."}, background=background_tasks)

    is_brute_force = login_limiter.record_attempt(ip)
    if is_brute_force:
        log_entry = AttackLog(
            timestamp=get_current_time(),
            raw_input=f"Brute force detected - Username: {login_data.username}",
            ip_address=ip, user_agent=user_agent, geo_location=None,
            classification=ClassificationResult(
                attack_type="BRUTE_FORCE", confidence=1.0, is_malicious=True,
            ),
            deception_response=DeceptionResponse(
                message="Brute force attack detected. Account temporarily locked.",
                delay_applied=0, http_status=429,
            ),
        )
        background_tasks.add_task(log_attack, log_entry.model_dump())
        return JSONResponse(status_code=429, content={"detail": "Brute force attack detected. Account temporarily locked."}, background=background_tasks)

    # ── 3. Normal Authentication Check ──
    if not verify_credentials(login_data.username, login_data.password):
        log_entry = AttackLog(
            timestamp=get_current_time(),
            raw_input=f"Failed login - Username: {login_data.username}",
            ip_address=ip, user_agent=user_agent, geo_location=None,
            classification=ClassificationResult(
                attack_type="BENIGN", confidence=0.5, is_malicious=False,
            ),
            deception_response=DeceptionResponse(
                message="Incorrect username or password",
                delay_applied=0, http_status=401,
            ),
        )
        background_tasks.add_task(log_attack, log_entry.model_dump())
        return JSONResponse(status_code=401, content={"detail": "Incorrect username or password"}, background=background_tasks)

    login_limiter.reset_attempts(ip)
    access_token = create_access_token(data={"sub": login_data.username})
    return LoginResponse(access_token=access_token)


# ========================================================================
# Dashboard
# ========================================================================

@app.get("/api/dashboard/stats", response_model=DashboardStats)
async def get_stats(username: str = Depends(verify_token)):
    stats = await get_dashboard_stats()
    recent_logs = await get_attack_logs(0, 100)
    merkle_root = blockchain_logger.get_merkle_root_for_recent_logs(recent_logs)
    stats["merkle_root"] = merkle_root
    flagged_ips = threat_score_system.get_flagged_ips(threshold=70)
    top_threats = threat_score_system.get_top_threats(limit=5)
    stats["flagged_ips_count"] = len(flagged_ips)
    stats["top_threats"] = top_threats
    return stats


@app.get("/api/dashboard/logs", response_model=List[AttackLog])
async def get_logs(skip: int = 0, limit: int = 50, username: str = Depends(verify_token)):
    return await get_attack_logs(skip, limit)


@app.get("/api/dashboard/logs/{log_id}", response_model=AttackLog)
async def get_log(log_id: str, username: str = Depends(verify_token)):
    log = await get_attack_by_id(log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log


@app.get("/api/dashboard/logs/ip/{ip_address}", response_model=List[AttackLog])
async def get_ip_logs(ip_address: str, username: str = Depends(verify_token)):
    return await get_logs_by_ip(ip_address)


# ========================================================================
# Reports
# ========================================================================

@app.post("/api/reports/generate/{ip_address}")
async def generate_report(ip_address: str, username: str = Depends(verify_token)):
    logs = await get_logs_by_ip(ip_address)
    stats = await get_dashboard_stats()
    pdf_bytes = report_generator.generate_incident_report(ip_address, logs, stats)
    filename = f"incident_report_{ip_address}_{int(datetime.utcnow().timestamp())}.pdf"
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ========================================================================
# Blockchain
# ========================================================================


# ========================================================================
# Honeypot Logging (attacker-facing — no auth required)
# ========================================================================

@app.post("/api/honeypot/log")
async def honeypot_log(request: Request, background_tasks: BackgroundTasks):
    """
    Receives attacker fingerprints from the TrapInterface decoy page.

    The frontend silently POSTs browser fingerprints (credentials attempted,
    canvas hash, fonts, WebGL renderer, timezone) on every interaction.
    These are logged to PostgreSQL for forensic correlation.
    """
    try:
        body = await request.json()
    except Exception:
        return {"status": "logged"}

    event_type = body.get("event", "UNKNOWN")
    event_data = body.get("data", {})

    # Extract attacker IP from proxy headers
    forwarded = request.headers.get("x-forwarded-for", "")
    attacker_ip = forwarded.split(",")[0].strip() if forwarded else (request.client.host if request.client else "unknown")

    logger.warning(
        "🍯 HONEYPOT TRIGGERED: event=%s ip=%s data=%s",
        event_type, attacker_ip, str(event_data)[:200],
    )

    # Optional: run ML classifier on the trapped username if it's a login attempt
    classification_dict = None
    if event_type == "LOGIN_ATTEMPT":
        username = event_data.get("username", "")
        if username:
            verdict = await evaluate_payload(username)
            classification = classifier.classify(username)
            is_malicious = (verdict == "BLOCK")
            
            classification.is_malicious = is_malicious
            classification.confidence = 0.99 if is_malicious else 0.01
            
            if is_malicious and classification.attack_type == AttackType.BENIGN:
                classification.attack_type = AttackType.BRUTE_FORCE
                
            if classification.is_malicious:
                classification_dict = {
                    "attack_type": classification.attack_type.value,
                    "confidence": classification.confidence,
                    "is_malicious": classification.is_malicious,
                }
                threat_score_system.calculate_threat_score(
                    attacker_ip, classification.attack_type, classification.is_malicious,
                )
                if classification.confidence > 0.85:
                    background_tasks.add_task(
                        alert_manager.trigger_critical_attack_alert,
                        ip_address=attacker_ip,
                        command=username,
                        score=classification.confidence,
                        session_id=None
                    )

    # Persist to PostgreSQL
    try:
        async with db.session_factory() as session:
            tenant = await get_default_tenant(session)
            tenant_id = str(tenant.id) if tenant else "00000000-0000-0000-0000-000000000000"
            log_meta = {
                "honeypot_event": event_type,
                "fingerprint_data": event_data,
                "user_agent": request.headers.get("user-agent", ""),
                "referer": request.headers.get("referer", ""),
            }
            if classification_dict:
                log_meta["classification"] = classification_dict
                
            log = HoneypotLog(
                tenant_id=tenant_id,
                attacker_ip=attacker_ip,
                command_entered=f"[HONEYPOT] {event_type}",
                response_sent="Decoy interaction logged",
                log_metadata=log_meta,
            )
            session.add(log)
            await session.commit()
    except Exception as e:
        logger.error("Failed to persist honeypot log: %s", e)

    return {"status": "logged"}


@app.get("/api/blockchain/verify")
async def verify_blockchain(username: str = Depends(verify_token)):
    integrity = blockchain_logger.verify_chain_integrity()
    return {"integrity": integrity, "chain_length": len(blockchain_logger.chain)}


# ========================================================================
# Threat Scores
# ========================================================================

@app.get("/api/threat-scores/")
async def list_all_threat_scores(username: str = Depends(verify_token)):
    """List all tracked IP reputation scores."""
    scores = []
    for ip, score in threat_score_system.ip_scores.items():
        level = threat_score_system.get_reputation_level(score)
        scores.append({
            "ip_address": ip,
            "score": score,
            "reputation_level": level,
        })
    scores.sort(key=lambda x: x["score"], reverse=True)
    return {"scores": scores, "total": len(scores)}


@app.get("/api/threat-scores/flagged")
async def get_flagged_ips(username: str = Depends(verify_token)):
    flagged = threat_score_system.get_flagged_ips(threshold=70)
    return {"flagged_ips": flagged, "count": len(flagged)}


@app.get("/api/threat-scores/top-threats")
async def get_top_threats(limit: int = 10, username: str = Depends(verify_token)):
    threats = threat_score_system.get_top_threats(limit=limit)
    return {"top_threats": threats, "count": len(threats)}


@app.get("/api/threat-scores/verify-chain")
async def verify_score_chain(username: str = Depends(verify_token)):
    integrity = threat_score_system.verify_chain_integrity()
    return {"integrity": integrity, "chain_length": len(threat_score_system.score_chain)}


@app.get("/api/threat-scores/blockchain")
async def get_blockchain_data(
    skip: int = 0, limit: int = 100,
    ip_address: Optional[str] = None,
    username: str = Depends(verify_token),
):
    chain = threat_score_system.score_chain
    if ip_address:
        chain = [b for b in chain if b.get("ip_address") == ip_address]
    total = len(chain)
    records = chain[skip : skip + limit]
    return {
        "total": total, "skip": skip, "limit": limit,
        "records": records,
        "chain_integrity": threat_score_system.verify_chain_integrity(),
    }


@app.get("/api/threat-scores/blockchain/block/{block_index}")
async def get_blockchain_block(block_index: int, username: str = Depends(verify_token)):
    if block_index < 0 or block_index >= len(threat_score_system.score_chain):
        raise HTTPException(status_code=404, detail="Block not found")
    block = threat_score_system.score_chain[block_index]
    is_valid = True
    if block_index > 0:
        prev = threat_score_system.score_chain[block_index - 1]
        is_valid = block["previous_hash"] == prev["hash"]
    return {
        "block_index": block_index, "block": block,
        "is_valid": is_valid,
        "total_blocks": len(threat_score_system.score_chain),
    }


@app.get("/api/threat-scores/blockchain/export")
async def export_blockchain(
    format: str = "json",
    ip_address: Optional[str] = None,
    username: str = Depends(verify_token),
):
    chain = threat_score_system.score_chain
    if ip_address:
        chain = [b for b in chain if b.get("ip_address") == ip_address]
    if format == "json":
        return {
            "blockchain": chain,
            "metadata": {
                "total_blocks": len(chain),
                "chain_integrity": threat_score_system.verify_chain_integrity(),
                "exported_at": datetime.utcnow().isoformat(),
                "filter_ip": ip_address,
            },
        }
    raise HTTPException(status_code=400, detail="Unsupported format")


@app.get("/api/threat-scores/analytics")
async def get_threat_analytics(username: str = Depends(verify_token)):
    chain = threat_score_system.score_chain
    total_ips = len(threat_score_system.ip_scores)
    score_distribution = {
        "TRUSTED": 0, "NEUTRAL": 0, "SUSPICIOUS": 0,
        "MALICIOUS": 0, "CRITICAL": 0,
    }
    for _, score in threat_score_system.ip_scores.items():
        level = threat_score_system.get_reputation_level(score)
        score_distribution[level] += 1
    attack_types: Dict[str, int] = {}
    ip_activity: Dict[str, int] = {}
    for block in chain:
        at = block.get("attack_type", "UNKNOWN")
        attack_types[at] = attack_types.get(at, 0) + 1
        bip = block.get("ip_address")
        ip_activity[bip] = ip_activity.get(bip, 0) + 1
    most_active = sorted(ip_activity.items(), key=lambda x: x[1], reverse=True)[:10]
    return {
        "total_ips_tracked": total_ips,
        "total_score_changes": len(chain),
        "score_distribution": score_distribution,
        "attack_type_distribution": attack_types,
        "most_active_ips": [{"ip": ip, "activity_count": c} for ip, c in most_active],
        "chain_integrity": threat_score_system.verify_chain_integrity(),
    }


@app.get("/api/threat-scores/{ip_address}")
async def get_ip_threat_score(ip_address: str, username: str = Depends(verify_token)):
    reputation = threat_score_system.get_ip_reputation(ip_address)
    history = threat_score_system.get_score_history(ip_address)
    return {"reputation": reputation, "history": history[:20]}


# ========================================================================
# Sessions
# ========================================================================

@app.get("/api/sessions/stats")
async def get_session_statistics(username: str = Depends(verify_token)):
    return await get_session_stats()


@app.get("/api/sessions/{fingerprint}")
async def get_session_details(fingerprint: str, username: str = Depends(verify_token)):
    from attacker_session import _session_store
    if fingerprint not in _session_store:
        raise HTTPException(status_code=404, detail="Session not found")
    return _session_store[fingerprint].model_dump()


@app.get("/api/sessions/ip/{ip_address}")
async def get_sessions_by_ip(ip_address: str, username: str = Depends(verify_token)):
    from attacker_session import _session_store
    matching = [s.model_dump() for s in _session_store.values()]
    return {"ip_address": ip_address, "sessions": matching[:10], "total_count": len(matching)}


# ========================================================================
# Threat Intelligence
# ========================================================================

@app.get("/api/threat-intel/reports")
async def get_threat_intel_reports(limit: int = 50, username: str = Depends(verify_token)):
    reports = threat_intel_service.get_threat_reports(limit=limit)
    return {"reports": reports, "count": len(reports)}


@app.get("/api/threat-intel/stats")
async def get_threat_intel_stats(username: str = Depends(verify_token)):
    return threat_intel_service.get_statistics()


@app.get("/api/threat-intel/feed")
async def get_threat_intel_feed(limit: int = 50, username: str = Depends(verify_token)):
    feed = threat_intel_service.get_threat_feed(limit=limit)
    return {
        "feed": feed, "count": len(feed),
        "statistics": threat_intel_service.get_statistics(),
    }


@app.get("/api/threat-intel/statistics")
async def get_threat_intel_statistics(username: str = Depends(verify_token)):
    return threat_intel_service.get_statistics()


@app.post("/api/threat-intel/verify-commitment")
async def verify_threat_commitment(
    payload: str, commitment: str, salt: str, timestamp: int,
    username: str = Depends(verify_token),
):
    commitment_data = {"commitment": commitment, "salt": salt, "timestamp": timestamp}
    is_valid = threat_intel_service.verify_commitment(payload, commitment_data)
    return {
        "valid": is_valid, "commitment": commitment,
        "verified_at": datetime.utcnow().isoformat(),
    }


# ========================================================================
# Health
# ========================================================================

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "ml_model": "chameleon_lstm_m4_50k",
        "device": str(predictor.device),
    }


# ========================================================================
# AI Chatbot
# ========================================================================

@app.post("/api/chatbot/chat", response_model=ChatResponse)
async def chat_with_bot(chat_message: ChatMessage, username: str = Depends(verify_token)):
    chatbot = get_chatbot(settings.GEMINI_API_KEY)
    result = await chatbot.chat(
        message=chat_message.message,
        use_search=chat_message.use_search,
        context=chat_message.context,
    )
    return ChatResponse(**result)


@app.get("/api/chatbot/history")
async def get_chat_history(limit: int = 50, username: str = Depends(verify_token)):
    chatbot = get_chatbot(settings.GEMINI_API_KEY)
    history = chatbot.get_chat_history(limit=limit)
    return {"history": history, "count": len(history)}


@app.post("/api/chatbot/clear-history")
async def clear_chat_history(username: str = Depends(verify_token)):
    chatbot = get_chatbot(settings.GEMINI_API_KEY)
    chatbot.clear_history()
    return {"success": True, "message": "Chat history cleared"}


@app.post("/api/chatbot/analyze-attack/{log_id}")
async def analyze_attack_with_ai(log_id: str, username: str = Depends(verify_token)):
    log = await get_attack_by_id(log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    chatbot = get_chatbot(settings.GEMINI_API_KEY)
    analysis = await chatbot.analyze_attack(log.model_dump())
    return {"log_id": log_id, "analysis": analysis, "timestamp": datetime.utcnow().isoformat()}


@app.post("/api/chatbot/suggest-response")
async def suggest_response_actions(
    threat_level: str, attack_type: str,
    username: str = Depends(verify_token),
):
    chatbot = get_chatbot(settings.GEMINI_API_KEY)
    suggestions = await chatbot.suggest_response(threat_level, attack_type)
    return {
        "threat_level": threat_level, "attack_type": attack_type,
        "suggestions": suggestions, "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/api/chatbot/search")
async def search_cybersecurity_info(
    query: str = Query(..., description="Search query"),
    max_results: int = Query(5, ge=1, le=10),
    username: str = Depends(verify_token),
):
    chatbot = get_chatbot(settings.GEMINI_API_KEY)
    results = chatbot.search_web(query, max_results=max_results)
    return {
        "query": query, "results": results,
        "count": len(results), "timestamp": datetime.utcnow().isoformat(),
    }


# ========================================================================
# Serve React Frontend (single-service deployment)
# ========================================================================

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

frontend_dist = os.path.join(os.path.dirname(__file__), "../frontend/dist")

if os.path.exists(frontend_dist):
    app.mount(
        "/assets",
        StaticFiles(directory=os.path.join(frontend_dist, "assets")),
        name="assets",
    )

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_react_app(full_path: str):
        """Serve React frontend for all non-API routes."""
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
else:
    logger.warning(
        "Frontend dist folder not found. Run 'npm run build' in frontend directory."
    )
