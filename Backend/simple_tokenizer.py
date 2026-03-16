# Compatibility shim — real source in src.ml_engine.simple_tokenizer
# This file preserves backward compatibility for all existing imports
from src.ml_engine.simple_tokenizer import *  # noqa: F401,F403
try:
    from src.ml_engine.simple_tokenizer import __all__
except ImportError:
    pass
