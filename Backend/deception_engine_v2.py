# Compatibility shim — real source in src.utils.deception_engine_v2
# This file preserves backward compatibility for all existing imports
from src.utils.deception_engine_v2 import *  # noqa: F401,F403
try:
    from src.utils.deception_engine_v2 import __all__
except ImportError:
    pass
