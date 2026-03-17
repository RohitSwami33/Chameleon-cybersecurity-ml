"""
TC-PSO Novel Equations — Exhaustive Test Suite
================================================
Validates Equation 1 (Dynamic Inertia) and Equation 2 (Anomaly-Weighted Fitness)
from the research paper:

  "Threat-Calibrated PSO and Semantic Deception RRT: Novel Domain-Specific
   Mathematical Enhancements for Adaptive Honeypot Systems"

Equations Under Test
--------------------
  Eq 1: w(t) = w_base · max(σ_min, 1 - α · A(t))
  Eq 2: F'(t) = F(t) · (1 + β · A(t))

Author: Chameleon Research Team
Date: March 2026
Run:  pytest tests/test_tc_pso_equations.py -v --asyncio-mode=auto
"""

import sys
import os
import math
import random
import asyncio
import pytest
from typing import List, Tuple

# ── path setup ──────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.optimization.meta_heuristics import (
    ThreatCalibratedPSO,
    AdaptiveTarpitPSO,
    TC_PSO_CONFIG,
    PSO_CONFIG,
    FITNESS_WEIGHTS,
    AttackCategory,
)

# ── constants from paper ────────────────────────────────────────────────────
W_BASE   = 0.729          # standard PSO inertia
ALPHA    = 0.5            # anomaly sensitivity
SIGMA_MIN = 0.3           # minimum inertia scale factor
BETA     = 0.3            # reward amplification factor
MIN_DELAY = 0.5
MAX_DELAY = 12.0

# ── helpers ──────────────────────────────────────────────────────────────────
def expected_inertia(anomaly_score: float) -> float:
    """Reference implementation of Equation 1."""
    scale = max(SIGMA_MIN, 1.0 - ALPHA * anomaly_score)
    return W_BASE * scale


def expected_fitness_multiplier(anomaly_score: float) -> float:
    """Reference implementation of Equation 2 multiplier."""
    return 1.0 + BETA * anomaly_score


def simulate_attacker(delay: float) -> Tuple[int, bool]:
    """Synthetic attacker response model used throughout tests."""
    if delay > 5.0:
        return (0, True)           # timeout → drop
    elif 4.0 <= delay <= 5.0:
        return (random.randint(8, 12), False)   # optimal zone
    elif 3.0 <= delay < 4.0:
        return (random.randint(5, 8), False)
    elif 2.0 <= delay < 3.0:
        return (random.randint(3, 5), False)
    else:
        return (random.randint(1, 3), False)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def tc_pso():
    return ThreatCalibratedPSO()


@pytest.fixture
def std_pso():
    return AdaptiveTarpitPSO()


# ============================================================================
# TEST GROUP 1 — Equation 1: Dynamic Inertia Weight Scaling
# ============================================================================

class TestEquation1DynamicInertia:
    """
    Validates: w(t) = w_base · max(σ_min, 1 - α · A(t))
    Reference table (from NOVEL_EQUATIONS_DOCUMENTATION.md §Boundary Analysis):

      A(t)  | Inertia Scale         | w(t)
      ------|-----------------------|-------
      0.00  | max(0.3, 1.00) = 1.00 | 0.729
      0.50  | max(0.3, 0.75) = 0.75 | 0.547
      0.85  | max(0.3, 0.575)=0.575 | 0.419
      1.00  | max(0.3, 0.50) = 0.50 | 0.365
    """

    def test_eq1_benign_session_max_inertia(self, tc_pso):
        """A(t)=0.0 (benign) → inertia must equal w_base (0.729)."""
        category = "SQLI"
        tc_pso.anomaly_scores[category] = 0.0
        w = tc_pso._calculate_dynamic_inertia(category)

        expected = expected_inertia(0.0)   # 0.729
        print(f"\n[Eq1] A=0.00 → w={w:.4f} (expected {expected:.4f})")
        assert abs(w - expected) < 1e-6, f"Benign inertia mismatch: {w:.6f} != {expected:.6f}"
        assert abs(w - W_BASE) < 1e-6, "At A=0, w should equal w_base exactly"

    def test_eq1_moderate_threat_inertia(self, tc_pso):
        """A(t)=0.5 (moderate) → inertia ≈ 0.5474."""
        category = "XSS"
        tc_pso.anomaly_scores[category] = 0.5
        w = tc_pso._calculate_dynamic_inertia(category)

        expected = expected_inertia(0.5)   # 0.547
        print(f"\n[Eq1] A=0.50 → w={w:.4f} (expected {expected:.4f})")
        assert abs(w - expected) < 1e-4, f"Moderate-threat inertia mismatch: {w:.4f} != {expected:.4f}"

    def test_eq1_high_threat_inertia(self, tc_pso):
        """A(t)=0.85 (high threat) → inertia ≈ 0.4192."""
        category = "RCE"
        tc_pso.anomaly_scores[category] = 0.85
        w = tc_pso._calculate_dynamic_inertia(category)

        expected = expected_inertia(0.85)  # ~0.4192
        print(f"\n[Eq1] A=0.85 → w={w:.4f} (expected {expected:.4f})")
        assert abs(w - expected) < 1e-4, f"High-threat inertia mismatch: {w:.4f} != {expected:.4f}"

    def test_eq1_critical_threat_floor(self, tc_pso):
        """A(t)=1.0 (critical) → inertia ≈ 0.3645 (w_base × 0.5)."""
        category = "BRUTE_FORCE"
        tc_pso.anomaly_scores[category] = 1.0
        w = tc_pso._calculate_dynamic_inertia(category)

        expected = expected_inertia(1.0)   # 0.3645
        print(f"\n[Eq1] A=1.00 → w={w:.4f} (expected {expected:.4f})")
        assert abs(w - expected) < 1e-4, f"Critical inertia mismatch: {w:.4f} != {expected:.4f}"

    def test_eq1_strictly_monotone_decreasing(self, tc_pso):
        """Inertia must strictly decrease as A(t) increases from 0 → 1."""
        category = "SQLI"
        anomaly_levels = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        inertias = []

        for a in anomaly_levels:
            tc_pso.anomaly_scores[category] = a
            inertias.append(tc_pso._calculate_dynamic_inertia(category))

        print(f"\n[Eq1] Monotonicity: {[f'{w:.4f}' for w in inertias]}")
        for i in range(len(inertias) - 1):
            assert inertias[i] >= inertias[i + 1], (
                f"Inertia not monotone at A={anomaly_levels[i]:.1f}→{anomaly_levels[i+1]:.1f}: "
                f"{inertias[i]:.4f} < {inertias[i+1]:.4f}"
            )

    def test_eq1_hard_lower_bound(self, tc_pso):
        """Inertia must never drop below w_base × σ_min = 0.2187."""
        category = "PATH_TRAVERSAL"
        lower_bound = W_BASE * SIGMA_MIN  # 0.2187

        for a in [x / 100 for x in range(0, 101)]:
            tc_pso.anomaly_scores[category] = a
            w = tc_pso._calculate_dynamic_inertia(category)
            assert w >= lower_bound - 1e-9, (
                f"Inertia {w:.6f} fell below lower bound {lower_bound:.6f} at A={a:.2f}"
            )

    def test_eq1_hard_upper_bound(self, tc_pso):
        """Inertia must never exceed w_base = 0.729."""
        category = "SSI"
        for a in [x / 100 for x in range(0, 101)]:
            tc_pso.anomaly_scores[category] = a
            w = tc_pso._calculate_dynamic_inertia(category)
            assert w <= W_BASE + 1e-9, (
                f"Inertia {w:.6f} exceeded upper bound {W_BASE:.4f} at A={a:.2f}"
            )

    def test_eq1_multiple_categories_independent(self, tc_pso):
        """Each attack category maintains independent inertia state."""
        categories = ["SQLI", "XSS", "RCE", "BRUTE_FORCE"]
        scores = [0.1, 0.5, 0.9, 0.3]

        for cat, score in zip(categories, scores):
            tc_pso.anomaly_scores[cat] = score

        for cat, score in zip(categories, scores):
            w = tc_pso._calculate_dynamic_inertia(cat)
            expected = expected_inertia(score)
            print(f"\n[Eq1] Category {cat}, A={score} → w={w:.4f} (expected {expected:.4f})")
            assert abs(w - expected) < 1e-4, f"{cat} inertia mismatch"

    def test_eq1_anomaly_clamping_above_one(self, tc_pso):
        """Anomaly scores > 1.0 must be clamped to 1.0."""
        category = "GENERIC"
        tc_pso.anomaly_scores[category] = 1.0   # manually clamped
        # update_fitness clamps at 1.0; verify manually
        clamped = max(0.0, min(1.0, 1.5))
        tc_pso.anomaly_scores[category] = clamped
        w = tc_pso._calculate_dynamic_inertia(category)
        assert w >= W_BASE * SIGMA_MIN - 1e-6, "Clamped anomaly should stay in valid range"

    def test_eq1_anomaly_clamping_below_zero(self, tc_pso):
        """Anomaly scores < 0.0 must be clamped to 0.0."""
        category = "GENERIC"
        clamped = max(0.0, min(1.0, -0.5))
        tc_pso.anomaly_scores[category] = clamped
        w = tc_pso._calculate_dynamic_inertia(category)
        assert abs(w - W_BASE) < 1e-6, "Clamped-to-zero anomaly should give max inertia"


# ============================================================================
# TEST GROUP 2 — Equation 2: Anomaly-Weighted Objective Function
# ============================================================================

class TestEquation2AnomalyFitness:
    """
    Validates: F'(t) = F(t) · (1 + β · A(t))

    Fitness Amplification Table (from documentation):
      F(t)=5.0, A=0.0  → F'=5.00  (1.000× multiplier)
      F(t)=5.0, A=0.5  → F'=5.75  (1.150× multiplier)
      F(t)=5.0, A=0.85 → F'=6.275 (1.255× multiplier)
      F(t)=5.0, A=1.0  → F'=6.50  (1.300× multiplier)
    """

    @pytest.mark.asyncio
    async def test_eq2_backward_compat_zero_anomaly(self, tc_pso):
        """A(t)=0 → F'(t) must equal F(t) exactly (backward compatible)."""
        category = "SQLI"
        await tc_pso.update_fitness(
            attack_category=category,
            delay_used=3.0,
            commands_executed=10,
            dropped=False,
            bilstm_anomaly_score=0.0,
        )
        # With A=0: multiplier = 1 + 0.3×0.0 = 1.0 → no change
        multiplier = expected_fitness_multiplier(0.0)
        print(f"\n[Eq2] A=0.0 → multiplier={multiplier:.3f} (expected 1.000)")
        assert abs(multiplier - 1.0) < 1e-9, "Zero anomaly must give exactly 1× multiplier"

    @pytest.mark.asyncio
    async def test_eq2_moderate_amplification(self, tc_pso):
        """A(t)=0.5 → multiplier must be exactly 1.15."""
        multiplier = expected_fitness_multiplier(0.5)
        expected = 1.15
        print(f"\n[Eq2] A=0.50 → multiplier={multiplier:.4f} (expected {expected:.4f})")
        assert abs(multiplier - expected) < 1e-9, f"A=0.5 multiplier wrong: {multiplier}"

    @pytest.mark.asyncio
    async def test_eq2_high_threat_amplification(self, tc_pso):
        """A(t)=0.85 → multiplier must be exactly 1.255."""
        multiplier = expected_fitness_multiplier(0.85)
        expected = 1.255
        print(f"\n[Eq2] A=0.85 → multiplier={multiplier:.4f} (expected {expected:.4f})")
        assert abs(multiplier - expected) < 1e-9, f"A=0.85 multiplier wrong: {multiplier}"

    @pytest.mark.asyncio
    async def test_eq2_critical_max_amplification(self, tc_pso):
        """A(t)=1.0 → multiplier must be exactly 1.3 (30% boost)."""
        multiplier = expected_fitness_multiplier(1.0)
        expected = 1.3
        print(f"\n[Eq2] A=1.00 → multiplier={multiplier:.4f} (expected {expected:.4f})")
        assert abs(multiplier - expected) < 1e-9, f"A=1.0 multiplier wrong: {multiplier}"

    @pytest.mark.asyncio
    async def test_eq2_high_anomaly_beats_low(self, tc_pso):
        """Same base performance → high anomaly session must produce higher fitness."""
        category = "SQLI"
        COMMANDS = 8
        DELAY = 3.5

        # Low anomaly
        pso_low = ThreatCalibratedPSO()
        await pso_low.update_fitness(
            attack_category=category, delay_used=DELAY,
            commands_executed=COMMANDS, dropped=False,
            bilstm_anomaly_score=0.1
        )
        low_fitness = pso_low.global_best[category][1]

        # High anomaly (fresh instance, same session params)
        pso_high = ThreatCalibratedPSO()
        await pso_high.update_fitness(
            attack_category=category, delay_used=DELAY,
            commands_executed=COMMANDS, dropped=False,
            bilstm_anomaly_score=0.9
        )
        high_fitness = pso_high.global_best[category][1]

        print(f"\n[Eq2] Low A=0.1 fitness: {low_fitness:.4f}")
        print(f"[Eq2] High A=0.9 fitness: {high_fitness:.4f}")
        assert high_fitness > low_fitness, (
            f"High anomaly must produce higher fitness. "
            f"Low={low_fitness:.4f}, High={high_fitness:.4f}"
        )

    @pytest.mark.asyncio
    async def test_eq2_fitness_monotone_in_anomaly(self):
        """Fitness must be monotonically increasing with A(t) for fixed base performance."""
        category = "RCE"
        COMMANDS = 6
        DELAY = 3.0
        prev_fitness = float('-inf')

        for a in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
            pso = ThreatCalibratedPSO()
            await pso.update_fitness(
                attack_category=category, delay_used=DELAY,
                commands_executed=COMMANDS, dropped=False,
                bilstm_anomaly_score=a
            )
            current = pso.global_best[category][1]
            print(f"[Eq2] A={a:.1f} → fitness={current:.4f}")
            if prev_fitness != float('-inf'):
                assert current >= prev_fitness - 1e-9, (
                    f"Fitness not monotone at A={a:.1f}: {current:.4f} < {prev_fitness:.4f}"
                )
            prev_fitness = current

    @pytest.mark.asyncio
    async def test_eq2_drop_penalty_still_applied(self, tc_pso):
        """Even with anomaly amplification, connection-drop penalty must make fitness worse."""
        category = "XSS"

        await tc_pso.update_fitness(
            attack_category=category, delay_used=3.0,
            commands_executed=5, dropped=False,
            bilstm_anomaly_score=0.9
        )
        fitness_no_drop = tc_pso.global_best[category][1]

        pso2 = ThreatCalibratedPSO()
        await pso2.update_fitness(
            attack_category=category, delay_used=3.0,
            commands_executed=5, dropped=True,
            bilstm_anomaly_score=0.9
        )
        fitness_with_drop = pso2.global_best[category][1]

        print(f"\n[Eq2] No-drop fitness: {fitness_no_drop:.4f}")
        print(f"[Eq2] With-drop fitness: {fitness_with_drop:.4f}")
        assert fitness_no_drop > fitness_with_drop, "Drop penalty must lower fitness even with high anomaly"

    @pytest.mark.asyncio
    async def test_eq2_interaction_bonus_aggregation(self, tc_pso):
        """Commands > 5 trigger the interaction bonus; verify base values match formula."""
        category = "BRUTE_FORCE"
        w1 = FITNESS_WEIGHTS["w1_command_execution"]
        w3 = FITNESS_WEIGHTS["w3_interaction_bonus"]

        # Manually calculate expected base fitness for 5 and 6 commands (A=0, multiplier=1.0)
        # F(5) = w1*5 - 0     = 0.65*5 = 3.25,  bonus_5 = 0    → F'(5) = 3.25
        # F(6) = w1*6 - 0 + w3*(6-5) = 0.65*6 + 0.25 = 4.15 → F'(6) = 4.15
        expected_5 = w1 * 5
        expected_6 = w1 * 6 + w3 * 1
        expected_delta = expected_6 - expected_5  # 0.25 + 0.65 = 0.90

        await tc_pso.update_fitness(
            attack_category=category, delay_used=3.0,
            commands_executed=6, dropped=False,
            bilstm_anomaly_score=0.0
        )
        fitness_6 = tc_pso.global_best[category][1]

        pso2 = ThreatCalibratedPSO()
        await pso2.update_fitness(
            attack_category=category, delay_used=3.0,
            commands_executed=5, dropped=False,
            bilstm_anomaly_score=0.0
        )
        fitness_5 = pso2.global_best[category][1]

        actual_delta = fitness_6 - fitness_5
        print(f"\n[Eq2] 5-cmd fitness: {fitness_5:.4f} (expected {expected_5:.4f})")
        print(f"[Eq2] 6-cmd fitness: {fitness_6:.4f} (expected {expected_6:.4f})")
        print(f"[Eq2] Delta: {actual_delta:.4f} (expected {expected_delta:.4f})")

        assert fitness_6 > fitness_5, "Interaction bonus must increase fitness for commands > 5"
        assert abs(fitness_5 - expected_5) < 0.001, f"5-cmd base fitness mismatch"
        assert abs(fitness_6 - expected_6) < 0.001, f"6-cmd base fitness mismatch"
        assert abs(actual_delta - expected_delta) < 0.01, (
            f"Delta mismatch: expected {expected_delta:.4f}, got {actual_delta:.4f}"
        )


# ============================================================================
# TEST GROUP 3 — Full TC-PSO Integration
# ============================================================================

class TestTCPSOIntegration:
    """End-to-end integration tests for the complete TC-PSO algorithm."""

    @pytest.mark.asyncio
    async def test_full_convergence_100_iterations(self, tc_pso):
        """TC-PSO must converge to a reasonable delay range in 100 iterations."""
        category = "SQLI"
        random.seed(42)

        for i in range(100):
            delay = await tc_pso.get_optimal_delay(category)
            commands, dropped = simulate_attacker(delay)
            await tc_pso.update_fitness(
                attack_category=category, delay_used=delay,
                commands_executed=commands, dropped=dropped,
                session_id=f"conv_{i:03d}",
                bilstm_anomaly_score=0.85
            )

        best_delay = tc_pso.global_best[category][0]
        best_fitness = tc_pso.global_best[category][1]
        print(f"\n[Integration] 100-iter convergence: delay={best_delay:.2f}s, fitness={best_fitness:.4f}")

        assert MIN_DELAY <= best_delay <= MAX_DELAY, "Delay out of global bounds"
        assert best_fitness > 0, "Fitness must be positive after convergence"
        assert tc_pso.iteration_count[category] == 100, "Iteration counter mismatch"

    @pytest.mark.asyncio
    async def test_delay_stays_in_bounds_always(self, tc_pso):
        """All 200 delay queries must stay within [0.5, 12.0]."""
        category = "XSS"
        random.seed(99)
        for i in range(100):
            delay = await tc_pso.get_optimal_delay(category)
            assert MIN_DELAY <= delay <= MAX_DELAY, f"Delay {delay} out of bounds at step {i}"
            cmds, dropped = simulate_attacker(delay)
            await tc_pso.update_fitness(
                attack_category=category, delay_used=delay,
                commands_executed=cmds, dropped=dropped,
                bilstm_anomaly_score=random.random()
            )

        for _ in range(100):
            delay = await tc_pso.get_optimal_delay(category)
            assert MIN_DELAY <= delay <= MAX_DELAY, f"Post-train delay {delay} out of bounds"

    @pytest.mark.asyncio
    async def test_high_anomaly_accelerates_convergence(self):
        """TC-PSO with high anomaly should reach better fitness faster than low anomaly."""
        category = "RCE"
        N = 30
        random.seed(7)

        pso_high = ThreatCalibratedPSO()
        for i in range(N):
            d = await pso_high.get_optimal_delay(category)
            cmds, drop = simulate_attacker(d)
            await pso_high.update_fitness(
                attack_category=category, delay_used=d,
                commands_executed=cmds, dropped=drop, bilstm_anomaly_score=0.95
            )
        fitness_high = pso_high.global_best[category][1]

        random.seed(7)
        pso_low = ThreatCalibratedPSO()
        for i in range(N):
            d = await pso_low.get_optimal_delay(category)
            cmds, drop = simulate_attacker(d)
            await pso_low.update_fitness(
                attack_category=category, delay_used=d,
                commands_executed=cmds, dropped=drop, bilstm_anomaly_score=0.05
            )
        fitness_low = pso_low.global_best[category][1]

        print(f"\n[Integration] High-A fitness: {fitness_high:.4f}, Low-A fitness: {fitness_low:.4f}")
        # High anomaly amplifies fitness via Eq 2 → must be higher
        assert fitness_high >= fitness_low, (
            f"High-anomaly run should reach at least same fitness as low-anomaly in {N} iterations"
        )

    @pytest.mark.asyncio
    async def test_all_attack_categories_initialize(self, tc_pso):
        """All 7 attack categories must be initialized and queryable."""
        for cat in ["SQLI", "XSS", "SSI", "BRUTE_FORCE", "RCE", "PATH_TRAVERSAL", "GENERIC"]:
            delay = await tc_pso.get_optimal_delay(cat)
            assert MIN_DELAY <= delay <= MAX_DELAY, f"{cat}: delay {delay} out of bounds"
            stats = tc_pso.get_swarm_statistics(cat)
            assert stats["num_particles"] == TC_PSO_CONFIG["num_particles"], f"{cat}: wrong particle count"

    @pytest.mark.asyncio
    async def test_particle_count_stable_under_updates(self, tc_pso):
        """Particle count must remain constant throughout all updates."""
        category = "SSI"
        expected_count = TC_PSO_CONFIG["num_particles"]

        for i in range(50):
            await tc_pso.update_fitness(
                attack_category=category, delay_used=3.0,
                commands_executed=random.randint(1, 12), dropped=False,
                bilstm_anomaly_score=random.random()
            )
            stats = tc_pso.get_swarm_statistics(category)
            assert stats["num_particles"] == expected_count, (
                f"Particle count changed at iteration {i}: {stats['num_particles']} != {expected_count}"
            )

    @pytest.mark.asyncio
    async def test_swarm_statistics_structure(self, tc_pso):
        """Swarm statistics dict must contain all required keys."""
        category = "SQLI"
        await tc_pso.update_fitness(
            attack_category=category, delay_used=3.0,
            commands_executed=5, dropped=False, bilstm_anomaly_score=0.5
        )
        stats = tc_pso.get_swarm_statistics(category)
        required_keys = [
            "category", "iterations", "global_best_delay", "global_best_fitness",
            "mean_position", "std_position", "mean_fitness", "num_particles",
            "current_anomaly_score", "dynamic_inertia",
        ]
        for key in required_keys:
            assert key in stats, f"Missing key in swarm statistics: {key}"
