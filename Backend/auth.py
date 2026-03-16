# Compatibility shim — real source in src.api.auth
# This file preserves backward compatibility for all existing imports
from src.api.auth import *  # noqa: F401,F403
try:
    from src.api.auth import __all__
except ImportError:
    pass
