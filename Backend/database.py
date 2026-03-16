# Compatibility shim — real source in src.core.database
# This file preserves backward compatibility for all existing imports
from src.core.database import *  # noqa: F401,F403
try:
    from src.core.database import __all__
except ImportError:
    pass
