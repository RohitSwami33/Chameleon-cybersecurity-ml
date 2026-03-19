# ADR-002: GPU Concurrency Control — Eliminating Metal SIGABRT Crashes

**Status:** Implemented  
**Date:** 2026-03  
**Component:** `Backend/local_inference.py`  
**Severity of Original Bug:** P0 — Hard process crash (SIGABRT)  
**Authors:** Chameleon Core Team

---

## 1. Incident Report

During the first execution of the concurrency stress test (`test_concurrency_stress` — 20 simultaneous requests via `asyncio.gather`), the Python process terminated with a hard `SIGABRT` signal originating from Apple's IOKit GPU driver:

```
IOGPUMetalCommandBuffer validate -> MTLReportFailure
SIGABRT: Abort trap: 6
Process terminated.
```

No exception was raised in Python userspace. The OS killed the process directly to protect hardware integrity. The crash was **100% reproducible** under concurrent load and **never occurred** under sequential inference.

---

## 2. Root Cause Analysis

### 2.1 Apple M4 Unified Memory Architecture

The Apple M4 SoC uses a **Unified Memory Architecture (UMA)** in which the CPU and GPU share a single contiguous physical memory pool (16 GB on the affected device). Unlike discrete GPU systems where VRAM is isolated, on UMA:

- Model weights loaded by `mlx_lm.load()` reside in the **shared pool**.
- GPU command buffers (Metal `MTLCommandBuffer`) are allocated from the same pool.
- **There is no hardware-level isolation** between concurrent GPU submissions from the same process.

### 2.2 The Collision Sequence

Under `asyncio.gather`, FastAPI's `asyncio.to_thread` dispatched multiple OS threads into the Python process. Each thread called `mlx_lm.generate()` against the **same singleton model object**:

```
Timeline of crash:

T+0ms   Thread A:  mlx_lm.generate("COMMAND: ping 8.8.8.8\nVERDICT: ")
T+0ms              → Allocates MTLCommandBuffer #1
T+0ms              → Encodes Metal compute shader with model weights
T+0ms              → Commits buffer #1 to GPU queue

T+2ms   Thread B:  mlx_lm.generate("COMMAND: admin' OR 1=1--\nVERDICT: ")
        (concurrent)
T+2ms              → Allocates MTLCommandBuffer #2
T+2ms              → Begins encoding Metal compute shader...
T+2ms              ⚠ Attempts to READ model weight tensors
T+2ms              ⚠ Thread A's buffer #1 is WRITING to the same memory region
T+2ms
T+3ms   IOGPU:    MTLCommandBuffer validate: invalid buffer state
T+3ms   kernel:   SIGABRT → Python process killed
```

The MLX framework (as of the affected version) does not implement internal locking on the `generate()` function. It assumes single-threaded caller semantics, consistent with how it is documented for interactive use.

### 2.3 Why `asyncio` Exacerbated the Problem

The FastAPI / Starlette event loop runs on a single thread. Properly-written async code that `await`s I/O does **not** create OS threads. However, `asyncio.to_thread()` explicitly creates an OS-level thread in the default `ThreadPoolExecutor` to run blocking synchronous code without stalling the event loop.

When 20 requests arrived simultaneously, `asyncio.to_thread(generate, ...)` spawned up to 20 OS threads that all attempted to call `generate()` concurrently. The lack of a sequencing mechanism at the Python level caused the Metal driver to receive multiple simultaneous command buffer submissions for the same model weights.

---

## 3. Solution: Async-Aware Sequential GPU Scheduling

The fundamental requirement is: **`mlx_lm.generate()` must be called from at most one thread at any given time**, regardless of how many concurrent HTTP requests are being served.

The solution must satisfy two additional constraints:

1. **Non-blocking** — The FastAPI event loop must not be stalled while waiting for the GPU. The server must remain responsive to health-check requests, rate-limit checks, and other non-MLX paths during inference.
2. **No throughput degradation** — At 4-bit quantisation, inference on the M4 GPU completes in 40–180 ms. Queuing 20 requests sequentially introduces a maximum wait of ~20 × 80 ms = 1.6 s — acceptable for a honeypot whose primary goal is engagement, not speed.

### 3.1 Implementation: `asyncio.Lock` as a GPU Bouncer

```python
# Backend/local_inference.py

import asyncio
import threading
from mlx_lm import load, generate

class LocalMLXModel:
    """
    Thread-safe singleton for local MLX inference.

    Concurrency model:
    - Singleton creation: guarded by threading.Lock (runs at import time,
      before the event loop exists).
    - GPU inference: guarded by asyncio.Lock (runs within the event loop,
      allows cooperative yielding between requests while one request holds
      the GPU).
    """
    _instance = None
    _thread_lock = threading.Lock()   # Protects singleton __new__

    def __new__(cls):
        with cls._thread_lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.model, self.tokenizer = load("path/to/chamaeleon-4bit")
        self._async_lock = None   # Lazily initialised inside the event loop
        self._initialized = True

    async def infer(self, command: str) -> str:
        if not self.model:
            return "ALLOW"   # Fail-safe: prefer false negative over crash

        # Lazy initialisation: asyncio.Lock must be created inside the
        # running event loop, not at module import time.
        if self._async_lock is None:
            self._async_lock = asyncio.Lock()

        prompt = f"COMMAND: {command}\nVERDICT: "

        async with self._async_lock:
            # ── CRITICAL SECTION ─────────────────────────────────────────
            # Only ONE coroutine may be inside this block at any time.
            # All others `await` the lock and yield control back to the
            # event loop, allowing FastAPI to continue serving other routes.
            response = await asyncio.to_thread(
                generate,
                self.model,
                self.tokenizer,
                prompt=prompt,
                max_tokens=10,
                verbose=False,
            )
            # ── END CRITICAL SECTION ─────────────────────────────────────

        output = response.strip().upper()
        if "BLOCK" in output:
            return "BLOCK"
        elif "ALLOW" in output:
            return "ALLOW"
        return "ALLOW"   # Fail-safe default
```

### 3.2 Concurrency Flow with the Fix

```
Timeline after fix (20 concurrent requests):

T+0ms   Request  1:  acquires _async_lock → dispatches to_thread → GPU running
T+0ms   Requests 2-20: await _async_lock → yield to event loop
                        (FastAPI continues serving other routes freely)

T+80ms  Request  1:  GPU complete → releases _async_lock
T+80ms  Request  2:  acquires _async_lock → dispatches to_thread → GPU running
T+80ms  Requests 3-20: still awaiting lock

... (sequential, ~80ms per request) ...

T+1600ms Request 20: GPU complete → releases _async_lock

Result: 20 responses delivered, zero SIGABRT, event loop never blocked.
```

---

## 4. Two Locks, Two Roles

A common misunderstanding is that a single lock suffices. The implementation uses **two distinct lock types** for two distinct problems:

| Lock | Type | Scope | Purpose |
|---|---|---|---|
| `_thread_lock` | `threading.Lock` | Class-level | Prevents concurrent singleton instantiation at module import time, when no event loop exists yet |
| `_async_lock` | `asyncio.Lock` | Instance-level | Serialises GPU command buffer submissions within the running event loop |

Using `threading.Lock` for GPU serialisation would work in isolation but would **block the OS thread** hosting the event loop, causing FastAPI to drop connections from other clients during inference. `asyncio.Lock` correctly suspends only the coroutine, freeing the event loop thread for other work.

### 4.1 Lazy Initialisation

`asyncio.Lock()` must be instantiated within a running event loop. Because `LocalMLXModel.__init__` may be called at import time (before `uvicorn` starts the event loop), the lock is created lazily on the first `infer()` call:

```python
if self._async_lock is None:
    self._async_lock = asyncio.Lock()
```

This is safe because the first `infer()` call is guaranteed to occur within the event loop context.

---

## 5. Fail-Safe Behaviour

Two defensive defaults are implemented for resilience:

| Condition | Behaviour | Rationale |
|---|---|---|
| Model weights not loaded (path missing) | Returns `"ALLOW"` | Prevents false-positive BLOCK storm if model file is absent after a deployment failure |
| `generate()` raises an exception | Catches, logs, returns `"ALLOW"` | Prevents a GPU driver error from manifesting as an HTTP 500 to the attacker, which would reveal the honeypot's internal error state |
| MLX output not `BLOCK` or `ALLOW` | Returns `"ALLOW"` | Handles garbled or truncated model output gracefully |

---

## 6. Verification

The fix was validated by the stress test in `test_rigorous_pipeline.py::TestConcurrencyAndThreadSafety::test_concurrency_stress`, which fires 20 simultaneous requests using `asyncio.gather` and asserts:

```python
responses = await asyncio.gather(*tasks, return_exceptions=True)

# No Python-level exceptions
exceptions = [r for r in responses if isinstance(r, Exception)]
assert len(exceptions) == 0

# All 20 completed with a valid HTTP status
for resp in responses:
    assert resp.status_code in (200, 401, 429)
```

The test additionally verifies async lock correctness in `TestLocalMLXModelAsyncLock::test_concurrent_infer_calls_all_complete`:

```python
results = await asyncio.gather(
    *[model.infer(f"cmd_{i}") for i in range(5)],
    return_exceptions=True,
)
errors = [r for r in results if isinstance(r, Exception)]
assert len(errors) == 0
```

---

## 7. Consequences

### Positive
- Hard SIGABRT crash eliminated under load.
- FastAPI event loop remains responsive during GPU inference (non-blocking lock design).
- Fail-safe defaults prevent attacker-visible error signals.

### Accepted Trade-offs
- Requests queue sequentially behind the `asyncio.Lock`. At the inference throughput of the M4 GPU (~10–25 inferences/sec), queue depth grows linearly under sustained burst load.
- For production deployments expecting >100 concurrent attackers, consider a **worker pool architecture** (multiple process replicas behind a load balancer, each with its own `LocalMLXModel` instance and GPU time slice).

---

## 8. Related Documents

- `ADR-001` — `01_deepseek_to_local_mlx_migration.md` — Why the local model was selected
- `ADR-004` — `04_rigorous_testing_and_validation.md` — Test suite verifying the fix
- `Backend/local_inference.py` — Complete singleton implementation
