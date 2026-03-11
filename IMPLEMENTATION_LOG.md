# Chameleon — Deception Hardening Implementation Log

## Session: 2026-03-11

---

## Pre-Implementation Reconnaissance
- ✅ Read: `attacker_session.py` — mapped `_session_store`, `generate_attacker_fingerprint()`, `initialize_session()`
- ✅ Read: `llm_controller.py` — mapped `LLMController`, `_sessions`, `generate_deceptive_response()`
- ✅ Read: `main.py` — mapped `trap_execute()`, deception pipeline, all endpoints
- ✅ Read: `pipeline.py` — mapped `evaluate_payload()`, two-stage MLX flow
- ✅ Read: `ml_classifier.py` — mapped `MLClassifier`, `heuristic_fallback()`
- ✅ Read: `deception_engine_v2.py` — mapped `ProgressiveDeceptionEngine`, stage progression
- ✅ Read: `config.py` — mapped `Settings`, database URLs, API keys
- ✅ Read: `database_postgres.py` — mapped async engine, session factory, `get_db()`
- ✅ Read: `models_sqlalchemy.py` — mapped `Base`, `HoneypotLog`, `BeaconEvent`, `ReputationScore`
- ✅ Read: `meta_heuristics.py` — mapped PSO + RRT optimizers

---

## Phase 1 — Algorithm A: HMAC-Seeded Deterministic Session Ledger

### Step A1 — Created `session_authority.py` (NEW)
- **What:** `SingleSourceSessionAuthority` class with PostgreSQL backend
- **Why:** Centralised session store replacing in-memory `_session_store` dict
- **Functions added:**
  - `compute_deterministic_fields(fingerprint)` — HMAC-SHA256 → db_type/table_name/column
  - `sign_state(session_data)` — HMAC signature for audit log
  - `SingleSourceSessionAuthority.get_or_create()` — PG upsert + fallback cache
  - `SingleSourceSessionAuthority.advance_stage()` — locked stage transitions
  - `SingleSourceSessionAuthority.update_session()` — generic field updates
- **DB tables created:** `session_ledger`, `session_audit_log`
- **Backward compatible:** ✅ Falls back to in-memory dict if PG unavailable

### Step A2 — Modified `attacker_session.py`
- **Change 1:** `generate_attacker_fingerprint()` → now uses `hmac.new(SESSION_SECRET, ...)` instead of plain SHA-256
- **Change 2:** `initialize_session()` → DB type selected deterministically via `compute_deterministic_fields()` instead of `random.choice()`
- **Change 3:** `_session_store` → synced with `SingleSourceSessionAuthority` via `_sync_from_authority()`
- **Change 4:** `get_or_create_session()` → calls `_sync_from_authority()` before local lookup
- **Change 5:** `update_session()` → syncs updates to SessionAuthority
- **Change 6:** `advance_session_stage()` → syncs stage advance to SessionAuthority

### Step A3 — Modified `llm_controller.py`
- **Change 1:** `__init__()` → imports SessionAuthority + ResponseValidator at init
- **Change 2:** `get_or_create_session()` → fetches db_type/table_name from SessionAuthority, attaches to CommandHistory metadata
- **Change 3:** `generate_deceptive_response()` → validates LLM output via ResponseValidator before returning

### Step A4 — Modified `main.py`
- **Change 1:** `session_id` in deception layer → now derived from `fingerprint[:8]` instead of `uuid.uuid4()[:8]`

### Step A5 — Modified `config.py`
- **Change 1:** Added `SESSION_SECRET` config variable with env fallback

---

## Phase 2 — Algorithm B: Multi-Layer Normalisation + VAC Behaviour Classifier

### Step B1 — Created `normalisation_pipeline.py` (NEW)
- **What:** `NormalisationPipeline` with 7 passes
- **Passes:** URL decode (iterative), HTML entity decode, Unicode NFKC, null byte strip, SQL comment removal, keyword reconstruction, whitespace normalise
- **Singleton:** `normalisation_pipeline`
- **Tests needed:** Double-encoded payloads, fullwidth Unicode, S/**/ELECT

### Step B2 — Created `behaviour_classifier.py` (NEW)
- **What:** `BehaviourClassifier` classifying traffic as HUMAN/FUZZER/SCANNER
- **Signals:** RPM, Shannon entropy, think-time variance, unique payload ratio
- **Routing:** SCANNER → stage-1 loop, FUZZER → junk response, HUMAN → full pipeline
- **Singleton:** `behaviour_classifier`

### Step B3 — Modified `pipeline.py`
- **Change 1:** Added Stage 0 (Normalisation) before heuristic classification
- **Change 2:** Added Stage 0.5 (Behaviour Classification) → short-circuits SCANNER/FUZZER
- **Change 3:** `evaluate_payload()` signature → added `ip_address` parameter
- **Change 4:** Module-level payload tracking (`_last_raw_payload`, `_last_normalised_payload`)
- **Change 5:** Heuristic classifier and MLX now receive normalised payload

### Step B4 — Modified `main.py`
- **Change 1:** `evaluate_payload(command)` → `evaluate_payload(command, ip_address=ip_address)` in `trap_execute()`

---

## Phase 3 — Algorithm C: Deep Attacker Binding + EAC Canary System

### Step C1 — Created `fingerprint_chain.py` (NEW)
- **What:** `FingerprintChain` with 8-signal weighted cosine similarity
- **Signals:** UA, Accept-Language, Accept-Encoding, JA3, cookies, quote preference, payload length, spacing
- **Match threshold:** 0.65 cosine similarity
- **Singleton:** `fingerprint_chain`

### Step C2 — Created `canary_system.py` (NEW)
- **What:** `CanaryTrapSystem` embedding unique trackable tokens in responses
- **Canary types:** api_key, jwt, sql_dump, file_path, generic
- **Detection:** `check_incoming()` scans all request data for planted canary IDs
- **Persistence:** PostgreSQL `canary_registry` table (best-effort)
- **Singleton:** `canary_system`

### Step C3 — Modified `main.py`  
- **Change 1:** `_FINGERPRINT_CHAIN_AVAILABLE` guard import at module level
- **Change 2:** `_CANARY_SYSTEM_AVAILABLE` guard import at module level
- **Change 3:** Deception layer checks for canary in incoming requests, re-binds session if found
- **Change 4:** `trap_execute()` runs fingerprint chain matching before ML pipeline
- **Change 5:** `trap_execute()` plants canary in high-confidence attack responses

---

## Phase 4 — Algorithm D: Adaptive Timing Mask + Deterministic Response Mutation

### Step D1 — Created `timing_mask.py` (NEW)
- **What:** `AdaptiveTimingMask` normalising all response times to Normal(0.4, 0.15)
- **Why:** Prevents timing side-channel between cache hits and LLM calls
- **Integration:** Replaces raw `asyncio.sleep(optimal_delay)` in `main.py` deception layer
- **Singleton:** `timing_mask`

### Step D2 — Created `response_mutator.py` (NEW)
- **What:** `ResponseMutationEngine` applying deterministic micro-mutations
- **Mutation types:** Whitespace, punctuation, timestamps (±30s), error codes (±1), word order shuffle
- **Determinism:** Seeded from `hash(session_id:request_count)` for reproducibility
- **Singleton:** `response_mutator`

### Step D3 — Modified `main.py`
- **Change 1:** Deception layer: `asyncio.sleep(optimal_delay)` → `timing_mask.serve_with_mask()` with PSO delay
- **Change 2:** `trap_execute()`: Response mutation applied before serving via `response_mutator.mutate()`

---

## Phase 5 — Algorithm E: Response Validator + Opaque State VM

### Step E1 — Created `response_validator.py` (NEW)
- **What:** `ResponseValidator` validating LLM output for safety
- **Checks:** Forbidden patterns (LLM names, "honeypot", "fake"), real path leaks, DB type consistency
- **Fallbacks:** Pre-warmed templates by DB type and stage
- **Sanitiser:** Strips internal fields (schema_id, execution_time_ms, is_safe, prediction_score)
- **Singleton:** `response_validator`

### Step E2 — Created `opaque_state.py` (NEW)
- **What:** `OpaqueStateVM` encoding stage numbers into opaque tokens
- **Algorithm:** `(stage XOR reg0) * reg1 % reg2` with HMAC-derived registers
- **Decoding:** Modular multiplicative inverse
- **Singleton:** `opaque_vm`

### Step E3 — Modified `deception_engine_v2.py`
- **Change 1:** `flavor_texts` → DB-type-aware dict instead of flat list
- **Change 2:** `add_flavor_text()` → deterministic indexing via `hash(fingerprint) % len(texts)`

### Step E4 — Modified `llm_controller.py`
- **Change 1:** `generate_deceptive_response()` → validates response via ResponseValidator at end of pipeline

### Step E5 — Modified `main.py`
- **Change 1:** Generic deception responses sanitised via `response_validator.sanitise_dict()`
- **Change 2:** `trap_execute()` → ResponseValidator validates LLM responses
- **Change 3:** `trap_execute()` → Final sanitise pass before returning response text

---

## Files Created (8)
| File | Algorithm | Purpose |
|------|-----------|---------|
| `session_authority.py` | A | PostgreSQL-backed HMAC session ledger |
| `normalisation_pipeline.py` | B | 7-pass input canonicalisation |
| `behaviour_classifier.py` | B | HUMAN/FUZZER/SCANNER classification |
| `fingerprint_chain.py` | C | Multi-signal attacker binding |
| `canary_system.py` | C | Trackable token (canary) system |
| `timing_mask.py` | D | Response timing normalisation |
| `response_mutator.py` | D | Deterministic response mutation |
| `response_validator.py` | E | LLM output safety gate |
| `opaque_state.py` | E | Stage number obfuscation VM |

## Files Modified (6)
| File | Algorithms | Changes |
|------|-----------|---------|
| `attacker_session.py` | A | HMAC fingerprint, deterministic DB type, SessionAuthority sync |
| `llm_controller.py` | A, E | SessionAuthority integration, response validation |
| `main.py` | A, B, C, D, E | All algorithms integrated into trap_execute + deception layer |
| `pipeline.py` | B | Normalisation + behaviour classification stages |
| `deception_engine_v2.py` | E | DB-type-aware flavors, deterministic indexing |
| `config.py` | A | SESSION_SECRET config variable |

## Backward Compatibility
- ✅ All new imports wrapped in `try/except` → original behaviour is fallback  
- ✅ No existing function signatures changed in incompatible ways  
- ✅ PostgreSQL features fail gracefully to in-memory stores  
- ✅ Original `_session_store` dict retained as local cache  
- ✅ `evaluate_payload()` new `ip_address` param has default value `"unknown"`
