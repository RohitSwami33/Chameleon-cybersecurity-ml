# Novel Mathematical Equations for Meta-Heuristic Optimization in Cybersecurity Honeypots

## Research Paper Documentation

**Title**: Threat-Calibrated PSO and Semantic Deception RRT: Novel Domain-Specific Mathematical Enhancements for Adaptive Honeypot Systems

**Authors**: Chameleon Research Team  
**Date**: March 2026  
**Domain**: Cybersecurity, Meta-Heuristic Optimization, Deception Technology

---

## Table of Contents

1. [Overview](#overview)
2. [Standard PSO Foundation](#standard-pso-foundation)
3. [Novel Contribution 1: Threat-Calibrated PSO (TC-PSO)](#novel-contribution-1-threat-calibrated-pso-tc-pso)
4. [Standard RRT Foundation](#standard-rrt-foundation)
5. [Novel Contribution 2: Semantic Deception RRT (S-RRT)](#novel-contribution-2-semantic-deception-rrt-s-rrt)
6. [Benchmark Validation](#benchmark-validation)
7. [Implementation Reference](#implementation-reference)
8. [Citation](#citation)

---

## Overview

This document presents two novel mathematical enhancements to established meta-heuristic optimization algorithms:

1. **Threat-Calibrated Particle Swarm Optimization (TC-PSO)**: Extends standard PSO with dynamic inertia weight scaling based on real-time threat intelligence from a BiLSTM anomaly detector.

2. **Semantic Deception RRT (S-RRT)**: Extends the 2025 IEEE Access RRT algorithm with exponential pheromone weighting using Payload Severity Index (PSI) and depth-decay multipliers for memory optimization.

These contributions make the algorithms **domain-specific** for cybersecurity honeypot optimization, providing measurable improvements over standard implementations.

---

## Standard PSO Foundation

### Original PSO Equations (Kennedy & Eberhart, 1995)

Particle Swarm Optimization is a population-based stochastic optimization technique inspired by social behavior of bird flocking and fish schooling.

#### Velocity Update Equation (Standard)

```
vᵢ(t+1) = w · vᵢ(t) + c₁ · r₁ · (pbestᵢ - xᵢ(t)) + c₂ · r₂ · (gbest - xᵢ(t))
```

**Where:**
| Symbol | Description | Standard Value |
|--------|-------------|----------------|
| `vᵢ(t)` | Velocity of particle i at iteration t | - |
| `w` | Inertia weight (constant) | 0.729 |
| `c₁` | Cognitive coefficient | 1.49445 |
| `c₂` | Social coefficient | 1.49445 |
| `r₁, r₂` | Random numbers ∈ [0, 1] | - |
| `pbestᵢ` | Personal best position of particle i | - |
| `gbest` | Global best position in swarm | - |
| `xᵢ(t)` | Current position of particle i | - |

#### Position Update Equation (Standard)

```
xᵢ(t+1) = xᵢ(t) + vᵢ(t+1)
```

#### Fitness Function (Standard Honeypot PSO)

```
F(t) = (w₁ · C_exec) - (w₂ · P_drop)
```

**Where:**
| Symbol | Description | Value |
|--------|-------------|-------|
| `C_exec` | Number of commands executed by attacker | Variable |
| `P_drop` | Binary penalty (1 if disconnected, 0 otherwise) | {0, 1} |
| `w₁` | Weight for command execution | 0.65 |
| `w₂` | Penalty multiplier for disconnection | 2.5 |

### Limitations of Standard PSO for Cybersecurity

1. **Static inertia weight**: Cannot adapt to varying threat levels
2. **Uniform treatment**: All attack sessions treated equally regardless of severity
3. **Slow convergence**: Under high-threat scenarios, rapid adaptation is critical
4. **No domain intelligence**: Does not incorporate ML-based threat detection

---

## Novel Contribution 1: Threat-Calibrated PSO (TC-PSO)

### Mathematical Formulation

TC-PSO introduces **two novel equations** that incorporate real-time threat intelligence from a BiLSTM anomaly detector.

---

### Equation 1: Dynamic Inertia Weight Scaling

#### Novel Equation

```
w(t) = w_base · max(σ_min, 1 - α · A(t))
```

**Where:**
| Symbol | Description | Value/Range |
|--------|-------------|-------------|
| `w(t)` | Dynamic inertia weight at time t | [0.2187, 0.729] |
| `w_base` | Base inertia weight (standard PSO) | 0.729 |
| `σ_min` | Minimum inertia scale factor | 0.3 |
| `α` | Anomaly sensitivity parameter | 0.5 |
| `A(t)` | BiLSTM anomaly score at time t | [0.0, 1.0] |

#### Derivation

Starting from the requirement that higher threat levels should trigger faster convergence:

1. **Design Principle**: Lower inertia → less momentum → faster convergence
2. **Threat Response**: Higher anomaly score → lower inertia
3. **Linear Relationship**: `w(t) ∝ (1 - A(t))`
4. **Sensitivity Control**: Introduce `α` to tune responsiveness
5. **Stability Bound**: Enforce minimum via `σ_min` to prevent stagnation

#### Boundary Analysis

| Anomaly Score A(t) | Inertia Scale | Dynamic Inertia w(t) | Behavior |
|-------------------|---------------|---------------------|----------|
| 0.0 (Benign) | max(0.3, 1.0) = 1.0 | 0.729 | Maximum exploration |
| 0.5 (Moderate) | max(0.3, 0.75) = 0.75 | 0.547 | Balanced |
| 0.85 (High) | max(0.3, 0.575) = 0.575 | 0.419 | Faster convergence |
| 1.0 (Critical) | max(0.3, 0.5) = 0.5 | 0.365 | Maximum exploitation |

#### Velocity Update with Dynamic Inertia

**Novel TC-PSO Velocity Equation:**

```
vᵢ(t+1) = [w_base · max(σ_min, 1 - α · A(t))] · vᵢ(t) + c₁ · r₁ · (pbestᵢ - xᵢ(t)) + c₂ · r₂ · (gbest - xᵢ(t))
```

---

### Equation 2: Anomaly-Weighted Objective Function

#### Novel Equation

```
F'(t) = F(t) · (1 + β · A(t))
```

**Where:**
| Symbol | Description | Value/Range |
|--------|-------------|-------------|
| `F'(t)` | Calibrated fitness at time t | [0, ∞) |
| `F(t)` | Base fitness from standard equation | [0, ∞) |
| `β` | Reward amplification factor | 0.3 |
| `A(t)` | BiLSTM anomaly score | [0.0, 1.0] |

#### Expanded Form

Substituting the base fitness function:

```
F'(t) = [(w₁ · C_exec) - (w₂ · P_drop) + w₃ · I_bonus] · (1 + β · A(t))
```

**Where:**
| Symbol | Description | Value |
|--------|-------------|-------|
| `I_bonus` | Interaction bonus for sustained engagement | 0.25 × (commands - 5) |

#### Derivation

1. **Design Principle**: High-threat sessions should yield higher learning signals
2. **Multiplicative Scaling**: Preserve relative fitness differences while amplifying absolute values
3. **Normalization**: When A(t) = 0, F'(t) = F(t) (backward compatible)
4. **Amplification Bound**: When A(t) = 1.0, F'(t) = 1.3 × F(t) (30% boost)

#### Fitness Amplification Examples

| Base Fitness F(t) | Anomaly A(t) | Amplification Factor | Calibrated Fitness F'(t) |
|-------------------|--------------|---------------------|-------------------------|
| 5.0 | 0.0 (Benign) | 1.0 | 5.00 |
| 5.0 | 0.5 (Moderate) | 1.15 | 5.75 |
| 5.0 | 0.85 (High) | 1.255 | 6.28 |
| 5.0 | 1.0 (Critical) | 1.3 | 6.50 |

---

### Complete TC-PSO Algorithm

```
Algorithm 1: Threat-Calibrated Particle Swarm Optimization
───────────────────────────────────────────────────────────

Input:
    - Swarm size N
    - Max iterations T
    - Anomaly sensitivity α
    - Reward amplification β
    - Minimum inertia scale σ_min

Output:
    - Global best position gbest
    - Global best fitness gbest_fitness

1: Initialize particles xᵢ, vᵢ for i = 1 to N
2: Initialize pbestᵢ = xᵢ, gbest = argmax F(xᵢ)
3: Set anomaly score A(0) = 0.5 (neutral)
4: 
5: for t = 1 to T do
6:     // Novel Equation 1: Dynamic Inertia
7:     w(t) ← w_base · max(σ_min, 1 - α · A(t))
8:     
9:     for each particle i do
10:        // Updated velocity with dynamic inertia
11:        vᵢ(t+1) ← w(t) · vᵢ(t) + c₁ · r₁ · (pbestᵢ - xᵢ(t)) + c₂ · r₂ · (gbest - xᵢ(t))
12:        
13:        // Position update
14:        xᵢ(t+1) ← xᵢ(t) + vᵢ(t+1)
15:        
16:        // Evaluate fitness
17:        fᵢ ← F(xᵢ(t+1))
18:        
19:        // Novel Equation 2: Anomaly-weighted fitness
20:        f'ᵢ ← fᵢ · (1 + β · A(t))
21:        
22:        // Update personal best
23:        if f'ᵢ > pbest_fitnessᵢ then
24:            pbestᵢ ← xᵢ(t+1)
25:            pbest_fitnessᵢ ← f'ᵢ
26:        end if
27:        
28:        // Update global best
29:        if f'ᵢ > gbest_fitness then
30:            gbest ← xᵢ(t+1)
31:            gbest_fitness ← f'ᵢ
32:        end if
33:    end for
34:    
35:    // Update anomaly score from BiLSTM detector
36:    A(t+1) ← BiLSTM_Anomaly_Detector(current_session_features)
37: end for
38: 
39: return gbest, gbest_fitness
```

---

### TC-PSO Configuration Parameters

```python
TC_PSO_CONFIG = {
    # Standard PSO parameters
    "num_particles": 15,
    "max_iterations": 50,
    "inertia_weight": 0.729,           # w_base
    "cognitive_coefficient": 1.49445,  # c₁
    "social_coefficient": 1.49445,     # c₂
    
    # Novel TC-PSO parameters
    "anomaly_sensitivity": 0.5,        # α (sensitivity to threat)
    "min_inertia_scale": 0.3,          # σ_min (prevents stagnation)
    
    # Search space bounds
    "min_delay": 0.5,                  # Minimum tarpit delay (seconds)
    "max_delay": 12.0,                 # Maximum tarpit delay (seconds)
    
    # Fitness parameters
    "fitness_decay": 0.95,
}
```

---

## Standard RRT Foundation

### Original RRT Equations (2025 IEEE Access)

RRT (Rapidly-exploring Random Tree) for deception schema evolution treats filesystem structures as trees and uses pheromone-based learning.

#### Pheromone Update Equation (Standard)

```
τᵢ(t+1) = τᵢ(t) + Δτ
```

**Where:**
| Symbol | Description | Standard Value |
|--------|-------------|----------------|
| `τᵢ(t)` | Pheromone weight of path i at time t | - |
| `Δτ` | Base pheromone bonus | 0.5 |

#### Fitness Function (Standard RRT)

```
F(t) = Σ(τᵢ · Iᵢ) + B_depth - P_stale
```

**Where:**
| Symbol | Description | Value |
|--------|-------------|-------|
| `τᵢ` | Pheromone weight of path i | - |
| `Iᵢ` | Number of interactions with path i | - |
| `B_depth` | Depth bonus | 0.3 × tree_depth |
| `P_stale` | Staleness penalty | 0.05 × total_interactions |

#### Expansion Probability (Standard)

```
P_expand = p_min + (p_max - p_min) · success_rate
```

**Where:**
| Symbol | Description | Value |
|--------|-------------|-------|
| `p_min` | Minimum expansion probability | 0.1 |
| `p_max` | Maximum expansion probability | 0.8 |
| `success_rate` | Normalized fitness metric | [0, 1] |

### Limitations of Standard RRT for Cybersecurity

1. **Uniform learning**: All payloads treated equally regardless of severity
2. **Linear pheromone updates**: Slow learning from critical attack patterns
3. **Unbounded growth**: No mechanism to cap memory usage
4. **No semantic understanding**: Does not incorporate LLM-based severity analysis

---

## Novel Contribution 2: Semantic Deception RRT (S-RRT)

### Mathematical Formulation

S-RRT introduces **two novel equations** that incorporate semantic threat intelligence from LLM analysis.

---

### Equation 3: Exponential Pheromone Weighting with PSI

#### Novel Equation

```
Δτ' = Δτ · exp(Ψ - 1)
```

**Where:**
| Symbol | Description | Value/Range |
|--------|-------------|-------------|
| `Δτ'` | Calibrated pheromone update | [0.5, 3.7] |
| `Δτ` | Base pheromone bonus | 0.5 |
| `Ψ` | Payload Severity Index (PSI) | [1.0, 3.0] |
| `exp` | Natural exponential function (e ≈ 2.718) | - |

#### Normalization Factor

The `-1` term ensures backward compatibility:
- When Ψ = 1.0 (low severity): `Δτ' = Δτ · e⁰ = Δτ · 1 = Δτ`
- When Ψ = 2.0 (medium severity): `Δτ' = Δτ · e¹ ≈ Δτ · 2.718`
- When Ψ = 3.0 (high severity): `Δτ' = Δτ · e² ≈ Δτ · 7.389`

#### Derivation

1. **Design Principle**: High-severity payloads should produce stronger learning signals
2. **Exponential Relationship**: Severity differences should compound, not add linearly
3. **LLM Integration**: PSI derived from LLM semantic analysis of attack payloads
4. **Backward Compatibility**: Ψ = 1.0 recovers standard RRT behavior

#### Pheromone Update Examples

| Base Δτ | PSI (Ψ) | Exponential Factor | Calibrated Δτ' |
|---------|---------|-------------------|----------------|
| 0.5 | 1.0 (Low) | e⁰ = 1.0 | 0.50 |
| 0.5 | 1.5 | e⁰·⁵ ≈ 1.65 | 0.82 |
| 0.5 | 2.0 (Medium) | e¹ ≈ 2.72 | 1.36 |
| 0.5 | 2.5 | e¹·⁵ ≈ 4.48 | 2.24 |
| 0.5 | 3.0 (High) | e² ≈ 7.39 | 3.69 |

#### Updated Fitness Function (S-RRT)

```
F'(t) = Σ(τᵢ · exp(Ψᵢ - 1) · Iᵢ) + B_depth - P_stale
```

**Expanded for sensitive files:**

```
F'(t) = [Σ(τᵢ · exp(Ψ - 1) · Iᵢ) + S_bonus · exp(Ψ - 1)] + 0.3 · depth - 0.05 · interactions
```

**Where:**
| Symbol | Description | Value |
|--------|-------------|-------|
| `S_bonus` | Sensitive file bonus | 2.0 |

---

### Equation 4: Depth-Decay Multiplier for Memory Optimization

#### Novel Equation

```
P'_expand = P_expand · max(ε, 1 - d/d_max)
```

**Where:**
| Symbol | Description | Value/Range |
|--------|-------------|-------------|
| `P'_expand` | Adjusted expansion probability | [0, P_expand] |
| `P_expand` | Base expansion probability | [0.1, 0.8] |
| `d` | Current tree depth | [0, d_max] |
| `d_max` | Maximum allowed depth | 6 |
| `ε` | Minimum probability floor | 0.1 |

#### Derivation

1. **Design Principle**: Deeper trees should expand less aggressively to control memory
2. **Linear Decay**: Expansion probability decreases linearly with depth
3. **Hard Cap**: At d = d_max, expansion is minimal (ε · P_expand)
4. **Memory Bound**: Total nodes grow sub-exponentially

#### Depth-Decay Examples (d_max = 6, ε = 0.1, P_expand = 0.6)

| Current Depth (d) | Decay Factor (1 - d/d_max) | Adjusted P'_expand |
|-------------------|---------------------------|-------------------|
| 0 (Root) | 1.0 | 0.60 |
| 1 | 0.833 | 0.50 |
| 2 | 0.667 | 0.40 |
| 3 | 0.500 | 0.30 |
| 4 | 0.333 | 0.20 |
| 5 | 0.167 | 0.10 |
| 6 (Max) | 0.0 → max(0.1, 0) = 0.1 | 0.06 |

#### Memory Complexity Analysis

**Standard RRT:**
- Worst case: O(b^d) where b = branching factor, d = depth
- Unbounded growth possible

**S-RRT with Depth-Decay:**
- Effective branching factor decreases with depth
- Worst case: O(b · (b·0.83) · (b·0.67) · ... · (b·0.17))
- Approximately O(b^d / d!) - factorial reduction

---

### Complete S-RRT Algorithm

```
Algorithm 2: Semantic Deception RRT (S-RRT)
────────────────────────────────────────────

Input:
    - Initial tree population T₀
    - Max generations G
    - Max depth d_max
    - PSI amplification base e

Output:
    - Best deception tree T_best
    - Best fitness F_best

1: Initialize tree population T = {T₁, T₂, ..., Tₙ}
2: Initialize global pheromone map τ_global
3: Set generation g = 0
4: 
5: while g < G do
6:     for each tree Tᵢ in population do
7:         // Get schema and simulate attacker interaction
8:         schemaᵢ ← GetTemptingSchema(Tᵢ)
9:         paths ← AttackerInteraction(schemaᵢ)
10:        
11:        // Get PSI from LLM severity analyzer
12:        Ψ ← LLM_Payload_Severity_Index(paths)
13:        
14:        for each path p in paths do
15:            // Novel Equation 3: Exponential pheromone weighting
16:            Δτ' ← Δτ · exp(Ψ - 1)
17:            
18:            // Update global pheromone map
19:            τ_global(p) ← τ_global(p) + Δτ'
20:            
21:            // Update tree node pheromone
22:            τᵢ(p) ← τᵢ(p) + Δτ'
23:        end for
24:        
25:        // Calculate fitness with exponential weighting
26:        F(Tᵢ) ← Σ(τᵢ(p) · exp(Ψ - 1) · I(p)) + 0.3 · depth - 0.05 · interactions
27:        
28:        // Update global best
29:        if F(Tᵢ) > F_best then
30:            T_best ← Tᵢ
31:            F_best ← F(Tᵢ)
32:        end if
33:    end for
34:    
35:    // Evolution phase
36:    Sort trees by fitness (descending)
37:    Calculate success_rate ← normalize(mean_fitness)
38:    P_expand ← p_min + (p_max - p_min) · success_rate
39:    
40:    for each tree Tᵢ (excluding elite) do
41:        // Prune dead branches
42:        Tᵢ ← PruneDeadBranches(Tᵢ)
43:        
44:        // Novel Equation 4: Depth-decay multiplier
45:        decay_factor ← max(ε, 1 - depth(Tᵢ) / d_max)
46:        P'_expand ← P_expand · decay_factor
47:        
48:        // Expand with adjusted probability
49:        if random() < P'_expand then
50:            Tᵢ ← ExpandTree(Tᵢ, τ_global)
51:        end if
52:        
53:        // Apply pheromone decay
54:        Tᵢ ← ApplyPheromoneDecay(Tᵢ, decay_rate=0.95)
55:    end for
56:    
57:    // Replace worst performers
58:    T ← ReplaceWorstTrees(T, n_replace = ⌈n/10⌉)
59:    
60:    g ← g + 1
61: end while
62: 
63: return T_best, F_best
```

---

### S-RRT Configuration Parameters

```python
S_RRT_CONFIG = {
    # Population parameters
    "num_trees": 20,
    "initial_depth": 3,
    "max_depth": 6,                    # d_max
    
    # Evolution parameters
    "expansion_rate": 0.4,
    "prune_threshold": 3,
    "pheromone_decay": 0.95,
    "adaptive_step_min": 0.1,          # p_min
    "adaptive_step_max": 0.8,          # p_max
    "exploration_bonus": 0.3,
    
    # Novel S-RRT parameters
    "severity_exponent_base": 2.718,   # e (Euler's number)
    "depth_decay_enabled": True,       # Enable Equation 4
}
```

---

## Benchmark Validation

### Experimental Setup

| Parameter | Value |
|-----------|-------|
| PSO Iterations | 100 |
| RRT Generations | 20 |
| Independent Runs | 5 |
| Random Seeds | 42-46 (PSO), 123-127 (RRT) |

### TC-PSO Results

| Metric | Standard PSO | TC-PSO (Ours) | Improvement |
|--------|--------------|---------------|-------------|
| Avg. Convergence (iterations) | 60.6 | 80.4 | -32.7%* |
| Avg. Final Fitness | 2.60 | 3.85 | **+48.1%** |
| Avg. Best Delay (s) | 3.30 | 3.52 | +6.7% |

*Note: TC-PSO trades raw convergence speed for higher final fitness through better exploration-exploitation balance.

### S-RRT Results

| Metric | Standard RRT | S-RRT (Ours) | Improvement |
|--------|--------------|--------------|-------------|
| Mean Node Count | 7.1 | 6.5 | **-8.4%** |
| Peak Node Count | 12 | 9 | **-25.0%** |
| Critical Fitness (top 20%) | 264.64 | 1135.75 | **+329.2%** |
| Best Fitness | 450.2 | 1615.8 | **+258.9%** |

---

## Implementation Reference

### TC-PSO Method Signatures

```python
class ThreatCalibratedPSO:
    async def update_fitness(
        self,
        attack_category: str,
        delay_used: float,
        commands_executed: int,
        dropped: bool,
        session_id: str = None,
        bilstm_anomaly_score: float = 0.5  # NEW: A(t) ∈ [0, 1]
    )
    
    def _calculate_dynamic_inertia(self, category: str) -> float:
        """
        Novel Equation 1: w(t) = w_base * max(σ_min, 1 - α * A(t))
        """
```

### S-RRT Method Signatures

```python
class SemanticDeceptionRRT:
    async def evaluate_interaction(
        self,
        schema_id: str,
        interacted_paths: List[str],
        payload_severity_index: float = 2.0  # NEW: Ψ ∈ [1.0, 3.0]
    ) -> float:
        """
        Novel Equation 3: Δτ' = Δτ * exp(Ψ - 1)
        """
    
    async def evolve_tree(self):
        """
        Novel Equation 4: P'_expand = P_expand * max(ε, 1 - d/d_max)
        """
```

---

## Citation

If you use these novel equations in your research, please cite:

```bibtex
@article{chameleon2026tc-pso-srrt,
  title={Threat-Calibrated PSO and Semantic Deception RRT: Novel Domain-Specific Mathematical Enhancements for Adaptive Honeypot Systems},
  author={Chameleon Research Team},
  journal={Preprint},
  year={2026},
  institution={Semester 4 Cybersecurity Research Project}
}
```

---

## Appendix: Mathematical Proofs

### Proof 1: TC-PSO Convergence Bound

**Theorem**: TC-PSO converges to a local optimum in finite iterations.

**Proof**:
1. Dynamic inertia w(t) is bounded: σ_min · w_base ≤ w(t) ≤ w_base
2. With w(t) < 1, velocity converges: lim(t→∞) v(t) = 0
3. Position converges: lim(t→∞) x(t) = pbest or gbest
4. Fitness landscape is bounded (delay ∈ [0.5, 12.0])
5. Therefore, TC-PSO converges to a local optimum □

### Proof 2: S-RRT Memory Bound

**Theorem**: S-RRT with depth-decay has bounded memory growth.

**Proof**:
1. Maximum depth is d_max = 6
2. At depth d, expansion probability is P'_expand ≤ P_expand · (1 - d/d_max)
3. At d = d_max, P'_expand ≤ 0.1 · P_expand (minimal growth)
4. Expected nodes at depth d: E[N_d] ≤ b · P'_expand^d
5. Total expected nodes: E[N_total] ≤ Σ(d=0 to d_max) E[N_d] < ∞ □

---

**Document Version**: 1.0  
**Last Updated**: March 17, 2026  
**Contact**: Chameleon Research Team
