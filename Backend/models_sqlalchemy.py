# Compatibility shim — real source in src.core.models_sqlalchemy
# This file preserves backward compatibility for all existing imports
from src.core.models_sqlalchemy import *  # noqa: F401,F403
try:
    from src.core.models_sqlalchemy import __all__
except ImportError:
    pass
