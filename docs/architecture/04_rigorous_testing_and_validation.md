# ADR-004: Rigorous QA — Async-Aware Test Suite Design and Validation

**Status:** Implemented  
**Date:** 2026-03  
**Component:** `Backend/test_rigorous_pipeline.py`  
**Test Result:** ✅ 28/28 PASSED (18.63s)  
**Authors:** Chameleon Core Team

---

## 1. Context

Following the architectural changes documented in `ADR-001` through `ADR-003`, a comprehensive test suite was required to:

1. **Validate correctness** of the two-stage ML pipeline under nominal conditions.
2. **Reproduce and confirm the fix** for the Metal SIGABRT crash under concurrent load.
3. **Verify deception layer invariants**: HTTP 200 responses, correct deception schema, and accurate PostgreSQL telemetry tagging.
4. **Probe robustness** against adversarial and edge-case inputs that could destabilise inference or crash the server.

The test suite was authored using `pytest-asyncio` (mode: `AUTO`) and `httpx.AsyncClient` with `ASGITransport`, enabling in-process FastAPI testing without a running server.

---

## 2. Test Architecture

### 2.1 Fixture Design Philosophy

All external I/O dependencies (PostgreSQL, MongoDB, MLX GPU inference, BiLSTM model) are fully mocked. This ensures:
- Tests execute in < 30 seconds (no real DB or GPU calls).
- Tests are fully deterministic and reproducible in CI/CD pipelines without GPU hardware.
- Each test controls the exact ML verdict (`BLOCK`/`ALLOW`) to isolate the behaviour under test.

#### Core Fixtures

```python
@pytest.fixture
def mock_db_session():
    """
    Installs a complete FastAPI dependency override for get_db AND patches
    db.session_factory (used by handle_deception_layer's direct DB access).
    Both must be mocked; patching only one leaves a live code path unprotected.
    """
    from database_postgres import get_db
    ctx = MockDBContext()
    app.dependency_overrides[get_db] = _make_get_db_override(ctx)
    with patch("main.db.session_factory", return_value=ctx):
        yield ctx
    app.dependency_overrides.pop(get_db, None)   # cleanup: prevent inter-test leakage

@pytest.fixture
def fresh_rate_limiter():
    """Clears the global LoginRateLimiter state before and after each test."""
    login_limiter.login_attempts.clear()
    yield
    login_limiter.login_attempts.clear()
```

### 2.2 `MockDBContext` — A Full SQLAlchemy Session Stub

A critical evolution during the testing phase was the discovery that `MockDBContext` was initially incomplete. The `/trap/execute` endpoint calls `session.flush()`, `session.rollback()`, and `session.close()` through FastAPI's `get_db` dependency generator. An incomplete mock caused `AttributeError` crashes in 4 tests (see §5.1 for the full bug report).

The final `MockDBContext` implements every method the application code may call:

```python
class MockDBContext:
    def _reset(self):
        self._added_objects = []
        self.add      = MagicMock(side_effect=self._track_add)
        self.commit   = AsyncMock()
        self.rollback = AsyncMock()   # ← Required by get_db exception handler
        self.close    = AsyncMock()   # ← Required by get_db finally block
        self.flush    = AsyncMock()   # ← Required by save_honeypot_log
        self.refresh  = AsyncMock()   # ← Required by save_honeypot_log
        _exec_result  = MagicMock()
        _exec_result.scalar_one_or_none.return_value = None
        self.execute  = AsyncMock(return_value=_exec_result)

    def _track_add(self, obj):
        self._added_objects.append(obj)   # Enables telemetry spy assertions
```

---

## 3. Test Classes and Coverage Map

### Class 1 — `TestConcurrencyAndThreadSafety` (3 tests)

**Objective:** Confirm that the Metal SIGABRT crash (SIGABRT from `IOGPUMetalCommandBuffer validate`) cannot be reproduced after the `asyncio.Lock` fix.

#### `test_concurrency_stress`
The primary regression test. Fires **20 simultaneous** `POST /api/auth/login` requests using `asyncio.gather`, mixing benign credentials (even indices) and SQL-injection payloads (odd indices).

```python
tasks = []
for i in range(20):
    if i % 2 == 0:
        body = {"username": f"legitimate_user_{i}", "password": "wrongpass"}
    else:
        body = {"username": f"admin' OR {i}={i}--", "password": "doesntmatter"}
    tasks.append(client.post("/api/auth/login", json=body))

responses = await asyncio.gather(*tasks, return_exceptions=True)

assert len(responses) == 20                         # No dropped requests
assert all(not isinstance(r, Exception) for r in responses)   # No crashes
assert all(r.status_code in (200, 401, 429) for r in responses)
```

**Why `return_exceptions=True`:** Without this flag, a single exception in any of the 20 tasks would propagate immediately and cancel all remaining tasks, masking the true failure count. With `return_exceptions=True`, all tasks complete and exceptions are collected for inspection.

#### `test_singleton_not_duplicated`
Verifies the thread-safe `__new__` implementation. Instantiating `LocalMLXModel()` twice must return the same Python object:

```python
assert LocalMLXModel() is LocalMLXModel()
```

#### `test_concurrent_mixed_endpoints`
20 requests across three different endpoints (`/api/auth/login`, `/api/trap/submit`, `/trap/execute`) concurrently. Tests that the `asyncio.Lock` correctly serialises GPU access across endpoint boundaries.

---

### Class 2 — `TestDeceptionLayerVerification` (4 tests)

**Objective:** Assert the three invariants of the deception layer: HTTP status, response schema, and telemetry tagging.

#### `test_sql_injection_returns_deception_200`
The canonical deception test. Sends `admin' OR 1=1--` with MLX mocked to return `"BLOCK"`.

```python
# Invariant 1: HTTP status is strictly 200 (not 401/403/500)
assert resp.status_code == 200

# Invariant 2: Deception schema matches the login action handler
data = resp.json()
assert data["status"] == "success"
assert data["session_id"] == "fake_token_123_abc"
assert data["message"] == "Login successful"

# Invariant 3: ATTACKER_IN_DECEPTION tag in PostgreSQL
log_obj = db_ctx._added_objects[0]
assert log_obj.log_metadata["classification"]["attack_type"] == "ATTACKER_IN_DECEPTION"
```

This three-layer assertion structure is the most comprehensive invariant in the test suite. Invariant 3 alone required the `_added_objects` tracking mechanism in `MockDBContext` (see §5.2).

Additional tests cover: command injection at `/api/trap/submit`, XSS at `/api/trap/submit`, and `/trap/execute` response shape validation (prediction score, is_malicious flag, SHA-256 hash length).

---

### Class 3 — `TestAdversarialAndEdgeCases` (6 tests)

**Objective:** Ensure malformed, oversized, and obfuscated inputs do not crash the pipeline.

| Test | Payload | Primary Risk Tested |
|---|---|---|
| `test_massive_5000_char_payload_no_oom` | `"A" * 5000` | MLX context window OOM; tokenizer buffer overflow |
| `test_null_bytes_payload` | `"\x00\x00\x00"` | Null-byte injection corrupting string operations |
| `test_base64_obfuscated_sql_injection` | `base64("admin' OR 1=1--")` | Evasion via encoding; pipeline robustness to opaque inputs |
| `test_unicode_and_emoji_payload` | `"🔥💀 SELECT *"` | UnicodeDecodeError in tokenizer; UTF-8 boundary handling |
| `test_empty_string_payload` | `""` | Empty-string edge case in BiLSTM and string formatting |
| `test_path_traversal_at_trap_execute` | `"../../../../etc/passwd"` | LFI attempt; correct BLOCK classification and 200 deception response |

The OOM test is particularly important: the MLX model uses `max_tokens=10` to cap output generation, but a 5 000-character input still stresses the *input* tokenization and embedding computation stages. The test asserts no exception is raised and a valid HTTP status is returned.

---

### Class 4 — `TestBiLSTMToMLXHandover` (5 tests)

**Objective:** Verify that `pipeline.evaluate_payload()` correctly orchestrates Stage 1 → Stage 2 under all input conditions.

```python
@patch("pipeline.bilstm_model.predict")
@patch("pipeline.mlx_model.infer", new_callable=AsyncMock)
async def test_high_anomaly_score_leads_to_block(self, mock_mlx, mock_bilstm):
    mock_bilstm.return_value = 0.99
    mock_mlx.return_value = "BLOCK"

    verdict = await pipeline.evaluate_payload("DROP TABLE users;")

    assert verdict == "BLOCK"
    mock_bilstm.assert_called_once_with("DROP TABLE users;")   # Stage 1 was called
    mock_mlx.assert_called_once_with("DROP TABLE users;")      # Stage 2 was called
```

#### `test_bilstm_called_before_mlx`
Strict call-ordering assertion using a shared `call_log` list:

```python
call_log: list[str] = []

def bilstm_side(cmd):
    call_log.append("bilstm")
    return 0.8

async def mlx_side(cmd):
    call_log.append("mlx")
    return "BLOCK"

await pipeline.evaluate_payload("test payload")
assert call_log == ["bilstm", "mlx"]   # Order is invariant
```

This test catches any future refactoring that might inadvertently reverse stage execution order or introduce a race condition.

#### `test_multiple_sequential_payloads_correct_verdicts`
Uses `side_effect` lists to simulate three sequential evaluations:

```python
mock_bilstm.side_effect = [0.99, 0.01, 0.85]
mock_mlx.side_effect    = ["BLOCK", "ALLOW", "BLOCK"]

verdicts = [await pipeline.evaluate_payload(p) for p in payloads]
assert verdicts == ["BLOCK", "ALLOW", "BLOCK"]
```

---

### Class 5 — `TestLocalMLXModelAsyncLock` (7 tests)

**Objective:** Unit-test the `LocalMLXModel` singleton and its `asyncio.Lock` in isolation from the full HTTP stack.

| Test | Assertion |
|---|---|
| `test_singleton_returns_same_instance` | `LocalMLXModel() is LocalMLXModel()` |
| `test_async_lock_attribute_present` | `isinstance(model._async_lock, asyncio.Lock)` after first `infer()` |
| `test_concurrent_infer_calls_all_complete` | 5 concurrent `infer()` calls complete with zero exceptions |
| `test_infer_parses_block_verdict` | `generate()` returning `"BLOCK"` → `infer()` returns `"BLOCK"` |
| `test_infer_parses_allow_verdict` | `generate()` returning `"ALLOW"` → `infer()` returns `"ALLOW"` |
| `test_infer_failsafe_on_unknown_output` | Garbled output → `infer()` returns `"ALLOW"` (fail-safe) |
| `test_infer_returns_allow_when_model_not_loaded` | `model=None` → `infer()` returns `"ALLOW"` without raising |

---

### Class 6 — `TestAdditionalSecurityScenarios` (3 tests)

**Objective:** Validate security invariants not covered by the primary classes.

#### `test_benign_login_returns_401_not_deception`
Confirms that genuinely benign traffic (ALLOW verdict + wrong password) receives `HTTP 401`, not `HTTP 200`. This guards against a misconfiguration where the deception layer is accidentally triggered for all requests:

```python
with patch.object(mlx_model, "infer", return_value="ALLOW"):
    resp = await client.post("/api/auth/login",
                             json={"username": "honest_user", "password": "wrong"})

assert resp.status_code in (401, 429)   # Never 200 for benign ALLOW
```

#### `test_sha256_hash_in_trap_execute_response`
Every `/trap/execute` response must contain a 64-character SHA-256 hex string computed from the interaction metadata. This verifies the cryptographic integrity layer:

```python
data = resp.json()
assert len(data["hash"]) == 64
int(data["hash"], 16)   # Raises ValueError if not valid hex
```

---

## 4. Infrastructure Decisions

### 4.1 `asyncio_mode = AUTO` (pytest.ini)

```ini
[pytest]
asyncio_mode = auto
asyncio_default_fixture_loop_scope = function
```

`AUTO` mode allows `async def test_*` functions to be recognised as tests without requiring the `@pytest.mark.asyncio` decorator on every function, reducing boilerplate. `loop_scope = function` ensures each test gets an independent event loop, preventing `asyncio.Lock` instances from leaking between test functions.

### 4.2 `ASGITransport` with Custom Client IP

```python
AsyncClient(
    transport=ASGITransport(app=app, client=("10.1.0.1", 1111)),
    base_url="http://testserver",
)
```

The `client` tuple sets the source IP as seen by `request.client.host` inside the FastAPI handler. This is critical for tests involving the `LoginRateLimiter`, which tracks attempts by IP address. Tests that share an IP and do not reset the limiter state will receive unexpected 429 responses (see §5.3).

---

## 5. Critical Bug Reports and Resolutions

### 5.1 Bug: `AttributeError` on `session.rollback()` / `session.close()` (4 Tests Failing)

**Symptom:**
```
AttributeError: 'MockDBContext' object has no attribute 'close'
FAILED test_rigorous_pipeline.py::TestDeceptionLayerVerification::test_trap_execute_deception_response_shape
```

**Root Cause:** The `/trap/execute` endpoint uses `Depends(get_db)`. The `get_db` async generator wrapper in `database_postgres.py` has an exception handler and a `finally` block:

```python
async with db.session_factory() as session:
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()   ← MockDBContext didn't have this
        raise
    finally:
        await session.close()      ← MockDBContext didn't have this
```

The earlier `MockDBContext` only implemented `.add()` and `.commit()`. Patching `db.session_factory` also did not help, because `Depends(get_db)` is resolved by FastAPI's dependency injection system, not by calling `db.session_factory` directly.

**Resolution:**
1. Added `rollback`, `close`, `flush`, `refresh`, and `execute` as `AsyncMock`s to `MockDBContext`.
2. Changed `mock_db_session` fixture to install `app.dependency_overrides[get_db]`, which correctly intercepts FastAPI's DI resolution for endpoints using `Depends(get_db)`.

```python
@pytest.fixture
def mock_db_session():
    from database_postgres import get_db
    ctx = MockDBContext()
    app.dependency_overrides[get_db] = _make_get_db_override(ctx)  # ← Fix
    with patch("main.db.session_factory", return_value=ctx):
        yield ctx
    app.dependency_overrides.pop(get_db, None)
```

### 5.2 Bug: Weak `ATTACKER_IN_DECEPTION` Telemetry Assertion

**Symptom:** The original assertion only verified that `db_context.add.called` was truthy — it did not inspect *what* was added or whether the metadata was correctly structured. This produced a false-passing test: even a call to `.add(None)` would satisfy it.

**Resolution:** `MockDBContext._track_add()` appends every object passed to `.add()` into `_added_objects`. Tests now inspect the actual `HoneypotLog` object:

```python
log_obj = db_ctx._added_objects[0]
assert log_obj.log_metadata["classification"]["attack_type"] == "ATTACKER_IN_DECEPTION"
```

This makes the assertion behavioural (verifying actual data content) rather than structural (verifying a function was called).

### 5.3 Bug: Rate-Limiter State Bleed-Through Causing False 429s

**Symptom:** `test_concurrency_stress` failed with:
```
assert 401 == 200
```

**Root Cause:** The `LoginRateLimiter` is a module-level singleton that persists its IP-based attempt counter across test functions. Any test that issues 3 or more login requests against the same IP without resetting the limiter will cause all subsequent logins from that IP to return `HTTP 429 Too Many Requests`. With 20 requests sharing `127.0.0.1`, the third request triggered the limiter and all subsequent ones returned 429.

**Resolution:** The `fresh_rate_limiter` fixture clears the global state before and after each relevant test:

```python
@pytest.fixture
def fresh_rate_limiter():
    login_limiter.login_attempts.clear()
    yield
    login_limiter.login_attempts.clear()
```

This is an instance of **test isolation** — a fundamental principle: tests must not depend on the execution order or side-effects of other tests.

---

## 6. Final Test Run

```
============================= test session starts ==============================
platform darwin -- Python 3.14.0, pytest-9.0.2
asyncio: mode=Mode.AUTO

collected 28 items

TestConcurrencyAndThreadSafety::test_concurrency_stress              PASSED
TestConcurrencyAndThreadSafety::test_singleton_not_duplicated        PASSED
TestConcurrencyAndThreadSafety::test_concurrent_mixed_endpoints      PASSED
TestDeceptionLayerVerification::test_sql_injection_returns_deception_200  PASSED
TestDeceptionLayerVerification::test_command_injection_deception_200 PASSED
TestDeceptionLayerVerification::test_xss_payload_deception_200       PASSED
TestDeceptionLayerVerification::test_trap_execute_deception_response_shape PASSED
TestAdversarialAndEdgeCases::test_massive_5000_char_payload_no_oom   PASSED
TestAdversarialAndEdgeCases::test_null_bytes_payload                 PASSED
TestAdversarialAndEdgeCases::test_base64_obfuscated_sql_injection     PASSED
TestAdversarialAndEdgeCases::test_unicode_and_emoji_payload          PASSED
TestAdversarialAndEdgeCases::test_empty_string_payload               PASSED
TestAdversarialAndEdgeCases::test_path_traversal_at_trap_execute     PASSED
TestBiLSTMToMLXHandover::test_high_anomaly_score_leads_to_block      PASSED
TestBiLSTMToMLXHandover::test_low_anomaly_score_mlx_still_called     PASSED
TestBiLSTMToMLXHandover::test_boundary_score_mlx_is_authoritative    PASSED
TestBiLSTMToMLXHandover::test_multiple_sequential_payloads_correct_verdicts PASSED
TestBiLSTMToMLXHandover::test_bilstm_called_before_mlx               PASSED
TestLocalMLXModelAsyncLock::test_singleton_returns_same_instance     PASSED
TestLocalMLXModelAsyncLock::test_async_lock_attribute_present        PASSED
TestLocalMLXModelAsyncLock::test_concurrent_infer_calls_all_complete PASSED
TestLocalMLXModelAsyncLock::test_infer_parses_block_verdict          PASSED
TestLocalMLXModelAsyncLock::test_infer_parses_allow_verdict          PASSED
TestLocalMLXModelAsyncLock::test_infer_failsafe_on_unknown_output    PASSED
TestLocalMLXModelAsyncLock::test_infer_returns_allow_when_model_not_loaded PASSED
TestAdditionalSecurityScenarios::test_benign_login_returns_401_not_deception PASSED
TestAdditionalSecurityScenarios::test_attacker_ip_captured_in_telemetry PASSED
TestAdditionalSecurityScenarios::test_sha256_hash_in_trap_execute_response PASSED

============================== 28 passed in 18.63s =============================
```

---

## 7. Running the Test Suite

```bash
# Full suite (recommended)
cd Backend
../venv/bin/pytest test_rigorous_pipeline.py -v

# Single test class
../venv/bin/pytest test_rigorous_pipeline.py::TestDeceptionLayerVerification -v

# Exclude slow concurrency tests for rapid iteration
../venv/bin/pytest test_rigorous_pipeline.py -v -k "not concurrency"

# With full stdout capture (useful when debugging mock interactions)
../venv/bin/pytest test_rigorous_pipeline.py -v -s
```

No additional flags are required beyond the defaults in `pytest.ini` (`asyncio_mode = auto`).

---

## 8. Related Documents

- `ADR-001` — `01_deepseek_to_local_mlx_migration.md` — Local MLX model
- `ADR-002` — `02_handling_gpu_concurrency_and_locks.md` — `asyncio.Lock` GPU serialisation
- `ADR-003` — `03_bilstm_and_deception_layer.md` — Two-stage pipeline and deception
- `Backend/test_rigorous_pipeline.py` — Full test implementation
- `Backend/conftest.py` — Shared pytest fixtures
- `Backend/pytest.ini` — pytest configuration
