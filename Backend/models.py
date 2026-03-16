# Compatibility shim — real source in src.core.models
# This file preserves backward compatibility for all existing imports
from src.core.models import *  # noqa: F401,F403
try:
    from src.core.models import __all__
except ImportError:
    pass
