#!/usr/bin/env python3
"""Add dummy attack data to MongoDB for testing"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone, timedelta
import sys
import os

# Add Backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Backend'))

from utils import get_current_time

# MongoDB connection
MONGODB_URL = "mongodb+srv://privatestudent33_db_user:sOTfe7nQeesfAsGF@cluster0.fuhrxya.mongodb.net/chameleon_db?retryWrites=true&w=majority"

async def add_dummy_data():
    """Add dummy attack logs to MongoDB"""
    
    print("🔌 Connecting to MongoDB...")
    try:
        client = AsyncIOMotorClient(
            MONGODB_URL,
            serverSelectionTimeoutMS=30000,
            tls=True,
            tlsInsecure=True
        )
        
        # Test connection
        await client.admin.command('ping')
        print("✅ Connected to MongoDB successfully!")
        
        db = client.chameleon_db
        
        # Dummy attack data
        dummy_attacks = [
            {
                "timestamp": get_current_time(),
                "raw_input": "admin' OR '1'='1",
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "geo_location": {
                    "country": "United States",
                    "region": "California",
                    "city": "San Francisco",
                    "latitude": 37.7749,
                    "longitude": -122.4194,
                    "isp": "Comcast Cable"
                },
                "classification": {
                    "attack_type": "SQLI",
                    "confidence": 0.95,
                    "is_malicious": True
                },
                "deception_response": {
                    "message": "Error 1064: You have an error in your SQL syntax",
                    "delay_applied": 2.5,
                    "http_status": 500
                }
            },
            {
                "timestamp": get_current_time() - timedelta(minutes=5),
                "raw_input": "<script>alert('XSS')</script>",
                "ip_address": "10.0.0.50",
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                "geo_location": {
                    "country": "India",
                    "region": "Maharashtra",
                    "city": "Mumbai",
                    "latitude": 19.0760,
                    "longitude": 72.8777,
                    "isp": "Reliance Jio"
                },
                "classification": {
                    "attack_type": "XSS",
                    "confidence": 0.92,
                    "is_malicious": True
                },
                "deception_response": {
                    "message": "Input sanitized. Potential XSS detected.",
                    "delay_applied": 1.8,
                    "http_status": 200
                }
            },
            {
                "timestamp": get_current_time() - timedelta(minutes=10),
                "raw_input": "<!--#exec cmd=\"ls\"-->",
                "ip_address": "172.16.0.25",
                "user_agent": "curl/7.68.0",
                "geo_location": {
                    "country": "China",
                    "region": "Beijing",
                    "city": "Beijing",
                    "latitude": 39.9042,
                    "longitude": 116.4074,
                    "isp": "China Telecom"
                },
                "classification": {
                    "attack_type": "SSI",
                    "confidence": 0.88,
                    "is_malicious": True
                },
                "deception_response": {
                    "message": "Server-side includes are disabled",
                    "delay_applied": 3.2,
                    "http_status": 403
                }
            },
            {
                "timestamp": get_current_time() - timedelta(minutes=15),
                "raw_input": "admin",
                "ip_address": "203.0.113.45",
                "user_agent": "Python-requests/2.28.0",
                "geo_location": {
                    "country": "Russia",
                    "region": "Moscow",
                    "city": "Moscow",
                    "latitude": 55.7558,
                    "longitude": 37.6173,
                    "isp": "Rostelecom"
                },
                "classification": {
                    "attack_type": "BRUTE_FORCE",
                    "confidence": 0.75,
                    "is_malicious": True
                },
                "deception_response": {
                    "message": "Invalid credentials",
                    "delay_applied": 5.0,
                    "http_status": 401
                }
            },
            {
                "timestamp": get_current_time() - timedelta(minutes=20),
                "raw_input": "Hello, how are you?",
                "ip_address": "198.51.100.10",
                "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X)",
                "geo_location": {
                    "country": "United Kingdom",
                    "region": "England",
                    "city": "London",
                    "latitude": 51.5074,
                    "longitude": -0.1278,
                    "isp": "British Telecom"
                },
                "classification": {
                    "attack_type": "BENIGN",
                    "confidence": 0.0,
                    "is_malicious": False
                },
                "deception_response": {
                    "message": "Request processed successfully",
                    "delay_applied": 0.0,
                    "http_status": 200
                }
            },
            {
                "timestamp": get_current_time() - timedelta(hours=1),
                "raw_input": "' UNION SELECT username, password FROM users--",
                "ip_address": "192.168.1.100",
                "user_agent": "sqlmap/1.6.12",
                "geo_location": {
                    "country": "United States",
                    "region": "California",
                    "city": "San Francisco",
                    "latitude": 37.7749,
                    "longitude": -122.4194,
                    "isp": "Comcast Cable"
                },
                "classification": {
                    "attack_type": "SQLI",
                    "confidence": 0.98,
                    "is_malicious": True
                },
                "deception_response": {
                    "message": "Database error: Table 'users' doesn't exist",
                    "delay_applied": 4.5,
                    "http_status": 500
                }
            },
            {
                "timestamp": get_current_time() - timedelta(hours=2),
                "raw_input": "<img src=x onerror=alert(document.cookie)>",
                "ip_address": "10.0.0.50",
                "user_agent": "Burp Suite Professional",
                "geo_location": {
                    "country": "India",
                    "region": "Maharashtra",
                    "city": "Mumbai",
                    "latitude": 19.0760,
                    "longitude": 72.8777,
                    "isp": "Reliance Jio"
                },
                "classification": {
                    "attack_type": "XSS",
                    "confidence": 0.94,
                    "is_malicious": True
                },
                "deception_response": {
                    "message": "Input blocked: Potential XSS detected",
                    "delay_applied": 2.1,
                    "http_status": 200
                }
            }
        ]
        
        print(f"\n📝 Inserting {len(dummy_attacks)} dummy attack logs...")
        result = await db.attack_logs.insert_many(dummy_attacks)
        print(f"✅ Inserted {len(result.inserted_ids)} records!")
        
        # Show stats
        total = await db.attack_logs.count_documents({})
        malicious = await db.attack_logs.count_documents({"classification.is_malicious": True})
        
        print(f"\n📊 Database Stats:")
        print(f"   Total logs: {total}")
        print(f"   Malicious: {malicious}")
        print(f"   Benign: {total - malicious}")
        
        client.close()
        print("\n✅ Done!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(add_dummy_data())
