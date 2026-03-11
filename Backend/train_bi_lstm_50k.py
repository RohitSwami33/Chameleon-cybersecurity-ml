#!/usr/bin/env python3
"""
Chameleon Bidirectional LSTM Training Pipeline (50k Dataset)
============================================================

Merges final_dataset.csv (44k) + custom_attack_data_6k.csv (6k)
Trains character-level Bi-LSTM with MPS acceleration.
Performs rigorous academic evaluation on 20% holdout test set.

Features:
- Character-level tokenization (max length 120)
- Bi-LSTM (Embedding: 64, Hidden: 128, 2 layers, Dropout: 0.3)
- Early stopping (patience=3)
- M4 GPU acceleration via Metal Performance Shaders
- Comprehensive evaluation metrics and visualizations

Author: Senior PyTorch ML Engineer
Date: February 2026
"""

import os
import sys
import json
import pickle
import random
import warnings
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict, Any

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torch.nn.utils.rnn import pad_sequence

# Suppress warnings
warnings.filterwarnings('ignore')

# Debug flag (set to True for quick testing)
DEBUG = False

# Configuration
BASE_DIR = Path("/Users/rohit/Documents/Sem-4_project/Chameleon-cybersecurity-ml")
FINAL_DATASET = BASE_DIR / "final_dataset.csv"
CUSTOM_DATASET = BASE_DIR / "custom_attack_data_6k.csv"
OUTPUT_DIR = BASE_DIR / "Backend"

MODEL_PATH = OUTPUT_DIR / "chameleon_lstm_m4_50k.pth"
TOKENIZER_PATH = OUTPUT_DIR / "tokenizer_50k.json"
CONFUSION_MATRIX_PATH = OUTPUT_DIR / "confusion_matrix_50k.png"
TRAINING_METRICS_PATH = OUTPUT_DIR / "training_metrics_50k.png"
TRAINING_HISTORY_PATH = OUTPUT_DIR / "training_history_50k.json"

# Model hyperparameters
MAX_SEQUENCE_LENGTH = 120  # Character length
EMBEDDING_DIM = 64
HIDDEN_DIM = 128
NUM_LAYERS = 2
DROPOUT = 0.3
BATCH_SIZE = 64
LEARNING_RATE = 0.001
MAX_EPOCHS = 50
EARLY_STOP_PATIENCE = 3
RANDOM_SEED = 42

# Set random seeds for reproducibility
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)
torch.manual_seed(RANDOM_SEED)
if torch.backends.mps.is_available():
    torch.mps.manual_seed(RANDOM_SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed(RANDOM_SEED)

print("=" * 80)
print("CHAMELEON BIDIRECTIONAL LSTM TRAINING PIPELINE (50k DATASET)")
print("=" * 80)
print(f"Device: {'MPS (M4 GPU)' if torch.backends.mps.is_available() else 'CPU'}")
print(f"Max sequence length: {MAX_SEQUENCE_LENGTH}")
print(f"Model: Bi-LSTM (embedding={EMBEDDING_DIM}, hidden={HIDDEN_DIM})")
print(f"Training/Test split: 80/20")
print("=" * 80)


class CharTokenizer:
    """
    Character-level tokenizer for shell command sequences.
    
    Maps each character to an integer index (1-indexed, 0 for padding).
    Includes all printable ASCII characters plus common special characters.
    """
    
    def __init__(self):
        # Define character vocabulary
        self.characters = set()
        self.char_to_idx = {}
        self.idx_to_char = {}
        
        # Add printable ASCII characters (32-126)
        for i in range(32, 127):
            self.characters.add(chr(i))
        
        # Add additional common characters in shell commands
        extra_chars = ['\t', '\n', '\r', '\\', '|', '&', ';', '`', '$', '*', '?', '[', ']', '{', '}']
        for ch in extra_chars:
            self.characters.add(ch)
        
        # Create mapping (1-indexed, 0 reserved for padding)
        self.characters = sorted(list(self.characters))
        self.char_to_idx = {ch: i+1 for i, ch in enumerate(self.characters)}
        self.idx_to_char = {i+1: ch for i, ch in enumerate(self.characters)}
        
        # Special tokens
        self.pad_token = 0
        self.unk_token = len(self.characters) + 1
        self.vocab_size = len(self.characters) + 2  # +2 for pad and unk
    
    def encode(self, text: str, max_len: int = MAX_SEQUENCE_LENGTH) -> List[int]:
        """Convert text to sequence of character indices."""
        
        sequence = []
        for ch in text[:max_len]:
            if ch in self.char_to_idx:
                sequence.append(self.char_to_idx[ch])
            else:
                sequence.append(self.unk_token)
        
        # Pad if shorter than max_len
        if len(sequence) < max_len:
            sequence.extend([self.pad_token] * (max_len - len(sequence)))
        
        return sequence
    
    def decode(self, sequence: List[int]) -> str:
        """Convert sequence of indices back to text."""
        chars = []
        for idx in sequence:
            if idx == self.pad_token:
                continue
            elif idx == self.unk_token:
                chars.append('?')
            elif idx in self.idx_to_char:
                chars.append(self.idx_to_char[idx])
            else:
                chars.append('?')
        return ''.join(chars)
    
    def save(self, filepath: Path):
        """Save tokenizer to JSON file."""
        data = {
            'characters': self.characters,
            'char_to_idx': self.char_to_idx,
            'idx_to_char': self.idx_to_char,
            'vocab_size': self.vocab_size,
            'pad_token': self.pad_token,
            'unk_token': self.unk_token,
            'max_sequence_length': MAX_SEQUENCE_LENGTH
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def load(cls, filepath: Path):
        """Load tokenizer from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        tokenizer = cls()
        tokenizer.characters = data['characters']
        tokenizer.char_to_idx = {k: v for k, v in data['char_to_idx'].items()}
        tokenizer.idx_to_char = {int(k): v for k, v in data['idx_to_char'].items()}
        tokenizer.vocab_size = data['vocab_size']
        tokenizer.pad_token = data['pad_token']
        tokenizer.unk_token = data['unk_token']
        
        return tokenizer


class CommandDataset(Dataset):
    """PyTorch Dataset for command sequences."""
    
    def __init__(self, sequences, labels):
        self.sequences = torch.tensor(sequences, dtype=torch.long)
        self.labels = torch.tensor(labels, dtype=torch.float32).unsqueeze(1)
    
    def __len__(self):
        return len(self.sequences)
    
    def __getitem__(self, idx):
        return self.sequences[idx], self.labels[idx]


class BiLSTMModel(nn.Module):
    """Bidirectional LSTM for attack classification."""
    
    def __init__(self, vocab_size, embedding_dim, hidden_dim, num_layers=2, dropout=0.3):
        super(BiLSTMModel, self).__init__()
        
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
        
        # Bidirectional LSTM outputs hidden_dim * 2
        self.fc = nn.Linear(hidden_dim * 2, 1)
        
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        embedded = self.embedding(x)
        
        lstm_out, (hidden, cell) = self.lstm(embedded)
        
        # Concatenate final forward and backward hidden states
        hidden_concat = torch.cat((hidden[-2], hidden[-1]), dim=1)
        
        dropped = self.dropout(hidden_concat)
        
        out = self.fc(dropped)
        
        return self.sigmoid(out)


def load_and_merge_datasets():
    """Load and merge final_dataset.csv and custom_attack_data_6k.csv."""
    print("\n[1] LOADING AND MERGING DATASETS")
    print("-" * 60)
    
    # Load final_dataset.csv
    df1 = pd.read_csv(FINAL_DATASET)
    print(f"Loaded final_dataset.csv: {len(df1):,} rows")
    print(f"  Columns: {list(df1.columns)}")
    
    # Load custom_attack_data_6k.csv
    df2 = pd.read_csv(CUSTOM_DATASET)
    print(f"Loaded custom_attack_data_6k.csv: {len(df2):,} rows")
    print(f"  Columns: {list(df2.columns)}")
    
    # Standardize column names
    if 'command_sequence' not in df1.columns:
        # Try to find the command column
        possible_cols = ['Sentence', 'sentence', 'query', 'command']
        for col in possible_cols:
            if col in df1.columns:
                df1 = df1.rename(columns={col: 'command_sequence'})
                break
    
    if 'label' not in df1.columns:
        if 'Label' in df1.columns:
            df1 = df1.rename(columns={'Label': 'label'})
    
    # Select only necessary columns
    df1 = df1[['command_sequence', 'label']].copy()
    df2 = df2[['command_sequence', 'label']].copy()
    
    # Merge datasets
    merged_df = pd.concat([df1, df2], ignore_index=True)
    print(f"Merged dataset: {len(merged_df):,} rows")
    
    # Clean data
    merged_df = merged_df.dropna(subset=['command_sequence', 'label'])
    merged_df['command_sequence'] = merged_df['command_sequence'].astype(str)
    merged_df['label'] = merged_df['label'].astype(int)
    
    # Remove duplicates
    before_dedup = len(merged_df)
    merged_df = merged_df.drop_duplicates(subset=['command_sequence'])
    after_dedup = len(merged_df)
    print(f"After deduplication: {after_dedup:,} rows (removed {before_dedup - after_dedup:,})")
    
    # Remove very short commands
    merged_df = merged_df[merged_df['command_sequence'].str.len() >= 3]
    print(f"After length filter: {len(merged_df):,} rows")
    
    # Balance check
    benign_count = (merged_df['label'] == 0).sum()
    malicious_count = (merged_df['label'] == 1).sum()
    
    print(f"\nClass distribution:")
    print(f"  Benign (0):     {benign_count:,} ({benign_count/len(merged_df)*100:.1f}%)")
    print(f"  Malicious (1):  {malicious_count:,} ({malicious_count/len(merged_df)*100:.1f}%)")
    
    return merged_df


def prepare_data(df, tokenizer, test_size=0.2, val_size=0.2):
    """Prepare data for training with 80/20 split and validation."""
    print("\n[2] PREPARING DATA WITH TRAIN/VAL/TEST SPLIT")
    print("-" * 60)
    
    X = df['command_sequence'].values
    y = df['label'].values
    
    # Encode all sequences
    print(f"Encoding {len(X):,} sequences with character-level tokenizer...")
    X_encoded = [tokenizer.encode(seq) for seq in X]
    X_encoded = np.array(X_encoded)
    
    print(f"Vocabulary size: {tokenizer.vocab_size:,}")
    print(f"Sequence shape: {X_encoded.shape}")
    
    # First split: train+val vs test (80/20)
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X_encoded, y, test_size=test_size, random_state=RANDOM_SEED,
        stratify=y, shuffle=True
    )
    
    # Second split: train vs val (80/20 of train_val)
    val_relative_size = val_size / (1 - test_size)  # val_size relative to train_val
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val, y_train_val, test_size=val_relative_size, random_state=RANDOM_SEED,
        stratify=y_train_val, shuffle=True
    )
    
    print(f"\nData split:")
    print(f"  Training set:    {len(X_train):,} samples ({len(X_train)/len(X)*100:.1f}%)")
    print(f"  Validation set:  {len(X_val):,} samples ({len(X_val)/len(X)*100:.1f}%)")
    print(f"  Test set:        {len(X_test):,} samples ({len(X_test)/len(X)*100:.1f}%)")
    
    return X_train, X_val, X_test, y_train, y_val, y_test


def create_data_loaders(X_train, X_val, X_test, y_train, y_val, y_test, batch_size=BATCH_SIZE):
    """Create PyTorch DataLoaders for train, validation, and test."""
    train_dataset = CommandDataset(X_train, y_train)
    val_dataset = CommandDataset(X_val, y_val)
    test_dataset = CommandDataset(X_test, y_test)
    
    train_loader = DataLoader(
        train_dataset, batch_size=batch_size, shuffle=True, num_workers=0
    )
    val_loader = DataLoader(
        val_dataset, batch_size=batch_size, shuffle=False, num_workers=0
    )
    test_loader = DataLoader(
        test_dataset, batch_size=batch_size, shuffle=False, num_workers=0
    )
    
    return train_loader, val_loader, test_loader


def setup_device():
    """Setup MPS device for M4 GPU acceleration."""
    print("\n[3] SETTING UP DEVICE")
    print("-" * 60)
    
    if torch.backends.mps.is_available():
        device = torch.device("mps")
        print("✅ M4 GPU detected! Using Metal Performance Shaders")
        
        # Test MPS with a simple operation
        test_tensor = torch.randn(100, 100).to(device)
        _ = test_tensor @ test_tensor.T
        print("✅ MPS test passed")
        
    elif torch.cuda.is_available():
        device = torch.device("cuda")
        print(f"✅ CUDA GPU detected: {torch.cuda.get_device_name(0)}")
    
    else:
        device = torch.device("cpu")
        print("⚠️  No GPU detected, using CPU (training will be slower)")
    
    print(f"Using device: {device}")
    return device


def train_model(model, train_loader, val_loader, device, epochs=MAX_EPOCHS, patience=EARLY_STOP_PATIENCE):
    """Train the model with early stopping using validation loss."""
    print("\n[4] TRAINING MODEL")
    print("-" * 60)
    
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', patience=2, factor=0.5
    )
    
    # Early stopping
    best_val_loss = float('inf')
    patience_counter = 0
    best_model_state = None
    
    history = {
        'train_loss': [],
        'train_acc': [],
        'val_loss': [],
        'val_acc': [],
        'learning_rate': []
    }
    
    for epoch in range(epochs):
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0
        
        for batch_idx, (sequences, labels) in enumerate(train_loader):
            sequences = sequences.to(device)
            labels = labels.to(device)
            
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
        
        avg_train_loss = train_loss / len(train_loader)
        train_accuracy = train_correct / train_total
        
        # Validation phase
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        with torch.no_grad():
            for sequences, labels in val_loader:
                sequences = sequences.to(device)
                labels = labels.to(device)
                
                outputs = model(sequences)
                loss = criterion(outputs, labels)
                val_loss += loss.item()
                
                predictions = (outputs >= 0.5).float()
                val_correct += (predictions == labels).sum().item()
                val_total += labels.size(0)
        
        avg_val_loss = val_loss / len(val_loader)
        val_accuracy = val_correct / val_total
        current_lr = optimizer.param_groups[0]['lr']
        
        history['train_loss'].append(avg_train_loss)
        history['train_acc'].append(train_accuracy)
        history['val_loss'].append(avg_val_loss)
        history['val_acc'].append(val_accuracy)
        history['learning_rate'].append(current_lr)
        
        print(f"Epoch {epoch+1:3d}/{epochs} | "
              f"Train Loss: {avg_train_loss:.4f} | "
              f"Train Acc: {train_accuracy:.4f} | "
              f"Val Loss: {avg_val_loss:.4f} | "
              f"Val Acc: {val_accuracy:.4f} | "
              f"LR: {current_lr:.6f}")
        
        # Early stopping check on validation loss
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            best_model_state = model.state_dict().copy()
            patience_counter = 0
        else:
            patience_counter += 1
        
        scheduler.step(avg_val_loss)
        
        if patience_counter >= patience:
            print(f"\n⏹️  Early stopping triggered after {epoch+1} epochs")
            print(f"Best validation loss: {best_val_loss:.4f}")
            break
    
    # Load best model weights
    if best_model_state is not None:
        model.load_state_dict(best_model_state)
    
    return model, history


def evaluate_model(model, test_loader, device):
    """Evaluate model on test set."""
    print("\n[5] EVALUATING MODEL ON TEST SET")
    print("-" * 60)
    
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
            all_labels.extend(labels.numpy().flatten())
    
    all_predictions = np.array(all_predictions)
    all_labels = np.array(all_labels)
    
    # Calculate metrics
    accuracy = accuracy_score(all_labels, all_predictions)
    precision = precision_score(all_labels, all_predictions, zero_division=0)
    recall = recall_score(all_labels, all_predictions, zero_division=0)
    f1 = f1_score(all_labels, all_predictions, zero_division=0)
    
    print(f"\n📊 TEST SET EVALUATION (n={len(all_labels):,})")
    print("-" * 40)
    print(f"Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1-Score:  {f1:.4f}")
    
    # Confusion matrix
    cm = confusion_matrix(all_labels, all_predictions)
    print(f"\nConfusion Matrix:")
    print(f"  True Negatives:  {cm[0][0]:>6}")
    print(f"  False Positives: {cm[0][1]:>6}")
    print(f"  False Negatives: {cm[1][0]:>6}")
    print(f"  True Positives:  {cm[1][1]:>6}")
    
    # Classification report
    print(f"\nClassification Report:")
    print(classification_report(all_labels, all_predictions, 
                                target_names=['Benign', 'Malicious'],
                                digits=4))
    
    return {
        'accuracy': float(accuracy),
        'precision': float(precision),
        'recall': float(recall),
        'f1': float(f1),
        'confusion_matrix': cm.tolist(),
        'predictions': all_predictions.tolist(),
        'labels': all_labels.tolist(),
        'probabilities': [float(p) for p in all_probs]
    }


def plot_confusion_matrix(cm, save_path):
    """Plot and save confusion matrix."""
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['Benign', 'Malicious'],
                yticklabels=['Benign', 'Malicious'])
    plt.title('Confusion Matrix - Test Set Evaluation')
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Confusion matrix saved to: {save_path}")


def plot_training_metrics(history, save_path):
    """Plot and save training and validation metrics."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    # Loss plot
    ax1.plot(history['train_loss'], label='Training Loss', color='blue', linewidth=2)
    ax1.plot(history['val_loss'], label='Validation Loss', color='red', linewidth=2, linestyle='--')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss')
    ax1.set_title('Training & Validation Loss')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Accuracy plot
    ax2.plot(history['train_acc'], label='Training Accuracy', color='green', linewidth=2)
    ax2.plot(history['val_acc'], label='Validation Accuracy', color='orange', linewidth=2, linestyle='--')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Accuracy')
    ax2.set_title('Training & Validation Accuracy')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Training metrics saved to: {save_path}")


def save_training_history(history, evaluation, save_path):
    """Save training history and evaluation results."""
    data = {
        'timestamp': datetime.now().isoformat(),
        'model_architecture': {
            'embedding_dim': EMBEDDING_DIM,
            'hidden_dim': HIDDEN_DIM,
            'num_layers': NUM_LAYERS,
            'dropout': DROPOUT,
            'vocab_size': None  # Will be filled later
        },
        'training_parameters': {
            'batch_size': BATCH_SIZE,
            'learning_rate': LEARNING_RATE,
            'max_epochs': MAX_EPOCHS,
            'early_stop_patience': EARLY_STOP_PATIENCE,
            'max_sequence_length': MAX_SEQUENCE_LENGTH
        },
        'training_history': history,
        'evaluation_results': evaluation,
        'dataset_info': {
            'final_dataset_rows': None,
            'custom_dataset_rows': None,
            'merged_rows': None
        }
    }
    
    with open(save_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Training history saved to: {save_path}")


def main():
    """Main training pipeline."""
    start_time = datetime.now()
    
    # Load and merge datasets
    df = load_and_merge_datasets()
    
    if DEBUG:
        print("DEBUG mode: exiting after data loading")
        sys.exit(0)
    
    # Create character tokenizer
    tokenizer = CharTokenizer()
    print(f"\n✅ Character tokenizer created with {tokenizer.vocab_size:,} tokens")
    
    # Prepare data with train/val/test split (64/16/20)
    X_train, X_val, X_test, y_train, y_val, y_test = prepare_data(df, tokenizer)
    
    # Create data loaders
    train_loader, val_loader, test_loader = create_data_loaders(X_train, X_val, X_test, y_train, y_val, y_test)
    
    # Setup device
    device = setup_device()
    
    # Create model
    model = BiLSTMModel(
        vocab_size=tokenizer.vocab_size,
        embedding_dim=EMBEDDING_DIM,
        hidden_dim=HIDDEN_DIM,
        num_layers=NUM_LAYERS,
        dropout=DROPOUT
    ).to(device)
    
    # Print model summary
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"\n📐 MODEL ARCHITECTURE")
    print("-" * 40)
    print(f"Bidirectional LSTM with {NUM_LAYERS} layers")
    print(f"Embedding dimension: {EMBEDDING_DIM}")
    print(f"Hidden dimension: {HIDDEN_DIM}")
    print(f"Total parameters: {total_params:,}")
    print(f"Trainable parameters: {trainable_params:,}")
    
    # Train model
    model, history = train_model(model, train_loader, val_loader, device)
    
    # Evaluate model
    evaluation = evaluate_model(model, test_loader, device)
    
    # Save model
    torch.save({
        'model_state_dict': model.state_dict(),
        'tokenizer_vocab_size': tokenizer.vocab_size,
        'embedding_dim': EMBEDDING_DIM,
        'hidden_dim': HIDDEN_DIM,
        'num_layers': NUM_LAYERS,
        'dropout': DROPOUT,
        'max_sequence_length': MAX_SEQUENCE_LENGTH,
        'evaluation_metrics': {
            'accuracy': evaluation['accuracy'],
            'precision': evaluation['precision'],
            'recall': evaluation['recall'],
            'f1': evaluation['f1']
        }
    }, MODEL_PATH)
    print(f"\n✅ Model saved to: {MODEL_PATH}")
    
    # Save tokenizer
    tokenizer.save(TOKENIZER_PATH)
    print(f"✅ Tokenizer saved to: {TOKENIZER_PATH}")
    
    # Generate visualizations
    cm = np.array(evaluation['confusion_matrix'])
    plot_confusion_matrix(cm, CONFUSION_MATRIX_PATH)
    plot_training_metrics(history, TRAINING_METRICS_PATH)
    
    # Save training history
    save_training_history(history, evaluation, TRAINING_HISTORY_PATH)
    
    # Final summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    print("\n" + "=" * 80)
    print("🎉 TRAINING PIPELINE COMPLETE")
    print("=" * 80)
    print(f"Total duration: {duration}")
    print(f"Final test accuracy: {evaluation['accuracy']:.4f} ({evaluation['accuracy']*100:.2f}%)")
    print(f"F1-Score: {evaluation['f1']:.4f}")
    print(f"\nArtifacts saved:")
    print(f"  • Model: {MODEL_PATH}")
    print(f"  • Tokenizer: {TOKENIZER_PATH}")
    print(f"  • Confusion matrix: {CONFUSION_MATRIX_PATH}")
    print(f"  • Training metrics: {TRAINING_METRICS_PATH}")
    print(f"  • Training history: {TRAINING_HISTORY_PATH}")
    print("=" * 80)


if __name__ == "__main__":
    main()