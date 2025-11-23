from fastapi import FastAPI, Request, BackgroundTasks, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import httpx
from datetime import datetime
from typing import List, Optional
from io import BytesIO

from config import settings
from models import (
    UserInput, AttackLog, GeoLocation, ClassificationResult, 
    DeceptionResponse, DashboardStats, LoginRequest, LoginResponse,
    AttackType
)
from pydantic import BaseModel

# Chatbot models
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
from auth import create_access_token, verify_token, verify_credentials
from database import (
    connect_to_mongo, close_mongo_connection, save_attack_log, 
    get_attack_logs, get_attack_by_id, get_dashboard_stats, 
    get_logs_by_ip
)
from ml_classifier import classifier
from deception_engine import deception_engine
from deception_engine_v2 import progressive_deception_engine
from attacker_session import (
    get_or_create_session, 
    update_session, 
    generate_attacker_fingerprint,
    get_session_stats
)
from tarpit_manager import tarpit_manager
from blockchain_logger import blockchain_logger
from report_generator import report_generator
from login_rate_limiter import login_limiter
from threat_score import threat_score_system
from threat_intel_service import threat_intel_service
from chatbot_service import get_chatbot
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(
    title="Chameleon Adaptive Deception System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration - Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default dev server
        "http://localhost:5174",  # Alternative Vite port
        "http://localhost:3000",  # React default
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:3000",
        "https://*.onrender.com",  # Render deployment
        "https://chameleon-frontend.onrender.com",  # Production frontend
        "*"  # Allow all origins (for development)
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    return request.client.host

async def fetch_geo_location(ip: str) -> Optional[GeoLocation]:
    if ip in ["127.0.0.1", "localhost", "::1"]:
        return None
        
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.GEOIP_API_URL}{ip}")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    return GeoLocation(
                        country=data.get("country"),
                        region=data.get("regionName"),
                        city=data.get("city"),
                        latitude=data.get("lat"),
                        longitude=data.get("lon"),
                        isp=data.get("isp")
                    )
    except Exception as e:
        print(f"GeoIP error: {e}")
    return None

async def log_attack(log_data: dict):
    # Add to blockchain
    block_info = blockchain_logger.add_block(log_data)
    log_data["hash"] = block_info["hash"]
    log_data["previous_hash"] = block_info["previous_hash"]
    
    # Save to DB
    await save_attack_log(log_data)

@app.post("/api/trap/submit")
async def submit_trap(user_input: UserInput, request: Request, background_tasks: BackgroundTasks):
    ip = user_input.ip_address or get_client_ip(request)
    user_agent = user_input.user_agent or request.headers.get("User-Agent")
    
    # Check if blocked
    if tarpit_manager.is_blocked(ip):
        # Even if blocked, we might want to return a standard error or just delay heavily
        # For now, let's just continue but with max delay implied by the tarpit logic
        pass

    # Tarpit logic
    is_tarpit, delay = tarpit_manager.record_request(ip)
    if is_tarpit and delay > 0:
        await asyncio.sleep(delay)
        
    # Classification
    classification = classifier.classify(user_input.input_text)
    
    # Geo Location
    geo_location = await fetch_geo_location(ip)
    
    # === PROGRESSIVE DECEPTION ENGINE V2 ===
    # Get or create attacker session
    session = await get_or_create_session(ip, user_agent, classification.attack_type.value)
    
    # Generate progressive, context-aware deceptive response
    progressive_message = await progressive_deception_engine.generate_progressive_response(
        classification.attack_type,
        user_input.input_text,
        session
    )
    
    # Determine HTTP status code based on attack type and stage
    http_status = 200
    if classification.attack_type == AttackType.SQLI:
        http_status = 500  # Internal Server Error for SQL errors
    elif classification.attack_type == AttackType.SSI:
        http_status = 403  # Forbidden for SSI attempts
    elif classification.attack_type == AttackType.BRUTE_FORCE:
        http_status = 401  # Unauthorized for auth failures
    elif classification.attack_type == AttackType.XSS:
        http_status = 200  # Success to make attacker think it worked (but it didn't)
    
    # Create deception response with progressive message
    deception = DeceptionResponse(
        message=progressive_message,
        delay_applied=delay,
        http_status=http_status
    )
    
    # Update session with this attempt
    await update_session(
        session,
        user_input.input_text,
        progressive_message,
        classification.attack_type.value
    )
    
    # Calculate threat score for this IP
    threat_score = threat_score_system.calculate_threat_score(
        ip,
        classification.attack_type,
        classification.is_malicious
    )
    
    # Get reputation info
    reputation = threat_score_system.get_ip_reputation(ip)
    
    # Create Log
    log_entry = AttackLog(
        timestamp=datetime.utcnow(),
        raw_input=user_input.input_text,
        ip_address=ip,
        user_agent=user_agent,
        geo_location=geo_location,
        classification=classification,
        deception_response=deception
    )
    
    # Convert to dict for storage
    log_dict = log_entry.model_dump()
    
    # === THREAT INTELLIGENCE SHARING ===
    # Check if this is a novel attack and create threat report
    if classification.is_malicious and threat_intel_service.is_novel_attack(
        user_input.input_text, 
        classification.attack_type
    ):
        threat_report = threat_intel_service.create_threat_report(
            user_input.input_text,
            classification.attack_type,
            ip,
            classification.confidence
        )
        if threat_report:
            print(f"🔔 Novel attack detected! Created threat intelligence report: {threat_report['pattern_hash'][:16]}...")
    
    # Background logging
    background_tasks.add_task(log_attack, log_dict)
    
    # === PRIVACY-PRESERVING THREAT INTELLIGENCE ===
    # Generate threat intel report for novel malicious attacks
    if classification.is_malicious and classification.attack_type in [AttackType.SQLI, AttackType.XSS]:
        if threat_intel_service.is_novel_attack(user_input.input_text):
            # Create privacy-preserving threat intelligence report
            threat_report = threat_intel_service.create_threat_intel_report(
                attack_type=classification.attack_type.value,
                payload=user_input.input_text,
                confidence=classification.confidence,
                timestamp=log_entry.timestamp
            )
            print(f"🔒 Generated privacy-preserving threat intel report: {threat_report['id']}")
    
    # Return response with appropriate status code
    from fastapi.responses import JSONResponse
    return JSONResponse(
        content=deception.model_dump(),
        status_code=deception.http_status
    )

@app.post("/api/auth/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, request: Request, background_tasks: BackgroundTasks):
    # Get client IP and user agent
    ip = get_client_ip(request)
    user_agent = request.headers.get("User-Agent")
    
    # Check if already rate limited
    if login_limiter.is_rate_limited(ip):
        # Log the blocked brute force attempt
        log_entry = AttackLog(
            timestamp=datetime.utcnow(),
            raw_input=f"Blocked login attempt - Username: {login_data.username}",
            ip_address=ip,
            user_agent=user_agent,
            geo_location=None,
            classification=ClassificationResult(
                attack_type="BRUTE_FORCE",
                confidence=1.0,
                is_malicious=True
            ),
            deception_response=DeceptionResponse(
                message="Too many login attempts. Account temporarily locked.",
                delay_applied=0,
                http_status=429
            )
        )
        background_tasks.add_task(log_attack, log_entry.model_dump())
        
        raise HTTPException(
            status_code=429,
            detail="Too many login attempts. Please try again later."
        )
    
    # Record this login attempt
    is_brute_force = login_limiter.record_attempt(ip)
    
    # If brute force detected, log and block
    if is_brute_force:
        # Log the brute force detection
        log_entry = AttackLog(
            timestamp=datetime.utcnow(),
            raw_input=f"Brute force detected - Username: {login_data.username}",
            ip_address=ip,
            user_agent=user_agent,
            geo_location=None,
            classification=ClassificationResult(
                attack_type="BRUTE_FORCE",
                confidence=1.0,
                is_malicious=True
            ),
            deception_response=DeceptionResponse(
                message="Brute force attack detected. Account temporarily locked.",
                delay_applied=0,
                http_status=429
            )
        )
        background_tasks.add_task(log_attack, log_entry.model_dump())
        
        raise HTTPException(
            status_code=429,
            detail="Brute force attack detected. Account temporarily locked."
        )
    
    # Verify credentials
    if not verify_credentials(login_data.username, login_data.password):
        # Failed login - log the failed attempt
        log_entry = AttackLog(
            timestamp=datetime.utcnow(),
            raw_input=f"Failed login - Username: {login_data.username}",
            ip_address=ip,
            user_agent=user_agent,
            geo_location=None,
            classification=ClassificationResult(
                attack_type="BENIGN",  # Single failed login is benign
                confidence=0.5,
                is_malicious=False
            ),
            deception_response=DeceptionResponse(
                message="Incorrect username or password",
                delay_applied=0,
                http_status=401
            )
        )
        background_tasks.add_task(log_attack, log_entry.model_dump())
        
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
    
    # Successful login - reset attempts for this IP
    login_limiter.reset_attempts(ip)
    
    access_token = create_access_token(data={"sub": login_data.username})
    return LoginResponse(access_token=access_token)



@app.get("/api/dashboard/stats", response_model=DashboardStats)
async def get_stats(username: str = Depends(verify_token)):
    stats = await get_dashboard_stats()
    
    # Calculate Merkle Root for recent logs
    recent_logs = await get_attack_logs(0, 100)
    merkle_root = blockchain_logger.get_merkle_root_for_recent_logs(recent_logs)
    stats["merkle_root"] = merkle_root
    
    # Add threat score statistics
    flagged_ips = threat_score_system.get_flagged_ips(threshold=70)
    top_threats = threat_score_system.get_top_threats(limit=5)
    
    stats["flagged_ips_count"] = len(flagged_ips)
    stats["top_threats"] = top_threats
    
    return stats

@app.get("/api/dashboard/logs", response_model=List[AttackLog])
async def get_logs(skip: int = 0, limit: int = 50, username: str = Depends(verify_token)):
    logs = await get_attack_logs(skip, limit)
    return logs

@app.get("/api/dashboard/logs/{log_id}", response_model=AttackLog)
async def get_log(log_id: str, username: str = Depends(verify_token)):
    log = await get_attack_by_id(log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log

@app.get("/api/dashboard/logs/ip/{ip_address}", response_model=List[AttackLog])
async def get_ip_logs(ip_address: str, username: str = Depends(verify_token)):
    logs = await get_logs_by_ip(ip_address)
    return logs

@app.post("/api/reports/generate/{ip_address}")
async def generate_report(ip_address: str, username: str = Depends(verify_token)):
    logs = await get_logs_by_ip(ip_address)
    stats = await get_dashboard_stats()
    
    pdf_bytes = report_generator.generate_incident_report(ip_address, logs, stats)
    
    filename = f"incident_report_{ip_address}_{int(datetime.utcnow().timestamp())}.pdf"
    
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/api/blockchain/verify")
async def verify_blockchain(username: str = Depends(verify_token)):
    integrity = blockchain_logger.verify_chain_integrity()
    return {
        "integrity": integrity,
        "chain_length": len(blockchain_logger.chain)
    }

@app.get("/api/threat-scores/flagged")
async def get_flagged_ips(username: str = Depends(verify_token)):
    """Get all flagged IPs with low threat scores"""
    flagged = threat_score_system.get_flagged_ips(threshold=70)
    return {"flagged_ips": flagged, "count": len(flagged)}

@app.get("/api/threat-scores/top-threats")
async def get_top_threats(limit: int = 10, username: str = Depends(verify_token)):
    """Get top threat IPs"""
    threats = threat_score_system.get_top_threats(limit=limit)
    return {"top_threats": threats, "count": len(threats)}

@app.get("/api/threat-scores/verify-chain")
async def verify_score_chain(username: str = Depends(verify_token)):
    """Verify integrity of threat score blockchain"""
    integrity = threat_score_system.verify_chain_integrity()
    return {
        "integrity": integrity,
        "chain_length": len(threat_score_system.score_chain)
    }

@app.get("/api/threat-scores/blockchain")
async def get_blockchain_data(
    skip: int = 0, 
    limit: int = 100,
    ip_address: Optional[str] = None,
    username: str = Depends(verify_token)
):
    """Get blockchain records with optional IP filtering"""
    chain = threat_score_system.score_chain
    
    # Filter by IP if specified
    if ip_address:
        chain = [block for block in chain if block.get("ip_address") == ip_address]
    
    # Paginate
    total = len(chain)
    records = chain[skip:skip + limit]
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "records": records,
        "chain_integrity": threat_score_system.verify_chain_integrity()
    }

@app.get("/api/threat-scores/blockchain/block/{block_index}")
async def get_blockchain_block(block_index: int, username: str = Depends(verify_token)):
    """Get specific blockchain block by index"""
    if block_index < 0 or block_index >= len(threat_score_system.score_chain):
        raise HTTPException(status_code=404, detail="Block not found")
    
    block = threat_score_system.score_chain[block_index]
    
    # Add verification info
    is_valid = True
    if block_index > 0:
        previous_block = threat_score_system.score_chain[block_index - 1]
        is_valid = block["previous_hash"] == previous_block["hash"]
    
    return {
        "block_index": block_index,
        "block": block,
        "is_valid": is_valid,
        "total_blocks": len(threat_score_system.score_chain)
    }

@app.get("/api/threat-scores/blockchain/export")
async def export_blockchain(
    format: str = "json",
    ip_address: Optional[str] = None,
    username: str = Depends(verify_token)
):
    """Export blockchain data in various formats"""
    chain = threat_score_system.score_chain
    
    # Filter by IP if specified
    if ip_address:
        chain = [block for block in chain if block.get("ip_address") == ip_address]
    
    if format == "json":
        return {
            "blockchain": chain,
            "metadata": {
                "total_blocks": len(chain),
                "chain_integrity": threat_score_system.verify_chain_integrity(),
                "exported_at": datetime.utcnow().isoformat(),
                "filter_ip": ip_address
            }
        }
    else:
        raise HTTPException(status_code=400, detail="Unsupported format")

@app.get("/api/threat-scores/analytics")
async def get_threat_analytics(username: str = Depends(verify_token)):
    """Get comprehensive threat analytics"""
    chain = threat_score_system.score_chain
    
    # Calculate statistics
    total_ips = len(threat_score_system.ip_scores)
    total_score_changes = len(chain)
    
    # Score distribution
    score_distribution = {
        "TRUSTED": 0,
        "NEUTRAL": 0,
        "SUSPICIOUS": 0,
        "MALICIOUS": 0,
        "CRITICAL": 0
    }
    
    for ip, score in threat_score_system.ip_scores.items():
        level = threat_score_system.get_reputation_level(score)
        score_distribution[level] += 1
    
    # Attack type distribution
    attack_types = {}
    for block in chain:
        attack_type = block.get("attack_type", "UNKNOWN")
        attack_types[attack_type] = attack_types.get(attack_type, 0) + 1
    
    # Most active IPs
    ip_activity = {}
    for block in chain:
        ip = block.get("ip_address")
        ip_activity[ip] = ip_activity.get(ip, 0) + 1
    
    most_active = sorted(ip_activity.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "total_ips_tracked": total_ips,
        "total_score_changes": total_score_changes,
        "score_distribution": score_distribution,
        "attack_type_distribution": attack_types,
        "most_active_ips": [
            {"ip": ip, "activity_count": count} for ip, count in most_active
        ],
        "chain_integrity": threat_score_system.verify_chain_integrity()
    }

@app.get("/api/threat-scores/{ip_address}")
async def get_ip_threat_score(ip_address: str, username: str = Depends(verify_token)):
    """Get threat score and reputation for specific IP"""
    reputation = threat_score_system.get_ip_reputation(ip_address)
    history = threat_score_system.get_score_history(ip_address)
    return {
        "reputation": reputation,
        "history": history[:20]  # Last 20 changes
    }

@app.get("/api/sessions/stats")
async def get_session_statistics(username: str = Depends(verify_token)):
    """Get statistics about active attacker sessions"""
    stats = await get_session_stats()
    return stats

@app.get("/api/sessions/{fingerprint}")
async def get_session_details(fingerprint: str, username: str = Depends(verify_token)):
    """Get detailed information about a specific attacker session"""
    from attacker_session import _session_store
    
    if fingerprint not in _session_store:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = _session_store[fingerprint]
    return session.model_dump()

@app.get("/api/sessions/ip/{ip_address}")
async def get_sessions_by_ip(ip_address: str, username: str = Depends(verify_token)):
    """Get all sessions for a specific IP address"""
    from attacker_session import _session_store, generate_attacker_fingerprint
    
    # Find all sessions matching this IP
    matching_sessions = []
    for session in _session_store.values():
        # Check if this session's fingerprint starts with the IP hash
        # This is a simplified check - in production you'd want better tracking
        matching_sessions.append(session.model_dump())
    
    return {
        "ip_address": ip_address,
        "sessions": matching_sessions[:10],  # Limit to 10 most recent
        "total_count": len(matching_sessions)
    }

@app.get("/api/threat-intel/reports")
async def get_threat_intel_reports(
    limit: int = 50,
    username: str = Depends(verify_token)
):
    """Get recent threat intelligence reports"""
    reports = threat_intel_service.get_threat_reports(limit=limit)
    return {
        "reports": reports,
        "count": len(reports)
    }

@app.get("/api/threat-intel/stats")
async def get_threat_intel_stats(username: str = Depends(verify_token)):
    """Get threat intelligence statistics"""
    stats = threat_intel_service.get_statistics()
    return stats

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}


# ============================================================================
# PRIVACY-PRESERVING THREAT INTELLIGENCE ENDPOINTS
# ============================================================================

@app.get("/api/threat-intel/feed")
async def get_threat_intel_feed(
    limit: int = 50,
    username: str = Depends(verify_token)
):
    """
    Get the privacy-preserving threat intelligence feed.
    
    This feed contains cryptographic commitments to novel attacks
    without revealing sensitive payload data.
    """
    feed = threat_intel_service.get_threat_feed(limit=limit)
    return {
        "feed": feed,
        "count": len(feed),
        "statistics": threat_intel_service.get_statistics()
    }

@app.get("/api/threat-intel/statistics")
async def get_threat_intel_statistics(username: str = Depends(verify_token)):
    """Get threat intelligence service statistics"""
    return threat_intel_service.get_statistics()

@app.post("/api/threat-intel/verify-commitment")
async def verify_threat_commitment(
    payload: str,
    commitment: str,
    salt: str,
    timestamp: int,
    username: str = Depends(verify_token)
):
    """
    Verify that a payload matches a cryptographic commitment.
    
    This allows consortium members to verify threat intelligence
    without the original reporter revealing the payload publicly.
    """
    commitment_data = {
        "commitment": commitment,
        "salt": salt,
        "timestamp": timestamp
    }
    
    is_valid = threat_intel_service.verify_commitment(payload, commitment_data)
    
    return {
        "valid": is_valid,
        "commitment": commitment,
        "verified_at": datetime.utcnow().isoformat()
    }


# ============================================================================
# AI CHATBOT ENDPOINTS
# ============================================================================

@app.post("/api/chatbot/chat", response_model=ChatResponse)
async def chat_with_bot(
    chat_message: ChatMessage,
    username: str = Depends(verify_token)
):
    """
    Chat with the AI cybersecurity assistant
    
    Features:
    - Gemini AI for intelligent responses
    - DuckDuckGo search for current threat intelligence
    - Context-aware responses based on system data
    """
    # Get chatbot instance with API key from settings
    chatbot = get_chatbot(settings.GEMINI_API_KEY)
    
    # Process the message
    result = await chatbot.chat(
        message=chat_message.message,
        use_search=chat_message.use_search,
        context=chat_message.context
    )
    
    return ChatResponse(**result)

@app.get("/api/chatbot/history")
async def get_chat_history(
    limit: int = 50,
    username: str = Depends(verify_token)
):
    """Get chat history"""
    chatbot = get_chatbot(settings.GEMINI_API_KEY)
    history = chatbot.get_chat_history(limit=limit)
    return {"history": history, "count": len(history)}

@app.post("/api/chatbot/clear-history")
async def clear_chat_history(username: str = Depends(verify_token)):
    """Clear chat history"""
    chatbot = get_chatbot(settings.GEMINI_API_KEY)
    chatbot.clear_history()
    return {"success": True, "message": "Chat history cleared"}

@app.post("/api/chatbot/analyze-attack/{log_id}")
async def analyze_attack_with_ai(
    log_id: str,
    username: str = Depends(verify_token)
):
    """Use AI to analyze a specific attack log"""
    # Get the attack log
    log = await get_attack_by_id(log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    
    # Get chatbot and analyze
    chatbot = get_chatbot(settings.GEMINI_API_KEY)
    analysis = await chatbot.analyze_attack(log.model_dump())
    
    return {
        "log_id": log_id,
        "analysis": analysis,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/chatbot/suggest-response")
async def suggest_response_actions(
    threat_level: str,
    attack_type: str,
    username: str = Depends(verify_token)
):
    """Get AI suggestions for responding to a threat"""
    chatbot = get_chatbot(settings.GEMINI_API_KEY)
    suggestions = await chatbot.suggest_response(threat_level, attack_type)
    
    return {
        "threat_level": threat_level,
        "attack_type": attack_type,
        "suggestions": suggestions,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/chatbot/search")
async def search_cybersecurity_info(
    query: str = Query(..., description="Search query"),
    max_results: int = Query(5, ge=1, le=10),
    username: str = Depends(verify_token)
):
    """Search DuckDuckGo for cybersecurity information"""
    chatbot = get_chatbot(settings.GEMINI_API_KEY)
    results = chatbot.search_web(query, max_results=max_results)
    
    return {
        "query": query,
        "results": results,
        "count": len(results),
        "timestamp": datetime.utcnow().isoformat()
    }
