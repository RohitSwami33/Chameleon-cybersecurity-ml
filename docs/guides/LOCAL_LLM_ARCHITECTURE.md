# Chameleon: Local LLM Architecture (MLX)

## 1. Executive Summary

The Chameleon honeypot system has undergone a pivotal architectural upgrade, transitioning from a cloud-reliant Large Language Model (LLM) API (DeepSeek) to a fully localized, low-latency inference engine. This upgrade utilizes Apple's MLX framework to deploy a locally trained, 4-bit quantized Qwen 3.5 2B model. This custom-tuned model serves as the core analytical engine for Chameleon, accurately classifying incoming payloads as `BLOCK` (malicious) or `ALLOW` (benign). By moving inference to the edge, the system achieves unprecedented security, privacy, and performance metrics critical for modern deception environments.

## 2. Why Local Inference is Superior for Chameleon

The transition to a localized MLX architecture introduces several mission-critical advantages tailored specifically to honeypot operations:

### Absolute Privacy (Air-Gapped Security)
Honeypots operate on the bleeding edge of threat intelligence, capturing highly sensitive data, including potentially unpatched zero-day exploits, proprietary attacker payloads, and internal network telemetry. Transmitting this raw, untrusted data to a third-party commercial API (such as DeepSeek or OpenAI) introduces a severe risk of data leakage, telemetry poisoning, and direct violation of strict Operations Security (OPSEC) protocols. Our localized Qwen 3.5 2B model guarantees 100% data sovereignty, ensuring that all payload analysis remains isolated and air-gapped within our controlled infrastructure.

### Bypassing Cloud Censorship and Safety Filters
Commercial LLM APIs inherently employ strict safety alignment filters engineered to reject malicious instructions or toxic inputs. When analyzing raw cyberattacks, these generic safety mechanisms actively hinder threat detection by refusing to process or evaluate malicious payloads. Our fine-tuned, localized model is explicitly trained without these restrictive safety guardrails, ensuring it accurately dissects and flags sophisticated attacks without being artificially censored.

### Zero Latency & Cost
Synchronous network round-trips to cloud-based inference servers introduce unacceptable overhead to the honeypot's deception loop. By migrating to local MLX inference leveraging Apple Silicon's unified memory architecture, network latency is entirely eliminated. Furthermore, this approach eradicates variable API token costs, enabling infinitely scalable, sustained threat analysis without financial constraints.

## 3. The Training & Quantization Pipeline

To ensure complete reproducibility of the Chameleon inference engine, the exact sequence of MLX operations used to synthesize the production model is documented below. The pipeline encompasses LoRA fine-tuning, adapter fusion, and weight quantization.

**I. Fine-Tuning (LoRA)**
We employed Low-Rank Adaptation (LoRA) to efficiently fine-tune the base Qwen 3.5 2B model on our highly curated dataset, minimizing memory overhead while maximizing domain-specific accuracy.
```bash
python -m mlx_lm.lora --model Qwen/Qwen3.5-2B --train --data ./data --iters 1500 --batch-size 2 --learning-rate 2e-5 --lora-layers 16 --rank 32
```

**II. Fusing the Adapter**
Post-training, the LoRA adapters were permanently fused into the base model weights, eliminating inference-time adapter calculation overhead.
```bash
python -m mlx_lm.fuse --model Qwen/Qwen3.5-2B --adapter-path ./adapters --save-path ./chamaeleon-fused
```

**III. 4-bit Quantization**
To optimize memory bandwidth and severely reduce the overall memory footprint for sustained execution alongside the backend services, the fused model was aggressively quantized to 4-bit precision.
```bash
python -m mlx_lm.convert --hf-path ./chamaeleon-fused --q-bits 4 --mlx-path ./chamaeleon-4bit
```

## 4. Application Integration Details

The integration of the MLX model into the FastAPI asynchronous event loop required precision engineering to guarantee thread safety and high concurrency without bottlenecks.

### Singleton "Hot" Memory State (`local_inference.py`)
Model instantiation consumes significant computational IO and memory bandwidth. To prevent memory allocation overhead on subsequent classifications, the MLX tokenizer and quantized weights are loaded exactly once into a thread-safe Singleton class (`LocalMLXModel`). This architectural design guarantees the model remains continuously "hot" in unified memory throughout the application's lifecycle, delivering millisecond inference.

### Strict Prompt Formatting
The fine-tuned model was explicitly aligned to a deterministic input-output scheme. The inference function strictly enforces the following rigid prompt template:
```text
COMMAND: {input}
VERDICT: 
```
By constraining the prompt format and aggressively limiting generation overhead (`max_tokens=10` parameter during inference), we guarantee the generation loop immediately halts regression after emitting the binary `BLOCK` or `ALLOW` classification token.

### Asynchronous Concurrency (`main.py`)
Native LLM generation relies on intensive matrix multiplication routines that inherently block the global interpreter locking mechanism and synchronous event loops. To prevent the MLX inference cycle from starving the FastAPI event loop and halting concurrent honeypot network traffic, the generation pipeline is meticulously offloaded using `asyncio.to_thread`:

```python
verdict = await asyncio.to_thread(mlx_model.infer, command)
```

This ensures that all heavy analytical logic sequences are continuously isolated to parallel, non-blocking worker threads, maintaining absolute responsiveness across all distributed honeypot endpoints.
