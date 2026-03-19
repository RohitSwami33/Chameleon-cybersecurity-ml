import random
import logging

logger = logging.getLogger(__name__)

class BiLSTMModel:
    """
    Mock/Stub class for the Bi-directional LSTM model.
    In a real scenario, this would load weights from PyTorch or TensorFlow/Keras.
    """
    def __init__(self):
        self._initialized = True
        logger.info("BiLSTM stub initialized.")

    def predict(self, command: str) -> float:
        """
        Returns an anomaly score between 0.0 and 1.0.
        Higher score indicates a higher likelihood of an anomaly/attack.
        """
        # For the stub, we'll return a score based on some basic keywords, 
        # or a random relatively high score to simulate suspicion for testing.
        command_lower = command.lower()
        if any(kw in command_lower for kw in ["select", "union", "script", "cat", "etc/passwd"]):
            score = random.uniform(0.7, 0.99)
        else:
            score = random.uniform(0.01, 0.4)
            
        logger.debug(f"[BiLSTM] Command: '{command}' => Anomaly Score: {score:.4f}")
        return score

bilstm_model = BiLSTMModel()
