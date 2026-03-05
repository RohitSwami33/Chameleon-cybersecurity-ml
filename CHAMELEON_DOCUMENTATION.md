# 🦎 Chameleon — Adaptive Deception-Based Cybersecurity System

## Complete Project Documentation

> **Chameleon** is an AI-powered honeypot system that uses machine learning, LLM-driven deception, blockchain-backed log integrity, and real-time threat intelligence to detect, classify, deceive, and forensically track cyber attackers.

---

## Table of Contents

1. [System Architecture](#1-system-architecture)
2. [Machine Learning Pipeline](#2-machine-learning-pipeline)
3. [Backend — FastAPI Server](#3-backend--fastapi-server)
4. [Deception Engine (LLM-Powered)](#4-deception-engine-llm-powered)
5. [Honeytoken & Beacon System](#5-honeytoken--beacon-system)
6. [Blockchain Integrity Layer](#6-blockchain-integrity-layer)
7. [Threat Intelligence Service](#7-threat-intelligence-service)
8. [IP Reputation & Threat Scoring](#8-ip-reputation--threat-scoring)
9. [Tarpit Manager](#9-tarpit-manager)
10. [Attacker Session Tracking](#10-attacker-session-tracking)
11. [AI Chatbot (Gemini)](#11-ai-chatbot-gemini)
12. [Database Layer (PostgreSQL)](#12-database-layer-postgresql)
13. [Frontend — React Dashboard](#13-frontend--react-dashboard)
14. [Smart Contract (Solidity)](#14-smart-contract-solidity)
15. [API Reference](#15-api-reference)
16. [Configuration & Environment](#16-configuration--environment)
17. [Dataset & Training Scripts](#17-dataset--training-scripts)
18. [Deployment](#18-deployment)
19. [Testing](#19-testing)

---

## 1. System Architecture

```
                        ┌─────────────────────────────────────────────┐
                        │            ATTACKER                          │
                        └──────────────────┬──────────────────────────┘
                                           │ HTTP POST /trap/execute
                                           ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                      CHAMELEON BACKEND (FastAPI)                          │
│                                                                          │
│  ┌──────────────┐   ┌──────────────────┐   ┌────────────────────────┐   │
│  │ BiLSTM Model │──▶│ Classification   │──▶│  Deception Engine       │   │
│  │ (50k trained) │   │ (malicious/benign)│   │  (DeepSeek LLM API)    │   │
│  └──────────────┘   └──────────────────┘   └────────────────────────┘   │
│         │                    │                        │                   │
│         ▼                    ▼                        ▼                   │
│  ┌──────────────┐   ┌──────────────────┐   ┌────────────────────────┐   │
│  │ Tarpit       │   │ Threat Score     │   │  Honeytoken Beacon     │   │
│  │ Manager      │   │ System           │   │  System                │   │
│  └──────────────┘   └──────────────────┘   └────────────────────────┘   │
│         │                    │                        │                   │
│         ▼                    ▼                        ▼                   │
│  ┌──────────────┐   ┌──────────────────┐   ┌────────────────────────┐   │
│  │ Merkle Tree  │──▶│ Blockchain Sync  │──▶│  Ethereum Sepolia      │   │
│  │ Integrity    │   │ (Web3.py)        │   │  Smart Contract        │   │
│  └──────────────┘   └──────────────────┘   └────────────────────────┘   │
│         │                    │                                           │
│         ▼                    ▼                                           │
│  ┌────────────────────────────────────┐                                  │
│  │         PostgreSQL Database         │                                  │
│  │  (honeypot_logs, tenants, etc.)     │                                  │
│  └────────────────────────────────────┘                                  │
└──────────────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                      REACT FRONTEND DASHBOARD                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐  │
│  │Dashboard │ │Analytics │ │Blockchain│ │ Threat   │ │ AI Chatbot   │  │
│  │Overview  │ │Page      │ │Explorer  │ │ Intel    │ │ (Gemini)     │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, Vite, Three.js, Recharts, Leaflet, Framer Motion |
| **Backend** | Python 3.12, FastAPI, Uvicorn, Pydantic |
| **ML Model** | PyTorch, Bidirectional LSTM (BiLSTM) |
| **Database** | PostgreSQL 17, SQLAlchemy (async), asyncpg |
| **LLM API** | DeepSeek Chat API (OpenAI-compatible) |
| **AI Chatbot** | Google Gemini 2.5 Pro + DuckDuckGo Search |
| **Blockchain** | Solidity ^0.8.19, Web3.py, Ethereum Sepolia Testnet |
| **Auth** | JWT (HS256), bcrypt |
| **DevOps** | Docker, Render YAML, Alembic migrations |

---

## 2. Machine Learning Pipeline

### Model: BiLSTM Character-Level Classifier

**File:** `Backend/ml_inference.py`  
**Trained Model:** `Backend/chameleon_lstm_m4_50k.pth` (2.4 MB)  
**Tokenizer:** `Backend/tokenizer_50k.json`

#### Architecture

```
Input (raw shell command string)
    │
    ▼
Character-Level Tokenizer
    │  Maps each character → integer index
    │  Padding to max_length = 120
    ▼
Embedding(vocab_size, 64, padding_idx=0)
    │
    ▼
Bi-LSTM(input=64, hidden=128, layers=2, dropout=0.3, bidirectional=True)
    │  Concatenate final forward + backward hidden states
    ▼
Dropout(0.3)
    │
    ▼
Linear(256 → 1)
    │
    ▼
Sigmoid → [0.0, 1.0]  (probability of malicious)
```

#### Hyperparameters

| Parameter | Value |
|-----------|-------|
| `MAX_SEQUENCE_LENGTH` | 120 |
| `EMBEDDING_DIM` | 64 |
| `HIDDEN_DIM` | 128 |
| `NUM_LAYERS` | 2 |
| `DROPOUT` | 0.3 |
| Training Samples | 50,000 |
| Device Priority | Apple MPS (Metal) → CUDA → CPU |

#### ChameleonPredictor (Singleton)

```python
from ml_inference import ChameleonPredictor

predictor = ChameleonPredictor()
score = await predictor.predict("cat /etc/passwd")   # ≈ 0.97 (malicious)
score = await predictor.predict("whoami")             # ≈ 0.02 (benign)
```

- Thread-safe singleton pattern (only loaded once)
- Character-level tokenizer mirrors training exactly
- Async `predict()` method for FastAPI integration
- Returns float in `[0.0, 1.0]` — values above `0.85` are high-confidence attacks

#### Attack Types Classified

| Attack Type | Description | Example |
|-------------|-------------|---------|
| `SQLI` | SQL Injection | `' OR 1=1; DROP TABLE users; --` |
| `XSS` | Cross-Site Scripting | `<script>alert('xss')</script>` |
| `SSI` | Server-Side Inclusion | `<!--#exec cmd="ls"--->` |
| `BRUTE_FORCE` | Brute Force Login | Repeated failed auth attempts |
| `BENIGN` | Legitimate Request | Normal user input |

#### Training Scripts

| Script | Description |
|--------|-------------|
| `Backend/train_bi_lstm_50k.py` | Main training script (50k dataset, BiLSTM) |
| `Backend/train_lstm.py` | Earlier LSTM training variant |
| `Backend/train_lstm_full.py` | Full dataset training |
| `Backend/train_lstm_quick.py` | Quick training for testing |
| `Backend/train_50k_lstm.py` | 50k dataset variant |

#### Training Artifacts

| File | Description |
|------|-------------|
| `chameleon_lstm_m4_50k.pth` | Trained BiLSTM model weights (2.4 MB) |
| `chameleon_lstm_model.pt` | Earlier LSTM model (9.6 MB) |
| `chameleon_char_cnn_gru.keras` | CNN-GRU model (Keras, 3.9 MB) |
| `tokenizer_50k.json` | Character-to-index mapping |
| `tokenizer.pkl` | Pickle tokenizer (legacy) |
| `training_history_50k.json` | Training curves, loss, accuracy per epoch |
| `training_metrics_50k.png` | Loss/accuracy visualization |
| `confusion_matrix_50k.png` | Confusion matrix visualization |

---

## 3. Backend — FastAPI Server

**File:** `Backend/main.py` (1,016 lines, 64 endpoints/functions)  
**Version:** 2.0.0

### Application Lifecycle

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect()              # PostgreSQL connection pool
    await db.create_tables()        # Ensure schema exists
    yield
    await db.disconnect()
```

### Core Honeypot Pipeline: `POST /trap/execute`

This is the **primary honeypot endpoint** — the core of the entire system:

```
1. Receive JSON → { "command": "...", "ip_address": "..." }
2. BiLSTM prediction → ChameleonPredictor.predict(command) → [0.0, 1.0]
3. Threshold gate:
   - score ≥ 0.50 → LLM deception (DeepSeek generates fake terminal output)
   - score < 0.50 → Static bash-like fallback (saves API costs)
4. SHA-256 log hash → Merkle integrity chain
5. PostgreSQL save → HoneypotLog with score + hash in JSONB metadata
6. Return deceptive text to the attacker
```

**Request:**
```json
{
  "command": "cat /etc/passwd",
  "ip_address": "142.93.12.77"  // optional — auto-detected
}
```

**Response:**
```json
{
  "response": "root:x:0:0:root:/root:/bin/bash\ndaemon:x:1:1:...",
  "prediction_score": 0.97,
  "is_malicious": true,
  "hash": "a1b2c3d4e5f6...",
  "session_id": "d0eba140-45f7-4a7c-ab1e-1dd8e1deab64"
}
```

### CORS Configuration

```python
allow_origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:8000",
    # ... production URLs
]
```

### Geolocation

Uses `ip-api.com/json/` to fetch real-time geo-location for every attacker IP:
- Country, region, city
- Latitude/longitude
- ISP, organization
- AS number

---

## 4. Deception Engine (LLM-Powered)

### Primary: LLM Controller (`Backend/llm_controller.py`)

**610 lines** — the brain of the honeypot's deception capability.

#### Multi-Provider Support

| Provider | API | Model |
|----------|-----|-------|
| **DeepSeek** (primary) | OpenAI-compatible REST | `deepseek-chat` |
| **GLM-5** (Zhipu AI) | Custom REST API | `chatglm_turbo` |
| **OpenAI** | OpenAI API | Configurable |

#### System Prompt

The LLM is instructed to act as a **vulnerable Ubuntu 22.04 server**:

```
You are a Ubuntu 22.04 LTS terminal. The user is a hacker.
RESPOND ONLY WITH REALISTIC TERMINAL OUTPUT — no explanations, no markdown.

IMPORTANT RULES:
1. Never reveal you are an AI or honeypot
2. Make output look genuinely vulnerable
3. Include realistic file paths, permissions, users
4. For database queries — show fake but realistic data
5. For file reads — show plausible content with embedded honeytoken URLs
```

#### Key Features

1. **Context-Aware Responses** — Maintains `CommandHistory` per attacker IP (last 20 commands)
2. **Honeytoken Injection** — Embeds beacon URLs in fake credential files:
   ```
   aws_access_key_id = AKIAIOSFODNN7EXAMPLE
   aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
   # Cleanup: http://localhost:8000/api/beacon/{session_id}
   ```
3. **Response Caching** — Caches common commands (ls, pwd, whoami) to save API costs
4. **Static Fallback** — If LLM API fails, generates realistic bash output with embedded honeytokens
5. **Session Management** — Per-IP session tracking with command history

#### Static Fallback Canary Files

When the LLM is unavailable, static responses include:
- `aws_production_keys.csv` — fake AWS credentials with beacon URL
- `.env.backup` — fake environment file with database passwords
- Directory listings with tempting filenames like `backup_2024.sql`, `admin_credentials.txt`

### Secondary: Rule-Based Deception Engine (`Backend/deception_engine.py`)

Pre-built response pools for each attack type:

| Attack Type | Response Strategy | HTTP Status |
|-------------|-------------------|-------------|
| `SQLI` | Fake MySQL/PostgreSQL error messages | 500 |
| `XSS` | "Content sanitized" / CSP violation messages | 200 |
| `SSI` | "SSI directives disabled" messages | 403 |
| `BRUTE_FORCE` | "Account locked" / remaining attempts | 401 |
| `BENIGN` | "Request processed successfully" | 200 |

**Context-aware variations for SQLi:**
- `UNION` → "Error: UNION query with different number of columns"
- `DROP` → "Error: DROP command denied to user 'webapp'@'localhost'"
- `information_schema` → "Error: SELECT command denied on table 'information_schema.tables'"

---

## 5. Honeytoken & Beacon System

### Beacon Tripwire: `GET /api/beacon/{session_id}`

**Purpose:** Silently detect data exfiltration.

When the LLM generates fake credential files (`.env.backup`, `aws_production_keys.csv`), it embeds invisible beacon URLs. If an attacker exfiltrates these files and accesses the URL:

1. Returns a **1×1 transparent PNG pixel** (appears as broken/dead link)
2. Silently logs the access to PostgreSQL with:
   - Session ID
   - Attacker IP address
   - User-Agent
   - Full request headers
   - Timestamp

**This is a HIGH-CONFIDENCE indicator of data exfiltration.**

```python
TRANSPARENT_PIXEL = b"\x89PNG\r\n\x1a\n..."  # 1x1 transparent PNG
```

### Frontend Fingerprinting: `POST /api/honeypot/log`

The Trap Interface (decoy login page) silently captures:
- Canvas fingerprint hash
- WebGL renderer string
- Available fonts
- Timezone offset
- Screen resolution
- Credentials attempted
- Browser plugins

---

## 6. Blockchain Integrity Layer

### Merkle Tree Implementation (`Backend/integrity.py`)

**686 lines** — Cryptographic integrity verification for all honeypot logs.

#### Components

| Class | Purpose |
|-------|---------|
| `MerkleNode` | Individual node in the binary tree |
| `MerkleTree` | Full Merkle tree built from log entries |
| `MerkleLogger` | High-level interface for adding logs and verifying integrity |

#### How It Works

```
Log Entry 1    Log Entry 2    Log Entry 3    Log Entry 4
     │              │              │              │
  SHA-256        SHA-256        SHA-256        SHA-256
     │              │              │              │
     H1             H2             H3             H4
      \            /                \            /
       Hash(H1+H2)                  Hash(H3+H4)
            \                            /
             \                          /
              Hash(H12 + H34)
                    │
              MERKLE ROOT ──────▶ Blockchain Anchor
```

#### Key Methods

```python
# Hash a log entry
hash_log_entry(log_data: dict) → str (SHA-256)

# Build tree from entries
tree = MerkleTree(log_entries)
root = tree.root_hash

# Generate proof for a specific leaf
proof = tree.get_proof(index=2)

# Verify a proof without the full tree
MerkleTree.verify_proof(leaf_hash, proof, root_hash) → bool
```

### Ethereum Sepolia Anchoring (`Backend/blockchain_sync.py`)

**350 lines** — Anchors Merkle root hashes to the Ethereum Sepolia testnet.

#### Flow

```
MerkleLogger.build_tree()
    → root_hash (SHA-256, 64 hex chars)
        → anchor_latest_root(root_hash)
            → Web3.py signs transaction
                → ChameleonLedger.storeMerkleRoot(root_hash)
                    → Stored permanently on Sepolia
```

#### Configuration

```env
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID
PRIVATE_KEY=0xYOUR_PRIVATE_KEY
CONTRACT_ADDRESS=0xYOUR_CONTRACT_ADDRESS
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/blockchain/verify` | GET | Verify local blockchain integrity |
| `/api/blockchain/data` | GET | Get blockchain blocks (paginated) |
| `/api/blockchain/block/{index}` | GET | Get specific block by index |
| `/api/blockchain/export` | GET | Export blockchain as JSON/CSV |

---

## 7. Threat Intelligence Service

**File:** `Backend/threat_intel_service.py` (276 lines)

### Privacy-Preserving Threat Intelligence

Uses cryptographic commitments to share attack patterns **without revealing sensitive data**.

#### Features

1. **Novel Attack Detection** — Identifies attack patterns not seen in the last 24 hours
2. **Pattern Hashing** — SHA-256 hashes of attack signatures (shareable without payload)
3. **Attack Signature Extraction** — Generalizes attack patterns:
   - SQLi: `UNION`, `OR 1=1`, `DROP TABLE`, `INFORMATION_SCHEMA`
   - XSS: `<script>`, `onerror`, `javascript:`, `eval(`
4. **Severity Calculation** — Combines attack type + confidence:
   - `CRITICAL`: SQLi with >90% confidence
   - `HIGH`: XSS with >80% confidence
   - `MEDIUM`: SSI or brute force
   - `LOW`: Low-confidence detections
5. **Threat Reports** — Structured intelligence reports with:
   - Hashed IP (privacy-preserving)
   - Attack signature (technique, not payload)
   - Severity level
   - Timestamp

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/threat-intel/reports` | GET | Get recent threat reports |
| `/api/threat-intel/stats` | GET | Threat intelligence statistics |
| `/api/threat-intel/feed` | GET | Live threat intelligence feed |
| `/api/threat-intel/statistics` | GET | Detailed statistics |
| `/api/threat-intel/verify` | POST | Verify a threat commitment |

---

## 8. IP Reputation & Threat Scoring

**File:** `Backend/threat_score.py` (206 lines)

### Blockchain-Backed Reputation System

Every attacker IP gets a reputation score from 0–100 maintained in a hash chain.

#### Score Penalties

| Attack Type | Penalty |
|-------------|---------|
| `SQLI` | -15 points |
| `XSS` | -12 points |
| `SSI` | -10 points |
| `BRUTE_FORCE` | -8 points |
| `BENIGN` | +1 point (slow recovery) |

#### Reputation Levels

| Level | Score Range | Color |
|-------|------------|-------|
| 🟢 TRUSTED | 90–100 | `#4CAF50` |
| 🟡 NEUTRAL | 70–89 | `#FFC107` |
| 🟠 SUSPICIOUS | 40–69 | `#FF9800` |
| 🔴 MALICIOUS | 20–39 | `#F44336` |
| ⚫ CRITICAL | 0–19 | `#B71C1C` |

#### Hash Chain Integrity

Every score change is recorded in a blockchain-like hash chain:
```json
{
  "ip_address": "142.93.12.77",
  "old_score": 100,
  "new_score": 85,
  "attack_type": "SQLI",
  "previous_hash": "0000...0000",
  "hash": "a1b2c3d4..."
}
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/threat-scores` | GET | List all IP reputation scores |
| `/api/threat-scores/flagged` | GET | Get flagged IPs (score < 40) |
| `/api/threat-scores/top` | GET | Top threat IPs (lowest scores) |
| `/api/threat-scores/verify` | GET | Verify score chain integrity |
| `/api/threat-scores/{ip}` | GET | Get specific IP reputation |
| `/api/threat-analytics` | GET | Threat analytics summary |

---

## 9. Tarpit Manager

**File:** `Backend/tarpit_manager.py` (64 lines)

### Adaptive Rate Limiting

Automatically slows down repeat attackers with progressive delays:

```
Request 1–5:  No delay (below threshold)
Request 6:    2.0s delay
Request 7:    2.5s delay
Request 8:    3.0s delay
...
Request N:    min(2.0 + (N-5)*0.5, 10.0)s delay
```

#### Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `TARPIT_THRESHOLD` | 5 | Requests before triggering |
| `TARPIT_DELAY_MIN` | 2.0s | Minimum delay |
| `TARPIT_DELAY_MAX` | 10.0s | Maximum delay cap |

#### Features

- **IP Tracking** — Per-IP request timestamps (last 60 seconds)
- **Random Variation** — ±0.5s jitter to avoid detection
- **IP Blocking** — Can block IPs for configurable duration
- **Auto-Cleanup** — Removes old timestamps automatically

---

## 10. Attacker Session Tracking

**File:** `Backend/attacker_session.py` (197 lines)

### Progressive Deception Journey

Tracks each attacker's journey through a **multi-stage deception pipeline**:

#### Session Model

```python
class AttackerSession:
    attacker_fingerprint: str   # SHA-256(IP + User-Agent)
    attempt_count: int          # Total attempts
    attack_type: str            # Primary attack vector
    current_stage: int          # 1–4 (progressive revelation)
    db_type: str                # "MySQL", "PostgreSQL", "SQLite", "MariaDB"
    guessed_table: str          # Table the attacker "discovered"
    guessed_column: str         # Column the attacker "discovered"
    history: List[SessionHistory]  # Complete attempt log
```

#### Deception Stages

| Stage | SQLi Response | XSS Response |
|-------|--------------|--------------|
| 1 | Generic SQL error | "Input validated" |
| 2 | Table name revealed | Form submission success |
| 3 | Column names leaked | Profile updated |
| 4 | Fake data returned | — |

- **Max 4 stages for SQLi**, 3 stages for XSS
- Session history capped at 50 entries per attacker
- Random database type assignment for realistic error messages

---

## 11. AI Chatbot (Gemini)

**File:** `Backend/chatbot_service.py` (203 lines)

### Google Gemini 2.5 Pro + DuckDuckGo Search

A cybersecurity-focused conversational AI assistant integrated into the dashboard.

#### Capabilities

1. **Threat Analysis** — Analyze attack logs and explain techniques
2. **Cybersecurity Q&A** — Answer security questions with accuracy
3. **Web Search** — DuckDuckGo search for current threat intelligence and CVEs
4. **Response Suggestions** — Recommend mitigation strategies
5. **Attack Log Analysis** — Auto-analyze individual attack entries

#### Configuration

```python
model = genai.GenerativeModel(
    model_name='gemini-2.5-pro',
    generation_config={
        'temperature': 0.7,
        'top_p': 0.8,
        'top_k': 40,
        'max_output_tokens': 2048,
    }
)
```

#### System Prompt

```
You are a cybersecurity expert AI assistant integrated into the
Chameleon Adaptive Deception System. Your role is to help security
analysts understand threats, attacks, and security concepts.
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chatbot/chat` | POST | Send message to chatbot |
| `/api/chatbot/history` | GET | Get chat history |
| `/api/chatbot/clear` | POST | Clear chat history |
| `/api/chatbot/analyze/{log_id}` | POST | AI-analyze an attack log |
| `/api/chatbot/suggest` | POST | Get response suggestions |
| `/api/chatbot/search` | GET | Search cybersecurity info |

---

## 12. Database Layer (PostgreSQL)

### Database Configuration (`Backend/database_postgres.py`)

**18,810 bytes** — Async PostgreSQL management with SQLAlchemy.

#### Connection Settings

```env
POSTGRES_USER=chameleon
POSTGRES_PASSWORD=chameleon123
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=chameleon_db
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
```

### SQLAlchemy Models (`Backend/models_sqlalchemy.py`)

| Model | Table | Description |
|-------|-------|-------------|
| `Tenant` | `tenants` | Multi-tenant support with API keys |
| `HoneypotLog` | `honeypot_logs` | Attack logs with JSONB metadata |
| `ReputationScore` | `reputation_scores` | IP reputation tracking |
| `BeaconEvent` | `beacon_events` | Honeytoken beacon access logs |

#### HoneypotLog Schema

```python
class HoneypotLog(Base):
    __tablename__ = "honeypot_logs"

    id            = Column(UUID, primary_key=True, default=uuid4)
    tenant_id     = Column(UUID, ForeignKey("tenants.id"))
    source_ip     = Column(String(45), index=True)
    source_port   = Column(Integer)
    protocol      = Column(String(10))
    raw_payload   = Column(Text)
    log_metadata  = Column(JSONB)         # Classification, geo, deception details
    risk_score    = Column(Float)
    logged_at     = Column(DateTime(timezone=True), server_default=func.now())
```

#### JSONB Metadata Structure

```json
{
  "classification": {
    "attack_type": "SQLI",
    "confidence": 0.97,
    "is_malicious": true
  },
  "geo_location": {
    "country": "Germany",
    "city": "Frankfurt",
    "lat": 50.1109,
    "lon": 8.6821,
    "isp": "Hetzner Online GmbH"
  },
  "deception_response": {
    "message": "Error: UNION query with different number of columns",
    "delay_applied": 2.5,
    "http_status": 500
  },
  "user_agent": "sqlmap/1.7.2",
  "hash": "a1b2c3d4...",
  "previous_hash": "e5f6a7b8..."
}
```

### Dashboard Data Layer (`Backend/database.py`)

**306 lines** — Maps PostgreSQL data to the frontend's expected format.

#### Functions

| Function | Description |
|----------|-------------|
| `save_attack_log(log_data)` | Persist attack log to PostgreSQL |
| `get_attack_logs(skip, limit)` | Paginated log retrieval |
| `get_attack_by_id(log_id)` | Single log by UUID |
| `get_logs_by_ip(ip_address)` | All logs from an IP |
| `get_dashboard_stats()` | Aggregate stats (total attacks, types, top IPs) |

### Database Seeding (`Backend/seed_attacks.py`)

Populates the database with **50 diverse, realistic attack logs** from **12 attacker profiles** across **8+ countries**:

| Country | IPs |
|---------|-----|
| 🇩🇪 Germany | 91.240.118.172 |
| 🇮🇳 India | 49.248.21.6, 103.104.226.58 |
| 🇺🇸 USA | 198.51.100.10 |
| 🇷🇺 Russia | 185.220.101.34 |
| 🇨🇳 China | 14.225.210.123 |
| 🇬🇧 UK | 77.68.11.215 |
| 🇧🇷 Brazil | 177.71.184.67 |
| 🇻🇳 Vietnam | 14.225.210.123 |
| 🇿🇦 South Africa | 41.77.135.32 |
| 🇹🇷 Turkey | 88.255.34.78 |
| 🇯🇵 Japan | 210.174.99.12 |
| 🇳🇱 Netherlands | 93.184.216.34 |

---

## 13. Frontend — React Dashboard

**Directory:** `frontend/src/`  
**Framework:** React 18 + Vite  
**Styling:** Custom CSS with cyberpunk/hacker aesthetic

### Pages (5)

| Page | File | Description |
|------|------|-------------|
| **Dashboard Overview** | `pages/DashboardOverview.jsx` | Main dashboard with stats, charts, and globe |
| **Analytics** | `pages/AnalyticsPage.jsx` | Detailed attack analytics with charts |
| **Attack Globe** | `pages/AttackGlobePage.jsx` | Full-page 3D attack globe visualization |
| **Chatbot** | `pages/ChatbotPage.jsx` | AI chatbot interface page |
| **Threat Intel** | `pages/ThreatIntelPage.jsx` | Threat intelligence feed page |

### Components (28)

#### Core Dashboard Components

| Component | File | Description |
|-----------|------|-------------|
| **Dashboard** | `Dashboard.jsx` (30,676 bytes) | Main dashboard layout — orchestrates stats, charts, map, and logs |
| **StatsCards** | `StatsCards.jsx` | Summary cards: Total Attacks, Malicious %, Top Attack Type, Active IPs |
| **AttackLogs** | `AttackLogs.jsx` | Paginated table of all attack logs with search and detail modals |
| **AttackChart** | `AttackChart.jsx` | Recharts-based bar/line charts of attack trends over time |
| **GeoMap** | `GeoMap.jsx` | Leaflet world map with attack origin markers |
| **WorldMap** | `WorldMap.jsx` | Alternative world map component |

#### 3D Visualizations (Three.js / React Three Fiber)

| Component | File | Description |
|-----------|------|-------------|
| **AttackGlobeSimple** | `AttackGlobeSimple.jsx` (14,497 bytes) | 3D globe showing attack origins with animated arcs |
| **AttackTerrainMap** | `AttackTerrainMap.jsx` (21,216 bytes) | 3D terrain map visualization of attacks |
| **BlockchainViz3D** | `BlockchainViz3D.jsx` (15,446 bytes) | 3D blockchain visualization with connected blocks |
| **MerkleTree3D** | `MerkleTree3D.jsx` (19,412 bytes) | 3D Merkle tree visualization with expandable nodes |
| **ServerRack3D** | `ServerRack3D.jsx` (19,494 bytes) | 3D animated server rack honeypot visualization |
| **ThreatRadar3D** | `ThreatRadar3D.jsx` | 3D radar display showing threat levels |
| **LoginShield3D** | `LoginShield3D.jsx` | 3D shield animation on login page |
| **LoginBackground3D** | `LoginBackground3D.jsx` | Animated 3D background particles on login |
| **AIOrb3D** | `AIOrb3D.jsx` | 3D pulsating orb for AI chatbot interface |

#### Blockchain Explorer

| Component | File | Description |
|-----------|------|-------------|
| **BlockchainExplorer** | `BlockchainExplorer.jsx` (20,903 bytes) | Full blockchain explorer: block list, Merkle proofs, chain verification, export |

#### Security Features

| Component | File | Description |
|-----------|------|-------------|
| **ThreatScorePanel** | `ThreatScorePanel.jsx` | IP reputation scores with color-coded levels |
| **ThreatIntelFeed** | `ThreatIntelFeed.jsx` | Live threat intelligence feed with severity indicators |
| **TrapInterface** | `TrapInterface.jsx` (28,907 bytes) | Decoy login page that captures attacker fingerprints |

#### AI & Chat

| Component | File | Description |
|-----------|------|-------------|
| **AIChatbot** | `AIChatbot.jsx` (14,424 bytes) | Chat interface with Gemini AI, web search toggle, attack analysis |

#### Navigation & Layout

| Component | File | Description |
|-----------|------|-------------|
| **Navbar** | `Navbar.jsx` (18,568 bytes) | Responsive navigation with animated transitions |
| **Login** | `Login.jsx` (11,532 bytes) | Authenticated login page with JWT |
| **ProtectedRoute** | `ProtectedRoute.jsx` | JWT auth guard for protected routes |
| **PageTransition** | `PageTransition.jsx` | Framer Motion page transitions |
| **GlobalBackground** | `GlobalBackground.jsx` | Animated cyberpunk grid background |
| **GlobalGridBackground** | `GlobalGridBackground.jsx` | Alternative grid background |
| **DepthLayers** | `DepthLayers.jsx` | Parallax depth effect layers |
| **TiltCard** | `TiltCard.jsx` | Interactive 3D tilt-on-hover card |

#### UI Primitives (`components/ui/`)

Contains 4 reusable UI components for consistent styling.

### State Management

| File | Description |
|------|-------------|
| `stores/authStore.js` | Zustand store for JWT auth state |
| `services/api.js` | Axios API client with JWT interceptors |
| `config/api.js` | API base URL configuration |

### Styling

| File | Description |
|------|-------------|
| `index.css` (5,963 bytes) | Global styles, CSS variables, cyberpunk theme |
| `trap.css` (14,720 bytes) | Trap interface styling (decoy page) |
| `App.css` | App-level layout styles |

### Design Aesthetic

- **Dark cyberpunk theme** — Deep navy/charcoal backgrounds with neon accents
- **Glassmorphism** — Frosted glass effects on panels
- **3D visualizations** — Three.js globe, Merkle tree, blockchain, server rack
- **Micro-animations** — Hover effects, transitions, loading states
- **Responsive design** — Mobile-friendly layout

---

## 14. Smart Contract (Solidity)

**File:** `Backend/contracts/ChameleonLedger.sol`  
**Network:** Ethereum Sepolia Testnet  
**Solidity Version:** ^0.8.19

### Contract: `ChameleonLedger`

```solidity
contract ChameleonLedger {
    address public owner;
    string[] private _roots;

    event RootStored(string rootHash, uint256 timestamp, uint256 index);

    modifier onlyOwner() { ... }

    function storeMerkleRoot(string memory _rootHash) external onlyOwner;
    function getRootCount() external view returns (uint256 count);
    function getRoot(uint256 index) external view returns (string memory rootHash);
    function getLatestRoot() external view returns (string memory rootHash);
}
```

#### Gas Optimizations

- Uses `string` instead of `bytes32` for human-readable SHA-256 hashes
- Minimal state writes (1 SSTORE per call)
- Array-only storage (no dynamic mapping)
- Custom `onlyOwner` modifier (avoids importing OpenZeppelin)

---

## 15. API Reference

### Authentication

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/auth/login` | POST | None | Login with username/password → JWT |

### Honeypot (Attacker-Facing)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/trap/execute` | POST | None | Core honeypot — classify & deceive |
| `/api/trap/submit` | POST | None | Legacy progressive deception |
| `/api/honeypot/log` | POST | None | Browser fingerprint logging |
| `/api/beacon/{session_id}` | GET | None | Honeytoken tripwire |

### Dashboard (Auth Required)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/dashboard/stats` | GET | JWT | Dashboard summary statistics |
| `/api/dashboard/logs` | GET | JWT | Paginated attack logs |
| `/api/dashboard/logs/{id}` | GET | JWT | Single attack log |
| `/api/dashboard/logs/ip/{ip}` | GET | JWT | Logs by IP address |

### Reports

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/reports/generate/{ip}` | GET | JWT | Generate forensic report for IP |

### Blockchain

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/blockchain/verify` | GET | JWT | Verify local chain integrity |
| `/api/blockchain/data` | GET | JWT | Blockchain blocks (paginated) |
| `/api/blockchain/block/{index}` | GET | JWT | Get specific block |
| `/api/blockchain/export` | GET | JWT | Export as JSON/CSV |

### Threat Scores

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/threat-scores` | GET | JWT | All IP reputation scores |
| `/api/threat-scores/flagged` | GET | JWT | Flagged malicious IPs |
| `/api/threat-scores/top` | GET | JWT | Top threats (lowest scores) |
| `/api/threat-scores/verify` | GET | JWT | Verify score chain |
| `/api/threat-scores/{ip}` | GET | JWT | Specific IP score |
| `/api/threat-analytics` | GET | JWT | Analytics summary |

### Sessions

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/sessions/stats` | GET | JWT | Session statistics |
| `/api/sessions/detail/{fingerprint}` | GET | JWT | Session details |
| `/api/sessions/ip/{ip}` | GET | JWT | Sessions by IP |

### Threat Intelligence

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/threat-intel/reports` | GET | JWT | Threat intelligence reports |
| `/api/threat-intel/stats` | GET | JWT | Threat intel statistics |
| `/api/threat-intel/feed` | GET | JWT | Live threat feed |
| `/api/threat-intel/statistics` | GET | JWT | Detailed statistics |
| `/api/threat-intel/verify` | POST | JWT | Verify threat commitment |

### AI Chatbot

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/chatbot/chat` | POST | JWT | Chat with AI |
| `/api/chatbot/history` | GET | JWT | Chat history |
| `/api/chatbot/clear` | POST | JWT | Clear history |
| `/api/chatbot/analyze/{log_id}` | POST | JWT | AI-analyze attack |
| `/api/chatbot/suggest` | POST | JWT | Response suggestions |
| `/api/chatbot/search` | GET | JWT | Web search |

### Health

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/health` | GET | None | Health check |

### Frontend Serving

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/{path}` | GET | None | Serves React SPA from `frontend/dist` |

---

## 16. Configuration & Environment

### Environment Variables (`.env`)

```env
# ── PostgreSQL ──
POSTGRES_USER=chameleon
POSTGRES_PASSWORD=chameleon123
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=chameleon_db

# ── Connection Pool ──
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# ── JWT Authentication ──
JWT_SECRET_KEY=your-secret-key-change-in-production-2024
ACCESS_TOKEN_EXPIRE_MINUTES=60

# ── LLM Deception Engine ──
DEEPSEEK_API_KEY=sk-...
DEEPSEEK_API_URL=https://api.deepseek.com/chat/completions
DEEPSEEK_MODEL=deepseek-chat
LLM_PROVIDER=deepseek                    # "deepseek" or "glm5"
LLM_MAX_TOKENS=100
LLM_TEMPERATURE=0.7
LLM_TIMEOUT=30
USE_LLM_DECEPTION=true

# ── Gemini Chatbot ──
GEMINI_API_KEY=AIzaSy...

# ── Blockchain (Sepolia) ──
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/...
PRIVATE_KEY=0x...
CONTRACT_ADDRESS=0x...

# ── Feature Flags ──
USE_MERKLE_INTEGRITY=true
FALLBACK_TO_STATIC_DECEPTION=true

# ── Honeypot Settings ──
CONFIDENCE_THRESHOLD=0.7
MAX_INPUT_LENGTH=200
HONEYPOT_DOMAIN=localhost:8000
```

### Admin Credentials

```
Username: admin
Password: chameleon2024
```

---

## 17. Dataset & Training Scripts

### Datasets

| File | Size | Description |
|------|------|-------------|
| `final_dataset.csv` | 3.9 MB | Full training dataset |
| `custom_attack_data.csv` | 81 KB | Custom attack samples |
| `custom_attack_data_6k.csv` | 948 KB | 6,000 DeepSeek-generated attack samples |

### Dataset Generation Scripts

| Script | Description |
|--------|-------------|
| `generate_attack_dataset.py` | Primary dataset generator |
| `generate_6k_dataset.py` | 6K sample generator |
| `generate_6k_deepseek_api.py` | Uses DeepSeek API to generate realistic attack payloads |

### Dataset Integrity

```json
{
  "total_samples": 50000,
  "hash": "sha256:...",
  "verified": true
}
```

---

## 18. Deployment

### Local Development

```bash
# Backend
cd Backend
source ../venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm install
npm run dev     # → http://localhost:5174
```

### Production (Single Service)

The backend serves the React frontend from `frontend/dist/`:

```bash
cd frontend && npm run build
cd ../Backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Docker

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY Backend/ .
COPY frontend/dist/ ../frontend/dist/
RUN pip install -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Render Deployment

```yaml
# render.yaml — multi-service
services:
  - type: web
    name: chameleon-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

## 19. Testing

### Test Files

| File | Description |
|------|-------------|
| `test_system.py` | End-to-end system tests |
| `test_trap_execute.py` | `/trap/execute` endpoint tests |
| `test_honeytoken.py` | Honeytoken beacon tests |
| `test_blockchain_sync.py` | Blockchain anchoring tests |
| `test_50k_model.py` | Model accuracy validation |
| `test_dataset_merge.py` | Dataset integrity tests |
| `test_refactored_modules.py` | Module integration tests |
| `test_modules_quick.py` | Quick module smoke tests |
| `test_progressive_deception.py` | Progressive deception stage tests |
| `test_local.py` | Local development tests |
| `test_chatbot.py` | Chatbot service tests |

### Shell Test Scripts

| File | Description |
|------|-------------|
| `test_integration.sh` | Full integration test suite |
| `test_deception.sh` | Deception engine tests |
| `test_blockchain_explorer.sh` | Blockchain explorer API tests |
| `test_dashboard_access.sh` | Dashboard access tests |
| `test_threat_scores.sh` | Threat score API tests |

### Quick Test: SQL Injection

```bash
curl -X POST 'http://localhost:8000/trap/execute' \
  -H 'Content-Type: application/json' \
  -d '{"command": "'\'' OR 1=1; DROP TABLE users; --"}'
```

**Expected Response:**
```json
{
  "response": "bash: ': command not found",
  "prediction_score": 0.74,
  "is_malicious": true,
  "hash": "d068ca9d...",
  "session_id": null
}
```

---

## Summary

**Chameleon** is a comprehensive, production-grade adaptive deception system with:

- 🤖 **BiLSTM ML model** trained on 50K samples for real-time attack classification
- 🎭 **LLM-powered deception** (DeepSeek) generating context-aware fake terminal responses
- 🔗 **Blockchain-backed integrity** via Merkle trees anchored to Ethereum Sepolia
- 🕵️ **Honeytoken beacons** for detecting data exfiltration
- 📊 **Rich dashboard** with 3D visualizations, live attack maps, and analytics
- 🤖 **AI chatbot** (Gemini 2.5 Pro) for cybersecurity Q&A
- 🛡️ **IP reputation scoring** with blockchain immutability
- 🔍 **Privacy-preserving threat intelligence** sharing
- 📱 **Full-stack React + FastAPI** with dark cyberpunk UI aesthetic
