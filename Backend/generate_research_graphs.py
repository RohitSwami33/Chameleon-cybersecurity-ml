"""
Research Graph Generator for Chameleon Meta-Heuristics
=======================================================
Generates high-quality matplotlib visualizations for the research paper:
1. PSO Convergence Graph - Shows adaptive tarpitting delay optimization
2. GA Evolution Graph - Shows deception schema filesystem evolution

Author: Chameleon Research Team
Date: March 2026
"""

import asyncio
import random
import math
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from meta_heuristics import AdaptiveTarpitPSO, DeceptionEvolutionGA, PSO_CONFIG

# Check for matplotlib
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend for server environments
    import matplotlib.pyplot as plt
    import seaborn as sns
except ImportError:
    print("❌ matplotlib or seaborn not installed.")
    print("Run: pip install matplotlib seaborn")
    sys.exit(1)

# Set high-quality plot styling
sns.set_style("whitegrid")
sns.set_context("paper", font_scale=1.2)

# Color palette for research paper
COLORS = {
    'primary': '#2E86AB',      # Blue
    'secondary': '#A23B72',    # Magenta
    'accent': '#F18F01',       # Orange
    'success': '#2ECC71',      # Green
    'dark': '#2C3E50',         # Dark blue-gray
}


# ============================================================================
# PSO Convergence Simulation
# ============================================================================

def simulate_pso_convergence(num_iterations: int = 100, optimal_delay: float = 4.5) -> tuple:
    """
    Simulate PSO convergence for adaptive tarpitting.
    
    Mathematically models the convergence behavior where delays around ~4.5s
    yield the best fitness (highest command execution, no drop penalty).
    
    The fitness function is modeled as:
    F(t) = w1 * commands_executed - w2 * drop_penalty
    
    Where commands_executed is maximized at optimal_delay and drops off
    exponentially as delay moves away from optimal.
    
    Args:
        num_iterations: Number of PSO iterations to simulate
        optimal_delay: The theoretically optimal delay (seconds)
    
    Returns:
        tuple: (iterations, global_best_history, swarm_mean_history, std_history)
    """
    random.seed(42)  # Reproducibility for research paper
    
    # Initialize particles
    num_particles = PSO_CONFIG["num_particles"]
    min_delay = PSO_CONFIG["min_delay"]
    max_delay = PSO_CONFIG["max_delay"]
    
    particles = []
    for _ in range(num_particles):
        position = random.uniform(min_delay, max_delay)
        velocity = random.uniform(-1.0, 1.0)
        particles.append({
            'position': position,
            'velocity': velocity,
            'best_position': position,
            'best_fitness': float('-inf')
        })
    
    # Global best
    g_best_position = random.uniform(min_delay, max_delay)
    g_best_fitness = float('-inf')
    
    # Tracking
    global_best_history = []
    swarm_mean_history = []
    std_history = []
    
    # PSO hyperparameters
    w = PSO_CONFIG["inertia_weight"]
    c1 = PSO_CONFIG["cognitive_coefficient"]
    c2 = PSO_CONFIG["social_coefficient"]
    
    def fitness_function(delay: float) -> float:
        """
        Simulated fitness function for tarpitting delay.
        
        Models attacker behavior:
        - Too short (< 2s): Attacker moves too fast, less engagement
        - Optimal (~4.5s): Maximum engagement, attacker doesn't suspect honeypot
        - Too long (> 8s): Attacker gets frustrated and disconnects
        """
        # Gaussian-like fitness centered at optimal_delay
        sigma = 1.5  # Spread of the fitness curve
        
        # Base fitness (bell curve around optimal)
        base_fitness = 10 * math.exp(-((delay - optimal_delay) ** 2) / (2 * sigma ** 2))
        
        # Asymmetric penalty for too-long delays (attackers more likely to drop)
        if delay > optimal_delay:
            drop_penalty = 0.5 * (delay - optimal_delay) ** 1.5
        else:
            drop_penalty = 0.1 * (optimal_delay - delay)
        
        # Command execution bonus (peaks at optimal)
        cmd_bonus = 5 * math.exp(-abs(delay - optimal_delay) / 2)
        
        return base_fitness + cmd_bonus - drop_penalty
    
    for iteration in range(num_iterations):
        # Update each particle
        for particle in particles:
            # Calculate fitness
            fitness = fitness_function(particle['position'])
            
            # Update personal best
            if fitness > particle['best_fitness']:
                particle['best_fitness'] = fitness
                particle['best_position'] = particle['position']
            
            # Update global best
            if fitness > g_best_fitness:
                g_best_fitness = fitness
                g_best_position = particle['position']
        
        # Record history
        global_best_history.append(g_best_position)
        positions = [p['position'] for p in particles]
        swarm_mean_history.append(sum(positions) / len(positions))
        
        variance = sum((x - sum(positions)/len(positions))**2 for x in positions) / len(positions)
        std_history.append(math.sqrt(variance))
        
        # Update velocities and positions
        for particle in particles:
            r1, r2 = random.random(), random.random()
            
            cognitive = c1 * r1 * (particle['best_position'] - particle['position'])
            social = c2 * r2 * (g_best_position - particle['position'])
            
            particle['velocity'] = w * particle['velocity'] + cognitive + social
            
            # Clamp velocity
            max_v = (max_delay - min_delay) * 0.3
            particle['velocity'] = max(-max_v, min(max_v, particle['velocity']))
            
            # Update position
            particle['position'] += particle['velocity']
            
            # Clamp to bounds
            particle['position'] = max(min_delay, min(particle['position'], max_delay))
        
        # Adaptive inertia weight (linearly decreasing)
        w = 0.9 - (iteration / num_iterations) * 0.5
    
    return (
        list(range(num_iterations)),
        global_best_history,
        swarm_mean_history,
        std_history
    )


def plot_pso_convergence(output_path: str = "pso_convergence_graph.png"):
    """
    Generate and save the PSO convergence graph.
    
    Shows the swarm's global best position converging to the optimal delay.
    """
    print("🔵 Generating PSO Convergence Graph...")
    
    # Run simulation
    iterations, g_best_history, swarm_mean, std_dev = simulate_pso_convergence(
        num_iterations=100,
        optimal_delay=4.5
    )
    
    # Create figure with high DPI for publication
    fig, ax = plt.subplots(figsize=(12, 7), dpi=150)
    
    # Plot global best convergence
    ax.plot(iterations, g_best_history, 
            color=COLORS['primary'], linewidth=2.5, 
            label='Global Best Delay', marker='o', 
            markersize=3, markevery=5, alpha=0.8)
    
    # Plot swarm mean
    ax.plot(iterations, swarm_mean, 
            color=COLORS['secondary'], linewidth=2, 
            label='Swarm Mean', linestyle='--', alpha=0.7)
    
    # Plot standard deviation as shaded area
    lower_bound = [max(0.5, m - s) for m, s in zip(swarm_mean, std_dev)]
    upper_bound = [min(12.0, m + s) for m, s in zip(swarm_mean, std_dev)]
    ax.fill_between(iterations, lower_bound, upper_bound, 
                    color=COLORS['secondary'], alpha=0.15, 
                    label='Swarm Std. Deviation')
    
    # Optimal delay reference line
    ax.axhline(y=4.5, color=COLORS['success'], linewidth=2, 
               linestyle='-.', alpha=0.8, label='Optimal Delay (4.5s)')
    
    # Labels and title
    ax.set_xlabel('Iterations', fontsize=14, fontweight='bold')
    ax.set_ylabel('Optimal Delay (Seconds)', fontsize=14, fontweight='bold')
    ax.set_title('PSO Convergence: Adaptive Tarpitting Delay Optimization\n'
                 'Particle Swarm Optimization for Honeypot Engagement Maximization',
                 fontsize=14, fontweight='bold', pad=15)
    
    # Legend
    ax.legend(loc='upper right', fontsize=11, framealpha=0.9)
    
    # Grid
    ax.grid(True, linestyle='--', alpha=0.6)
    
    # Set axis limits
    ax.set_xlim(0, 100)
    ax.set_ylim(0.5, 12)
    
    # Add convergence annotation
    ax.annotate('Convergence Zone',
                xy=(70, 4.5), xytext=(50, 8),
                arrowprops=dict(arrowstyle='->', color=COLORS['dark'], 
                               lw=2, alpha=0.7),
                fontsize=11, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                         edgecolor=COLORS['dark'], alpha=0.8))
    
    # Add initial randomness annotation
    ax.annotate('Random Initialization',
                xy=(5, g_best_history[5]), xytext=(15, 10),
                arrowprops=dict(arrowstyle='->', color=COLORS['dark'], 
                               lw=2, alpha=0.7),
                fontsize=11, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                         edgecolor=COLORS['dark'], alpha=0.8))
    
    # Tight layout
    plt.tight_layout()
    
    # Save with high quality
    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    
    print(f"   ✅ Saved: {output_path}")
    print(f"   📊 Final converged delay: {g_best_history[-1]:.3f}s")
    
    return g_best_history[-1]


# ============================================================================
# GA Filesystem Evolution Simulation
# ============================================================================

def simulate_ga_evolution(num_generations: int = 15, 
                          target_file: str = "/var/www/html/.env") -> tuple:
    """
    Simulate GA evolution for deception schema filesystem.
    
    Models attacker interactions that highly reward a specific fake file (.env).
    The frequency of this file should increase across generations.
    
    Args:
        num_generations: Number of GA generations to simulate
        target_file: The target file path to track
    
    Returns:
        tuple: (generations, frequency_history, avg_fitness_history)
    """
    random.seed(42)  # Reproducibility for research paper
    
    population_size = 20
    elitism_count = 3
    
    # Initialize population with random schemas
    # Each schema is a set of file paths
    all_possible_files = [
        "/etc/passwd",
        "/etc/shadow",
        "/var/www/html/config.php",
        "/var/www/html/.env",  # Target file - highly rewarded
        "/var/www/html/backup.sql",
        "/home/admin/.ssh/id_rsa",
        "/home/admin/.bash_history",
        "/tmp/api_keys.json",
        "/root/.my.cnf",
        "/var/log/auth.log",
        "/tmp/backup.zip",
        "/home/dev/.aws/credentials",
        "/var/www/html/wp-config.php.bak",
        "/etc/mysql/debian.cnf",
        "/root/.bashrc",
    ]
    
    # Initialize population (each individual has 4-8 random files)
    population = []
    for _ in range(population_size):
        num_files = random.randint(4, 8)
        files = set(random.sample(all_possible_files, num_files))
        population.append(files)
    
    # Tracking
    generations = list(range(1, num_generations + 1))
    frequency_history = []
    avg_fitness_history = []
    
    def fitness(schema: set) -> float:
        """
        Fitness function that rewards the target file.
        
        Attackers are highly attracted to .env files containing credentials.
        """
        base_fitness = len(schema) * 0.5  # Base fitness for schema size
        
        # High reward for target file
        if target_file in schema:
            base_fitness += 15.0  # Strong selection pressure
        
        # Bonus for other sensitive files
        sensitive_files = [".env", "id_rsa", "credentials", "password", "secret", "backup"]
        for f in schema:
            if any(s in f.lower() for s in sensitive_files) and f != target_file:
                base_fitness += 2.0
        
        return base_fitness
    
    def tournament_selection(pop, k=3):
        """Tournament selection."""
        tournament = random.sample(pop, min(k, len(pop)))
        return max(tournament, key=fitness)
    
    def crossover(parent1, parent2):
        """Uniform crossover."""
        child = set()
        all_files = parent1 | parent2
        
        for f in all_files:
            if f in parent1 and f in parent2:
                child.add(f)
            elif f in parent1:
                if random.random() < 0.5:
                    child.add(f)
            else:
                if random.random() < 0.5:
                    child.add(f)
        
        # Ensure minimum size
        while len(child) < 3:
            child.add(random.choice(all_possible_files))
        
        return child
    
    def mutate(schema):
        """Mutation operator."""
        mutated = schema.copy()
        
        if random.random() < 0.3:  # Add file
            available = [f for f in all_possible_files if f not in mutated]
            if available:
                mutated.add(random.choice(available))
        elif len(mutated) > 3 and random.random() < 0.3:  # Remove file
            to_remove = random.choice(list(mutated))
            if to_remove != target_file:  # Don't remove target easily
                mutated.remove(to_remove)
        
        return mutated
    
    for gen in range(num_generations):
        # Calculate target file frequency
        count_with_target = sum(1 for schema in population if target_file in schema)
        frequency = (count_with_target / population_size) * 100
        frequency_history.append(frequency)
        
        # Calculate average fitness
        avg_fit = sum(fitness(s) for s in population) / population_size
        avg_fitness_history.append(avg_fit)
        
        # Sort by fitness
        sorted_pop = sorted(population, key=fitness, reverse=True)
        
        # Elitism
        new_population = sorted_pop[:elitism_count].copy()
        
        # Generate offspring
        while len(new_population) < population_size:
            parent1 = tournament_selection(sorted_pop)
            parent2 = tournament_selection(sorted_pop)
            
            child = crossover(parent1, parent2)
            
            if random.random() < 0.15:  # Mutation rate
                child = mutate(child)
            
            new_population.append(child)
        
        population = new_population
    
    return generations, frequency_history, avg_fitness_history


def plot_ga_evolution(output_path: str = "ga_evolution_graph.png"):
    """
    Generate and save the GA evolution graph.
    
    Shows the frequency of the target file (.env) increasing across generations.
    """
    print("🟢 Generating GA Evolution Graph...")
    
    # Run simulation
    generations, frequency_history, avg_fitness = simulate_ga_evolution(
        num_generations=15,
        target_file="/var/www/html/.env"
    )
    
    # Create figure with high DPI
    fig, ax1 = plt.subplots(figsize=(12, 7), dpi=150)
    
    # Primary axis: File frequency
    bars = ax1.bar(generations, frequency_history,
                   color=COLORS['primary'], alpha=0.7,
                   label='Target File Frequency', edgecolor=COLORS['dark'], linewidth=1.5)
    
    ax1.set_xlabel('Generation', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Frequency of Target File (%)', 
                   fontsize=14, fontweight='bold', color=COLORS['primary'])
    ax1.tick_params(axis='y', labelcolor=COLORS['primary'])
    ax1.set_ylim(0, 105)
    
    # Secondary axis: Average fitness
    ax2 = ax1.twinx()
    line = ax2.plot(generations, avg_fitness,
                    color=COLORS['accent'], linewidth=3,
                    marker='s', markersize=8,
                    label='Avg. Population Fitness', alpha=0.8)
    
    ax2.set_ylabel('Average Fitness', 
                   fontsize=14, fontweight='bold', color=COLORS['accent'])
    ax2.tick_params(axis='y', labelcolor=COLORS['accent'])
    
    # Title
    fig.suptitle('GA Evolution: Deception Schema Filesystem Optimization\n'
                 'Genetic Algorithm for Attacker Engagement Maximization',
                 fontsize=14, fontweight='bold', y=1.02)
    
    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2,
               loc='lower right', fontsize=11, framealpha=0.9)
    
    # Grid
    ax1.grid(True, linestyle='--', alpha=0.6, axis='y')
    
    # Add annotations
    # Initial frequency
    ax1.annotate(f'{frequency_history[0]:.0f}%',
                 xy=(generations[0], frequency_history[0]),
                 xytext=(generations[0] - 0.5, frequency_history[0] + 15),
                 fontsize=11, fontweight='bold',
                 arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=2),
                 bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                          edgecolor=COLORS['dark'], alpha=0.8))
    
    # Final frequency
    ax1.annotate(f'{frequency_history[-1]:.0f}%',
                 xy=(generations[-1], frequency_history[-1]),
                 xytext=(generations[-1] - 2, frequency_history[-1] - 20),
                 fontsize=11, fontweight='bold',
                 arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=2),
                 bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                          edgecolor=COLORS['dark'], alpha=0.8))
    
    # Evolution arrow
    ax1.annotate('Selection Pressure →',
                 xy=(7, 50), xytext=(3, 70),
                 fontsize=10, fontweight='bold', color=COLORS['secondary'],
                 arrowprops=dict(arrowstyle='->', color=COLORS['secondary'], 
                                lw=2, alpha=0.7))
    
    # Tight layout
    plt.tight_layout()
    
    # Save with high quality
    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    
    print(f"   ✅ Saved: {output_path}")
    print(f"   📊 Final frequency: {frequency_history[-1]:.1f}%")
    
    return frequency_history[-1]


# ============================================================================
# Main Execution
# ============================================================================

def main():
    """Generate all research graphs."""
    print("=" * 60)
    print("Chameleon Research Graph Generator")
    print("=" * 60)
    print()
    
    # Get output directory (root of project)
    output_dir = os.path.join(os.path.dirname(__file__), "..")
    
    # Generate PSO graph
    pso_output = os.path.join(output_dir, "pso_convergence_graph.png")
    final_delay = plot_pso_convergence(pso_output)
    
    print()
    
    # Generate GA graph
    ga_output = os.path.join(output_dir, "ga_evolution_graph.png")
    final_freq = plot_ga_evolution(ga_output)
    
    print()
    print("=" * 60)
    print("✅ All graphs generated successfully!")
    print("=" * 60)
    print()
    print("Output files:")
    print(f"   1. {pso_output}")
    print(f"      - Shows PSO converging to ~{final_delay:.2f}s optimal delay")
    print()
    print(f"   2. {ga_output}")
    print(f"      - Shows target file reaching {final_freq:.1f}% frequency")
    print()
    print("These graphs demonstrate:")
    print("   • PSO adapts tarpitting delays to maximize attacker engagement")
    print("   • GA evolves filesystem schemas that attract attacker interaction")
    print("=" * 60)


if __name__ == "__main__":
    main()
