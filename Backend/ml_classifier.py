try:
    import tensorflow as tf
except ImportError:
    tf = None  # TensorFlow not available (e.g. Python 3.14) — heuristic mode only
import numpy as np
import re
from config import settings, MODEL_PATH
from models import AttackType, ClassificationResult
import os

class MLClassifier:
    def __init__(self):
        self.model = None
        self.char_to_idx = {}
        self.idx_to_class = {
            0: AttackType.BENIGN,
            1: AttackType.SQLI,
            2: AttackType.XSS,
            3: AttackType.SSI
        }
        
        try:
            if tf is not None and os.path.exists(MODEL_PATH):
                # Register custom objects before loading
                custom_objects = {
                    'custom_standardization': lambda x: x,  # Placeholder
                    'char_split': lambda x: x  # Placeholder
                }
                self.model = tf.keras.models.load_model(
                    MODEL_PATH,
                    custom_objects=custom_objects,
                    compile=False  # Skip compilation to avoid issues
                )
                print(f"✅ Loaded ML model from {MODEL_PATH}")
            else:
                print(f"⚠️  Model file not found at {MODEL_PATH}")
                print(f"⚠️  Using heuristic-based classification only")
        except Exception as e:
            print(f"⚠️  Error loading ML model: {e}")
            print(f"⚠️  Falling back to heuristic-based classification")
            self.model = None
            
        self.build_char_mapping()

    def build_char_mapping(self):
        # Printable ASCII characters
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
        self.char_to_idx = {char: idx + 1 for idx, char in enumerate(chars)}
        # 0 is reserved for padding

    def encode_input(self, text: str) -> np.ndarray:
        text = str(text)
        encoded = [self.char_to_idx.get(c, 0) for c in text]
        encoded = encoded[:settings.MAX_INPUT_LENGTH]
        # Pad with zeros
        if len(encoded) < settings.MAX_INPUT_LENGTH:
            encoded += [0] * (settings.MAX_INPUT_LENGTH - len(encoded))
        return np.array([encoded])

    def heuristic_fallback(self, text: str) -> tuple[AttackType, float]:
        text_lower = text.lower()
        
        # SSI patterns - Check first as they're more specific
        ssi_patterns = [
            r"<!--#exec", r"<!--#include", r"<!--#echo", r"<!--#config",
            r"<!--#set", r"<!--#printenv", r"<!--#flastmod", r"<!--#fsize"
        ]
        for pattern in ssi_patterns:
            if re.search(pattern, text_lower):
                return AttackType.SSI, 0.88

        # XSS patterns - Check before SQLi as they can have similar chars
        xss_patterns = [
            r"<script>", r"javascript:", r"onerror=", r"onload=", 
            r"<iframe>", r"document\.cookie", r"alert\("
        ]
        for pattern in xss_patterns:
            if re.search(pattern, text_lower):
                return AttackType.XSS, 0.90

        # SQLi patterns
        sqli_patterns = [
            r"union\s+select", r"or\s+1=1", r"--", r"drop\s+table", 
            r"insert\s+into", r"update\s+set", r"admin'\s*--", r"'\s*or\s*'"
        ]
        for pattern in sqli_patterns:
            if re.search(pattern, text_lower):
                return AttackType.SQLI, 0.85

        # OS Command Injection / Destructive Commands
        os_patterns = [
            r"rm\s+-rf", r"wget\s+http", r"curl\s+http", r"cat\s+/etc/passwd",
            r"nc\s+-e", r"bash\s+-i", r"chmod\s+\+x"
        ]
        for pattern in os_patterns:
            if re.search(pattern, text_lower):
                # We categorize RCE under a high-severity bucket. We can map it to SQLI or SSI for now.
                return AttackType.SSI, 0.95

        # Brute Force (heuristic: short text with common keywords that look like password attempts)
        # Exclude patterns that are just usernames or normal login identifiers
        bf_keywords = ["password", "123456", "admin", "root"]
        # Only classify as brute force if it looks like a password attempt (contains numbers or is very short with password keyword)
        if len(text) < 15 and any(keyword in text_lower for keyword in bf_keywords):
            # Additional check: should look like a password attempt, not just a username
            if any(c.isdigit() for c in text) or "password" in text_lower:
                return AttackType.BRUTE_FORCE, 0.75

        return AttackType.BENIGN, 0.0

    def classify(self, text: str) -> ClassificationResult:
        attack_type = AttackType.BENIGN
        confidence = 0.0
        is_malicious = False

        # Disable ML model prediction on Render due to dtype issues
        # Use heuristic-based detection which works reliably
        # TODO: Fix ML model compatibility with TensorFlow 2.16.1
        
        # Use heuristic detection
        heuristic_type, heuristic_conf = self.heuristic_fallback(text)
        if heuristic_type != AttackType.BENIGN:
            attack_type = heuristic_type
            confidence = heuristic_conf

        is_malicious = attack_type != AttackType.BENIGN
        
        return ClassificationResult(
            attack_type=attack_type,
            confidence=confidence,
            is_malicious=is_malicious
        )

classifier = MLClassifier()
