from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Dict, Any, List
import uuid
from datetime import datetime

# Adjust imports to your structure
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database_postgres import get_db, get_default_tenant
from models_sqlalchemy import HoneypotLog
from auth import verify_token

stix_router = APIRouter()

def create_stix_bundle(logs: List[HoneypotLog]) -> Dict[str, Any]:
    """
    Converts a list of HoneypotLog objects into a STIX 2.1 Bundle.
    """
    objects = []
    
    # 1. Identity (The Honeypot System itself)
    identity_id = f"identity--{uuid.uuid5(uuid.NAMESPACE_URL, 'chameleon.honeypot')}"
    objects.append({
        "type": "identity",
        "spec_version": "2.1",
        "id": identity_id,
        "created": datetime.utcnow().isoformat() + "Z",
        "modified": datetime.utcnow().isoformat() + "Z",
        "name": "Chameleon Honeypot System",
        "identity_class": "system"
    })
    
    # 2. Process each log as an observed IPv4 indicator and a corresponding Incident/Sighting
    for log in logs:
        # Indicator for the attacker IP
        indicator_id = f"indicator--{uuid.uuid4()}"
        objects.append({
            "type": "indicator",
            "spec_version": "2.1",
            "id": indicator_id,
            "created": log.timestamp.isoformat() + "Z",
            "modified": log.timestamp.isoformat() + "Z",
            "name": "Malicious IP Connection",
            "description": f"Automated honeypot detection. Command entered: {log.command_entered}",
            "pattern": f"[ipv4-addr:value = '{log.attacker_ip}']",
            "pattern_type": "stix",
            "valid_from": log.timestamp.isoformat() + "Z"
        })
        
        # Attack Pattern (if applicable)
        if log.log_metadata.get("is_malicious"):
            attack_pattern_id = f"attack-pattern--{uuid.uuid4()}"
            objects.append({
                "type": "attack-pattern",
                "spec_version": "2.1",
                "id": attack_pattern_id,
                "created": log.timestamp.isoformat() + "Z",
                "modified": log.timestamp.isoformat() + "Z",
                "name": "Honeypot Exploitation Attempt",
                "description": log.command_entered
            })
            
            # Sighting linking the indicator to the attack pattern
            objects.append({
                "type": "sighting",
                "spec_version": "2.1",
                "id": f"sighting--{uuid.uuid4()}",
                "created": log.timestamp.isoformat() + "Z",
                "modified": log.timestamp.isoformat() + "Z",
                "sighting_of_ref": indicator_id,
                "where_sighted_refs": [identity_id]
            })

    # 3. Wrap everything in a STIX 2.1 Bundle
    bundle = {
        "type": "bundle",
        "id": f"bundle--{uuid.uuid4()}",
        "objects": objects
    }
    
    return bundle


@stix_router.get("/stix")
async def export_stix(
    limit: int = Query(100, ge=1, le=1000),
    username: str = Depends(verify_token),
    session: AsyncSession = Depends(get_db)
):
    """
    Exports the latest Honeypot logs in STIX 2.1 JSON format for SIEM ingestion.
    Requires Authentication via JWT token.
    """
    tenant = await get_default_tenant(session)
    if not tenant:
        raise HTTPException(status_code=404, detail="No tenant found")

    stmt = select(HoneypotLog).where(
        HoneypotLog.tenant_id == tenant.id
    ).order_by(HoneypotLog.timestamp.desc()).limit(limit)
    
    result = await session.execute(stmt)
    logs = result.scalars().all()
    
    if not logs:
        return {
            "type": "bundle",
            "id": f"bundle--{uuid.uuid4()}",
            "objects": []
        }
        
    return create_stix_bundle(logs)
