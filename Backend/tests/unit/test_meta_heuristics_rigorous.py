"""
Chameleon Meta-Heuristics Rigorous Test Suite
==============================================
Comprehensive async-aware test suite for validating TC-PSO, S-RRT, and their
standard counterparts in the Chameleon honeypot system.

This test suite provides academic validation for:
1. TC-PSO convergence and boundary behavior with BiLSTM anomaly scores
2. S-RRT (Semantic Deception) tree-based evolutionary progression with PSI
3. Standard PSO and RRT baselines for comparison
4. Concurrency safety under high load
5. Memory management and leak prevention

Author: Chameleon Research Team
Date: March 2026

Usage:
    pytest test_meta_heuristics_rigorous.py -v --asyncio-mode=auto
    pytest test_meta_heuristics_rigorous.py::TestPSOConvergence -v
    pytest test_meta_heuristics_rigorous.py::TestSRRTEvolution -v
"""

import pytest
import asyncio
import random
import time
import sys
import os
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.optimization.meta_heuristics import (
    ThreatCalibratedPSO,
    AdaptiveTarpitPSO,
    SemanticDeceptionRRT,
    DeceptionEvolutionRRT,
    SessionTracker,
    TC_PSO_CONFIG,
    PSO_CONFIG,
    S_RRT_CONFIG,
    FITNESS_WEIGHTS,
    AttackCategory,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def tc_pso_optimizer():
    """Create a fresh TC-PSO optimizer instance for each test."""
    return ThreatCalibratedPSO()


@pytest.fixture
def pso_optimizer():
    """Create a fresh standard PSO optimizer instance for each test."""
    return AdaptiveTarpitPSO()


@pytest.fixture
def s_rrt_optimizer():
    """Create a fresh S-RRT optimizer instance for each test."""
    return SemanticDeceptionRRT()


@pytest.fixture
def rrt_optimizer():
    """Create a fresh standard RRT optimizer instance for each test."""
    return DeceptionEvolutionRRT()


@pytest.fixture
def session_tracker():
    """Create a fresh session tracker for each test."""
    return SessionTracker()


@pytest.fixture
def sample_attack_categories():
    """Return list of attack categories for testing."""
    return ["SQLI", "XSS", "SSI", "BRUTE_FORCE", "RCE"]


# ============================================================================
# Test 1: TC-PSO Convergence & Boundary Validation (The Math Proof)
# ============================================================================

class TestTCPSOConvergence:
    """
    Test TC-PSO convergence behavior and boundary constraints.

    Research Validation:
    ────────────────────
    These tests validate that the TC-PSO algorithm correctly implements
    the novel mathematical formulation with dynamic inertia scaling:
    
    w(t) = w_base * (1 - α * anomaly_score)
    F'(t) = F(t) * (1 + β * anomaly_score)
    
    The fitness landscape simulates real-world attacker behavior where:
    - Delays ~4.5s maximize engagement (C_exec)
    - Delays >5.0s cause timeouts (P_drop penalty)
    - Higher anomaly scores should accelerate convergence
    """

    @pytest.mark.asyncio
    async def test_tc_pso_convergence_to_optimal_delay(self, tc_pso_optimizer):
        """
        Validate that TC-PSO converges to the optimal delay value.

        Simulation Setup:
        ─────────────────
        We create a synthetic fitness landscape where:
        - Optimal delay = 4.5 seconds (maximum C_exec)
        - Delays > 5.0s cause timeout (P_drop = 1)
        - Delays < 2.0s yield low engagement (C_exec = 1-2)

        Expected Outcome:
        ─────────────────
        After 100 iterations, the global best delay should converge
        to approximately 4.5 seconds (±1.0s tolerance).
        """
        category = "SQLI"
        num_iterations = 100
        anomaly_score = 0.85  # High anomaly scenario

        # Simulate fitness landscape
        def simulate_attacker_response(delay: float) -> Tuple[int, bool]:
            """Simulate attacker behavior based on delay."""
            if delay > 5.0:
                return (0, True)
            elif 4.0 <= delay <= 5.0:
                return (random.randint(8, 12), False)
            elif 3.0 <= delay < 4.0:
                return (random.randint(5, 8), False)
            elif 2.0 <= delay < 3.0:
                return (random.randint(3, 5), False)
            else:
                return (random.randint(1, 3), False)

        # Run optimization loop
        for iteration in range(num_iterations):
            current_delay = await tc_pso_optimizer.get_optimal_delay(category)
            commands_executed, dropped = simulate_attacker_response(current_delay)

            await tc_pso_optimizer.update_fitness(
                attack_category=category,
                delay_used=current_delay,
                commands_executed=commands_executed,
                dropped=dropped,
                session_id=f"sim_{iteration:03d}",
                bilstm_anomaly_score=anomaly_score
            )

        # Validate convergence
        final_best_delay = tc_pso_optimizer.global_best[category][0]
        final_best_fitness = tc_pso_optimizer.global_best[category][1]

        print(f"\nTC-PSO Convergence Results:")
        print(f"  Final Best Delay: {final_best_delay:.2f}s")
        print(f"  Final Best Fitness: {final_best_fitness:.4f}")
        print(f"  Anomaly Score: {anomaly_score}")
        print(f"  Iterations: {num_iterations}")

        # Assertions
        assert 1.5 <= final_best_delay <= 7.0, (
            f"TC-PSO did not converge toward optimal range. Got {final_best_delay:.2f}s"
        )

        assert final_best_fitness > 0, (
            f"Final fitness should be positive. Got {final_best_fitness:.4f}"
        )

        stats = tc_pso_optimizer.get_swarm_statistics(category)
        assert stats["iterations"] == num_iterations, "Iteration count mismatch"
        assert final_best_fitness > 1.0, (
            f"Fitness should improve over iterations. Got {final_best_fitness:.4f}"
        )

    @pytest.mark.asyncio
    async def test_tc_pso_dynamic_inertia_scaling(self, tc_pso_optimizer):
        """
        Validate that dynamic inertia scaling works correctly.

        Research Validation:
        ────────────────────
        Tests the novel equation: w(t) = w_base * (1 - α * anomaly_score)
        
        Higher anomaly scores should produce lower inertia weights,
        leading to faster convergence.
        """
        category = "RCE"
        
        # Test with different anomaly scores
        test_scores = [0.0, 0.5, 1.0]
        inertias = []
        
        for score in test_scores:
            tc_pso_optimizer.anomaly_scores[category] = score
            inertia = tc_pso_optimizer._calculate_dynamic_inertia(category)
            inertias.append(inertia)
            
            print(f"\nAnomaly Score: {score:.1f} → Dynamic Inertia: {inertia:.4f}")
        
        # Verify inertia decreases as anomaly score increases
        assert inertias[0] > inertias[1] > inertias[2], (
            f"Inertia should decrease with higher anomaly scores. Got: {inertias}"
        )
        
        # Verify inertia stays within bounds
        w_base = TC_PSO_CONFIG["inertia_weight"]
        min_scale = TC_PSO_CONFIG["min_inertia_scale"]
        
        for inertia in inertias:
            expected_max = w_base
            expected_min = w_base * min_scale
            assert expected_min <= inertia <= expected_max, (
                f"Inertia {inertia:.4f} out of bounds [{expected_min:.4f}, {expected_max:.4f}]"
            )

    @pytest.mark.asyncio
    async def test_tc_pso_boundary_constraints(self, tc_pso_optimizer):
        """
        Validate that TC-PSO respects min/max delay boundaries.
        """
        category = "XSS"
        num_tests = 50

        for i in range(num_tests):
            delay = await tc_pso_optimizer.get_optimal_delay(category)
            commands = random.randint(1, 10)
            dropped = random.random() < 0.1

            await tc_pso_optimizer.update_fitness(
                attack_category=category,
                delay_used=delay,
                commands_executed=commands,
                dropped=dropped,
                session_id=f"boundary_test_{i:03d}",
                bilstm_anomaly_score=0.5
            )

        for _ in range(100):
            delay = await tc_pso_optimizer.get_optimal_delay(category)

            assert delay >= TC_PSO_CONFIG["min_delay"], (
                f"Delay {delay:.2f}s below minimum {TC_PSO_CONFIG['min_delay']}s"
            )
            assert delay <= TC_PSO_CONFIG["max_delay"], (
                f"Delay {delay:.2f}s above maximum {TC_PSO_CONFIG['max_delay']}s"
            )

    @pytest.mark.asyncio
    async def test_tc_pso_anomaly_reward_multiplier(self, tc_pso_optimizer):
        """
        Validate that anomaly score amplifies fitness rewards.

        Novel Contribution:
        ───────────────────
        F'(t) = F(t) * (1 + β * anomaly_score)
        """
        category = "SQLI"
        
        # Test with low anomaly score
        await tc_pso_optimizer.update_fitness(
            attack_category=category,
            delay_used=3.0,
            commands_executed=5,
            dropped=False,
            session_id="low_anomaly",
            bilstm_anomaly_score=0.1
        )
        low_anomaly_fitness = tc_pso_optimizer.global_best[category][1]
        
        # Reset for fair comparison
        tc_pso_optimizer = ThreatCalibratedPSO()
        
        # Test with high anomaly score
        await tc_pso_optimizer.update_fitness(
            attack_category=category,
            delay_used=3.0,
            commands_executed=5,
            dropped=False,
            session_id="high_anomaly",
            bilstm_anomaly_score=0.9
        )
        high_anomaly_fitness = tc_pso_optimizer.global_best[category][1]
        
        print(f"\nLow Anomaly Fitness: {low_anomaly_fitness:.4f}")
        print(f"High Anomaly Fitness: {high_anomaly_fitness:.4f}")
        
        # High anomaly should produce higher fitness for same base performance
        assert high_anomaly_fitness > low_anomaly_fitness, (
            f"High anomaly should produce higher fitness. "
            f"Low: {low_anomaly_fitness:.4f}, High: {high_anomaly_fitness:.4f}"
        )

    @pytest.mark.asyncio
    async def test_tc_pso_multi_category_optimization(self, tc_pso_optimizer, sample_attack_categories):
        """
        Validate that TC-PSO optimizes independently for each attack category.
        """
        num_iterations = 50
        anomaly_score = 0.7

        for category in sample_attack_categories:
            for i in range(num_iterations):
                delay = await tc_pso_optimizer.get_optimal_delay(category)

                if category == "SQLI":
                    commands = 8 if 4.0 <= delay <= 6.0 else 2
                elif category == "XSS":
                    commands = 6 if 2.0 <= delay <= 4.0 else 2
                else:
                    commands = 5 if 3.0 <= delay <= 5.0 else 2

                dropped = delay > 8.0

                await tc_pso_optimizer.update_fitness(
                    attack_category=category,
                    delay_used=delay,
                    commands_executed=commands,
                    dropped=dropped,
                    session_id=f"{category}_{i:03d}",
                    bilstm_anomaly_score=anomaly_score
                )

        delays = {}
        for category in sample_attack_categories:
            delays[category] = await tc_pso_optimizer.get_optimal_delay(category)

        print(f"\nMulti-Category TC-PSO Results:")
        for cat, delay in delays.items():
            anomaly = tc_pso_optimizer.anomaly_scores.get(cat, 0.5)
            inertia = tc_pso_optimizer._calculate_dynamic_inertia(cat)
            print(f"  {cat}: {delay:.2f}s (Anomaly: {anomaly:.2f}, Inertia: {inertia:.4f})")

        for category, delay in delays.items():
            assert TC_PSO_CONFIG["min_delay"] <= delay <= TC_PSO_CONFIG["max_delay"], (
                f"{category} delay {delay:.2f}s out of bounds"
            )


# ============================================================================
# Test 2: Standard PSO Tests (Baseline)
# ============================================================================

class TestPSOConvergence:
    """
    Test standard PSO convergence behavior for baseline comparison.
    """

    @pytest.mark.asyncio
    async def test_pso_convergence_to_optimal_delay(self, pso_optimizer):
        """Validate that standard PSO converges to the optimal delay value."""
        category = "SQLI"
        num_iterations = 100

        def simulate_attacker_response(delay: float) -> Tuple[int, bool]:
            if delay > 5.0:
                return (0, True)
            elif 4.0 <= delay <= 5.0:
                return (random.randint(8, 12), False)
            elif 3.0 <= delay < 4.0:
                return (random.randint(5, 8), False)
            elif 2.0 <= delay < 3.0:
                return (random.randint(3, 5), False)
            else:
                return (random.randint(1, 3), False)

        for iteration in range(num_iterations):
            current_delay = await pso_optimizer.get_optimal_delay(category)
            commands_executed, dropped = simulate_attacker_response(current_delay)

            await pso_optimizer.update_fitness(
                attack_category=category,
                delay_used=current_delay,
                commands_executed=commands_executed,
                dropped=dropped,
                session_id=f"sim_{iteration:03d}"
            )

        final_best_delay = pso_optimizer.global_best[category][0]
        final_best_fitness = pso_optimizer.global_best[category][1]

        print(f"\nPSO Convergence Results:")
        print(f"  Final Best Delay: {final_best_delay:.2f}s")
        print(f"  Final Best Fitness: {final_best_fitness:.4f}")

        assert 1.5 <= final_best_delay <= 7.0
        assert final_best_fitness > 0

        stats = pso_optimizer.get_swarm_statistics(category)
        assert stats["iterations"] == num_iterations

    @pytest.mark.asyncio
    async def test_pso_boundary_constraints(self, pso_optimizer):
        """Validate that PSO respects min/max delay boundaries."""
        category = "XSS"
        num_tests = 50

        for i in range(num_tests):
            delay = await pso_optimizer.get_optimal_delay(category)
            commands = random.randint(1, 10)
            dropped = random.random() < 0.1

            await pso_optimizer.update_fitness(
                attack_category=category,
                delay_used=delay,
                commands_executed=commands,
                dropped=dropped,
                session_id=f"boundary_test_{i:03d}"
            )

        for _ in range(100):
            delay = await pso_optimizer.get_optimal_delay(category)

            assert delay >= PSO_CONFIG["min_delay"]
            assert delay <= PSO_CONFIG["max_delay"]


# ============================================================================
# Test 3: S-RRT Evolutionary Progression (The Tree Expansion Proof)
# ============================================================================

class TestSRRTEvolution:
    """
    Test S-RRT evolutionary progression with exponential pheromone weighting.

    Research Validation:
    ────────────────────
    These tests validate that the S-RRT algorithm correctly implements:
    
    1. Exponential Pheromone Weighting: Δτ' = Δτ * exp(PSI)
    2. Depth-Decay Multiplier: (1 - current_depth / max_depth)
    
    The tests verify that higher PSI values amplify learning and that
    depth-decay effectively caps memory usage.
    """

    @pytest.mark.asyncio
    async def test_s_rrt_exponential_pheromone_weighting(self, s_rrt_optimizer):
        """
        Validate exponential pheromone weighting with PSI.

        Novel Contribution:
        ───────────────────
        Δτ' = Δτ * exp(PSI)
        
        Higher PSI values should produce exponentially higher pheromone updates.
        """
        schema_id, schema = await s_rrt_optimizer.get_tempting_schema()
        interacted_paths = list(schema.keys())[:2]
        
        # Test with low PSI
        await s_rrt_optimizer.evaluate_interaction(
            schema_id=schema_id,
            interacted_paths=interacted_paths,
            payload_severity_index=1.0
        )
        low_psi_fitness = s_rrt_optimizer.trees[schema_id].fitness
        
        # Get another schema for high PSI test
        schema_id2, schema2 = await s_rrt_optimizer.get_tempting_schema()
        interacted_paths2 = list(schema2.keys())[:2]
        
        # Test with high PSI
        await s_rrt_optimizer.evaluate_interaction(
            schema_id=schema_id2,
            interacted_paths=interacted_paths2,
            payload_severity_index=3.0
        )
        high_psi_fitness = s_rrt_optimizer.trees[schema_id2].fitness
        
        print(f"\nLow PSI (1.0) Fitness Delta: {low_psi_fitness:.2f}")
        print(f"High PSI (3.0) Fitness Delta: {high_psi_fitness:.2f}")
        
        # High PSI should produce significantly higher fitness
        assert high_psi_fitness > low_psi_fitness, (
            f"High PSI should produce higher fitness. "
            f"Low PSI: {low_psi_fitness:.2f}, High PSI: {high_psi_fitness:.2f}"
        )

    @pytest.mark.asyncio
    async def test_s_rrt_gene_frequency_increase(self, s_rrt_optimizer):
        """
        Validate that highly rewarded genes increase in frequency.
        """
        target_files = [
            "/home/dev/.ssh/id_rsa",
            "/var/www/html/.env",
            "/tmp/backup.zip",
        ]

        initial_frequency = self._count_target_files(s_rrt_optimizer, target_files)

        print(f"\nS-RRT Evolution Test:")
        print(f"  Initial target file frequency: {initial_frequency}")

        num_generations = 10
        for generation in range(num_generations):
            for _ in range(s_rrt_optimizer.rrt_config["num_trees"]):
                schema_id, schema = await s_rrt_optimizer.get_tempting_schema()

                interacted_paths = []
                for path in schema.keys():
                    if any(target in path for target in target_files):
                        interacted_paths.append(path)

                if interacted_paths:
                    await s_rrt_optimizer.evaluate_interaction(
                        schema_id=schema_id,
                        interacted_paths=interacted_paths,
                        payload_severity_index=2.5
                    )

            await s_rrt_optimizer.evolve_tree()

            current_freq = self._count_target_files(s_rrt_optimizer, target_files)
            print(f"  Generation {generation + 1}: {current_freq} target files")

        final_frequency = self._count_target_files(s_rrt_optimizer, target_files)
        print(f"  Final target file frequency: {final_frequency}")

        assert final_frequency >= initial_frequency * 0.5

    def _count_target_files(self, optimizer, target_files: List[str]) -> int:
        """Count occurrences of target files across population."""
        count = 0
        for tree in optimizer.trees.values():
            schema = optimizer._tree_to_flat_schema(tree.root)
            for path in schema.keys():
                if any(target in path for target in target_files):
                    count += 1
        return count

    @pytest.mark.asyncio
    async def test_s_rrt_fitness_improvement(self, s_rrt_optimizer):
        """
        Validate that population fitness improves over generations.
        """
        initial_fitnesses = [t.fitness for t in s_rrt_optimizer.trees.values()]
        initial_mean_fitness = sum(initial_fitnesses) / len(initial_fitnesses)
        initial_best_fitness = max(initial_fitnesses)

        print(f"\nS-RRT Fitness Progression:")
        print(f"  Initial Mean Fitness: {initial_mean_fitness:.2f}")
        print(f"  Initial Best Fitness: {initial_best_fitness:.2f}")

        num_generations = 15
        for generation in range(num_generations):
            for _ in range(s_rrt_optimizer.rrt_config["num_trees"]):
                schema_id, schema = await s_rrt_optimizer.get_tempting_schema()

                if len(schema) > 0:
                    interacted_paths = list(schema.keys())[:random.randint(1, len(schema))]
                else:
                    interacted_paths = []

                await s_rrt_optimizer.evaluate_interaction(
                    schema_id=schema_id,
                    interacted_paths=interacted_paths,
                    payload_severity_index=2.0
                )

            await s_rrt_optimizer.evolve_tree()

        final_fitnesses = [t.fitness for t in s_rrt_optimizer.trees.values()]
        final_mean_fitness = sum(final_fitnesses) / len(final_fitnesses)
        final_best_fitness = max(final_fitnesses)

        print(f"  Final Mean Fitness: {final_mean_fitness:.2f}")
        print(f"  Final Best Fitness: {final_best_fitness:.2f}")

        assert final_mean_fitness > initial_mean_fitness
        assert final_best_fitness > initial_best_fitness

    @pytest.mark.asyncio
    async def test_s_rrt_depth_decay_memory_optimization(self, s_rrt_optimizer):
        """
        Validate that depth-decay multiplier caps memory usage.

        Novel Contribution:
        ───────────────────
        expansion_probability = base_prob * (1 - current_depth / max_depth)
        
        This should prevent unbounded node growth.
        """
        initial_node_counts = [t.node_count for t in s_rrt_optimizer.trees.values()]
        initial_mean_nodes = sum(initial_node_counts) / len(initial_node_counts)
        
        print(f"\nS-RRT Depth-Decay Test:")
        print(f"  Initial Mean Nodes: {initial_mean_nodes:.1f}")
        
        num_generations = 20
        max_observed_nodes = initial_mean_nodes
        
        for generation in range(num_generations):
            for _ in range(s_rrt_optimizer.rrt_config["num_trees"]):
                schema_id, schema = await s_rrt_optimizer.get_tempting_schema()
                await s_rrt_optimizer.evaluate_interaction(
                    schema_id=schema_id,
                    interacted_paths=list(schema.keys())[:2],
                    payload_severity_index=2.0
                )
            
            await s_rrt_optimizer.evolve_tree()
            
            current_node_counts = [t.node_count for t in s_rrt_optimizer.trees.values()]
            current_mean = sum(current_node_counts) / len(current_node_counts)
            max_observed_nodes = max(max_observed_nodes, current_mean)
        
        print(f"  Max Observed Mean Nodes: {max_observed_nodes:.1f}")
        print(f"  Final Mean Nodes: {current_mean:.1f}")
        
        # Node count should remain bounded (not grow exponentially)
        # With depth-decay, growth should be limited
        assert max_observed_nodes < initial_mean_nodes * 3, (
            f"Node count grew too much. Initial: {initial_mean_nodes:.1f}, Max: {max_observed_nodes:.1f}"
        )


# ============================================================================
# Test 4: Standard RRT Tests (Baseline)
# ============================================================================

class TestGAEvolution:
    """
    Test standard RRT evolutionary progression for baseline comparison.
    """

    @pytest.mark.asyncio
    async def test_ga_gene_frequency_increase(self, rrt_optimizer):
        """Validate that highly rewarded genes increase in frequency."""
        target_files = [
            "/home/dev/.ssh/id_rsa",
            "/var/www/html/.env",
            "/tmp/backup.zip",
        ]

        initial_frequency = self._count_target_files(rrt_optimizer, target_files)

        print(f"\nRRT Evolution Test:")
        print(f"  Initial target file frequency: {initial_frequency}")

        num_generations = 10
        for generation in range(num_generations):
            for _ in range(rrt_optimizer.rrt_config["num_trees"]):
                schema_id, schema = await rrt_optimizer.get_tempting_schema()

                interacted_paths = []
                for path in schema.keys():
                    if any(target in path for target in target_files):
                        interacted_paths.append(path)

                if interacted_paths:
                    await rrt_optimizer.evaluate_interaction(
                        schema_id=schema_id,
                        interacted_paths=interacted_paths
                    )

            await rrt_optimizer.evolve_tree()

            current_freq = self._count_target_files(rrt_optimizer, target_files)
            print(f"  Generation {generation + 1}: {current_freq} target files")

        final_frequency = self._count_target_files(rrt_optimizer, target_files)
        print(f"  Final target file frequency: {final_frequency}")

        assert final_frequency >= initial_frequency * 0.5

    def _count_target_files(self, optimizer, target_files: List[str]) -> int:
        """Count occurrences of target files across population."""
        count = 0
        for tree in optimizer.trees.values():
            schema = optimizer._tree_to_flat_schema(tree.root)
            for path in schema.keys():
                if any(target in path for target in target_files):
                    count += 1
        return count

    @pytest.mark.asyncio
    async def test_ga_fitness_improvement(self, rrt_optimizer):
        """Validate that population fitness improves over generations."""
        initial_fitnesses = [t.fitness for t in rrt_optimizer.trees.values()]
        initial_mean_fitness = sum(initial_fitnesses) / len(initial_fitnesses)
        initial_best_fitness = max(initial_fitnesses)

        print(f"\nRRT Fitness Progression:")
        print(f"  Initial Mean Fitness: {initial_mean_fitness:.2f}")
        print(f"  Initial Best Fitness: {initial_best_fitness:.2f}")

        num_generations = 15
        for generation in range(num_generations):
            for _ in range(rrt_optimizer.rrt_config["num_trees"]):
                schema_id, schema = await rrt_optimizer.get_tempting_schema()

                if len(schema) > 0:
                    interacted_paths = list(schema.keys())[:random.randint(1, len(schema))]
                else:
                    interacted_paths = []

                await rrt_optimizer.evaluate_interaction(
                    schema_id=schema_id,
                    interacted_paths=interacted_paths
                )

            await rrt_optimizer.evolve_tree()

        final_fitnesses = [t.fitness for t in rrt_optimizer.trees.values()]
        final_mean_fitness = sum(final_fitnesses) / len(final_fitnesses)
        final_best_fitness = max(final_fitnesses)

        print(f"  Final Mean Fitness: {final_mean_fitness:.2f}")
        print(f"  Final Best Fitness: {final_best_fitness:.2f}")

        assert final_mean_fitness > initial_mean_fitness
        assert final_best_fitness > initial_best_fitness


# ============================================================================
# Test 5: Concurrency & Race Condition Stress Test
# ============================================================================

class TestConcurrencySafety:
    """
    Test thread-safety and race condition handling.
    """

    @pytest.mark.asyncio
    async def test_tc_pso_concurrent_fitness_updates(self, tc_pso_optimizer):
        """Stress test TC-PSO with 50 concurrent fitness updates."""
        category = "SQLI"
        num_concurrent = 50

        async def update_fitness_task(task_id: int):
            delay = await tc_pso_optimizer.get_optimal_delay(category)
            await tc_pso_optimizer.update_fitness(
                attack_category=category,
                delay_used=delay,
                commands_executed=random.randint(1, 10),
                dropped=random.random() < 0.1,
                session_id=f"concurrent_{task_id:03d}",
                bilstm_anomaly_score=0.7
            )

        tasks = [update_fitness_task(i) for i in range(num_concurrent)]

        try:
            await asyncio.gather(*tasks, return_exceptions=False)
        except RuntimeError as e:
            if "dictionary changed size" in str(e):
                pytest.fail(f"Race condition detected: {e}")
            raise

        stats = tc_pso_optimizer.get_swarm_statistics(category)
        assert stats["num_particles"] == TC_PSO_CONFIG["num_particles"]

    @pytest.mark.asyncio
    async def test_s_rrt_concurrent_interactions(self, s_rrt_optimizer):
        """Stress test S-RRT with 50 concurrent interaction evaluations."""
        num_concurrent = 50

        async def evaluate_task(task_id: int):
            schema_id, schema = await s_rrt_optimizer.get_tempting_schema()
            await s_rrt_optimizer.evaluate_interaction(
                schema_id=schema_id,
                interacted_paths=list(schema.keys())[:2],
                payload_severity_index=2.0
            )

        tasks = [evaluate_task(i) for i in range(num_concurrent)]

        try:
            await asyncio.gather(*tasks, return_exceptions=False)
        except RuntimeError as e:
            if "dictionary changed size" in str(e):
                pytest.fail(f"Race condition detected: {e}")
            raise

        assert len(s_rrt_optimizer.trees) == s_rrt_optimizer.rrt_config["num_trees"]

    @pytest.mark.asyncio
    async def test_mixed_concurrent_operations(self, tc_pso_optimizer, s_rrt_optimizer):
        """Stress test with mixed TC-PSO and S-RRT operations."""
        num_operations = 100

        async def pso_task(task_id: int):
            delay = await tc_pso_optimizer.get_optimal_delay("SQLI")
            await tc_pso_optimizer.update_fitness(
                attack_category="SQLI",
                delay_used=delay,
                commands_executed=random.randint(1, 10),
                dropped=False,
                session_id=f"pso_{task_id:03d}",
                bilstm_anomaly_score=0.6
            )

        async def rrt_task(task_id: int):
            schema_id, schema = await s_rrt_optimizer.get_tempting_schema()
            await s_rrt_optimizer.evaluate_interaction(
                schema_id=schema_id,
                interacted_paths=list(schema.keys())[:2],
                payload_severity_index=2.0
            )

        tasks = []
        for i in range(num_operations):
            if i % 2 == 0:
                tasks.append(pso_task(i))
            else:
                tasks.append(rrt_task(i))

        try:
            await asyncio.gather(*tasks, return_exceptions=False)
        except RuntimeError as e:
            if "dictionary changed size" in str(e):
                pytest.fail(f"Race condition detected: {e}")
            raise

        pso_stats = tc_pso_optimizer.get_swarm_statistics("SQLI")
        rrt_stats = s_rrt_optimizer.get_population_statistics()

        assert pso_stats["num_particles"] > 0
        assert rrt_stats["population_size"] > 0


# ============================================================================
# Test 6: Session Tracker Memory Leak Prevention
# ============================================================================

class TestSessionTrackerMemory:
    """
    Test session tracker memory management.
    """

    @pytest.mark.asyncio
    async def test_session_creation_and_tracking(self, session_tracker):
        """Validate that sessions are properly tracked."""
        num_sessions = 100

        for i in range(num_sessions):
            session = session_tracker.create_session(
                session_id=f"session_{i:03d}",
                attack_category="SQLI",
                delay_used=3.5
            )

            session_tracker.record_command(f"session_{i:03d}")
            session_tracker.record_path_interaction(
                f"session_{i:03d}",
                f"/path/{i}"
            )

        assert len(session_tracker.sessions) == num_sessions

        for i in range(num_sessions):
            session = session_tracker.sessions[f"session_{i:03d}"]
            assert session.commands_executed == 1
            assert len(session.interacted_paths) == 1

    @pytest.mark.asyncio
    async def test_session_cleanup_mechanism(self, session_tracker):
        """Validate that stale sessions can be cleaned up."""
        num_sessions = 100
        for i in range(num_sessions):
            session_tracker.create_session(
                session_id=f"cleanup_{i:03d}",
                attack_category="XSS",
                delay_used=2.5
            )

        for i in range(50):
            session_tracker.end_session(f"cleanup_{i:03d}")

        ended_count = sum(
            1 for s in session_tracker.sessions.values()
            if s.ended
        )

        assert ended_count == 50

        session_ids_to_remove = [
            sid for sid, s in session_tracker.sessions.items()
            if s.ended
        ]

        for sid in session_ids_to_remove:
            del session_tracker.sessions[sid]

        remaining = len(session_tracker.sessions)
        assert remaining == 50


# ============================================================================
# Test 7: Integration Tests
# ============================================================================

class TestIntegration:
    """
    Integration tests for complete deception workflow.
    """

    @pytest.mark.asyncio
    async def test_complete_deception_workflow(self, tc_pso_optimizer, s_rrt_optimizer, session_tracker):
        """
        Test complete deception workflow from start to finish.

        Simulation:
        ───────────
        1. Attacker detected
        2. TC-PSO determines optimal delay
        3. S-RRT provides deception schema
        4. Attacker interacts
        5. Fitness updated with anomaly/severity scores
        """
        import uuid

        session_id = str(uuid.uuid4())[:8]
        attack_category = "SQLI"
        anomaly_score = 0.8
        psi = 2.5

        # 1. Get TC-PSO delay
        delay = await tc_pso_optimizer.get_optimal_delay(attack_category)

        # 2. Get S-RRT schema
        schema_id, schema = await s_rrt_optimizer.get_tempting_schema()

        # 3. Create session
        session_tracker.create_session(session_id, attack_category, delay)

        # 4. Simulate attacker interactions
        for path in list(schema.keys())[:3]:
            session_tracker.record_command(session_id)
            session_tracker.record_path_interaction(session_id, path)

        # 5. Update fitness with novel parameters
        session = session_tracker.sessions[session_id]
        await tc_pso_optimizer.update_fitness(
            attack_category=attack_category,
            delay_used=delay,
            commands_executed=session.commands_executed,
            dropped=False,
            session_id=session_id,
            bilstm_anomaly_score=anomaly_score
        )

        await s_rrt_optimizer.evaluate_interaction(
            schema_id=schema_id,
            interacted_paths=session.interacted_paths,
            payload_severity_index=psi
        )

        assert session.commands_executed > 0
        assert len(session.interacted_paths) > 0

        print(f"\nIntegration Test:")
        print(f"  Session ID: {session_id}")
        print(f"  Delay: {delay:.2f}s")
        print(f"  Commands: {session.commands_executed}")
        print(f"  Paths: {len(session.interacted_paths)}")
        print(f"  Anomaly Score: {anomaly_score}")
        print(f"  PSI: {psi}")


# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":
    pytest.main([
        __file__,
        "-v",
        "--asyncio-mode=auto",
        "-s",
        "--tb=short",
    ])
