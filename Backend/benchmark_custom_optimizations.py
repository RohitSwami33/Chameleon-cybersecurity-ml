# Compatibility shim — real source in src.optimization.benchmark_custom_optimizations
# This file preserves backward compatibility for all existing imports
from src.optimization.benchmark_custom_optimizations import *  # noqa: F401,F403
try:
    from src.optimization.benchmark_custom_optimizations import __all__
except ImportError:
    pass
