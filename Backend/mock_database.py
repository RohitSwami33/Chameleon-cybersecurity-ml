# Compatibility shim — real source in src.utils.mock_database
# This file preserves backward compatibility for all existing imports
from src.utils.mock_database import *  # noqa: F401,F403
try:
    from src.utils.mock_database import __all__
except ImportError:
    pass
