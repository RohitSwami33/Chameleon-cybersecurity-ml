# Compatibility shim — real source in src.optimization.meta_heuristics
# This file preserves backward compatibility for all existing imports
from src.optimization.meta_heuristics import *  # noqa: F401,F403
try:
    from src.optimization.meta_heuristics import __all__
except ImportError:
    pass
