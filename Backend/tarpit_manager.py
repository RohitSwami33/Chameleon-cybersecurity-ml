# Compatibility shim — real source in src.utils.tarpit_manager
# This file preserves backward compatibility for all existing imports
from src.utils.tarpit_manager import *  # noqa: F401,F403
try:
    from src.utils.tarpit_manager import __all__
except ImportError:
    pass
