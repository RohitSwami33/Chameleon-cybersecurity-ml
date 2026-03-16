# Compatibility shim — real source in src.api.pipeline
# This file preserves backward compatibility for all existing imports
from src.api.pipeline import *  # noqa: F401,F403
try:
    from src.api.pipeline import __all__
except ImportError:
    pass
