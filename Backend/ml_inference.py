"""
Chameleon ML Inference Module
==============================

Singleton ChameleonPredictor that loads the trained 50k BiLSTM model
and character-level tokenizer for high-speed async inference.

Device priority: Apple MPS (Metal) → CUDA → CPU

Usage:
    from ml_inference import ChameleonPredictor

    predictor = ChameleonPredictor()
    score = await predictor.predict("cat /etc/passwd")
    # score ≈ 0.97 (malicious)
"""

import json
import logging
import threading
from pathlib import Path
from typing import List

import torch
import torch.nn as nn

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths (relative to this file's directory)
# ---------------------------------------------------------------------------
_BASE_DIR = Path(__file__).parent
_MODEL_PATH = _BASE_DIR / "chameleon_lstm_m4_50k.pth"
_TOKENIZER_PATH = _BASE_DIR / "tokenizer_50k.json"

# ---------------------------------------------------------------------------
# Hyperparameters (must match training exactly)
# ---------------------------------------------------------------------------
MAX_SEQUENCE_LENGTH = 120
EMBEDDING_DIM = 64
HIDDEN_DIM = 128
NUM_LAYERS = 2
DROPOUT = 0.3


# ============================================================
# Character-Level Tokenizer
# ============================================================

class ChameleonTokenizer:
    """
    Character-level tokenizer for shell command sequences.

    Mirrors the CharTokenizer used during training so that inference
    produces identical integer encodings for the same input strings.

    Index 0 is reserved for padding.  The last index is <UNK>.
    """

    def __init__(self, filepath: Path = _TOKENIZER_PATH):
        with open(filepath, "r") as f:
            data = json.load(f)

        self.characters: List[str] = data["characters"]
        self.char_to_idx: dict = {k: v for k, v in data["char_to_idx"].items()}
        self.idx_to_char: dict = {int(k): v for k, v in data["idx_to_char"].items()}
        self.vocab_size: int = data["vocab_size"]
        self.pad_token: int = data["pad_token"]          # 0
        self.unk_token: int = data["unk_token"]
        self.max_len: int = data.get("max_sequence_length", MAX_SEQUENCE_LENGTH)

    def encode(self, text: str, max_len: int | None = None) -> List[int]:
        """Convert a raw string to a padded list of character indices."""
        max_len = max_len or self.max_len
        sequence: List[int] = []
        for ch in text[:max_len]:
            sequence.append(self.char_to_idx.get(ch, self.unk_token))

        # Right-pad to fixed length
        if len(sequence) < max_len:
            sequence.extend([self.pad_token] * (max_len - len(sequence)))

        return sequence


# ============================================================
# BiLSTM Model Definition (exact training architecture)
# ============================================================

class ChameleonLSTM(nn.Module):
    """
    Bidirectional LSTM for binary attack classification.

    Architecture (matches training checkpoint):
        Embedding(vocab, 64, pad=0)
        → Bi-LSTM(64→128, 2 layers, dropout=0.3)
        → Dropout(0.3)
        → Linear(256→1)
        → Sigmoid
    """

    def __init__(
        self,
        vocab_size: int,
        embedding_dim: int = EMBEDDING_DIM,
        hidden_dim: int = HIDDEN_DIM,
        num_layers: int = NUM_LAYERS,
        dropout: float = DROPOUT,
    ):
        super().__init__()

        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)

        self.lstm = nn.LSTM(
            input_size=embedding_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0,
        )

        self.dropout = nn.Dropout(dropout)
        # Bidirectional → hidden_dim * 2
        self.fc = nn.Linear(hidden_dim * 2, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        embedded = self.embedding(x)
        _, (hidden, _) = self.lstm(embedded)
        # Concat final forward (hidden[-2]) and backward (hidden[-1]) states
        hidden_concat = torch.cat((hidden[-2], hidden[-1]), dim=1)
        dropped = self.dropout(hidden_concat)
        out = self.fc(dropped)
        return self.sigmoid(out)


# ============================================================
# Singleton Predictor
# ============================================================

class ChameleonPredictor:
    """
    Thread-safe singleton that loads the BiLSTM model once and
    provides a fast ``predict()`` coroutine for the FastAPI layer.

    Instantiate anywhere — only the first call actually loads
    weights to the accelerator.

    Example::

        predictor = ChameleonPredictor()
        score = await predictor.predict("whoami")   # ≈ 0.02
        score = await predictor.predict("rm -rf /") # ≈ 0.98
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls) -> "ChameleonPredictor":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    instance._initialised = False
                    cls._instance = instance
        return cls._instance

    def __init__(self) -> None:
        if self._initialised:
            return
        self._initialised = True

        logger.info("ChameleonPredictor: loading model and tokenizer …")

        # ---- Device selection ------------------------------------------------
        if torch.backends.mps.is_available():
            self.device = torch.device("mps")
            logger.info("  → Using Apple MPS (Metal Performance Shaders)")
        elif torch.cuda.is_available():
            self.device = torch.device("cuda")
            logger.info(f"  → Using CUDA: {torch.cuda.get_device_name(0)}")
        else:
            self.device = torch.device("cpu")
            logger.info("  → Using CPU (no GPU detected)")

        # ---- Tokenizer -------------------------------------------------------
        self.tokenizer = ChameleonTokenizer(_TOKENIZER_PATH)

        # ---- Model -----------------------------------------------------------
        checkpoint = torch.load(
            _MODEL_PATH,
            map_location=self.device,
            weights_only=False,
        )

        self.model = ChameleonLSTM(
            vocab_size=checkpoint.get("tokenizer_vocab_size", self.tokenizer.vocab_size),
            embedding_dim=checkpoint.get("embedding_dim", EMBEDDING_DIM),
            hidden_dim=checkpoint.get("hidden_dim", HIDDEN_DIM),
            num_layers=checkpoint.get("num_layers", NUM_LAYERS),
            dropout=checkpoint.get("dropout", DROPOUT),
        )
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.to(self.device)
        self.model.eval()  # permanent eval mode — no training here

        total_params = sum(p.numel() for p in self.model.parameters())
        logger.info(
            f"  → Model loaded: {total_params:,} params on {self.device}"
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def predict(self, command: str) -> float:
        """
        Score a raw shell command for maliciousness.

        Args:
            command: Raw shell command string.

        Returns:
            Float in [0.0, 1.0] — probability that the command is
            malicious.  Values above 0.85 are high-confidence attacks.
        """
        encoded = self.tokenizer.encode(command)
        tensor = torch.tensor([encoded], dtype=torch.long, device=self.device)

        with torch.no_grad():
            output = self.model(tensor)

        return float(output.item())
