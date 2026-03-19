# Chameleon Honeypot - Integration Guide

## Overview

This document provides a comprehensive guide for integrating the new PostgreSQL database, GLM-5 deception engine, and Merkle Tree integrity modules into the Chameleon honeypot system.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Database Setup](#database-setup)
3. [GLM-5 Deception Engine](#glm-5-deception-engine)
4. [Merkle Tree Integrity](#merkle-tree-integrity)
5. [API Integration](#api-integration)
6. [Migration Guide](#migration-guide)

---

## Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL 14+
- GLM-5 API Key (optional, for LLM deception)

### Installation

```bash
# Navigate to backend directory
cd Chameleon-cybersecurity-ml/Backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env
# Edit .env with your settings
```

### Database Initialization

```bash
# Start PostgreSQL (macOS with Homebrew)
brew services start postgresql@14

# Create database
createdb chameleon_db

# Run migrations
cd Backend
alembic upgrade head
```

---

## Database Setup

### PostgreSQL Configuration

The new database module (`database_postgres.py`) provides async SQLAlchemy connection to PostgreSQL.

#### Environment Variables

```env
POSTGRES_USER=chameleon
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=chameleon_db
```

#### Database Models

Three tables are defined in [`models_sqlalchemy.py`](models_sqlalchemy.py):

| Table | Purpose |
|-------|---------|
| `tenants` | API key management and credit tracking |
| `honeypot_logs` | Attack logs with command/response tracking |
| `reputation_scores` | IP reputation with Merkle Tree integrity |

#### Usage Example

```python
from database_postgres import (
    init_database,
    close_database,
    get_db,
    save_honeypot_log,
    get_honeypot_logs,
    get_or_create_reputation_score
)

# Initialize database (call once at startup)
await init_database()

# Use in FastAPI endpoints
@app.get("/api/logs")
async def get_logs(db: AsyncSession = Depends(get_db)):
    logs = await get_honeypot_logs(db, skip=0, limit=50)
    return logs

# Cleanup (call on shutdown)
await close_database()
```

---

## GLM-5 Deception Engine

### Overview

The [`llm_controller.py`](llm_controller.py) module provides intelligent, context-aware deceptive responses using GLM-5.

### Key Features

- **Ubuntu Terminal Simulation**: Generates realistic Linux terminal output
- **Session Tracking**: Maintains command history per IP address
- **Fallback Support**: Falls back to static responses if API fails
- **Caching**: Caches common commands for performance

### Usage

```python
from llm_controller import generate_deceptive_response, get_session

# Get or create a session for an IP
session = get_session("192.168.1.100")

# Generate deceptive response
response = await generate_deceptive_response(
    command="ls -la /etc",
    ip_address="192.168.1.100",
    history=session
)

print(response)
# Output: 
# total 48
# drwxr-xr-x  2 root root 4096 Jan 15 09:23 .
# -rw-r--r--  1 root root  423 Jan 12 11:30 passwd
# ...
```

### System Prompt

The deception engine uses a detailed system prompt that instructs GLM-5 to:

1. Never execute actual commands
2. Generate realistic Ubuntu terminal output
3. Maintain consistency with previous commands
4. Simulate common services (nginx, mysql, ssh)
5. Return appropriate error messages for privileged operations

### Configuration

```env
GLM5_API_KEY=your_api_key_here
GLM5_API_URL=https://open.bigmodel.cn/api/paas/v3/model-api/chatglm_turbo/invoke
GLM5_MODEL=chatglm_turbo
LLM_MAX_TOKENS=500
LLM_TEMPERATURE=0.7
USE_LLM_DECEPTION=true
```

---

## Merkle Tree Integrity

### Overview

The [`integrity.py`](integrity.py) module provides cryptographic integrity verification for honeypot logs using Merkle Trees.

### How It Works

```
                    Root Hash
                   /          \
              Hash A          Hash B
             /      \        /      \
         Hash1    Hash2   Hash3    Hash4
           |        |       |        |
        Log1     Log2    Log3     Log4
```

1. Each log entry is hashed using SHA-256
2. Pairs of hashes are combined and hashed again
3. Process repeats until a single "root hash" is produced
4. Root hash is stored in `ReputationScores.merkle_root`
5. Any modification to logs changes the root hash

### Usage

```python
from integrity import (
    hash_log_entry,
    MerkleLogger,
    MerkleTree,
    update_reputation_merkle_root,
    verify_ip_log_integrity
)

# Hash a single log entry
log_data = {
    "id": "abc123",
    "timestamp": "2024-01-15T10:30:00Z",
    "attacker_ip": "192.168.1.100",
    "command_entered": "ls -la",
    "response_sent": "total 48..."
}
entry_hash = hash_log_entry(log_data)

# Build Merkle Tree from logs
logs = [log1, log2, log3, log4]
tree = MerkleTree(logs)
root_hash = tree.root_hash

# Generate proof for a specific log
proof = tree.get_proof(0)

# Verify proof
is_valid = MerkleTree.verify_proof(
    leaf_hash=entry_hash,
    proof=proof,
    root_hash=root_hash
)

# Update reputation score with Merkle root
merkle_root, behavior_hash = await update_reputation_merkle_root(
    session, 
    "192.168.1.100", 
    logs
)

# Verify integrity later
result = await verify_ip_log_integrity(
    session,
    "192.168.1.100",
    stored_root_hash=merkle_root
)
print(result["valid"])  # True if no tampering
```

### Integration with ReputationScores

The `merkle_root` field in `ReputationScores` table stores the root hash for each IP's logs:

```python
# After logging attacks, update Merkle root
logs = await get_logs_by_ip(session, ip_address)
merkle_root, _ = await update_reputation_merkle_root(session, ip_address, logs)
```

---

## API Integration

### Updating main.py

To integrate the new modules into your FastAPI application:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database_postgres import (
    init_database, 
    close_database, 
    get_db,
    save_honeypot_log,
    get_or_create_reputation_score
)
from llm_controller import generate_deceptive_response, get_session
from integrity import hash_log_entry, MerkleLogger

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_database()
    yield
    # Shutdown
    await close_database()

app = FastAPI(lifespan=lifespan)

@app.post("/api/trap/submit")
async def submit_trap(
    command: str,
    ip_address: str,
    db: AsyncSession = Depends(get_db)
):
    # Get session for command history
    session = get_session(ip_address)
    
    # Generate deceptive response using GLM-5
    response = await generate_deceptive_response(
        command=command,
        ip_address=ip_address,
        history=session
    )
    
    # Save log to database
    log = await save_honeypot_log(
        session=db,
        tenant_id="default-tenant-id",
        attacker_ip=ip_address,
        command_entered=command,
        response_sent=response,
        metadata={"classification": {...}}
    )
    
    # Update reputation score
    await get_or_create_reputation_score(db, ip_address)
    
    return {"message": response}
```

---

## Migration Guide

### From MongoDB to PostgreSQL

1. **Export MongoDB Data**:
   ```bash
   mongoexport --db chameleon_db --collection attack_logs --out attack_logs.json
   ```

2. **Transform Data**:
   ```python
   import json
   
   with open('attack_logs.json') as f:
       mongo_logs = json.load(f)
   
   # Transform to new schema
   postgres_logs = []
   for log in mongo_logs:
       postgres_logs.append({
           "tenant_id": "default-tenant-uuid",
           "attacker_ip": log.get("ip_address"),
           "command_entered": log.get("raw_input"),
           "response_sent": log.get("deception_response", {}).get("message"),
           "timestamp": log.get("timestamp"),
           "metadata": {
               "classification": log.get("classification"),
               "geo_location": log.get("geo_location")
           }
       })
   ```

3. **Import to PostgreSQL**:
   ```python
   async with get_db_context() as session:
       for log in postgres_logs:
           await save_honeypot_log(session, **log)
   ```

### Alembic Commands

```bash
# Create a new migration
alembic revision --autogenerate -m "description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

---

## File Structure

```
Chameleon-cybersecurity-ml/Backend/
├── config.py                    # Updated with PostgreSQL settings
├── database_postgres.py         # NEW: PostgreSQL async connection
├── models_sqlalchemy.py         # NEW: SQLAlchemy ORM models
├── llm_controller.py            # NEW: GLM-5 deception engine
├── integrity.py                 # NEW: Merkle Tree integrity
├── .env.example                 # NEW: Environment configuration
├── alembic.ini                  # NEW: Alembic configuration
├── migrations/                  # NEW: Migration scripts
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 20260216_initial_schema.py
├── main.py                      # Existing (needs integration)
├── models.py                    # Existing Pydantic models
├── database.py                  # Existing MongoDB (kept for reference)
└── requirements.txt             # Updated dependencies
```

---

## Troubleshooting

### Database Connection Issues

```python
# Test connection
from database_postgres import db

await db.connect()
if db.connected:
    print("Connected to PostgreSQL!")
else:
    print("Connection failed")
```

### GLM-5 API Issues

```python
from llm_controller import llm_controller

# Check statistics
stats = llm_controller.get_stats()
print(f"Total requests: {stats['total_requests']}")
print(f"Failed requests: {stats['failed_requests']}")

# Test with static fallback
response = llm_controller._static_fallback("whoami")
print(response)  # Should print: www-data
```

### Merkle Tree Verification Failed

If integrity verification fails, it means logs have been modified:

```python
result = await verify_ip_log_integrity(session, ip, stored_root)
if not result["valid"]:
    # Logs have been tampered with!
    # Investigate the discrepancy
    print(f"Expected root: {stored_root}")
    print(f"Current root: {result['merkle_root']}")
```

---

## Support

For issues or questions, refer to:
- [Architecture Plan](../plans/chameleon-refactoring-plan.md)
- [Main README](../README.md)