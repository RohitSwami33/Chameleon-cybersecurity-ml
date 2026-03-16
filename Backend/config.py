# Compatibility shim — real source in src.core.config
# This file preserves backward compatibility for all existing imports
from src.core.config import *  # noqa: F401,F403
try:
    from src.core.config import __all__
except ImportError:
    pass
