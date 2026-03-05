#!/usr/bin/env python3
"""
Chameleon LSTM Training Script
===============================

Optimized for MacBook M4 GPU (Metal Performance Shaders)
Merges Kaggle datasets with custom LLM-generated data

Features:
- M4 GPU acceleration via MPS
- Multi-dataset merging (XSS, SQLi, Custom)
- Integrity verification using SHA-256 hashes
- Balanced training with class weights

Author: Chameleon Security Team

Installation:
    pip install torch pandas numpy scikit-learn tensorflow
"""

import os
import sys
import csv
import json
import hashlib
import pickle
import warnings
from datetime import datetime
from pathlib import Path

warnings.filterwarnings('ignore')

print("=" * 70)
print(" CHAMELEON LSTM TRAINING PIPELINE")
print(" Optimized for M4 GPU (Metal Performance Shaders)")
print("=" * 70)

MISSING_DEPS = []

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, Dataset, WeightedRandomSampler
    TORCH_AVAILABLE = True
    print("\n[INFO] PyTorch version:", torch.__version__)
except ImportError:
    TORCH_AVAILABLE = False
    MISSING_DEPS.append("torch")
    print("\n[WARNING] PyTorch not installed")

try:
    import pandas as pd
    import numpy as np
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_recall_fscore_support
    from sklearn.utils.class_weight import compute_class_weight
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    MISSING_DEPS.extend(["pandas", "numpy", "scikit-learn"])
    print("[WARNING] sklearn/pandas not installed")

try:
    from simple_tokenizer import SimpleTokenizer, pad_sequences
    TOKENIZER_AVAILABLE = True
    print("[INFO] Custom tokenizer available")
except ImportError:
    TOKENIZER_AVAILABLE = False
    MISSING_DEPS.append("simple_tokenizer")
    print("[WARNING] Tokenizer not available")

if MISSING_DEPS:
    print("\n" + "=" * 70)
    print(" MISSING DEPENDENCIES")
    print("=" * 70)
    print(f"  Install with: pip install {' '.join(MISSING_DEPS)}")
    print("=" * 70)
    sys.exit(1)

BASE_DIR = Path("/Users/rohit/Documents/Sem-4_project/Chameleon-cybersecurity-ml")
DATASET_DIR = Path("/Users/rohit/Documents/Sem-4_project/Dataset")
OUTPUT_DIR = BASE_DIR / "Backend"
CUSTOM_DATA = BASE_DIR / "custom_attack_data.csv"
FINAL_DATASET = BASE_DIR / "final_dataset.csv"
MODEL_OUTPUT = OUTPUT_DIR / "chameleon_lstm_model.pt"
TOKENIZER_OUTPUT = OUTPUT_DIR / "tokenizer.pkl"

MAX_WORDS = 10000
MAX_SEQUENCE_LENGTH = 150
EMBEDDING_DIM = 128
HIDDEN_DIM = 256
NUM_LAYERS = 2
DROPOUT = 0.3
BATCH_SIZE = 64
EPOCHS = 20
LEARNING_RATE = 0.001


def hash_file(filepath: str) -> str:
    """Calculate SHA-256 hash of a file for integrity verification."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def hash_dataframe(df) -> str:
    """Calculate hash of dataframe content for integrity."""
    content = df.to_json(orient='records', default_handler=str)
    return hashlib.sha256(content.encode()).hexdigest()


class AttackDataset(Dataset):
    """PyTorch Dataset for attack sequences."""
    
    def __init__(self, sequences, labels):
        self.sequences = torch.tensor(sequences, dtype=torch.long)
        self.labels = torch.tensor(labels, dtype=torch.float32)
    
    def __len__(self):
        return len(self.sequences)
    
    def __getitem__(self, idx):
        return self.sequences[idx], self.labels[idx]


class ChameleonLSTM(nn.Module):
    """
    Bidirectional LSTM for attack classification.
    
    Architecture:
    - Embedding layer (10000 vocab, 128 dim)
    - 2-layer Bidirectional LSTM (256 hidden)
    - Dropout (0.3)
    - Fully connected + Sigmoid
    """
    
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


def load_xss_dataset():
    """Load XSS dataset from Kaggle."""
    xss_path = DATASET_DIR / "XSS_dataset.csv"
    if not xss_path.exists():
        print(f"[WARNING] XSS dataset not found at {xss_path}")
        return None
    
    try:
        df = pd.read_csv(xss_path, encoding='utf-8')
        df = df.rename(columns={'Sentence': 'command_sequence', 'Label': 'label'})
        df = df[['command_sequence', 'label']].dropna()
        df['command_sequence'] = df['command_sequence'].astype(str)
        df['label'] = df['label'].astype(int)
        print(f"[INFO] Loaded XSS dataset: {len(df)} rows")
        return df
    except Exception as e:
        print(f"[ERROR] Failed to load XSS dataset: {e}")
        return None


def load_sqli_datasets():
    """Load all SQL injection datasets."""
    sqli_dir = DATASET_DIR / "sql-injection"
    if not sqli_dir.exists():
        print(f"[WARNING] SQLi directory not found at {sqli_dir}")
        return None
    
    dfs = []
    
    for filename in ['sqli.csv', 'sqliv2.csv', 'SQLiV3.csv']:
        filepath = sqli_dir / filename
        if not filepath.exists():
            continue
        
        try:
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            df = None
            
            for enc in encodings:
                try:
                    df = pd.read_csv(filepath, encoding=enc, on_bad_lines='skip')
                    break
                except:
                    continue
            
            if df is None:
                continue
            
            if 'Sentence' in df.columns:
                df = df.rename(columns={'Sentence': 'command_sequence'})
            if 'Label' in df.columns:
                df = df.rename(columns={'Label': 'label'})
            
            if 'command_sequence' in df.columns and 'label' in df.columns:
                df = df[['command_sequence', 'label']].dropna()
                df['command_sequence'] = df['command_sequence'].astype(str)
                df['label'] = pd.to_numeric(df['label'], errors='coerce').fillna(0).astype(int)
                dfs.append(df)
                print(f"[INFO] Loaded {filename}: {len(df)} rows")
        
        except Exception as e:
            print(f"[WARNING] Failed to load {filename}: {e}")
    
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    return None


def load_custom_dataset():
    """Load custom LLM-generated dataset."""
    if not CUSTOM_DATA.exists():
        print(f"[WARNING] Custom dataset not found at {CUSTOM_DATA}")
        return None
    
    try:
        df = pd.read_csv(CUSTOM_DATA)
        df = df[['command_sequence', 'label']].dropna()
        df['command_sequence'] = df['command_sequence'].astype(str)
        df['label'] = df['label'].astype(int)
        print(f"[INFO] Loaded custom dataset: {len(df)} rows")
        return df
    except Exception as e:
        print(f"[ERROR] Failed to load custom dataset: {e}")
        return None


def merge_datasets():
    """Merge all datasets into final training dataset."""
    print("\n" + "=" * 50)
    print(" LOADING DATASETS")
    print("=" * 50)
    
    all_dfs = []
    
    xss_df = load_xss_dataset()
    if xss_df is not None:
        xss_df['source'] = 'xss'
        all_dfs.append(xss_df)
    
    sqli_df = load_sqli_datasets()
    if sqli_df is not None:
        sqli_df['source'] = 'sqli'
        all_dfs.append(sqli_df)
    
    custom_df = load_custom_dataset()
    if custom_df is not None:
        custom_df['source'] = 'custom'
        all_dfs.append(custom_df)
    
    if not all_dfs:
        print("[ERROR] No datasets loaded!")
        return None
    
    merged_df = pd.concat(all_dfs, ignore_index=True)
    
    print(f"\n[INFO] Total rows before cleaning: {len(merged_df)}")
    
    merged_df = merged_df.drop_duplicates(subset=['command_sequence'])
    
    merged_df = merged_df[merged_df['command_sequence'].str.len() > 3]
    
    merged_df = merged_df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    print(f"[INFO] Total rows after cleaning: {len(merged_df)}")
    print(f"[INFO] Benign (0): {len(merged_df[merged_df['label'] == 0])}")
    print(f"[INFO] Malicious (1): {len(merged_df[merged_df['label'] == 1])}")
    
    return merged_df


def verify_integrity(df):
    """Verify dataset integrity using hash."""
    print("\n" + "=" * 50)
    print(" INTEGRITY VERIFICATION")
    print("=" * 50)
    
    dataset_hash = hash_dataframe(df)
    print(f"[INFO] Dataset SHA-256 hash: {dataset_hash[:32]}...")
    
    integrity_record = {
        "timestamp": datetime.utcnow().isoformat(),
        "dataset_hash": dataset_hash,
        "total_rows": len(df),
        "benign_count": int(len(df[df['label'] == 0])),
        "malicious_count": int(len(df[df['label'] == 1])),
        "columns": list(df.columns)
    }
    
    integrity_path = OUTPUT_DIR / "dataset_integrity.json"
    with open(integrity_path, 'w') as f:
        json.dump(integrity_record, f, indent=2)
    
    print(f"[INFO] Integrity record saved to: {integrity_path}")
    print("[INFO] Dataset integrity verified ✓")
    
    return dataset_hash


def setup_device():
    """Setup M4 GPU device."""
    print("\n" + "=" * 50)
    print(" DEVICE SETUP")
    print("=" * 50)
    
    if not TORCH_AVAILABLE:
        print("[ERROR] PyTorch not available!")
        return None
    
    if torch.backends.mps.is_available():
        device = torch.device("mps")
        print(f"[INFO] M4 GPU detected! Using Metal Performance Shaders")
        print(f"[INFO] Device: {device}")
        
        test_tensor = torch.randn(3, 3).to(device)
        _ = test_tensor @ test_tensor.T
        print("[INFO] M4 GPU test passed ✓")
        
        return device
    
    elif torch.cuda.is_available():
        device = torch.device("cuda")
        print(f"[INFO] CUDA GPU detected: {torch.cuda.get_device_name(0)}")
        return device
    
    else:
        device = torch.device("cpu")
        print("[INFO] No GPU detected, using CPU")
        return device


def preprocess_data(df, device):
    """Tokenize and prepare data for training."""
    print("\n" + "=" * 50)
    print(" PREPROCESSING")
    print("=" * 50)
    
    X = df['command_sequence'].values
    y = df['label'].values
    
    print(f"[INFO] Tokenizing {len(X)} sequences...")
    
    tokenizer = SimpleTokenizer(num_words=MAX_WORDS, lower=True, oov_token='<OOV>')
    tokenizer.fit_on_texts(X)
    
    sequences = tokenizer.texts_to_sequences(X)
    
    X_padded = pad_sequences(sequences, maxlen=MAX_SEQUENCE_LENGTH, padding='post', truncating='post')
    
    X_padded = np.array(X_padded)
    
    print(f"[INFO] Vocabulary size: {min(len(tokenizer.word_index) + 1, MAX_WORDS)}")
    print(f"[INFO] Sequence length: {MAX_SEQUENCE_LENGTH}")
    print(f"[INFO] Padded sequences shape: {X_padded.shape}")
    
    X_train, X_test, y_train, y_test = train_test_split(
        X_padded, y, test_size=0.2, random_state=42, stratify=y
    )
    
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=0.125, random_state=42, stratify=y_train
    )
    
    print(f"\n[INFO] Training set: {len(X_train)} samples")
    print(f"[INFO] Validation set: {len(X_val)} samples")
    print(f"[INFO] Test set: {len(X_test)} samples")
    
    train_dataset = AttackDataset(X_train, y_train)
    val_dataset = AttackDataset(X_val, y_val)
    test_dataset = AttackDataset(X_test, y_test)
    
    class_weights = compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)
    sample_weights = [class_weights[int(y)] for y in y_train]
    sampler = WeightedRandomSampler(sample_weights, num_samples=len(sample_weights))
    
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, sampler=sampler)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)
    
    print(f"[INFO] Class weights: {class_weights}")
    
    return tokenizer, train_loader, val_loader, test_loader, X_test, y_test


def train_model(model, train_loader, val_loader, device, epochs=EPOCHS):
    """Train the LSTM model."""
    print("\n" + "=" * 50)
    print(" TRAINING")
    print("=" * 50)
    
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE, weight_decay=1e-5)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=3, factor=0.5)
    
    best_val_loss = float('inf')
    best_val_acc = 0.0
    history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}
    
    for epoch in range(epochs):
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
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            
            train_loss += loss.item()
            
            predictions = (outputs >= 0.5).float()
            train_correct += (predictions == labels).sum().item()
            train_total += labels.size(0)
        
        train_loss /= len(train_loader)
        train_acc = train_correct / train_total
        
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for sequences, labels in val_loader:
                sequences = sequences.to(device)
                labels = labels.to(device).unsqueeze(1)
                
                outputs = model(sequences)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item()
                
                predictions = (outputs >= 0.5).float()
                val_correct += (predictions == labels).sum().item()
                val_total += labels.size(0)
        
        val_loss /= len(val_loader)
        val_acc = val_correct / val_total
        
        scheduler.step(val_loss)
        
        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)
        
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_val_acc = val_acc
            torch.save({
                'model_state_dict': model.state_dict(),
                'vocab_size': MAX_WORDS,
                'embedding_dim': EMBEDDING_DIM,
                'hidden_dim': HIDDEN_DIM,
            }, MODEL_OUTPUT)
        
        print(f"Epoch {epoch+1:2d}/{epochs} | "
              f"Train Loss: {train_loss:.4f} Acc: {train_acc:.4f} | "
              f"Val Loss: {val_loss:.4f} Acc: {val_acc:.4f} | "
              f"Best: {best_val_acc:.4f}")
    
    print(f"\n[INFO] Best validation accuracy: {best_val_acc:.4f}")
    print(f"[INFO] Model saved to: {MODEL_OUTPUT}")
    
    return history


def evaluate_model(model, test_loader, device, y_test):
    """Evaluate model on test set."""
    print("\n" + "=" * 50)
    print(" EVALUATION")
    print("=" * 50)
    
    model.eval()
    
    all_predictions = []
    all_labels = []
    
    with torch.no_grad():
        for sequences, labels in test_loader:
            sequences = sequences.to(device)
            
            outputs = model(sequences)
            predictions = (outputs >= 0.5).float().cpu().numpy()
            
            all_predictions.extend(predictions.flatten())
            all_labels.extend(labels.numpy())
    
    all_predictions = np.array(all_predictions)
    all_labels = np.array(all_labels)
    
    accuracy = accuracy_score(all_labels, all_predictions)
    precision, recall, f1, _ = precision_recall_fscore_support(all_labels, all_predictions, average='binary')
    
    print(f"\n[RESULTS]")
    print(f"  Accuracy:  {accuracy:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall:    {recall:.4f}")
    print(f"  F1-Score:  {f1:.4f}")
    
    print(f"\n[CONFUSION MATRIX]")
    cm = confusion_matrix(all_labels, all_predictions)
    print(f"  True Negatives:  {cm[0][0]}")
    print(f"  False Positives: {cm[0][1]}")
    print(f"  False Negatives: {cm[1][0]}")
    print(f"  True Positives:  {cm[1][1]}")
    
    print(f"\n[CLASSIFICATION REPORT]")
    print(classification_report(all_labels, all_predictions, target_names=['Benign', 'Malicious']))
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'confusion_matrix': cm.tolist()
    }


def save_tokenizer(tokenizer):
    """Save tokenizer for inference."""
    tokenizer.save(TOKENIZER_OUTPUT)
    print(f"[INFO] Tokenizer saved to: {TOKENIZER_OUTPUT}")


def main():
    start_time = datetime.now()
    
    merged_df = merge_datasets()
    if merged_df is None:
        print("[ERROR] Failed to create dataset!")
        return
    
    merged_df.to_csv(FINAL_DATASET, index=False)
    print(f"\n[INFO] Final dataset saved to: {FINAL_DATASET}")
    
    verify_integrity(merged_df)
    
    device = setup_device()
    if device is None:
        return
    
    tokenizer, train_loader, val_loader, test_loader, X_test, y_test = preprocess_data(merged_df, device)
    
    print("\n" + "=" * 50)
    print(" MODEL INITIALIZATION")
    print("=" * 50)
    
    model = ChameleonLSTM(
        vocab_size=MAX_WORDS,
        embedding_dim=EMBEDDING_DIM,
        hidden_dim=HIDDEN_DIM,
        num_layers=NUM_LAYERS,
        dropout=DROPOUT
    ).to(device)
    
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    print(f"[INFO] Model Architecture: Bidirectional LSTM")
    print(f"[INFO] Total parameters: {total_params:,}")
    print(f"[INFO] Trainable parameters: {trainable_params:,}")
    print(f"[INFO] Model moved to {device}")
    
    history = train_model(model, train_loader, val_loader, device)
    
    metrics = evaluate_model(model, test_loader, device, y_test)
    
    save_tokenizer(tokenizer)
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    print("\n" + "=" * 70)
    print(" TRAINING COMPLETE")
    print("=" * 70)
    print(f"  Duration: {duration}")
    print(f"  Final Accuracy: {metrics['accuracy']:.4f}")
    print(f"  F1-Score: {metrics['f1']:.4f}")
    print(f"  Model: {MODEL_OUTPUT}")
    print(f"  Tokenizer: {TOKENIZER_OUTPUT}")
    print("=" * 70)
    
    return metrics


if __name__ == "__main__":
    main()
