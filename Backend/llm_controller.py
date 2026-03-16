# Compatibility shim — real source in src.utils.llm_controller
# This file preserves backward compatibility for all existing imports
from src.utils.llm_controller import *  # noqa: F401,F403
try:
    from src.utils.llm_controller import __all__
except ImportError:
    pass
