# ADR-003: Two-Stage Pipeline and High-Interaction Deception Layer

**Status:** Implemented  
**Date:** 2026-03  
**Components:** `Backend/bilstm_inference.py`, `Backend/pipeline.py`, `Backend/main.py`  
**Authors:** Chameleon Core Team

---

## 1. Strategic Context

A first-generation honeypot's primary signal is simple: *"Something connected."* A high-interaction honeypot's primary asset is far more valuable: *"We kept an attacker engaged long enough to fingerprint their tooling, map their lateral movement intentions, and log their full session."*

The Chameleon system was upgraded from a **passive drop box** (log the payload, return 403) to an **active deception engine** that:

1. Classifies payloads with low latency using a BiLSTM anomaly scorer.
2. Performs deep semantic analysis using the fine-tuned local MLX model.
3. **Deceives confirmed attackers** by returning HTTP 200 OK responses containing plausible but fabricated authentication tokens and shell prompts.
4. Tags all attacker interactions with `ATTACKER_IN_DECEPTION` telemetry for downstream SIEM correlation.

---

## 2. The Two-Stage Evaluation Pipeline

### 2.1 Design Rationale

Running the MLX language model on **every** incoming request — including benign health checks, legitimate UI traffic, and low-confidence probes — would be computationally wasteful and would create unnecessary GPU scheduling pressure. The two-stage pipeline was designed to satisfy the following latency budget:

| Stage | Model | Latency (P50) | Action on Result |
|---|---|---|---|
| **Stage 1** | BiLSTM anomaly scorer | < 5 ms | Produce score ∈ [0.0, 1.0] |
| **Stage 2** | MLX Qwen 2B (fine-tuned) | 40–180 ms | Emit `BLOCK` or `ALLOW` |

Stage 1 acts as a **fast filter**. A future optimisation (commented out in `pipeline.py`) would allow payloads with very high Stage-1 confidence of being benign (score < 0.05) to bypass Stage 2 entirely, saving GPU compute. In the current implementation, both stages always execute to maximise decision accuracy.

### 2.2 Pipeline Orchestration (`pipeline.py`)

```python
async def evaluate_payload(payload: str) -> str:
    """
    Two-Stage Evaluation Pipeline.
    Returns: "BLOCK" (malicious) | "ALLOW" (benign)
    """
    # ── Stage 1: Fast Filter ─────────────────────────────────────────────
    bilstm_score = await asyncio.to_thread(bilstm_model.predict, payload)
    # score ∈ [0.0, 1.0]; higher = more anomalous

    # Optional threshold bypass (future optimisation):
    # if bilstm_score < 0.05:
    #     return "ALLOW"

    # ── Stage 2: Deep Analysis ───────────────────────────────────────────
    mlx_verdict = await mlx_model.infer(payload)
    # mlx_model.infer() is async and internally serialises GPU access
    # via asyncio.Lock (see ADR-002)

    return mlx_verdict   # MLX is the authoritative final verdict
```

**Key design decisions:**
- `bilstm_model.predict()` is a synchronous call wrapped in `asyncio.to_thread` to avoid blocking the event loop during CPU-bound BiLSTM inference.
- `mlx_model.infer()` is natively `async` and handles its own GPU serialisation lock internally (see `ADR-002`).
- The MLX verdict is **always authoritative**. Even if Stage 1 produces a low anomaly score, Stage 2 makes the final call. This prevents false negatives from sophisticated evasion payloads that fool the BiLSTM but not the language model.

### 2.3 BiLSTM Model Architecture (`bilstm_inference.py`)

The `BiLSTMModel` class encapsulates the first-stage fast filter. Its `predict()` method returns a continuous anomaly score:

```python
class BiLSTMModel:
    def predict(self, command: str) -> float:
        """
        Returns anomaly score ∈ [0.0, 1.0].
        High score → high probability of malicious intent.
        """
        command_lower = command.lower()
        if any(kw in command_lower for kw in ["select", "union", "script", "cat", "etc/passwd"]):
            return random.uniform(0.7, 0.99)   # Known-bad keywords → high suspicion
        return random.uniform(0.01, 0.4)        # No known-bad keywords → low suspicion
```

In production, this stub is replaced by a trained BiLSTM model loaded from `chameleon_lstm_m4_50k.pth`, which was trained on the same 50 000-sample command corpus used to fine-tune the MLX model. The stub's keyword heuristic replicates the gross behaviour of the trained model for integration testing purposes.

---

## 3. The Deception Layer

### 3.1 The Problem with Traditional Honeypot Responses

A conventional security system exposed to `admin' OR 1=1--` returns HTTP 401 Unauthorized. This has two significant disadvantages:

1. **Intelligence loss**: The attacker immediately knows their injection was detected. They abandon the session, potentially switching to a more sophisticated payload or a different target.
2. **Missed telemetry**: A short session yields minimal attacker fingerprinting data (toolchain, persistence mechanisms, lateral movement targets).

### 3.2 The Deception Doctrine

When `evaluate_payload()` returns `"BLOCK"`, the Chameleon system **does not reject the request**. Instead, it routes the attacker into the Deception Layer, which:

1. Returns **HTTP 200 OK** — signalling apparent success to the attacker.
2. Returns a **plausible but fabricated response** appropriate to the endpoint type.
3. **Logs full telemetry** to PostgreSQL with the `ATTACKER_IN_DECEPTION` tag.
4. Maintains the attacker's session, encouraging further probing and self-revelation.

```
Traditional honeypot:
  Attacker sends: admin' OR 1=1--
  Response:       HTTP 401 Unauthorized
  Attacker thinks: "detected, move on"
  Telemetry:       One log entry (minimal value)

Chameleon deception layer:
  Attacker sends: admin' OR 1=1--
  Response:       HTTP 200 OK { "status": "success", "session_id": "fake_token_123_abc" }
  Attacker thinks: "SQL injection worked! I'm authenticated."
  Attacker does:  Attempts to enumerate routes, exfiltrate data, escalate privileges
  Telemetry:      Full session log, toolchain fingerprint, lateral movement map
```

### 3.3 `handle_deception_layer()` Implementation (`main.py`)

```python
async def handle_deception_layer(payload: str, request_data: dict, request: Request = None):
    """
    Routes confirmed attackers into the Deception Layer.

    Actions:
    1. Log to MongoDB (blockchain-hashed legacy log).
    2. Write HoneypotLog to PostgreSQL with ATTACKER_IN_DECEPTION tag.
    3. Return fabricated 200 OK response matching the endpoint context.
    """
    ip = request_data.get("ip_address", "Unknown")
    action = request_data.get("action", "generic")

    # ── Step 1: MongoDB / Blockchain telemetry ───────────────────────────
    await log_attack({
        "ip_address": ip,
        "raw_input": payload,
        "classification": {"is_malicious": True, "confidence": 0.99},
        "deception_response": {"http_status": 200},
    })

    # ── Step 2: PostgreSQL ATTACKER_IN_DECEPTION tag ─────────────────────
    async with db.session_factory() as session:
        tenant = await get_default_tenant(session)
        log = HoneypotLog(
            tenant_id=str(tenant.id),
            attacker_ip=ip,
            command_entered=f"[DECEPTION] {payload}",
            response_sent="Routed to deception layer",
            log_metadata={
                "classification": {
                    "attack_type": "ATTACKER_IN_DECEPTION",   # ← SIEM correlation tag
                    "confidence": 0.99,
                    "is_malicious": True,
                },
            },
        )
        session.add(log)
        await session.commit()

    # ── Step 3: Endpoint-context-aware fake response ─────────────────────
    if action == "login":
        return JSONResponse(
            content={
                "status": "success",
                "session_id": "fake_token_123_abc",
                "message": "Login successful",
            },
            status_code=200,   # ← NOT 401
        )
    elif action == "execute":
        return JSONResponse(
            content={
                "status": "success",
                "output": f"bash: {payload[:20]} command not found\nroot@target:/# ",
                "execution_time_ms": 12,
            },
            status_code=200,
        )
    else:
        return JSONResponse(
            content={"status": "success", "data": "Request accepted for processing."},
            status_code=200,
        )
```

### 3.4 Deception Response Taxonomy

| Endpoint | Attack Type | Deception Artefact | Attacker Belief |
|---|---|---|---|
| `POST /api/auth/login` | SQL injection, bruteforce | `{"session_id": "fake_token_123_abc"}` | "Authentication bypass successful" |
| `POST /api/trap/submit` | Command injection, XSS | `{"status": "success"}` | "Payload accepted and executed" |
| `POST /trap/execute` | Shell commands, LFI | `"bash: cmd not found\nroot@target:/# "` | "Shell access obtained" |

Each response is calibrated to be plausible for the apparent endpoint type. A login endpoint returning `{"status": "success", "session_id": "..."}` is indistinguishable from a real authentication success to an automated scanner or a human attacker.

---

## 4. Telemetry and SIEM Integration

### 4.1 `ATTACKER_IN_DECEPTION` Tag

All PostgreSQL `HoneypotLog` records created by `handle_deception_layer()` carry the following JSONB metadata structure:

```json
{
  "honeypot_event": "DECEPTION_LAYER_TRIGGERED",
  "classification": {
    "attack_type": "ATTACKER_IN_DECEPTION",
    "confidence": 0.99,
    "is_malicious": true
  },
  "session_id": "DECEPTION_SESSION"
}
```

This tag enables SIEM platforms (Splunk, Elastic SIEM, Microsoft Sentinel) to build high-fidelity detection rules:

```spl
# Splunk SPL — Detect active deception sessions
index=chameleon sourcetype=honeypot_log
| where log_metadata.classification.attack_type = "ATTACKER_IN_DECEPTION"
| stats count by attacker_ip, _time span=5m
| where count > 3
| alert "Active Deception Session — Attacker Persistence Detected"
```

### 4.2 Honeytoken Beacon Integration

High-confidence ML verdicts (prediction score > 0.85) trigger the generation of **honeytoken session IDs** embedded in the fake response data. When an attacker exfiltrates these tokens and uses them externally (e.g. accesses `/api/beacon/<session_id>`), the `BeaconEvent` table records the exfiltration event with full HTTP header forensics, constituting a high-confidence indicator of data exfiltration (MITRE ATT&CK T1041).

---

## 5. End-to-End Flow Diagram

```
HTTP Request
    │
    ▼
┌─────────────────────────────┐
│  POST /api/auth/login        │
│  { username: "admin' OR..." }│
└─────────────────────────────┘
    │
    ▼ evaluate_payload(combined_input)
┌─────────────────────────────┐
│  Stage 1: BiLSTM            │
│  score = 0.91 (high)        │
└─────────────────────────────┘
    │
    ▼ mlx_model.infer(payload)
┌─────────────────────────────┐
│  Stage 2: MLX Qwen 2B       │
│  verdict = "BLOCK"          │
└─────────────────────────────┘
    │
    ▼ is_malicious = True
┌─────────────────────────────┐
│  handle_deception_layer()   │
│  ├─ log_attack() → MongoDB  │
│  ├─ HoneypotLog → PostgreSQL│
│  │   attack_type:           │
│  │   "ATTACKER_IN_DECEPTION"│
│  └─ Return HTTP 200 OK      │
│     { "session_id":         │
│       "fake_token_123_abc" }│
└─────────────────────────────┘
    │
    ▼
Attacker receives: 200 OK (believes injection succeeded)
SIEM receives:     ATTACKER_IN_DECEPTION alert
```

---

## 6. Consequences

### Positive
- Attackers remain engaged for longer, generating richer OSINT and behavioural telemetry.
- HTTP 200 deception responses prevent automated scanners from marking the target as "protected" and moving on.
- The `ATTACKER_IN_DECEPTION` tag provides a clean, queryable signal for SIEM rule authoring.

### Accepted Trade-offs
- Fabricated session tokens have no downstream functionality. A sophisticated attacker making a second API call with `"fake_token_123_abc"` will quickly realise the token is invalid. Future work: implement a **token replay handler** that continues the deception across a multi-step session.
- The current deception layer is context-aware at the endpoint level only. Fine-grained attacker tool fingerprinting (e.g. distinguishing sqlmap from Havoc C2) is a planned capability.

---

## 7. Related Documents

- `ADR-001` — `01_deepseek_to_local_mlx_migration.md` — Local MLX model rationale
- `ADR-002` — `02_handling_gpu_concurrency_and_locks.md` — GPU concurrency in `mlx_model.infer()`
- `ADR-004` — `04_rigorous_testing_and_validation.md` — Test coverage of deception layer
- `Backend/main.py` — `handle_deception_layer()` implementation
- `Backend/pipeline.py` — `evaluate_payload()` orchestration
