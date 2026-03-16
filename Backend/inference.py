# Compatibility shim — real source in src.ml_engine.inference
# This file preserves backward compatibility for all existing imports
from src.ml_engine.inference import *  # noqa: F401,F403
try:
    from src.ml_engine.inference import __all__
except ImportError:
    pass
