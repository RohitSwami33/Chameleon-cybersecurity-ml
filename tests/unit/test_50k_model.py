#!/usr/bin/env python3
"""
Chameleon LSTM Model Testing Script
====================================

Loads the trained LSTM model and evaluates on test set.
Also provides single command classification.

Usage:
    python test_50k_model.py evaluate
    python test_50k_model.py classify "whoami"
    python test_50k_model.py classify "cat /etc/passwd"
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_recall_fscore_support

import torch
import torch.nn as nn
from simple_tokenizer import SimpleTokenizer, pad_sequences

MODEL_PATH = Path(__file__).parent / "chameleon_lstm_model.pt"
TOKENIZER_PATH = Path(__file__).parent / "tokenizer.pkl"
DATASET_PATH = Path(__file__).parent.parent / "custom_attack_data_6k.csv"

MAX_SEQUENCE_LENGTH = 150


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


def load_model_and_tokenizer(device='cpu'):
    """Load trained model and tokenizer."""
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
    if not TOKENIZER_PATH.exists():
        raise FileNotFoundError(f"Tokenizer not found at {TOKENIZER_PATH}")
    
    tokenizer = SimpleTokenizer.load(str(TOKENIZER_PATH))
    
    checkpoint = torch.load(MODEL_PATH, map_location=device, weights_only=False)
    vocab_size = checkpoint.get('vocab_size', 10000)
    embedding_dim = checkpoint.get('embedding_dim', 128)
    hidden_dim = checkpoint.get('hidden_dim', 256)
    num_layers = checkpoint.get('num_layers', 2)
    
    model = ChameleonLSTM(
        vocab_size=vocab_size,
        embedding_dim=embedding_dim,
        hidden_dim=hidden_dim,
        num_layers=num_layers
    )
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    model.eval()
    
    return model, tokenizer


def preprocess_command(command, tokenizer, max_len=MAX_SEQUENCE_LENGTH):
    """Tokenize and pad a single command."""
    sequence = tokenizer.texts_to_sequences([command])
    padded = pad_sequences(sequence, maxlen=max_len, padding='post', truncating='post')
    return torch.tensor(padded, dtype=torch.long)


def classify_command(model, tokenizer, command, device='cpu'):
    """Classify a single command."""
    model.eval()
    with torch.no_grad():
        input_tensor = preprocess_command(command, tokenizer).to(device)
        output = model(input_tensor)
        prob = output.item()
        label = 1 if prob >= 0.5 else 0
        return label, prob


def evaluate_on_test_set(model, tokenizer, device='cpu', test_size=0.15):
    """Evaluate model on the test split of the dataset."""
    print("Loading dataset...")
    df = pd.read_csv(DATASET_PATH)
    df = df.drop_duplicates(subset=['command_sequence'])
    df = df[df['command_sequence'].str.len() > 3]
    
    X = df['command_sequence'].astype(str).values
    y = df['label'].values
    
    from sklearn.model_selection import train_test_split
    _, X_test, _, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=y
    )
    
    print(f"Test set size: {len(X_test)}")
    
    # Tokenize
    sequences = tokenizer.texts_to_sequences(X_test)
    X_padded = np.array(pad_sequences(sequences, maxlen=MAX_SEQUENCE_LENGTH, padding='post', truncating='post'))
    
    # Convert to tensor
    X_tensor = torch.tensor(X_padded, dtype=torch.long).to(device)
    y_tensor = torch.tensor(y_test, dtype=torch.float32).unsqueeze(1).to(device)
    
    # Predict
    model.eval()
    all_predictions = []
    all_probs = []
    
    batch_size = 64
    with torch.no_grad():
        for i in range(0, len(X_tensor), batch_size):
            batch = X_tensor[i:i+batch_size]
            outputs = model(batch)
            probs = outputs.cpu().numpy().flatten()
            predictions = (outputs >= 0.5).float().cpu().numpy().flatten()
            all_predictions.extend(predictions)
            all_probs.extend(probs)
    
    all_predictions = np.array(all_predictions)
    
    accuracy = accuracy_score(y_test, all_predictions)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, all_predictions, average='binary')
    
    print("\n" + "=" * 70)
    print(" EVALUATION RESULTS")
    print("=" * 70)
    print(f" Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f" Precision: {precision:.4f}")
    print(f" Recall:    {recall:.4f}")
    print(f" F1-Score:  {f1:.4f}")
    
    cm = confusion_matrix(y_test, all_predictions)
    print(f"\n Confusion Matrix:")
    print(f" TN: {cm[0][0]:>6}  FP: {cm[0][1]:>6}")
    print(f" FN: {cm[1][0]:>6}  TP: {cm[1][1]:>6}")
    
    print(f"\n Classification Report:")
    print(classification_report(y_test, all_predictions, target_names=['Benign', 'Malicious']))
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'confusion_matrix': cm.tolist()
    }


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    # Setup device
    if torch.backends.mps.is_available():
        device = torch.device("mps")
        print("Using M4 GPU (Metal Performance Shaders)")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
        print("Using CUDA GPU")
    else:
        device = torch.device("cpu")
        print("Using CPU")
    
    try:
        model, tokenizer = load_model_and_tokenizer(device)
        print(f"Loaded model and tokenizer")
    except Exception as e:
        print(f"Error loading model/tokenizer: {e}")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "evaluate":
        evaluate_on_test_set(model, tokenizer, device)
    
    elif command == "classify":
        if len(sys.argv) < 3:
            print("Please provide a command to classify")
            sys.exit(1)
        cmd = sys.argv[2]
        label, prob = classify_command(model, tokenizer, cmd, device)
        print(f"\nCommand: {cmd}")
        print(f"Prediction: {'MALICIOUS' if label == 1 else 'BENIGN'} (probability: {prob:.4f})")
    
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()