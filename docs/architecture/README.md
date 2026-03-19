# Chameleon — Architecture Timeline

This directory documents the evolution of the Chameleon Adaptive Deception Honeypot from its initial cloud-based prototype to its production-ready, air-gapped, locally-inferred architecture.

Each file is an Architecture Decision Record (ADR) following a consistent format: context, decision, rationale, implementation detail, and consequences.

---

## Document Index

| # | File | Topic | Status |
|---|------|--------|--------|
| 01 | [01_deepseek_to_local_mlx_migration.md](./01_deepseek_to_local_mlx_migration.md) | DeepSeek API → Local MLX Qwen 2B (OPSEC, LoRA fine-tuning, 4-bit quantization) | ✅ Implemented |
| 02 | [02_handling_gpu_concurrency_and_locks.md](./02_handling_gpu_concurrency_and_locks.md) | Metal SIGABRT crash diagnosis and `asyncio.Lock` fix | ✅ Implemented |
| 03 | [03_bilstm_and_deception_layer.md](./03_bilstm_and_deception_layer.md) | Two-stage BiLSTM + MLX pipeline and HTTP-200 deception routing | ✅ Implemented |
| 04 | [04_rigorous_testing_and_validation.md](./04_rigorous_testing_and_validation.md) | 28-test async-aware pytest suite — design, bugs found, and final results | ✅ 28/28 Passing |

---

## Chronological Summary

```
Phase 1 (ADR-001): Replace cloud API inference with air-gapped local MLX
    ↓
Phase 2 (ADR-002): Fix Metal GPU command buffer collision under concurrent load
    ↓
Phase 3 (ADR-003): Integrate BiLSTM fast-filter + deception layer (HTTP 200 trap)
    ↓
Phase 4 (ADR-004): Validate full stack with 28-test async test suite
```

---

## Running Tests

```bash
cd Backend
../venv/bin/pytest test_rigorous_pipeline.py -v
# Expected: 28 passed
```
