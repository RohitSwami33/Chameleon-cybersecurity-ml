import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ml_engine.ml_classifier import classifier

text = "LOGIN:SELECT * FROM users WHERE '1'='1'"
print("Heuristic fallback:", classifier.heuristic_fallback(text))
print("Full classify:", classifier.classify(text))
