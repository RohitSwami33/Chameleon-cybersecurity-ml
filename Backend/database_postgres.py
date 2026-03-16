# Compatibility shim — real source in src.core.database_postgres
# This file preserves backward compatibility for all existing imports
from src.core.database_postgres import *  # noqa: F401,F403
try:
    from src.core.database_postgres import __all__
except ImportError:
    pass
