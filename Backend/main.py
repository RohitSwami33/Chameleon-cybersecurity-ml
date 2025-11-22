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
    DeceptionResponse, DashboardStats, LoginRequest, LoginResponse
)
from auth import create_access_token, verify_token, verify_credentials
from database import (
    connect_to_mongo, close_mongo_connection, save_attack_log, 
    get_attack_logs, get_attack_by_id, get_dashboard_stats, 
    get_logs_by_ip
)
from ml_classifier import classifier
from deception_engine import deception_engine
from tarpit_manager import tarpit_manager
from blockchain_logger import blockchain_logger
from report_generator import report_generator
from login_rate_limiter import login_limiter
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

@app.post("/api/trap/submit", response_model=DeceptionResponse)
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
    
    # Generate Deception
    deception = deception_engine.generate_response(
        classification.attack_type, 
        delay
    )
    
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
    
    # Background logging
    background_tasks.add_task(log_attack, log_dict)
    
    # Return response with appropriate status code
    # We need to set the status code on the response object, but FastAPI 
    # allows returning a JSONResponse or just the model. 
    # To set status code dynamically, we can use Response parameter or raise HTTPException
    # But for deception, we want to return the body even if status is 401/500.
    # FastAPI's default behavior with return model is 200.
    # We can use a custom response class or just return the dict and let the client handle it.
    # However, the requirements say "Return DeceptionResponse with appropriate status code".
    # Let's use the Response object to set the status code.
    
    from fastapi import Response
    response = Response(
        content=log_entry.deception_response.model_dump_json(),
        media_type="application/json",
        status_code=deception.http_status
    )
    return response

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

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}
