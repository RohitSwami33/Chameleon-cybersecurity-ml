# Rigorous Async Test Suite for Chameleon Two-Stage ML Pipeline

Rewrite `test_rigorous_pipeline.py` to address bugs in the existing tests and add deeper assertions for all five scenario groups.

## Architecture Summary

The Chameleon honeypot uses a **two-stage ML pipeline**:

1. **Stage 1 – BiLSTM** (`bilstm_inference.py`): fast anomaly scorer (0.0–1.0)
2. **Stage 2 – MLX Qwen 2B** (`local_inference.py`): deep analysis returning `BLOCK`/`ALLOW`
3. **Pipeline** (`pipeline.py`): orchestrates Stage 1 → Stage 2 via `evaluate_payload()`
4. **Deception Layer** (`main.py:handle_deception_layer`): on `BLOCK` verdict, returns a fake 200 OK with deception content and logs `ATTACKER_IN_DECEPTION` telemetry to PostgreSQL

The `LocalMLXModel` singleton uses an `asyncio.Lock` to serialize GPU access (already implemented).

## Proposed Changes

### Test Suite

#### [MODIFY] [test_rigorous_pipeline.py](file:///Users/rohit/Documents/Sem-4_project/Chameleon-cybersecurity-ml/Backend/test_rigorous_pipeline.py)

Complete rewrite with these key improvements:

**1. Concurrency Stress Test (fixed)**
- Reset `login_limiter` before the test to prevent 429s from rate-limiter state
- Use unique source IPs per request group via `ASGITransport(client=...)` pattern
- Assert all 20 responses are `200` or `401` (never exceptions or dropped)

**2. Deception Layer Verification (strengthened)**
- Assert HTTP 200 strictly (not 401/403/500)
- Assert deception schema: `status=success`, `session_id=fake_token_123_abc`
- Spy on `db.session_factory` mock to verify `HoneypotLog` was `.add()`ed with `log_metadata["classification"]["attack_type"] == "ATTACKER_IN_DECEPTION"`

**3. Adversarial & Edge-Case Payloads**
- 5,000-char massive string
- Null bytes `\x00\x00\x00`
- Base64-encoded injection
- Unicode/emoji payload
- Empty string
- Nested quotes / path traversal

**4. BiLSTM→MLX Handover (unit tests on `pipeline.evaluate_payload`)**
- Mock `bilstm_model.predict` to return high anomaly → verify `mlx_model.infer` is called
- Mock low anomaly → verify MLX still called (bypass threshold not active)
- Multiple sequential payloads with `side_effect`

**5. Async Lock Verification**
- `LocalMLXModel._async_lock` attribute existence
- Concurrent `infer()` calls with mocked `generate` → all complete without crash
- Verify BLOCK/ALLOW parsing from model output

## Verification Plan

### Automated Tests

Run the complete test suite:

```bash
cd /Users/rohit/Documents/Sem-4_project/Chameleon-cybersecurity-ml/Backend
../venv/bin/pytest test_rigorous_pipeline.py -v
```

All tests must pass. Expected: 20+ tests across 6 test classes, 0 failures.
