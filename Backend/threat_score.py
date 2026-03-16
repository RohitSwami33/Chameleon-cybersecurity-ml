# Compatibility shim — real source in src.utils.threat_score
# This file preserves backward compatibility for all existing imports
from src.utils.threat_score import *  # noqa: F401,F403
try:
    from src.utils.threat_score import __all__
except ImportError:
    pass
