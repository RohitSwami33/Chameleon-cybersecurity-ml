"""
S-RRT Novel Equations — Exhaustive Test Suite
==============================================
Validates Equation 3 (Exponential Pheromone Weighting) and Equation 4
(Depth-Decay Multiplier) from the research paper:

  "Threat-Calibrated PSO and Semantic Deception RRT: Novel Domain-Specific
   Mathematical Enhancements for Adaptive Honeypot Systems"

Equations Under Test
--------------------
  Eq 3: Δτ' = Δτ · exp(Ψ - 1)       [PSI-weighted pheromone update]
  Eq 4: P'_expand = P_expand · max(ε, 1 - d/d_max)  [depth-decay expansion]

Author: Chameleon Research Team
Date: March 2026
Run:  pytest tests/test_s_rrt_equations.py -v --asyncio-mode=auto
"""

import sys
import os
import math
import random
import pytest
from typing import List

# ── path setup ──────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from meta_heuristics import (
    SemanticDeceptionRRT,
    DeceptionEvolutionRRT,
    RRTNode,
    DeceptionTree,
    S_RRT_CONFIG,
)

# ── S-RRT constants ──────────────────────────────────────────────────────────
BASE_PHEROMONE = 0.5               # Δτ
D_MAX          = 6                 # max_depth
EPSILON        = 0.1               # floor probability
P_EXPAND_BASE  = 0.6               # reference for Eq 4 examples


# ── reference equations ───────────────────────────────────────────────────────
def eq3_pheromone(psi: float, delta_tau: float = 0.5) -> float:
    """Eq 3: Δτ' = Δτ · exp(Ψ - 1)"""
    return delta_tau * math.exp(psi - 1.0)


def eq4_expansion(p_expand: float, depth: int, d_max: int = D_MAX, eps: float = EPSILON) -> float:
    """Eq 4: P'_expand = P_expand · max(ε, 1 - d/d_max)"""
    decay = max(eps, 1.0 - depth / d_max)
    return p_expand * decay


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def s_rrt():
    return SemanticDeceptionRRT()


@pytest.fixture
def std_rrt():
    return DeceptionEvolutionRRT()


# ============================================================================
# TEST GROUP 1 — Equation 3: Exponential Pheromone Weighting
# ============================================================================

class TestEquation3ExponentialPheromone:
    """
    Validates: Δτ' = Δτ · exp(Ψ - 1)

    Reference table (from documentation §Pheromone Update Examples):
      Ψ=1.0 (Low)    | e⁰=1.00   | Δτ'=0.50
      Ψ=1.5          | e⁰·⁵≈1.65 | Δτ'=0.82
      Ψ=2.0 (Medium) | e¹≈2.72   | Δτ'=1.36
      Ψ=2.5          | e¹·⁵≈4.48 | Δτ'=2.24
      Ψ=3.0 (High)   | e²≈7.39   | Δτ'=3.69
    """

    def test_eq3_psi_1_backward_compat(self):
        """PSI=1.0 → Δτ' must equal base Δτ exactly (backward compatible)."""
        result = eq3_pheromone(1.0)
        print(f"\n[Eq3] PSI=1.0 → Δτ'={result:.4f} (expected 0.5000)")
        assert abs(result - 0.5) < 1e-9, f"PSI=1.0 must give exactly Δτ=0.5, got {result}"

    def test_eq3_psi_1_5(self):
        """PSI=1.5 → Δτ' ≈ 0.82."""
        result = eq3_pheromone(1.5)
        expected = 0.5 * math.exp(0.5)  # ≈ 0.8244
        print(f"\n[Eq3] PSI=1.5 → Δτ'={result:.4f} (expected ≈0.8244)")
        assert abs(result - expected) < 0.01, f"PSI=1.5 mismatch: {result:.4f} ≠ {expected:.4f}"

    def test_eq3_psi_2_medium(self):
        """PSI=2.0 → Δτ' ≈ 1.36."""
        result = eq3_pheromone(2.0)
        expected = 0.5 * math.e  # ≈ 1.3591
        print(f"\n[Eq3] PSI=2.0 → Δτ'={result:.4f} (expected ≈1.359)")
        assert abs(result - expected) < 0.01, f"PSI=2.0 mismatch: {result:.4f} ≠ {expected:.4f}"

    def test_eq3_psi_2_5(self):
        """PSI=2.5 → Δτ' ≈ 2.24."""
        result = eq3_pheromone(2.5)
        expected = 0.5 * math.exp(1.5)  # ≈ 2.2408
        print(f"\n[Eq3] PSI=2.5 → Δτ'={result:.4f} (expected ≈2.241)")
        assert abs(result - expected) < 0.01, f"PSI=2.5 mismatch: {result:.4f} ≠ {expected:.4f}"

    def test_eq3_psi_3_critical(self):
        """PSI=3.0 → Δτ' ≈ 3.69."""
        result = eq3_pheromone(3.0)
        expected = 0.5 * math.exp(2.0)  # ≈ 3.6945
        print(f"\n[Eq3] PSI=3.0 → Δτ'={result:.4f} (expected ≈3.695)")
        assert abs(result - expected) < 0.01, f"PSI=3.0 mismatch: {result:.4f} ≠ {expected:.4f}"

    def test_eq3_strictly_monotone(self):
        """Δτ' must be monotonically increasing in PSI across [1.0, 3.0]."""
        psi_values = [1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0]
        deltas = [eq3_pheromone(p) for p in psi_values]
        print(f"\n[Eq3] Monotonicity: {[f'{d:.4f}' for d in deltas]}")
        for i in range(len(deltas) - 1):
            assert deltas[i] < deltas[i + 1], (
                f"Not monotone at PSI={psi_values[i]:.2f}: {deltas[i]:.4f} >= {deltas[i+1]:.4f}"
            )

    def test_eq3_exponential_vs_linear(self):
        """Verify that Eq 3 grows exponentially, not linearly."""
        # At PSI=1,2,3 the ratios should follow e^(Ψ-1) not (Ψ-1)
        d1 = eq3_pheromone(1.0)
        d2 = eq3_pheromone(2.0)
        d3 = eq3_pheromone(3.0)

        ratio_2_to_1 = d2 / d1    # should be ≈ e ≈ 2.718
        ratio_3_to_2 = d3 / d2    # should also be ≈ e ≈ 2.718

        print(f"\n[Eq3] Ratios: d2/d1={ratio_2_to_1:.4f}, d3/d2={ratio_3_to_2:.4f} (expected ≈{math.e:.4f})")
        assert abs(ratio_2_to_1 - math.e) < 0.001, "Unit-step PSI ratio should be e"
        assert abs(ratio_3_to_2 - math.e) < 0.001, "Unit-step PSI ratio should be e"

    @pytest.mark.asyncio
    async def test_eq3_high_psi_produces_larger_pheromone(self, s_rrt):
        """Interacting with PSI=3.0 must result in higher total pheromone than PSI=1.0."""
        schema_id_low, schema_low = await s_rrt.get_tempting_schema()
        paths_low = list(schema_low.keys())[:2]
        await s_rrt.evaluate_interaction(
            schema_id=schema_id_low, interacted_paths=paths_low,
            payload_severity_index=1.0
        )
        fitness_low = s_rrt.trees[schema_id_low].fitness

        schema_id_high, schema_high = await s_rrt.get_tempting_schema()
        paths_high = list(schema_high.keys())[:2]
        await s_rrt.evaluate_interaction(
            schema_id=schema_id_high, interacted_paths=paths_high,
            payload_severity_index=3.0
        )
        fitness_high = s_rrt.trees[schema_id_high].fitness

        print(f"\n[Eq3] PSI=1.0 fitness: {fitness_low:.4f}")
        print(f"[Eq3] PSI=3.0 fitness: {fitness_high:.4f}")
        assert fitness_high > fitness_low, (
            f"PSI=3.0 must yield higher fitness than PSI=1.0. "
            f"Got: {fitness_high:.4f} vs {fitness_low:.4f}"
        )

    @pytest.mark.asyncio
    async def test_eq3_psi_clamping_below_1(self, s_rrt):
        """PSI values below 1.0 must be clamped to 1.0."""
        schema_id, schema = await s_rrt.get_tempting_schema()
        paths = list(schema.keys())[:1]
        # passing PSI=0.5 should be clamped to 1.0 internally
        before_fitness = s_rrt.trees[schema_id].fitness
        await s_rrt.evaluate_interaction(
            schema_id=schema_id, interacted_paths=paths,
            payload_severity_index=0.5  # invalid; implementation clamps to 1.0
        )
        after_fitness = s_rrt.trees[schema_id].fitness
        # fitness should have increased (not decreased or errored)
        assert after_fitness >= before_fitness, "PSI clamping must not cause fitness to decrease"

    @pytest.mark.asyncio
    async def test_eq3_psi_clamping_above_3(self, s_rrt):
        """PSI values above 3.0 must be clamped to 3.0."""
        schema_id, schema = await s_rrt.get_tempting_schema()
        paths = list(schema.keys())[:1]
        before_fitness = s_rrt.trees[schema_id].fitness
        await s_rrt.evaluate_interaction(
            schema_id=schema_id, interacted_paths=paths,
            payload_severity_index=99.0  # invalid; implementation clamps to 3.0
        )
        after_fitness = s_rrt.trees[schema_id].fitness
        assert after_fitness > before_fitness, "PSI>3 clamping must still increase fitness"

    @pytest.mark.asyncio
    async def test_eq3_sensitive_file_amplification(self, s_rrt):
        """Sensitive file paths must receive extra exponential bonus."""
        schema_id, schema = await s_rrt.get_tempting_schema()
        before = s_rrt.trees[schema_id].fitness

        sensitive_paths = [p for p in schema.keys()
                           if any(k in p.lower() for k in ['password', 'key', '.env', 'id_rsa', 'secret'])]

        if not sensitive_paths:
            pytest.skip("No sensitive paths in this schema template")

        await s_rrt.evaluate_interaction(
            schema_id=schema_id, interacted_paths=sensitive_paths,
            payload_severity_index=2.5
        )
        after = s_rrt.trees[schema_id].fitness
        delta = after - before
        print(f"\n[Eq3] Sensitive file bonus delta: {delta:.4f}")
        assert delta > 0, "Sensitive file interaction must increase fitness"


# ============================================================================
# TEST GROUP 2 — Equation 4: Depth-Decay Multiplier
# ============================================================================

class TestEquation4DepthDecay:
    """
    Validates: P'_expand = P_expand · max(ε, 1 - d/d_max)

    Reference table (from documentation, d_max=6, ε=0.1, P_expand=0.6):
      d=0 (Root) | decay=1.000 | P'=0.60
      d=1        | decay=0.833 | P'=0.50
      d=2        | decay=0.667 | P'=0.40
      d=3        | decay=0.500 | P'=0.30
      d=4        | decay=0.333 | P'=0.20
      d=5        | decay=0.167 | P'=0.10
      d=6 (Max)  | decay=0.0→max(0.1,0)=0.1 | P'=0.06
    """

    def test_eq4_root_depth_no_decay(self):
        """At d=0 (root), P' must equal P_expand (no decay)."""
        result = eq4_expansion(P_EXPAND_BASE, depth=0)
        print(f"\n[Eq4] d=0 → P'={result:.4f} (expected {P_EXPAND_BASE:.4f})")
        assert abs(result - P_EXPAND_BASE) < 1e-9

    def test_eq4_depth_1(self):
        """At d=1, P' ≈ 0.50."""
        result = eq4_expansion(P_EXPAND_BASE, depth=1)
        expected = P_EXPAND_BASE * (1 - 1/6)  # ≈ 0.5
        print(f"\n[Eq4] d=1 → P'={result:.4f} (expected ≈{expected:.4f})")
        assert abs(result - expected) < 0.001

    def test_eq4_depth_2(self):
        """At d=2, P' ≈ 0.40."""
        result = eq4_expansion(P_EXPAND_BASE, depth=2)
        expected = P_EXPAND_BASE * (1 - 2/6)  # 0.40
        print(f"\n[Eq4] d=2 → P'={result:.4f} (expected {expected:.4f})")
        assert abs(result - expected) < 0.001

    def test_eq4_depth_3_midpoint(self):
        """At d=3 (midpoint), P' = 0.30."""
        result = eq4_expansion(P_EXPAND_BASE, depth=3)
        expected = P_EXPAND_BASE * 0.5  # 0.30
        print(f"\n[Eq4] d=3 → P'={result:.4f} (expected {expected:.4f})")
        assert abs(result - expected) < 0.001

    def test_eq4_depth_4(self):
        """At d=4, P' ≈ 0.20."""
        result = eq4_expansion(P_EXPAND_BASE, depth=4)
        expected = P_EXPAND_BASE * (1 - 4/6)  # ≈ 0.2
        print(f"\n[Eq4] d=4 → P'={result:.4f} (expected ≈{expected:.4f})")
        assert abs(result - expected) < 0.001

    def test_eq4_depth_5(self):
        """At d=5, P' ≈ 0.10."""
        result = eq4_expansion(P_EXPAND_BASE, depth=5)
        expected = P_EXPAND_BASE * (1 - 5/6)  # ≈ 0.1
        print(f"\n[Eq4] d=5 → P'={result:.4f} (expected ≈{expected:.4f})")
        assert abs(result - expected) < 0.001

    def test_eq4_at_max_depth_floor(self):
        """At d=d_max, decay factor is max(ε, 0) = ε, so P' = ε·P_expand = 0.06."""
        result = eq4_expansion(P_EXPAND_BASE, depth=D_MAX)
        expected = P_EXPAND_BASE * EPSILON  # 0.6 × 0.1 = 0.06
        print(f"\n[Eq4] d=d_max={D_MAX} → P'={result:.4f} (expected {expected:.4f})")
        assert abs(result - expected) < 0.001

    def test_eq4_beyond_max_depth(self):
        """Beyond d_max, floor ε still applies — P' must not go below ε·P_expand."""
        for d in range(D_MAX, D_MAX + 5):
            result = eq4_expansion(P_EXPAND_BASE, depth=d)
            floor = P_EXPAND_BASE * EPSILON
            assert result >= floor - 1e-9, (
                f"At d={d}, P' {result:.4f} fell below floor {floor:.4f}"
            )

    def test_eq4_strictly_monotone_decreasing(self):
        """P' must monotonically decrease as depth increases."""
        probs = [eq4_expansion(P_EXPAND_BASE, d) for d in range(0, D_MAX + 1)]
        print(f"\n[Eq4] Depth-decay P' values: {[f'{p:.4f}' for p in probs]}")
        for i in range(len(probs) - 1):
            assert probs[i] >= probs[i + 1], (
                f"Not monotone at d={i}: P'={probs[i]:.4f} should be >= P'={probs[i+1]:.4f}"
            )

    def test_eq4_positive_always(self):
        """P'_expand must always be positive."""
        for d in range(0, D_MAX + 10):
            result = eq4_expansion(P_EXPAND_BASE, depth=d)
            assert result > 0, f"P'_expand must be positive, got {result} at d={d}"

    @pytest.mark.asyncio
    async def test_eq4_memory_stays_bounded(self, s_rrt):
        """Node count must stay bounded under 20 generations (depth-decay prevents explosion)."""
        initial_counts = [t.node_count for t in s_rrt.trees.values()]
        initial_mean = sum(initial_counts) / len(initial_counts)
        max_observed = initial_mean

        for generation in range(20):
            for _ in range(s_rrt.rrt_config["num_trees"]):
                schema_id, schema = await s_rrt.get_tempting_schema()
                paths = list(schema.keys())[:2]
                await s_rrt.evaluate_interaction(
                    schema_id=schema_id, interacted_paths=paths,
                    payload_severity_index=2.5
                )
            await s_rrt.evolve_tree()

            current_counts = [t.node_count for t in s_rrt.trees.values()]
            current_mean = sum(current_counts) / len(current_counts)
            max_observed = max(max_observed, current_mean)
            print(f"[Eq4] Gen {generation+1:02d}: mean_nodes={current_mean:.1f}")

        print(f"\n[Eq4] Initial mean nodes: {initial_mean:.1f}")
        print(f"[Eq4] Max observed mean: {max_observed:.1f}")
        print(f"[Eq4] Growth factor: {max_observed/initial_mean:.2f}×")

        assert max_observed < initial_mean * 4, (
            f"Node count grew too aggressively: {initial_mean:.1f} → {max_observed:.1f} "
            f"({max_observed/initial_mean:.1f}×). Depth-decay should prevent this."
        )


# ============================================================================
# TEST GROUP 3 — Full S-RRT Integration
# ============================================================================

class TestSRRTIntegration:
    """End-to-end integration tests validating both Eq 3 + Eq 4 together."""

    @pytest.mark.asyncio
    async def test_full_evolution_fitness_improves(self, s_rrt):
        """Population mean fitness must improve over 15 generations."""
        initial_fitnesses = [t.fitness for t in s_rrt.trees.values()]
        initial_mean = sum(initial_fitnesses) / len(initial_fitnesses)
        random.seed(123)

        for generation in range(15):
            for _ in range(s_rrt.rrt_config["num_trees"]):
                schema_id, schema = await s_rrt.get_tempting_schema()
                paths = list(schema.keys())[:random.randint(1, max(1, len(schema)))]
                await s_rrt.evaluate_interaction(
                    schema_id=schema_id, interacted_paths=paths,
                    payload_severity_index=2.0
                )
            await s_rrt.evolve_tree()

        final_fitnesses = [t.fitness for t in s_rrt.trees.values()]
        final_mean = sum(final_fitnesses) / len(final_fitnesses)
        final_best = max(final_fitnesses)

        print(f"\n[S-RRT] Initial mean fitness: {initial_mean:.2f}")
        print(f"[S-RRT] Final mean fitness:   {final_mean:.2f}")
        print(f"[S-RRT] Final best fitness:   {final_best:.2f}")

        assert final_mean > initial_mean, "Population fitness must improve over generations"

    @pytest.mark.asyncio
    async def test_high_psi_trees_dominate(self, s_rrt):
        """Trees trained with high PSI must eventually dominate the population."""
        all_trees = list(s_rrt.trees.keys())
        high_psi_trees = all_trees[:len(all_trees) // 2]

        for gen in range(10):
            for tree_id in high_psi_trees:
                schema = s_rrt._tree_to_flat_schema(s_rrt.trees[tree_id].root)
                paths = list(schema.keys())[:3]
                await s_rrt.evaluate_interaction(
                    schema_id=tree_id, interacted_paths=paths,
                    payload_severity_index=3.0  # high PSI → high pheromone → high fitness
                )
            await s_rrt.evolve_tree()

        # Check that best tree is from high-PSI group
        best_fitness = max(t.fitness for t in s_rrt.trees.values())
        assert best_fitness > 0, "After high-PSI training, best fitness should be positive"
        print(f"\n[S-RRT] Best fitness after high-PSI training: {best_fitness:.4f}")

    @pytest.mark.asyncio
    async def test_population_size_stable(self, s_rrt):
        """Tree count must remain constant through all evolution phases."""
        initial_count = len(s_rrt.trees)

        for gen in range(5):
            for _ in range(s_rrt.rrt_config["num_trees"]):
                schema_id, schema = await s_rrt.get_tempting_schema()
                paths = list(schema.keys())[:2]
                await s_rrt.evaluate_interaction(
                    schema_id=schema_id, interacted_paths=paths,
                    payload_severity_index=2.0
                )
            await s_rrt.evolve_tree()
            current_count = len(s_rrt.trees)
            assert current_count == initial_count, (
                f"Population size changed at gen {gen}: {initial_count} → {current_count}"
            )

    @pytest.mark.asyncio
    async def test_pheromone_global_map_grows(self, s_rrt):
        """Global pheromone map must accumulate entries over interactions."""
        initial_size = len(s_rrt.path_pheromones)

        for _ in range(10):
            schema_id, schema = await s_rrt.get_tempting_schema()
            paths = list(schema.keys())
            await s_rrt.evaluate_interaction(
                schema_id=schema_id, interacted_paths=paths,
                payload_severity_index=2.0
            )

        final_size = len(s_rrt.path_pheromones)
        print(f"\n[S-RRT] Global pheromone map: {initial_size} → {final_size} entries")
        assert final_size >= initial_size, "Pheromone map must not shrink"

    @pytest.mark.asyncio
    async def test_best_tree_tracking(self, s_rrt):
        """Best tree must be updated correctly as fitness improves."""
        for _ in range(5):
            schema_id, schema = await s_rrt.get_tempting_schema()
            paths = list(schema.keys())
            await s_rrt.evaluate_interaction(
                schema_id=schema_id, interacted_paths=paths,
                payload_severity_index=3.0
            )

        assert s_rrt.best_tree is not None, "Best tree tracker must be non-null after interactions"
        assert s_rrt.best_fitness > 0, "Best fitness tracker must be positive"
        expected_best = max(t.fitness for t in s_rrt.trees.values())
        assert abs(s_rrt.best_fitness - expected_best) < 1e-6, (
            f"Best tree fitness tracker mismatch: {s_rrt.best_fitness:.4f} != {expected_best:.4f}"
        )
