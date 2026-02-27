"""Mock in-memory database with hardcoded attack data"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from utils import get_current_time
import random

class MockDatabase:
    def __init__(self):
        self.attack_logs = []
        self.initialize_data()
    
    def initialize_data(self):
        """Initialize with hardcoded attack data"""
        # Use current IST time as base
        from datetime import datetime, timezone, timedelta
        IST = timezone(timedelta(hours=5, minutes=30))
        base_time = datetime.now(IST)
        
        # Hardcoded attack data
        self.attack_logs = [
            {
                "id": "log_001",
                "timestamp": base_time - timedelta(minutes=5),
                "raw_input": "admin' OR '1'='1",
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
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
                "id": "log_002",
                "timestamp": base_time - timedelta(minutes=10),
                "raw_input": "<script>alert('XSS')</script>",
                "ip_address": "103.104.226.58",
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
                "id": "log_003",
                "timestamp": base_time - timedelta(minutes=15),
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
                "id": "log_004",
                "timestamp": base_time - timedelta(minutes=20),
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
                "id": "log_005",
                "timestamp": base_time - timedelta(minutes=25),
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
                "id": "log_006",
                "timestamp": base_time - timedelta(hours=1),
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
                "id": "log_007",
                "timestamp": base_time - timedelta(hours=2),
                "raw_input": "<img src=x onerror=alert(document.cookie)>",
                "ip_address": "103.104.226.58",
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
            },
            {
                "id": "log_008",
                "timestamp": base_time - timedelta(hours=3),
                "raw_input": "1' AND 1=1--",
                "ip_address": "49.248.21.6",
                "user_agent": "Mozilla/5.0 (X11; Linux x86_64)",
                "geo_location": {
                    "country": "Japan",
                    "region": "Tokyo",
                    "city": "Tokyo",
                    "latitude": 35.6762,
                    "longitude": 139.6503,
                    "isp": "NTT Communications"
                },
                "classification": {
                    "attack_type": "SQLI",
                    "confidence": 0.91,
                    "is_malicious": True
                },
                "deception_response": {
                    "message": "Query returned 0 results",
                    "delay_applied": 3.0,
                    "http_status": 200
                }
            },
            {
                "id": "log_009",
                "timestamp": base_time - timedelta(hours=4),
                "raw_input": "<!--#include virtual=\"/etc/passwd\"-->",
                "ip_address": "172.16.0.25",
                "user_agent": "Nikto/2.1.6",
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
                    "confidence": 0.89,
                    "is_malicious": True
                },
                "deception_response": {
                    "message": "File not found",
                    "delay_applied": 2.8,
                    "http_status": 404
                }
            },
            {
                "id": "log_010",
                "timestamp": base_time - timedelta(hours=5),
                "raw_input": "password123",
                "ip_address": "203.0.113.45",
                "user_agent": "Hydra v9.2",
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
                    "confidence": 0.78,
                    "is_malicious": True
                },
                "deception_response": {
                    "message": "Account locked due to multiple failed attempts",
                    "delay_applied": 8.0,
                    "http_status": 429
                }
            }
        ]
    
    async def save_attack_log(self, log_data: dict) -> str:
        """Save attack log to in-memory database"""
        log_id = f"log_{len(self.attack_logs) + 1:03d}"
        log_data["id"] = log_id
        self.attack_logs.append(log_data)
        return log_id
    
    async def get_attack_logs(self, skip: int, limit: int) -> List[dict]:
        """Get attack logs with pagination"""
        # Update timestamps to be relative to current time (for display purposes)
        from datetime import datetime, timezone, timedelta
        IST = timezone(timedelta(hours=5, minutes=30))
        current_time = datetime.now(IST)
        
        # Create a copy with updated timestamps
        updated_logs = []
        for i, log in enumerate(self.attack_logs):
            log_copy = log.copy()
            # Set timestamps relative to now (most recent first)
            minutes_ago = i * 5  # 5 minutes apart
            log_copy["timestamp"] = current_time - timedelta(minutes=minutes_ago)
            updated_logs.append(log_copy)
        
        # Sort by timestamp descending
        sorted_logs = sorted(updated_logs, key=lambda x: x["timestamp"], reverse=True)
        return sorted_logs[skip:skip + limit]
    
    async def get_attack_by_id(self, log_id: str) -> Optional[dict]:
        """Get specific attack log by ID"""
        for log in self.attack_logs:
            if log.get("id") == log_id:
                return log
        return None
    
    async def get_dashboard_stats(self) -> dict:
        """Get dashboard statistics"""
        total = len(self.attack_logs)
        malicious = sum(1 for log in self.attack_logs if log["classification"]["is_malicious"])
        benign = total - malicious
        
        # Attack distribution
        attack_dist = {}
        for log in self.attack_logs:
            attack_type = log["classification"]["attack_type"]
            attack_dist[attack_type] = attack_dist.get(attack_type, 0) + 1
        
        # Top attackers (last 24 hours) - all mock data is considered recent
        from datetime import datetime, timezone, timedelta
        IST = timezone(timedelta(hours=5, minutes=30))
        cutoff = datetime.now(IST) - timedelta(hours=24)
        # All mock attacks are considered recent for demo purposes
        recent_attacks = [log for log in self.attack_logs if log["classification"]["is_malicious"]]
        
        ip_counts = {}
        ip_last_seen = {}
        for log in recent_attacks:
            ip = log["ip_address"]
            ip_counts[ip] = ip_counts.get(ip, 0) + 1
            if ip not in ip_last_seen or log["timestamp"] > ip_last_seen[ip]:
                ip_last_seen[ip] = log["timestamp"]
        
        top_attackers = [
            {"ip": ip, "count": count, "last_seen": ip_last_seen[ip]}
            for ip, count in sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
        
        # Geographic distribution
        geo_counts = {}
        for log in self.attack_logs:
            if log["classification"]["is_malicious"] and log.get("geo_location"):
                geo = log["geo_location"]
                key = f"{geo['country']}_{geo['city']}"
                if key not in geo_counts:
                    geo_counts[key] = {
                        "country": geo["country"],
                        "city": geo["city"],
                        "latitude": geo["latitude"],
                        "longitude": geo["longitude"],
                        "count": 0
                    }
                geo_counts[key]["count"] += 1
        
        geo_locations = sorted(geo_counts.values(), key=lambda x: x["count"], reverse=True)[:50]
        
        return {
            "total_attempts": total,
            "malicious_attempts": malicious,
            "benign_attempts": benign,
            "attack_distribution": attack_dist,
            "top_attackers": top_attackers,
            "geo_locations": geo_locations
        }
    
    async def get_logs_by_ip(self, ip_address: str) -> List[dict]:
        """Get all logs for a specific IP address"""
        return [log for log in self.attack_logs if log["ip_address"] == ip_address]

# Global mock database instance
mock_db = MockDatabase()
