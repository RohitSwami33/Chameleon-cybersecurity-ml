# Compatibility shim — real source in src.utils.report_generator
# This file preserves backward compatibility for all existing imports
from src.utils.report_generator import *  # noqa: F401,F403
try:
    from src.utils.report_generator import __all__
except ImportError:
    pass
