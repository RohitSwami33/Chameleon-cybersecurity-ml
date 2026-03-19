# Chameleon — Implementation Dependencies & Special Conditions

> This file tracks every external dependency, env var, migration, and special condition
> introduced by the 44 edge case solutions. Append to this file after each EC is applied.

---

## New Package Dependencies

| EC | Package | Version | Install Command | Fallback if Absent |
|---|---|---|---|---|
| EC-014 | redis[asyncio] | >=4.0.0 | `pip install redis[asyncio]` | JWT revocation disabled — expiry-only mode |
| EC-038 | cachetools | >=5.0.0 | `pip install cachetools` | System will OOM on high-traffic — MUST install |
| EC-039 | cachetools | >=5.0.0 | (same as EC-038) | Same |

### Verify all dependencies:
```bash
python -c "import redis; print('redis ok')"
python -c "from cachetools import TTLCache; print('cachetools ok')"
python -c "import httpx; print('httpx ok')"
python -c "from jose import jwt; print('jose ok')"
python -c "import unicodedata; print('unicodedata ok')"  # stdlib
python -c "import hashlib; print('hashlib ok')"          # stdlib
python -c "import secrets; print('secrets ok')"          # stdlib
python -c "import math; print('math ok')"                # stdlib
```

---

## New Environment Variables Required

| EC | Variable | Required/Optional | Description | Example |
|---|---|---|---|---|
| EC-009 | `ADMIN_USERNAME` | REQUIRED | Dashboard admin username | `chameleon_admin` |
| EC-009 | `ADMIN_PASSWORD` | REQUIRED | Dashboard admin password (strong) | 32+ char random string |
| EC-009 | `JWT_SECRET_KEY` | REQUIRED | JWT signing secret (strong) | 64+ char random string |
| EC-009 | `POSTGRES_USER` | REQUIRED | PostgreSQL username | `chameleon_user` |
| EC-009 | `POSTGRES_PASSWORD` | REQUIRED | PostgreSQL password (strong) | 32+ char random string |
| EC-014 | `REDIS_URL` | OPTIONAL | Redis connection string | `redis://localhost:6379/0` |
| EC-029 | `WEBHOOK_URL` | OPTIONAL | Alert webhook (Discord/Slack) | `https://discord.com/api/webhooks/...` |
| EC-034 | `WEBHOOK_URL` | OPTIONAL | (same as EC-029) | |

### Weak values that will trigger startup abort (EC-009):
```
"", "admin", "password", "chameleon123", "changeme", "secret",
"your-secret-key-change-in-production", "default", "test", "123456",
"pass", "postgres", "chameleon"
```

### Generate strong secrets:
```bash
python -c "import secrets; print(secrets.token_hex(32))"   # 64-char hex secret
python -c "import secrets; print(secrets.token_urlsafe(48))"  # URL-safe secret
```

---

## Database Migrations Required

| EC | Migration | Type | SQL |
|---|---|---|---|
| EC-005 | user_agent column resize | ALTER TABLE | `ALTER TABLE beacon_events ALTER COLUMN user_agent TYPE VARCHAR(512);` |
| EC-019 | reputation_score check constraint | ADD CONSTRAINT | `ALTER TABLE reputation_scores ADD CONSTRAINT reputation_score_valid CHECK (reputation_score >= 0.0 AND reputation_score <= 100.0 AND reputation_score = reputation_score);` |
| EC-024 | honeypot_logs covering index | CREATE INDEX | `CREATE INDEX IF NOT EXISTS idx_honeypot_logs_created ON honeypot_logs(created_at DESC);` |
| EC-024 | honeypot_logs IP index | CREATE INDEX | `CREATE INDEX IF NOT EXISTS idx_honeypot_logs_ip ON honeypot_logs(source_ip);` |

### Run migrations:
```bash
cd Backend
alembic revision --autogenerate -m "ec_solutions_$(date +%Y%m%d)"
alembic upgrade head
```

---

## New Files Created

| EC | File | Purpose |
|---|---|---|
| EC-006 | `Backend/src/utils/trap_rate_limiter.py` | Token bucket per-IP limiter |
| EC-025 | `Backend/src/ml_engine/normaliser.py` | Full normalisation pipeline (NFKC-HCM + SMN + WCP + TLN) |

---

## Special Conditions & Constraints

### Deception Surface Contract
Every solution that touches a request/response path MUST comply:
- `/trap/execute` ALWAYS returns HTTP 200 with a JSON body containing `response`, `prediction_score`, `is_malicious`
- No 4xx or 5xx from `/trap/execute` under ANY circumstances
- No error messages, stack traces, or debug output in any response visible to the attacker
- Response timing must remain consistent — no timing side channels

### Circuit Breaker Behaviour (EC-043)
When the DeepSeek/GLM circuit is OPEN:
- Static fallback responses are served from `get_static_fallback(command)`
- Operators are warned via SWAD digest alert
- Circuit resets to HALF_OPEN after 30 seconds automatically
- No operator intervention required for recovery

### Redis Unavailability (EC-014)
If Redis is down or not configured:
- JWT revocation is disabled automatically
- System logs a WARNING (not ERROR) — this is expected in development environments
- Token expiry (15 minutes) provides adequate security without revocation
- No user-facing impact

### Model Failure Mode (EC-029)
If the ML model fails to load:
- `MODEL_HEALTHY = False` is set globally
- Heuristic classifier handles all classification
- Detection accuracy drops from ~95% to ~60-70% (heuristic-only)
- Operators are alerted via webhook (if configured) or stderr
- Honeypot continues operating — no downtime

---

## Execution Log Template

Copy this template into `logs/implementation.log` and fill in as you apply each EC:

```
=== CHAMELEON IMPLEMENTATION LOG ===
Started: [DATE]
Operator: [NAME]

[TIMESTAMP] EC-001 | Status: [ ] PENDING | File: api/main.py
[TIMESTAMP] EC-002 | Status: [ ] PENDING | File: utils/utils.py, api/main.py
[TIMESTAMP] EC-003 | Status: [ ] PENDING | File: core/config.py
[TIMESTAMP] EC-004 | Status: [ ] PENDING | File: deception_engine.py
[TIMESTAMP] EC-005 | Status: [ ] PENDING | File: api/main.py
[TIMESTAMP] EC-006 | Status: [ ] PENDING | New file: utils/trap_rate_limiter.py
[TIMESTAMP] EC-007 | Status: [ ] PENDING | File: [geo function file]
[TIMESTAMP] EC-008 | Status: [ ] PENDING | File: [geo function file]
[TIMESTAMP] EC-009 | Status: [ ] PENDING | File: core/config.py, api/main.py
[TIMESTAMP] EC-010 | Status: [ ] PENDING | File: api/auth.py
[TIMESTAMP] EC-011 | Status: [ ] PENDING | File: api/auth.py
[TIMESTAMP] EC-012 | Status: [ ] PENDING | File: api/auth.py
[TIMESTAMP] EC-013 | Status: [ ] PENDING | File: api/auth.py
[TIMESTAMP] EC-014 | Status: [ ] PENDING | File: api/auth.py, core/config.py
[TIMESTAMP] EC-015 | Status: [ ] PENDING | File: api/auth.py
[TIMESTAMP] EC-016 | Status: [ ] PENDING | File: api/auth.py
[TIMESTAMP] EC-017 | Status: [ ] PENDING | File: core/config.py
[TIMESTAMP] EC-018 | Status: [ ] PENDING | File: core/database_postgres.py
[TIMESTAMP] EC-019 | Status: [ ] PENDING | File: utils/threat_score.py
[TIMESTAMP] EC-020 | Status: [ ] PENDING | File: ml_engine/ml_inference.py
[TIMESTAMP] EC-021 | Status: [ ] PENDING | File: core/database_postgres.py
[TIMESTAMP] EC-022 | Status: [ ] PENDING | File: core/database.py
[TIMESTAMP] EC-023 | Status: [ ] PENDING | File: utils/utils.py
[TIMESTAMP] EC-024 | Status: [ ] PENDING | File: core/database.py
[TIMESTAMP] EC-025 | Status: [ ] PENDING | New file: ml_engine/normaliser.py
[TIMESTAMP] EC-026 | Status: [ ] PENDING | File: ml_engine/normaliser.py
[TIMESTAMP] EC-027 | Status: [ ] PENDING | File: ml_engine/ml_classifier.py
[TIMESTAMP] EC-028 | Status: [ ] PENDING | File: ml_engine/normaliser.py
[TIMESTAMP] EC-029 | Status: [ ] PENDING | File: ml_engine/ml_inference.py
[TIMESTAMP] EC-030 | Status: [ ] PENDING | File: ml_engine/simple_tokenizer.py
[TIMESTAMP] EC-031 | Status: [ ] PENDING | File: ml_engine/normaliser.py
[TIMESTAMP] EC-032 | Status: [ ] PENDING | File: ml_engine/ml_inference.py
[TIMESTAMP] EC-033 | Status: [ ] PENDING | File: utils/alert_manager.py
[TIMESTAMP] EC-034 | Status: [ ] PENDING | File: utils/alert_manager.py
[TIMESTAMP] EC-035 | Status: [ ] PENDING | File: utils/alert_manager.py
[TIMESTAMP] EC-036 | Status: [ ] PENDING | File: utils/alert_manager.py
[TIMESTAMP] EC-037 | Status: [ ] PENDING | File: utils/alert_manager.py
[TIMESTAMP] EC-038 | Status: [ ] PENDING | File: utils/attacker_session.py
[TIMESTAMP] EC-039 | Status: [ ] PENDING | File: utils/llm_controller.py
[TIMESTAMP] EC-040 | Status: [ ] PENDING | File: utils/attacker_session.py
[TIMESTAMP] EC-041 | Status: [ ] PENDING | File: utils/llm_controller.py
[TIMESTAMP] EC-042 | Status: [ ] PENDING | File: utils/llm_controller.py
[TIMESTAMP] EC-043 | Status: [ ] PENDING | File: utils/llm_controller.py
[TIMESTAMP] EC-044 | Status: [ ] PENDING | File: utils/llm_controller.py

=== END LOG ===
```

---

*Chameleon Dependencies & Conditions — March 2026*
