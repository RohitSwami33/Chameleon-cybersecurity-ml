import logging
import threading
import asyncio
from typing import Optional
from pathlib import Path

try:
    from mlx_lm import load, generate
except ImportError:
    load, generate = None, None

logger = logging.getLogger(__name__)

# Absolute path to the model relative to Backend
# Using the newly trained balanced model (retrained on 2930 balanced samples)
MODEL_DIR = Path(__file__).parent / "chamaeleon-4bit-balanced"

class LocalMLXModel:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(LocalMLXModel, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self.model = None
        self.tokenizer = None
        self._async_lock = None
        
        if load is None:
            logger.error("mlx_lm could not be imported. MLX local inference is disabled. Make sure `mlx-lm` is installed.")
            self._initialized = True
            return

        try:
            model_path = str(MODEL_DIR)
            if not MODEL_DIR.exists():
                logger.warning(f"Model path {MODEL_DIR} not found.")
            
            logger.info(f"Loading MLX local model from {model_path}")
            self.model, self.tokenizer = load(model_path)
            logger.info("MLX local model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load MLX model: {e}")
            
        self._initialized = True

    async def infer(self, command: str) -> str:
        """
        Runs inference on the command.
        Returns 'BLOCK' if malicious, 'ALLOW' otherwise.
        """
        if not self.model or not self.tokenizer:
            logger.error("MLX model is not loaded. Defaulting to ALLOW.")
            return "ALLOW"
            
        if self._async_lock is None:
            self._async_lock = asyncio.Lock()

        # Strictly formatted prompt based on training
        prompt = f"COMMAND: {command}\nVERDICT: "
        
        try:
            # Enforce sequential GPU scheduling via Asyncio Lock to prevent Metal IOGPU crashes
            async with self._async_lock:
                # Setting max_tokens=10 because it should output a single word verdict.
                response = await asyncio.to_thread(
                    generate,
                    self.model,
                    self.tokenizer,
                    prompt=prompt,
                    max_tokens=10,
                    verbose=False
                )
            
            output = response.strip().upper()
            if "BLOCK" in output:
                return "BLOCK"
            elif "ALLOW" in output:
                return "ALLOW"
            elif output.startswith("BLOCK"):
                return "BLOCK"
            elif output.startswith("ALLOW"):
                return "ALLOW"
            else:
                # Failsafe default
                return "ALLOW"
                
        except Exception as e:
            logger.error(f"Error during MLX inference: {e}")
            return "ALLOW"

# Ensure singleton instance is exported
mlx_model = LocalMLXModel()
