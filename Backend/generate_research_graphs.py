# Compatibility shim — real source in src.optimization.generate_research_graphs
# This file preserves backward compatibility for all existing imports
from src.optimization.generate_research_graphs import *  # noqa: F401,F403
try:
    from src.optimization.generate_research_graphs import __all__
except ImportError:
    pass
