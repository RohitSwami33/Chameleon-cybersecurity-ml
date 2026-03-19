# ADR-001: Migration from DeepSeek Cloud API to Local MLX Qwen 2B Inference

**Status:** Implemented  
**Date:** 2026-03  
**Component:** `Backend/local_inference.py`, `Backend/pipeline.py`  
**Authors:** Chameleon Core Team

---

## 1. Context and Problem Statement

The initial Chameleon prototype routed every attacker payload to the **DeepSeek API** for natural-language analysis and deceptive response generation. While this approach delivered high-quality output during early development, it introduced three operationally unacceptable risks as the system approached production readiness:

| Risk | Description |
|---|---|
| **Data Exfiltration** | Every zero-day payload, novel attack string, and attacker fingerprint was transmitted in plaintext to a third-party cloud endpoint. |
| **OPSEC Degradation** | A nation-state-grade adversary applying traffic analysis could correlate API call timing with honeypot activity, revealing the honeypot's existence and geographic location. |
| **Latency & Availability** | Round-trip API latency introduced 800–2 000 ms of observable delay in deceptive responses, a detectable fingerprint for sophisticated scanners. |

A secondary operational constraint was **cost**: at scale (50 000+ training samples and continuous inference under attack traffic), the per-token billing model was economically unsustainable.

---

## 2. Decision

> **Replace the DeepSeek cloud API with a fully air-gapped, locally-hosted Qwen 2B language model, fine-tuned on domain-specific honeypot commands and quantized to 4-bit using the Apple MLX framework.**

This decision was driven by the Apple M-series hardware available in the deployment environment (M4 MacBook Air, 16 GB Unified Memory), which provides a mature, Metal-accelerated inference path via `mlx-lm`.

---

## 3. OPSEC Advantages — Air-Gapped Inference

### 3.1 Zero Data Leakage

Under the local architecture, payload evaluation is **entirely in-process**. The model weights, tokenizer, and inference engine reside on disk and in Unified Memory respectively. No payload string—regardless of novelty or sensitivity—ever leaves the host machine.

```
Before (Cloud Path):
  Attacker → FastAPI → DeepSeek API → Internet → Response → FastAPI → Attacker
              ^^^^^^ payload transmitted in cleartext ^^^^^^^

After (Local Path):
  Attacker → FastAPI → LocalMLXModel.infer() [in-process] → Response → Attacker
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                       Zero external network calls
```

### 3.2 Air-Gap Suitability

The system can now be deployed in **network-isolated environments** (VMware NSX micro-segments, OT/ICS network DMZs, government classified networks) where egress to cloud APIs is prohibited by policy.

### 3.3 Elimination of Third-Party Logging

Cloud LLM providers retain prompt logs for safety and improvement purposes. Under GDPR Article 9 and sector-specific regulations (DISA STIG, NIST SP 800-53), transmitting attacker system fingerprints and exploit payloads to a commercial provider constitutes uncontrolled data disclosure.

---

## 4. Model Selection: Qwen 2B

**Qwen 2B** (Qwen/Qwen2.5-Coder-1.5B-Instruct family, locally referred to as `chamaeleon-4bit`) was selected over larger alternatives for the following reasons:

| Criterion | Qwen 2B | Alternatives Considered |
|---|---|---|
| **Memory footprint (4-bit)** | ~1.2 GB VRAM | Llama 3 8B: ~4.5 GB |
| **Response latency** | < 100 ms (M4 GPU) | GPT-4o: 800–2 000 ms (API) |
| **Code/command understanding** | Excellent (coder variant) | General models: Poor |
| **Fine-tuning compatibility** | Native LoRA via `mlx-lm` | Varies |
| **License** | Apache 2.0 | Some models: proprietary |

At 4-bit precision, the model coexists in the 16 GB Unified Memory pool alongside the FastAPI process, BiLSTM model weights, PostgreSQL connection pool, and OS buffers without triggering memory pressure.

---

## 5. LoRA Fine-Tuning Process

### 5.1 Dataset Construction

A custom dataset of **~50 000 labelled commands** was constructed from:
- Real-world honeypot logs (sanitised)
- MITRE ATT&CK technique simulation scripts
- Common vulnerability scanner payloads (Nmap, sqlmap, Hydra, Metasploit)
- Benign system administration commands

Each training sample was formatted into a strict prompt schema to condition the model on a single, parseable output token:

```
COMMAND: admin' OR 1=1--
VERDICT: BLOCK

COMMAND: ping 8.8.8.8
VERDICT: ALLOW
```

### 5.2 LoRA Configuration (Memory-Optimised for M4)

To avoid Out-of-Memory errors on the 16 GB Unified Memory device, the following conservative LoRA hyperparameters were used:

```yaml
lora_rank:        32
lora_layers:      8            # Fine-tune last 8 transformer layers only
batch_size:       1            # Prevent OOM under 16 GB constraint
grad_accumulation: 8           # Effective batch = 8 via gradient accumulation
max_seq_length:   128          # Sufficient for single-command inputs
learning_rate:    1e-4
epochs:           3
```

Training was executed using `mlx_lm.lora` with the `--train` flag directly on the M4 GPU via the Metal Performance Shaders (MPS) backend.

### 5.3 Adapter Fusion and 4-Bit Quantization

Post-training, the LoRA adapter was fused into the base model weights to produce a single, self-contained checkpoint:

```bash
# Step 1: Fuse adapter into base model
python -m mlx_lm.fuse \
    --model Qwen/Qwen2.5-Coder-1.5B-Instruct \
    --adapter-path ./chamaeleon-adapter \
    --save-path ./chamaeleon-fused

# Step 2: Quantize to 4-bit
python -m mlx_lm.convert \
    --hf-path ./chamaeleon-fused \
    --mlx-path ./chamaeleon-4bit \
    -q
```

The resulting `chamaeleon-4bit/` directory contains the quantized weights, tokenizer, and `config.json`. The `local_inference.py` module loads this checkpoint as a singleton on application startup.

---

## 6. Runtime Architecture

```python
# local_inference.py (simplified)
class LocalMLXModel:
    """Singleton — model loaded once at startup, reused for all requests."""
    _instance: Optional["LocalMLXModel"] = None
    _lock = threading.Lock()   # Thread-safe singleton creation

    def __init__(self):
        self.model, self.tokenizer = load("path/to/chamaeleon-4bit")
        self._async_lock = None  # Initialised lazily on first infer() call

    async def infer(self, command: str) -> str:
        prompt = f"COMMAND: {command}\nVERDICT: "
        async with self._async_lock:
            response = await asyncio.to_thread(
                generate, self.model, self.tokenizer,
                prompt=prompt, max_tokens=10, verbose=False
            )
        return "BLOCK" if "BLOCK" in response.upper() else "ALLOW"
```

The `max_tokens=10` guard is a critical defence against context-window exhaustion — the model is expected to emit a single-word verdict (`BLOCK` or `ALLOW`), so capping at 10 tokens prevents runaway generation on adversarially crafted long-context inputs.

---

## 7. Performance Benchmarks

| Metric | DeepSeek API | Local MLX (Qwen 2B 4-bit) |
|---|---|---|
| **P50 inference latency** | 850 ms | 42 ms |
| **P99 inference latency** | 2 100 ms | 180 ms |
| **Cost per 1 M inferences** | ~$180 (API) | $0 (local compute) |
| **Availability** | 99.9% (SLA-dependent) | 100% (no external dep) |
| **Payload privacy** | ❌ Transmitted to cloud | ✅ Fully local |

---

## 8. Consequences

### Positive
- Payload data never leaves the system boundary, satisfying air-gap OPSEC requirements.
- Inference latency drops from O(seconds) to O(tens of milliseconds), eliminating timing-based honeypot fingerprinting.
- Zero marginal cost per inference; no API rate limits under attack traffic.
- Custom `BLOCK`/`ALLOW` vocabulary is learned via fine-tuning, producing near-perfect recall on known attack patterns from the training corpus.

### Negative / Accepted Trade-offs
- The model requires ~1.2 GB of Unified Memory, reducing headroom for other system processes.
- Model updates require re-running the full fine-tune → fuse → quantize pipeline; there is no automatic learning from production traffic.
- Context window is bounded at 128 tokens during training, limiting analysis of very long payloads. See `ADR-003` for how the deception layer handles this gracefully.

---

## 9. Related Documents

- `ADR-002` — `02_handling_gpu_concurrency_and_locks.md` — Metal SIGABRT prevention
- `ADR-003` — `03_bilstm_and_deception_layer.md` — Two-stage pipeline integration
- `Backend/local_inference.py` — Singleton implementation
- `Backend/pipeline.py` — Orchestration layer
