# Rigorous Pipeline Test Suite — Walkthrough

## Result

```
28 passed in 18.63s
```

All tests green. Zero warnings promoted to failures.

---

## What Was Built

### `test_rigorous_pipeline.py` — 28 tests across 6 classes

| # | Class | Count | What it verifies |
|---|-------|-------|-----------------|
| 1 | `TestConcurrencyAndThreadSafety` | 3 | 20 async-gathered `asyncio.gather` requests; singleton identity; mixed-endpoint concurrency |
| 2 | `TestDeceptionLayerVerification` | 4 | HTTP 200 strictly; deception schema (`fake_token_123_abc`); `ATTACKER_IN_DECEPTION` tag in PostgreSQL mock |
| 3 | `TestAdversarialAndEdgeCases` | 6 | 5 000-char payload, null bytes, base64 obfuscation, unicode/emoji, empty string, path traversal |
| 4 | `TestBiLSTMToMLXHandover` | 5 | High/low/boundary anomaly scores; `side_effect` chain; strict call-order assertion |
| 5 | `TestLocalMLXModelAsyncLock` | 7 | `asyncio.Lock` lazy-init; 5 concurrent `infer()` calls; BLOCK/ALLOW parsing; failsafe; unloaded model |
| 6 | `TestAdditionalSecurityScenarios` | 3 | Benign → 401 (not 200); IP fingerprint capture; 64-char SHA-256 hash format |

---

## Key Fixes vs Previous Suite

### 1. Rate-Limiter Bleed-Through in Concurrency Test
**Problem:** All 20 requests from the same IP → `LoginRateLimiter` blocks after 3 attempts → unexpected 429s → `test_concurrency_stress` failed with `assert 401 == 200`.

**Fix:** Added `fresh_rate_limiter` fixture that calls `login_limiter.login_attempts.clear()` before and after each test.

### 2. `MockDBContext` Missing Methods
**Problem:** `/trap/execute` uses FastAPI's `get_db` Depends, which calls `session.flush()`, `session.rollback()`, `session.close()`. Previous mock lacked these → `AttributeError` in 4 tests.

**Fix:** `MockDBContext` now implements all required methods as `AsyncMock`s:
```python
self.flush    = AsyncMock()
self.rollback = AsyncMock()
self.close    = AsyncMock()
self.execute  = AsyncMock(return_value=...) # with scalar_one_or_none
```

### 3. FastAPI Dependency Override for `get_db`
**Problem:** Patching `db.session_factory` doesn't affect `Depends(get_db)` — FastAPI resolves the dependency independently.

**Fix:** `mock_db_session` fixture now installs `app.dependency_overrides[get_db]` → yields the `MockDBContext` directly, then cleans up after the test.
```python
app.dependency_overrides[get_db] = _make_get_db_override(ctx)
```

### 4. `ATTACKER_IN_DECEPTION` Telemetry Spy (Strengthened)
`MockDBContext` now tracks every object passed to `.add()` in `_added_objects`. The deception layer test inspects the actual `HoneypotLog` object:
```python
log_obj = db_ctx._added_objects[0]
assert log_obj.log_metadata["classification"]["attack_type"] == "ATTACKER_IN_DECEPTION"
```

---

## How to Run

```bash
cd /path/to/project/Backend
../venv/bin/pytest test_rigorous_pipeline.py -v

# Single class:
../venv/bin/pytest test_rigorous_pipeline.py::TestDeceptionLayerVerification -v

# Skip slow concurrency test:
../venv/bin/pytest test_rigorous_pipeline.py -v -k "not concurrency"
```

`pytest.ini` already sets `asyncio_mode = auto` — no extra flags needed.
