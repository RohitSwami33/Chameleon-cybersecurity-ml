from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import pymongo
from bson import ObjectId
import certifi

class Database:
    client: AsyncIOMotorClient = None

db = Database()

async def connect_to_mongo():
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)
    database = db.client[settings.DATABASE_NAME]
    
    # Create indexes
    await database.attack_logs.create_index([("timestamp", pymongo.DESCENDING)])
    await database.attack_logs.create_index([("ip_address", pymongo.ASCENDING)])
    await database.attack_logs.create_index([("classification.attack_type", pymongo.ASCENDING)])
    
    print("Connected to MongoDB")

async def close_mongo_connection():
    if db.client:
        db.client.close()
        print("Closed MongoDB connection")

def get_database():
    return db.client[settings.DATABASE_NAME]

async def save_attack_log(log_data: dict) -> str:
    database = get_database()
    result = await database.attack_logs.insert_one(log_data)
    return str(result.inserted_id)

async def get_attack_logs(skip: int, limit: int) -> List[dict]:
    database = get_database()
    cursor = database.attack_logs.find().sort("timestamp", pymongo.DESCENDING).skip(skip).limit(limit)
    logs = await cursor.to_list(length=limit)
    # Convert ObjectId to string for Pydantic compatibility if needed, 
    # but usually we handle this in the model or response. 
    # For now, just returning the dicts.
    for log in logs:
        log["id"] = str(log["_id"])
        del log["_id"]
    return logs

async def get_attack_by_id(log_id: str) -> Optional[dict]:
    database = get_database()
    try:
        log = await database.attack_logs.find_one({"_id": ObjectId(log_id)})
        if log:
            log["id"] = str(log["_id"])
            del log["_id"]
        return log
    except:
        return None

async def get_dashboard_stats() -> dict:
    database = get_database()
    
    total_attempts = await database.attack_logs.count_documents({})
    malicious_attempts = await database.attack_logs.count_documents({"classification.is_malicious": True})
    benign_attempts = await database.attack_logs.count_documents({"classification.is_malicious": False})
    
    # Aggregate attack distribution
    pipeline = [
        {"$group": {"_id": "$classification.attack_type", "count": {"$sum": 1}}}
    ]
    distribution_cursor = database.attack_logs.aggregate(pipeline)
    attack_distribution = {}
    async for doc in distribution_cursor:
        attack_distribution[doc["_id"]] = doc["count"]
        
    # Top attackers in last 24 hours
    last_24h = datetime.utcnow() - timedelta(hours=24)
    attacker_pipeline = [
        {"$match": {"timestamp": {"$gte": last_24h}, "classification.is_malicious": True}},
        {"$group": {
            "_id": "$ip_address", 
            "count": {"$sum": 1},
            "last_seen": {"$max": "$timestamp"}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    top_attackers_cursor = database.attack_logs.aggregate(attacker_pipeline)
    top_attackers = []
    async for doc in top_attackers_cursor:
        top_attackers.append({
            "ip": doc["_id"],
            "count": doc["count"],
            "last_seen": doc["last_seen"]
        })
        
    return {
        "total_attempts": total_attempts,
        "malicious_attempts": malicious_attempts,
        "benign_attempts": benign_attempts,
        "attack_distribution": attack_distribution,
        "top_attackers": top_attackers
    }

async def get_logs_by_ip(ip_address: str) -> List[dict]:
    database = get_database()
    cursor = database.attack_logs.find({"ip_address": ip_address}).sort("timestamp", pymongo.DESCENDING)
    logs = await cursor.to_list(length=None)
    for log in logs:
        log["id"] = str(log["_id"])
        del log["_id"]
    return logs
