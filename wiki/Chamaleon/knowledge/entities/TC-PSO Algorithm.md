---
created: 2026-04-10
updated: 2026-04-10
tags: [entity, algorithm, optimization, TC-PSO, tarpit]
sources: 0
status: active
---

# TC-PSO Algorithm

## Summary
**Threat-Calibrated Particle Swarm Optimization** - A novel meta-heuristic algorithm that dynamically tunes tarpit delay per attack category to maximize attacker dwell time without triggering timeouts.

## Location
`Backend/src/optimization/meta_heuristics.py`

## Purpose
Traditional PSO uses fixed parameters. TC-PSO introduces **threat-awareness** by calibrating PSO parameters based on the BiLSTM anomaly score, making the optimization adaptive to attack severity.

## Mathematical Foundation

### Equation 1: Dynamic Inertia Weight
```
w(t) = w_base * max(σ_min, 1 - α * A(t))
```

**Variables:**
- `w(t)` - Inertia weight at iteration t
- `w_base` - Base inertia value
- `σ_min` - Minimum inertia threshold
- `α` - Scaling coefficient
- `A(t)` - BiLSTM anomaly score [0.0, 1.0]

**Behavior:**
- **High anomaly** (A(t) → 1.0) → Lower inertia → Faster convergence (aggressive optimization)
- **Low anomaly** (A(t) → 0.0) → Higher inertia → More exploration (conservative optimization)

### Equation 2: Anomaly-Weighted Fitness
```
F'(t) = F(t) * (1 + β * A(t))
```

**Variables:**
- `F'(t)` - Adjusted fitness score
- `F(t)` - Base fitness = (w₁ * commands_executed) - (w₂ * drop_penalty)
- `β` - Anomaly weighting factor
- `A(t)` - BiLSTM anomaly score

**Behavior:**
- High-threat sessions receive proportionally higher rewards
- Prioritizes keeping dangerous attackers engaged longer

## Application: Tarpit Delay Optimization
- **Range:** 0.5s to 12.0s delay
- **Per attack category:** SQLi, XSS, RCE, etc. each get optimized delays
- **Goal:** Maximize dwell time without triggering attacker suspicion/timeouts

## Performance Benchmark
| Metric | Standard PSO | TC-PSO | Improvement |
|--------|-------------|--------|-------------|
| Avg Fitness (5 runs) | 2.60 | 3.85 | **+48.1%** |

## Validation
- 24 dedicated unit tests in `Backend/tests/test_tc_pso_equations.py`
- Mathematical proofs in `Backend/tests/test_mathematical_proofs.py`
- Comparison tests in `Backend/tests/test_comparison_algorithms.py`

## Visualization
- `pso_convergence_graph.png` - PSO convergence visualization
- `Backend/docs/tc_pso_vs_standard.png` - TC-PSO vs standard PSO comparison
- Frontend: `TCPSOTarpitMonitor.jsx` - Real-time monitoring dashboard

## Integration Point
Called after classification in the pipeline:
```python
optimal_delay = tc_pso.calculate_delay(attack_category, anomaly_score)
asyncio.sleep(optimal_delay)  # Slows down attacker
```

## Research Contribution
This is one of **two novel algorithms** introduced by the Chameleon project, representing a significant advancement in adaptive honeypot systems by linking threat severity to optimization parameters.

## See Also
- [[knowledge/entities/S-RRT Algorithm|S-RRT Algorithm]]
- [[knowledge/entities/Two-Stage Evaluation Pipeline|Two-Stage Evaluation Pipeline]]
- [[knowledge/concepts/Tarpit Strategy|Tarpit Strategy]]
- [[knowledge/entities/BiLSTM Model|BiLSTM Model]]
