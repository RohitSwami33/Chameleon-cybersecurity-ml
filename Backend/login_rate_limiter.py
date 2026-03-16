# Compatibility shim — real source in src.utils.login_rate_limiter
# This file preserves backward compatibility for all existing imports
from src.utils.login_rate_limiter import *  # noqa: F401,F403
try:
    from src.utils.login_rate_limiter import __all__
except ImportError:
    pass
