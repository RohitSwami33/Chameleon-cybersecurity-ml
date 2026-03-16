# Compatibility shim — real source in src.utils.deception_engine
# This file preserves backward compatibility for all existing imports
from src.utils.deception_engine import *  # noqa: F401,F403
try:
    from src.utils.deception_engine import __all__
except ImportError:
    pass
