#!/usr/bin/env python3
"""
Chameleon LSTM Training Script (6k Dataset)
===========================================

Trains on the custom 6,000 row dataset with early stopping.
Optimized for M4 GPU (Metal Performance Shaders).

Features:
- Custom dataset training (6,000 rows)
- Early stopping (patience=5)
- Learning rate scheduling
- Model checkpointing
- Training history logging

Run: python train_50k_lstm.py
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
CUSTOM_DATASET = BASE_DIR / "custom_attack_data_6k.csv"
OUTPUT_DIR = BASE_DIR / "Backend"
MODEL_OUTPUT = OUTPUT_DIR / "chameleon_lstm_model.pt"
TOKENIZER_OUTPUT = OUTPUT_DIR / "tokenizer.pkl"
HISTORY_OUTPUT = OUTPUT_DIR / "training_history.json"

MAX_WORDS = 10000
MAX_SEQUENCE_LENGTH = 150
EMBEDDING_DIM = 128
HIDDEN_DIM = 256
NUM_LAYERS = 2
DROPOUT = 0.3
BATCH_SIZE = 64
MAX_EPOCHS = 100
LEARNING_RATE = 0.001
EARLY_STOP_PATIENCE = 5

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset, WeightedRandomSampler

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_recall_fscore_support
from sklearn.utils.class_weight import compute_class_weight

from simple_tokenizer import SimpleTokenizer, pad_sequences

print("=" * 70, flush=True)
print(" CHAMELEON LSTM TRAINING (6k Dataset)", flush=True)
print("=" * 70, flush=True)
print(f" Max Epochs: {MAX_EPOCHS}", flush=True)
print(f" Early Stop Patience: {EARLY_STOP_PATIENCE}", flush=True)
print(f" Batch Size: {BATCH_SIZE}", flush=True)
print("=" * 70, flush=True)


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


class EarlyStopping:
    """Early stopping to stop training when validation loss doesn't improve."""
    
    def __init__(self, patience=5, min_delta=0.0001, mode='min'):
        self.patience = patience
        self.min_delta = min_delta
        self.mode = mode
        self.counter = 0
        self.best_score = None
        self.early_stop = False
        self.best_epoch = 0
    
    def __call__(self, score, epoch):
        if self.best_score is None:
            self.best_score = score
            self.best_epoch = epoch
            return False
        
        if self.mode == 'min':
            improved = score < self.best_score - self.min_delta
        else:
            improved = score > self.best_score + self.min_delta
        
        if improved:
            self.best_score = score
            self.best_epoch = epoch
            self.counter = 0
            return False
        else:
            self.counter += 1
            if self.counter >= self.patience:
                self.early_stop = True
                return True
            return False


def main():
    start_time = datetime.now()
    
    print("\n[1] Loading Custom Dataset (6k)...")
    print("-" * 50)
    df = pd.read_csv(CUSTOM_DATASET)
    
    df = df.drop_duplicates(subset=['command_sequence'])
    df = df[df['command_sequence'].str.len() > 3]
    
    print(f"   Total rows: {len(df)}")
    print(f"   Benign (0): {len(df[df['label'] == 0])} ({len(df[df['label'] == 0])/len(df)*100:.1f}%)")
    print(f"   Malicious (1): {len(df[df['label'] == 1])} ({len(df[df['label'] == 1])/len(df)*100:.1f}%)")
    
    dataset_hash = hashlib.sha256(df.to_json(orient='records').encode()).hexdigest()[:32]
    print(f"   Dataset hash: {dataset_hash}...")
    
    print("\n[2] Setting up Device...")
    print("-" * 50)
    if torch.backends.mps.is_available():
        device = torch.device("mps")
        print("   ✓ M4 GPU detected (Metal Performance Shaders)")
        test = torch.randn(100, 100).to(device)
        _ = test @ test.T
        del test
        torch.mps.empty_cache()
        print("   ✓ GPU test passed")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
        print("   ✓ CUDA GPU detected")
    else:
        device = torch.device("cpu")
        print("   Using CPU")
    print(f"   Device: {device}")
    
    print("\n[3] Tokenizing...")
    print("-" * 50)
    X = df['command_sequence'].astype(str).values
    y = df['label'].values
    
    tokenizer = SimpleTokenizer(num_words=MAX_WORDS, lower=True, oov_token='<OOV>')
    tokenizer.fit_on_texts(X)
    
    sequences = tokenizer.texts_to_sequences(X)
    X_padded = np.array(pad_sequences(sequences, maxlen=MAX_SEQUENCE_LENGTH, padding='post', truncating='post'))
    
    vocab_size = min(len(tokenizer.word_index) + 1, MAX_WORDS)
    print(f"   Vocabulary size: {vocab_size}")
    print(f"   Sequence length: {MAX_SEQUENCE_LENGTH}")
    print(f"   Padded shape: {X_padded.shape}")
    
    print("\n[4] Splitting Data...")
    print("-" * 50)
    X_train, X_test, y_train, y_test = train_test_split(
        X_padded, y, test_size=0.15, random_state=42, stratify=y
    )
    
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=0.15, random_state=42, stratify=y_train
    )
    
    print(f"   Training:   {len(X_train):>6} samples ({len(X_train)/len(df)*100:.1f}%)")
    print(f"   Validation: {len(X_val):>6} samples ({len(X_val)/len(df)*100:.1f}%)")
    print(f"   Test:       {len(X_test):>6} samples ({len(X_test)/len(df)*100:.1f}%)")
    
    train_dataset = AttackDataset(X_train, y_train)
    val_dataset = AttackDataset(X_val, y_val)
    test_dataset = AttackDataset(X_test, y_test)
    
    class_weights = compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)
    sample_weights = [class_weights[int(y)] for y in y_train]
    sampler = WeightedRandomSampler(sample_weights, num_samples=len(sample_weights))
    
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, sampler=sampler, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)
    
    print(f"   Class weights: {class_weights}")
    
    print("\n[5] Creating Model...")
    print("-" * 50)
    model = ChameleonLSTM(
        vocab_size=vocab_size,
        embedding_dim=EMBEDDING_DIM,
        hidden_dim=HIDDEN_DIM,
        num_layers=NUM_LAYERS,
        dropout=DROPOUT
    ).to(device)
    
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    print(f"   Embedding dim: {EMBEDDING_DIM}")
    print(f"   Hidden dim: {HIDDEN_DIM}")
    print(f"   Layers: {NUM_LAYERS} (bidirectional)")
    print(f"   Total parameters: {total_params:,}")
    print(f"   Trainable parameters: {trainable_params:,}")
    
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE, weight_decay=1e-5)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=3, factor=0.5)
    
    early_stopping = EarlyStopping(patience=EARLY_STOP_PATIENCE, min_delta=0.0001, mode='min')
    
    print(f"\n[6] Training ({MAX_EPOCHS} max epochs, early stop: {EARLY_STOP_PATIENCE})...")
    print("=" * 70)
    
    history = {
        'train_loss': [], 'train_acc': [],
        'val_loss': [], 'val_acc': [],
        'learning_rates': []
    }
    
    best_val_loss = float('inf')
    best_val_acc = 0.0
    best_epoch = 0
    
    for epoch in range(MAX_EPOCHS):
        epoch_start = datetime.now()
        
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
        
        current_lr = optimizer.param_groups[0]['lr']
        scheduler.step(val_loss)
        
        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)
        history['learning_rates'].append(current_lr)
        
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_val_acc = val_acc
            best_epoch = epoch + 1
            
            torch.save({
                'model_state_dict': model.state_dict(),
                'vocab_size': vocab_size,
                'embedding_dim': EMBEDDING_DIM,
                'hidden_dim': HIDDEN_DIM,
                'num_layers': NUM_LAYERS,
                'epoch': epoch + 1,
                'val_loss': val_loss,
                'val_acc': val_acc,
            }, MODEL_OUTPUT)
        
        epoch_time = (datetime.now() - epoch_start).total_seconds()
        
        print(f"Epoch {epoch+1:3d}/{MAX_EPOCHS} | "
              f"Train: L={train_loss:.4f} A={train_acc:.4f} | "
              f"Val: L={val_loss:.4f} A={val_acc:.4f} | "
              f"Best: {best_val_acc:.4f} @ {best_epoch} | "
              f"LR: {current_lr:.6f} | "
              f"{epoch_time:.1f}s")
        
        if early_stopping(val_loss, epoch + 1):
            print("\n" + "=" * 70)
            print(f" EARLY STOPPING at epoch {epoch + 1}")
            print(f" Best validation loss: {early_stopping.best_score:.4f} at epoch {early_stopping.best_epoch}")
            print("=" * 70)
            break
    
    print(f"\n[7] Loading Best Model (epoch {best_epoch})...")
    print("-" * 50)
    checkpoint = torch.load(MODEL_OUTPUT, map_location=device, weights_only=False)
    model.load_state_dict(checkpoint['model_state_dict'])
    print(f"   Loaded model from epoch {checkpoint.get('epoch', best_epoch)}")
    print(f"   Validation loss: {checkpoint.get('val_loss', best_val_loss):.4f}")
    print(f"   Validation accuracy: {checkpoint.get('val_acc', best_val_acc):.4f}")
    
    print(f"\n[8] Evaluating on Test Set...")
    print("-" * 50)
    model.eval()
    
    all_predictions = []
    all_labels = []
    all_probs = []
    
    with torch.no_grad():
        for sequences, labels in test_loader:
            sequences = sequences.to(device)
            outputs = model(sequences)
            probs = outputs.cpu().numpy().flatten()
            predictions = (outputs >= 0.5).float().cpu().numpy().flatten()
            
            all_predictions.extend(predictions)
            all_probs.extend(probs)
            all_labels.extend(labels.numpy())
    
    all_predictions = np.array(all_predictions)
    all_labels = np.array(all_labels)
    all_probs = np.array(all_probs)
    
    accuracy = accuracy_score(all_labels, all_predictions)
    precision, recall, f1, _ = precision_recall_fscore_support(all_labels, all_predictions, average='binary')
    
    print(f"\n   TEST RESULTS:")
    print(f"   Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"   Precision: {precision:.4f}")
    print(f"   Recall:    {recall:.4f}")
    print(f"   F1-Score:  {f1:.4f}")
    
    cm = confusion_matrix(all_labels, all_predictions)
    print(f"\n   Confusion Matrix:")
    print(f"   TN: {cm[0][0]:>6}  FP: {cm[0][1]:>6}")
    print(f"   FN: {cm[1][0]:>6}  TP: {cm[1][1]:>6}")
    
    print(f"\n   Classification Report:")
    print(classification_report(all_labels, all_predictions, target_names=['Benign', 'Malicious']))
    
    print(f"\n[9] Saving Artifacts...")
    print("-" * 50)
    
    tokenizer.save(str(TOKENIZER_OUTPUT))
    print(f"   Tokenizer: {TOKENIZER_OUTPUT}")
    print(f"   Model: {MODEL_OUTPUT}")
    
    history['final_test_accuracy'] = accuracy
    history['final_test_precision'] = precision
    history['final_test_recall'] = recall
    history['final_test_f1'] = f1
    history['best_epoch'] = best_epoch
    history['best_val_loss'] = best_val_loss
    history['best_val_acc'] = best_val_acc
    history['total_epochs'] = epoch + 1
    history['training_time_seconds'] = (datetime.now() - start_time).total_seconds()
    history['dataset_hash'] = dataset_hash
    history['dataset_size'] = len(df)
    history['model_params'] = total_params
    
    with open(HISTORY_OUTPUT, 'w') as f:
        json.dump(history, f, indent=2)
    print(f"   History: {HISTORY_OUTPUT}")
    
    duration = datetime.now() - start_time
    
    print("\n" + "=" * 70)
    print(" TRAINING COMPLETE")
    print("=" * 70)
    print(f"   Total epochs: {epoch + 1}")
    print(f"   Best epoch: {best_epoch}")
    print(f"   Training time: {duration}")
    print(f"   Final test accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"   F1-Score: {f1:.4f}")
    print("=" * 70)
    
    return accuracy, f1


if __name__ == "__main__":
    main()