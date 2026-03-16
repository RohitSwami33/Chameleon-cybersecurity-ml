# Compatibility shim — real source in src.utils.attacker_session
# This file preserves backward compatibility for all existing imports
from src.utils.attacker_session import *  # noqa: F401,F403
try:
    from src.utils.attacker_session import __all__
except ImportError:
    pass
