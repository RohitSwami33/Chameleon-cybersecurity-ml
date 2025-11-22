import tensorflow as tf
import numpy as np
import re
from config import settings
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
            if os.path.exists(settings.MODEL_PATH):
                self.model = tf.keras.models.load_model(settings.MODEL_PATH)
                print(f"Loaded model from {settings.MODEL_PATH}")
            else:
                print(f"Model file not found at {settings.MODEL_PATH}. Using heuristic fallback only.")
        except Exception as e:
            print(f"Error loading model: {e}")
            
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

        # Brute Force (heuristic: short text with common keywords)
        bf_keywords = ["admin", "password", "login", "root", "123456"]
        if len(text) < 20 and any(keyword in text_lower for keyword in bf_keywords):
            return AttackType.BRUTE_FORCE, 0.75

        return AttackType.BENIGN, 0.0

    def classify(self, text: str) -> ClassificationResult:
        attack_type = AttackType.BENIGN
        confidence = 0.0
        is_malicious = False

        # Try model prediction first
        if self.model:
            try:
                encoded_input = self.encode_input(text)
                prediction = self.model.predict(encoded_input, verbose=0)[0]
                class_idx = np.argmax(prediction)
                confidence = float(prediction[class_idx])
                
                if confidence >= settings.CONFIDENCE_THRESHOLD:
                    attack_type = self.idx_to_class.get(class_idx, AttackType.BENIGN)
            except Exception as e:
                print(f"Prediction error: {e}")

        # Fallback if confidence is low or model failed
        if confidence < settings.CONFIDENCE_THRESHOLD:
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
