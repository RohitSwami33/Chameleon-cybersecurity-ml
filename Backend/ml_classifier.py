# Compatibility shim — real source in src.ml_engine.ml_classifier
# This file preserves backward compatibility for all existing imports
from src.ml_engine.ml_classifier import *  # noqa: F401,F403
try:
    from src.ml_engine.ml_classifier import __all__
except ImportError:
    pass
