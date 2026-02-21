#!/usr/bin/env python3
"""
Quick Test Training Script
==========================

Tests LSTM training with reduced parameters for verification.
"""

import os
import sys
import json
import hashlib
import pickle
import warnings
from datetime import datetime
from pathlib import Path

warnings.filterwarnings('ignore')

BASE_DIR = Path("/Users/rohit/Documents/Sem-4_project/Chameleon-cybersecurity-ml")
FINAL_DATASET = BASE_DIR / "final_dataset.csv"
OUTPUT_DIR = BASE_DIR / "Backend"
MODEL_OUTPUT = OUTPUT_DIR / "chameleon_lstm_model.pt"
TOKENIZER_OUTPUT = OUTPUT_DIR / "tokenizer.pkl"

MAX_WORDS = 5000
MAX_SEQUENCE_LENGTH = 100
EMBEDDING_DIM = 64
HIDDEN_DIM = 128
NUM_LAYERS = 2
DROPOUT = 0.3
BATCH_SIZE = 32
EPOCHS = 3
LEARNING_RATE = 0.001
SAMPLE_SIZE = 5000

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset, WeightedRandomSampler

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.utils.class_weight import compute_class_weight

from simple_tokenizer import SimpleTokenizer, pad_sequences

print("=" * 70)
print(" CHAMELEON LSTM TRAINING (QUICK TEST)")
print("=" * 70)

class AttackDataset(Dataset):
    def __init__(self, sequences, labels):
        self.sequences = torch.tensor(sequences, dtype=torch.long)
        self.labels = torch.tensor(labels, dtype=torch.float32)
    
    def __len__(self):
        return len(self.sequences)
    
    def __getitem__(self, idx):
        return self.sequences[idx], self.labels[idx]


class ChameleonLSTM(nn.Module):
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


def main():
    start_time = datetime.now()
    
    print("\n[1] Loading Dataset...")
    df = pd.read_csv(FINAL_DATASET)
    
    if len(df) > SAMPLE_SIZE:
        df = df.sample(n=SAMPLE_SIZE, random_state=42).reset_index(drop=True)
    
    print(f"   Loaded: {len(df)} rows")
    print(f"   Benign: {len(df[df['label'] == 0])}")
    print(f"   Malicious: {len(df[df['label'] == 1])}")
    
    print("\n[2] Setting up Device...")
    if torch.backends.mps.is_available():
        device = torch.device("mps")
        print(f"   Using M4 GPU (MPS)")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
        print(f"   Using CUDA GPU")
    else:
        device = torch.device("cpu")
        print(f"   Using CPU")
    
    print("\n[3] Tokenizing...")
    X = df['command_sequence'].astype(str).values
    y = df['label'].values
    
    tokenizer = SimpleTokenizer(num_words=MAX_WORDS, lower=True, oov_token='<OOV>')
    tokenizer.fit_on_texts(X)
    
    sequences = tokenizer.texts_to_sequences(X)
    X_padded = np.array(pad_sequences(sequences, maxlen=MAX_SEQUENCE_LENGTH, padding='post', truncating='post'))
    
    print(f"   Vocabulary: {len(tokenizer.word_index)} words")
    print(f"   Sequence length: {MAX_SEQUENCE_LENGTH}")
    
    print("\n[4] Splitting Data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X_padded, y, test_size=0.2, random_state=42, stratify=y
    )
    
    train_dataset = AttackDataset(X_train, y_train)
    test_dataset = AttackDataset(X_test, y_test)
    
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)
    
    print(f"   Train: {len(X_train)}, Test: {len(X_test)}")
    
    print("\n[5] Creating Model...")
    model = ChameleonLSTM(
        vocab_size=MAX_WORDS,
        embedding_dim=EMBEDDING_DIM,
        hidden_dim=HIDDEN_DIM,
        num_layers=NUM_LAYERS,
        dropout=DROPOUT
    ).to(device)
    
    total_params = sum(p.numel() for p in model.parameters())
    print(f"   Parameters: {total_params:,}")
    
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    
    print(f"\n[6] Training ({EPOCHS} epochs)...")
    print("-" * 50)
    
    for epoch in range(EPOCHS):
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0
        
        for batch_idx, (sequences, labels) in enumerate(train_loader):
            sequences = sequences.to(device)
            labels = labels.to(device).unsqueeze(1)
            
            optimizer.zero_grad()
            outputs = model(sequences)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            predictions = (outputs >= 0.5).float()
            train_correct += (predictions == labels).sum().item()
            train_total += labels.size(0)
        
        train_acc = train_correct / train_total
        print(f"   Epoch {epoch+1}/{EPOCHS} | Loss: {train_loss/len(train_loader):.4f} | Acc: {train_acc:.4f}")
    
    print("\n[7] Evaluating...")
    model.eval()
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for sequences, labels in test_loader:
            sequences = sequences.to(device)
            outputs = model(sequences)
            predictions = (outputs >= 0.5).float().cpu().numpy()
            all_preds.extend(predictions.flatten())
            all_labels.extend(labels.numpy())
    
    accuracy = accuracy_score(all_labels, all_preds)
    print(f"   Test Accuracy: {accuracy:.4f}")
    
    print("\n[Classification Report]")
    print(classification_report(all_labels, all_preds, target_names=['Benign', 'Malicious']))
    
    print("\n[8] Saving Model...")
    torch.save({
        'model_state_dict': model.state_dict(),
        'vocab_size': MAX_WORDS,
        'embedding_dim': EMBEDDING_DIM,
        'hidden_dim': HIDDEN_DIM,
    }, MODEL_OUTPUT)
    
    tokenizer.save(TOKENIZER_OUTPUT)
    
    print(f"   Model: {MODEL_OUTPUT}")
    print(f"   Tokenizer: {TOKENIZER_OUTPUT}")
    
    duration = datetime.now() - start_time
    print("\n" + "=" * 70)
    print(f" TRAINING COMPLETE in {duration}")
    print(f" Final Accuracy: {accuracy:.4f}")
    print("=" * 70)


if __name__ == "__main__":
    main()
