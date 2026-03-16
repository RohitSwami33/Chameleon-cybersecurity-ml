# Compatibility shim — real source in src.utils.integrity
# This file preserves backward compatibility for all existing imports
from src.utils.integrity import *  # noqa: F401,F403
try:
    from src.utils.integrity import __all__
except ImportError:
    pass
