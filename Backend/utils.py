# Compatibility shim — real source in src.utils.utils
# This file preserves backward compatibility for all existing imports
from src.utils.utils import *  # noqa: F401,F403
try:
    from src.utils.utils import __all__
except ImportError:
    pass
