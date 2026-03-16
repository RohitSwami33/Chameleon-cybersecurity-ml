# Compatibility shim — real source in src.utils.alert_manager
# This file preserves backward compatibility for all existing imports
from src.utils.alert_manager import *  # noqa: F401,F403
try:
    from src.utils.alert_manager import __all__
except ImportError:
    pass
