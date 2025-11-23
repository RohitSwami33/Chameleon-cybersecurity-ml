from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import pymongo
from bson import ObjectId
import certifi
import logging

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    connected: bool = False

db = Database()

async def connect_to_mongo():
    """Connect to MongoDB with error handling"""
    try:
        # MongoDB connection with SSL workaround
        connection_url = settings.MONGODB_URL
        
        # Create client with relaxed SSL settings for compatibility
        db.client = AsyncIOMotorClient(
            connection_url,
            serverSelectionTimeoutMS=30000,
            connectTimeoutMS=30000,
            socketTimeoutMS=30000,
            tls=True,
            tlsInsecure=True  # Disable certificate and hostname verification
        )
        
        # Test the connection
        await db.client.admin.command('ping')
        
        database = db.client[settings.DATABASE_NAME]
        
        # Create indexes
        await database.attack_logs.create_index([("timestamp", pymongo.DESCENDING)])
        await database.attack_logs.create_index([("ip_address", pymongo.ASCENDING)])
        await database.attack_logs.create_index([("classification.attack_type", pymongo.ASCENDING)])
        
        db.connected = True
        print("✅ Connected to MongoDB successfully")
        logger.info("Connected to MongoDB")
        
    except Exception as e:
        db.connected = False
        print(f"⚠️  WARNING: Could not connect to MongoDB: {e}")
        print("⚠️  The application will run in LIMITED MODE without database persistence")
        print("⚠️  To fix: Install MongoDB or use MongoDB Atlas")
        print("   - Local: https://www.mongodb.com/try/download/community")
        print("   - Cloud: https://www.mongodb.com/cloud/atlas (FREE)")
        logger.warning(f"MongoDB connection failed: {e}")

async def close_mongo_connection():
    if db.client:
        db.client.close()
        print("Closed MongoDB connection")

def get_database():
    if not db.connected:
        return None
    return db.client[settings.DATABASE_NAME]

async def save_attack_log(log_data: dict) -> str:
    """Save attack log to MongoDB (if connected)"""
    if not db.connected:
        logger.warning("MongoDB not connected - attack log not saved")
        return "no-db-connection"
    
    try:
        database = get_database()
        result = await database.attack_logs.insert_one(log_data)
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error saving attack log: {e}")
        return "error"

async def get_attack_logs(skip: int, limit: int) -> List[dict]:
    """Get attack logs from MongoDB (returns empty list if not connected)"""
    if not db.connected:
        return []
    
    try:
        database = get_database()
        cursor = database.attack_logs.find().sort("timestamp", pymongo.DESCENDING).skip(skip).limit(limit)
        logs = await cursor.to_list(length=limit)
        
        for log in logs:
            log["id"] = str(log["_id"])
            del log["_id"]
        return logs
    except Exception as e:
        logger.error(f"Error fetching attack logs: {e}")
        return []

async def get_attack_by_id(log_id: str) -> Optional[dict]:
    """Get specific attack log by ID"""
    if not db.connected:
        return None
    
    try:
        database = get_database()
        log = await database.attack_logs.find_one({"_id": ObjectId(log_id)})
        if log:
            log["id"] = str(log["_id"])
            del log["_id"]
        return log
    except Exception as e:
        logger.error(f"Error fetching attack by ID: {e}")
        return None

async def get_dashboard_stats() -> dict:
    """Get dashboard statistics (returns defaults if MongoDB not connected)"""
    if not db.connected:
        return {
            "total_attempts": 0,
            "malicious_attempts": 0,
            "benign_attempts": 0,
            "attack_distribution": {},
            "top_attackers": [],
            "geo_locations": []
        }
    
    try:
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
        
        # Geographic distribution of attacks
        geo_pipeline = [
            {"$match": {"geo_location": {"$ne": None}, "classification.is_malicious": True}},
            {"$group": {
                "_id": {
                    "country": "$geo_location.country",
                    "city": "$geo_location.city",
                    "latitude": "$geo_location.latitude",
                    "longitude": "$geo_location.longitude"
                },
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 50}
        ]
        geo_cursor = database.attack_logs.aggregate(geo_pipeline)
        geo_locations = []
        async for doc in geo_cursor:
            if doc["_id"]["country"]:
                geo_locations.append({
                    "country": doc["_id"]["country"],
                    "city": doc["_id"]["city"],
                    "latitude": doc["_id"]["latitude"],
                    "longitude": doc["_id"]["longitude"],
                    "count": doc["count"]
                })
            
        return {
            "total_attempts": total_attempts,
            "malicious_attempts": malicious_attempts,
            "benign_attempts": benign_attempts,
            "attack_distribution": attack_distribution,
            "top_attackers": top_attackers,
            "geo_locations": geo_locations
        }
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {e}")
        return {
            "total_attempts": 0,
            "malicious_attempts": 0,
            "benign_attempts": 0,
            "attack_distribution": {},
            "top_attackers": [],
            "geo_locations": []
        }

async def get_logs_by_ip(ip_address: str) -> List[dict]:
    """Get all logs for a specific IP address"""
    if not db.connected:
        return []
    
    try:
        database = get_database()
        cursor = database.attack_logs.find({"ip_address": ip_address}).sort("timestamp", pymongo.DESCENDING)
        logs = await cursor.to_list(length=None)
        for log in logs:
            log["id"] = str(log["_id"])
            del log["_id"]
        return logs
    except Exception as e:
        logger.error(f"Error fetching logs by IP: {e}")
        return []
