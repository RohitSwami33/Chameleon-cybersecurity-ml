import sys
import os
sys.path.append(os.path.abspath('/Users/rohit/Documents/Sem-4_project/Chameleon-cybersecurity-ml/Backend'))

from src.ml_engine.ml_classifier import classifier

text = "LOGIN:SELECT * FROM users WHERE '1'='1'"
print("Heuristic fallback:", classifier.heuristic_fallback(text))
print("Full classify:", classifier.classify(text))
