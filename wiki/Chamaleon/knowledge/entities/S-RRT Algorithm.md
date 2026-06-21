---
created: 2026-04-10
updated: 2026-04-10
tags: [entity, algorithm, optimization, S-RRT, deception]
sources: 0
status: active
---

# S-RRT Algorithm

## Summary
**Semantic Deception Rapid-exploring Random Tree** - A novel tree-based evolutionary algorithm that evolves deception filesystem schemas (fake file trees with tempting content) to maximize attacker engagement.

## Location
`Backend/src/optimization/meta_heuristics.py`

## Purpose
Traditional RRT explores space randomly. S-RRT introduces **semantic awareness** by weighting tree expansion based on payload severity and controlling memory growth through depth-decay mechanisms.

## Mathematical Foundation

### Equation 3: Exponential Pheromone Weighting
```
Δτ' = Δτ * exp(Ψ - 1)
```

**Variables:**
- `Δτ'` - Adjusted pheromone update
- `Δτ` - Base pheromone increment
- `Ψ` (PSI) - Payload Severity Index from LLM analysis
- `exp()` - Exponential function

**Behavior:**
- High severity (Ψ > 1) → Exponential amplification of pheromone learning
- Low severity (Ψ < 1) → Reduced pheromone influence
- Creates stronger attraction to high-value deception paths

### Equation 4: Depth-Decay Expansion Multiplier
```
P'_expand = P_expand * max(ε, 1 - d/d_max)
```

**Variables:**
- `P'_expand` - Adjusted expansion probability
- `P_expand` - Base expansion probability
- `ε` - Minimum probability threshold
- `d` - Current tree depth
- `d_max` - Maximum tree depth

**Behavior:**
- Shallow nodes (d → 0) → Full expansion probability
- Deep nodes (d → d_max) → Reduced probability (caps memory growth)
- Prevents exponential memory explosion

## Application: Deception Schema Evolution
- **What it evolves:** Filesystem schemas (fake file trees with tempting content)
- **Examples:** 
  - Fake AWS credentials files
  - Staged .env backups
  - Decoy database configs
  - Honeytoken-laden documents
- **Goal:** Create increasingly convincing fake environments that keep attackers engaged

## Performance Benchmark
| Metric | Standard RRT | S-RRT | Improvement |
|--------|-------------|-------|-------------|
| Best Fitness (5 runs) | 450.2 | 1,615.8 | **+258.9%** |

*Note: This massive improvement demonstrates the power of semantic weighting over random exploration*

## Validation
- 27 dedicated unit tests in `Backend/tests/test_s_rrt_equations.py`
- Mathematical proofs in `Backend/tests/test_mathematical_proofs.py`
- Comparison tests in `Backend/tests/test_comparison_algorithms.py`

## Visualization
- `Backend/docs/s_rrt_memory_optimization.png` - S-RRT memory optimization chart
- Frontend: `SRTDeceptionMap.jsx` - Deception schema visualization

## Integration Point
Called after classification to select deception schema:
```python
schema = s_rrt.select_schema(attack_category, severity_index)
populate_fake_shell_db(schema)  # Injects fake files/content
```

## How It Works End-to-End
1. **Population initialization:** Generate diverse filesystem schemas
2. **Fitness evaluation:** Measure schema effectiveness (attacker engagement metrics)
3. **Pheromone update:** Weight by PSI (Equation 3)
4. **Tree expansion:** Apply depth-decay (Equation 4)
5. **Selection:** Keep highest-fitness schemas
6. **Repeat:** Evolve over generations

## Research Contribution
This is one of **two novel algorithms** introduced by Chameleon, representing a breakthrough in automated deception generation by treating it as an optimization problem solvable through tree-based evolutionary search.

## See Also
- [[knowledge/entities/TC-PSO Algorithm|TC-PSO Algorithm]]
- [[knowledge/concepts/Deception Engine|Deception Engine]]
- [[knowledge/entities/Two-Stage Evaluation Pipeline|Two-Stage Evaluation Pipeline]]
- [[knowledge/concepts/Honeytoken Strategy|Honeytoken Strategy]]
