# Compatibility shim — real source in src.utils.chatbot_service
# This file preserves backward compatibility for all existing imports
from src.utils.chatbot_service import *  # noqa: F401,F403
try:
    from src.utils.chatbot_service import __all__
except ImportError:
    pass
