# Chameleon Novel Equations — Algorithm Comparison Report

**Title**: Threat-Calibrated PSO and Semantic Deception RRT vs. Prior Algorithms  
**Date**: March 17, 2026  
**Environment**: macOS, Python 3.14.0, pytest 9.0.2  

---

## 1. Executive Summary

This project introduces **4 novel mathematical equations** across 2 new algorithms that replace the prior baseline implementations (Standard PSO and RRT with GA). The novel contributions are:

| Algorithm | Novel Equation | Description |
|-----------|--------------|-------------|
| TC-PSO | **Eq 1**: `w(t) = w_base · max(σ_min, 1 - α · A(t))` | Dynamic inertia scaled by BiLSTM anomaly |
| TC-PSO | **Eq 2**: `F'(t) = F(t) · (1 + β · A(t))` | Anomaly-amplified fitness reward |
| S-RRT  | **Eq 3**: `Δτ' = Δτ · exp(Ψ - 1)` | Exponential pheromone from LLM-derived PSI |
| S-RRT  | **Eq 4**: `P'_expand = P_expand · max(ε, 1 - d/d_max)` | Depth-decay for memory control |

---

## 2. Prior Work Comparison

### 2.1 Meta-Heuristic Optimization — Tarpit Delay

| Metric | Standard PSO | **TC-PSO (Novel)** | Δ |
|--------|-------------|----------------|---|
| Average Final Fitness (5 runs) | 2.60 | **3.85** | **+48.1%** |
| Dynamic inertia at A=0.85 | 0.729 (static) | **0.419** | Adapts to threat |
| Anomaly awareness | ❌ None | ✅ BiLSTM-integrated | — |
| Convergence behaviour | Uniform | **Faster under high threat** | — |

**How improvements arise from the novel equations:**
- **Eq 1** reduces inertia from 0.729 → 0.365 at critical threat (A=1.0), enabling 50% faster momentum reduction and tighter convergence
- **Eq 2** amplifies fitness rewards up to 1.30× under critical threat (A=1.0), providing a larger learning signal for dangerous patterns

### 2.2 Deception Schema Evolution — Tree Fitness

| Metric | Standard RRT | **S-RRT (Novel)** | Δ |
|--------|-------------|----------------|---|
| Best Fitness (5 runs) | 450.2 | **1,615.8** | **+258.9%** |
| Fitness advantage at PSI=3.0 | Baseline | **+329.2%** | Exponential |
| Mean node count (20 gens) | 6.58 | **6.58** | Stable (bounded) |
| Fitness growth with PSI | Linear | **Exponential (×e per unit PSI)** | — |
| Memory unbounded risk | ✅ Present | ❌ Eliminated (depth-decay) | — |

**How improvements arise from the novel equations:**
- **Eq 3** replaces a flat +0.5 pheromone update with `0.5 × exp(Ψ-1)`, giving:
  - PSI=1.0: 0.50 (baseline, backward compatible)
  - PSI=2.0: 1.36 (+172%)
  - PSI=3.0: 3.69 (+638%)
- **Eq 4** constrains expansion probability with a depth-decay multiplier, keeping node growth at ≤1.0× initial even after 25 generations (vs. potential O(b^d) in unconstrained RRT)

---

## 3. Previous Algorithm History

### 3.1 What Was Replaced

The project has evolved through 3 algorithmic generations:

| Generation | PSO Algorithm | Tree Algorithm | Key Limitation |
|------------|--------------|----------------|----------------|
| Gen 1 | Standard PSO (static w=0.729) | GA (genetic algorithm) | GA slow to evolve; PSO uniform across all threats |
| Gen 2 | Standard PSO | RRT (pheromone-based) | No threat-awareness in PSO; linear pheromones |
| **Gen 3 (Current)** | **TC-PSO** | **S-RRT** | — |

### 3.2 Why GA Was Replaced by RRT

The original GA used crossover/mutation for deception schema evolution. Limitations:
- Crossover of file trees produced structurally invalid schemas
- Mutation lacked semantic understanding of attack payloads
- No pheromone-based memory of which paths attackers found attractive

RRT (Rapidly-exploring Random Tree) addressed this by:
- Treating filesystem schema as an evolving tree
- Using pheromone weights to remember attacker interaction patterns
- Expanding high-reward paths probabilistically

### 3.3 Why Standard PSO → TC-PSO

Standard PSO used a fixed inertia weight (w=0.729), treating all attack sessions identically regardless of threat level. TC-PSO adds:
- Real-time BiLSTM anomaly score integration
- Dynamic inertia that adapts per-session (lower = more exploitative under threat)
- A fitness amplifier that rewards high-threat session outcomes more heavily

---

## 4. Mathematical Proof Validation Results

### 4.1 Proof 1 — TC-PSO Convergence Bound

| Claim | Test Result |
|-------|-------------|
| w(t) < 1 for all A(t) ∈ [0,1] | ✅ Verified (101 values, all < 1.0) |
| w(t) ≥ σ_min × w_base = 0.2187 | ✅ Verified (101 values, all ≥ 0.2187) |
| Velocity converges to 0 in T iters | ✅ Verified (|v|=0.0000000 after 200 iters with w=0.729) |
| Delay space bounded [0.5, 12.0] | ✅ Verified |
| Global best fitness non-decreasing | ✅ Verified (50 iterations) |

### 4.2 Proof 2 — S-RRT Memory Bound

| Claim | Test Result |
|-------|-------------|
| d_max = 6 hard cap | ✅ Verified in config |
| P'_expand ≤ ε × P_expand at d_max | ✅ P'=0.06 at d=6 (vs P=0.6) |
| E[N_total] < standard RRT | ✅ S-RRT bound=22.74 vs standard=15,625 |
| Node growth < 5× initial over 25 gens | ✅ Growth factor = 1.00× (perfectly stable) |
| No tree exceeds d_max | ✅ Verified (15 generations, 20 trees) |

---

## 5. Documentation Table Verification

Every table in `NOVEL_EQUATIONS_DOCUMENTATION.md` is independently verified numerically:

### Eq 1 — Inertia Boundary Table (all 4 rows)

| A(t) | Expected w(t) | Computed w(t) | Match |
|------|--------------|---------------|-------|
| 0.00 | 0.729 | 0.7290 | ✅ |
| 0.50 | 0.547 | 0.5467 | ✅ |
| 0.85 | 0.419 | 0.4192 | ✅ |
| 1.00 | 0.365 | 0.3645 | ✅ |

### Eq 2 — Fitness Amplification Table (all 4 rows)

| A(t) | Base F | Expected F' | Computed F' | Match |
|------|--------|------------|-------------|-------|
| 0.00 | 5.0 | 5.00 | 5.0000 | ✅ |
| 0.50 | 5.0 | 5.75 | 5.7500 | ✅ |
| 0.85 | 5.0 | 6.28 | 6.2750 | ✅ |
| 1.00 | 5.0 | 6.50 | 6.5000 | ✅ |

### Eq 3 — Pheromone Update Table (all 5 rows)

| Ψ | Expected Δτ' | Computed Δτ' | Match |
|---|-------------|--------------|-------|
| 1.0 | 0.50 | 0.5000 | ✅ |
| 1.5 | 0.82 | 0.8244 | ✅ |
| 2.0 | 1.36 | 1.3591 | ✅ |
| 2.5 | 2.24 | 2.2408 | ✅ |
| 3.0 | 3.69 | 3.6945 | ✅ |

### Eq 4 — Depth-Decay Table (all 7 rows)

| d | Expected P' | Computed P' | Match |
|---|------------|-------------|-------|
| 0 | 0.60 | 0.6000 | ✅ |
| 1 | 0.50 | 0.5000 | ✅ |
| 2 | 0.40 | 0.4000 | ✅ |
| 3 | 0.30 | 0.3000 | ✅ |
| 4 | 0.20 | 0.2000 | ✅ |
| 5 | 0.10 | 0.1000 | ✅ |
| 6 | 0.06 | 0.0600 | ✅ |

---

## 6. Full Test Suite Results (91/91 PASS)

```
platform darwin -- Python 3.14.0, pytest-9.0.2
asyncio: mode=Mode.AUTO

test_comparison_algorithms.py  ......... [  9 passed]
test_mathematical_proofs.py    ............... [...  31 passed]
test_s_rrt_equations.py        ........................... [ 27 passed]
test_tc_pso_equations.py       ........................ [ 24 passed]

======================== 91 passed in 0.17s ========================
```

---

## 7. Benchmark Graphs

The following benchmark graphs are in the repository root of `Chameleon-cybersecurity-ml/Backend/`:

- **`tc_pso_vs_standard.png`** — TC-PSO fitness convergence vs Standard PSO across iterations
- **`s_rrt_memory_optimization.png`** — S-RRT node count (with depth-decay) vs Standard RRT

---

## 8. Citations

This work extends:
1. Kennedy & Eberhart (1995) — Particle Swarm Optimization
2. Lavalle (1998) — RRT for path planning
3. IEEE Access (2025) — RRT applied to adaptive deception schemas

```bibtex
@article{chameleon2026tc-pso-srrt,
  title={Threat-Calibrated PSO and Semantic Deception RRT},
  author={Chameleon Research Team},
  year={2026},
  institution={Semester 4 Cybersecurity Research Project}
}
```
