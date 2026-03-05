# Rigorous Pipeline Test Suite Rewrite

- [x] Review architecture files (main.py, pipeline.py, local_inference.py, bilstm_inference.py)
- [x] Create implementation plan
- [/] Rewrite `test_rigorous_pipeline.py` with improved test suite
  - [x] Fix concurrency stress test (rate limiter interference → fresh_rate_limiter fixture + unique IPs)
  - [x] Strengthen deception layer ATTACKER_IN_DECEPTION telemetry assertions
  - [x] Add adversarial edge-case payloads (5000 char, null bytes, base64)
  - [x] Add BiLSTM→MLX handover unit tests with proper mocking
  - [x] Add async lock serialization verification
  - [x] Fix MockDBContext (add flush/rollback/close) + get_db dependency override
- [/] Run full test suite and verify all tests pass
