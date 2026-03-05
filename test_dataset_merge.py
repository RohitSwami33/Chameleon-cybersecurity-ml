#!/usr/bin/env python3
"""
Dataset Merger & Integrity Test
================================

Tests dataset merging without ML dependencies.
Verifies all data sources are correctly loaded and merged.

Run with: python test_dataset_merge.py
"""

import os
import sys
import csv
import json
import hashlib
from datetime import datetime
from pathlib import Path

print("=" * 70)
print(" CHAMELEON DATASET MERGE TEST")
print("=" * 70)

BASE_DIR = Path("/Users/rohit/Documents/Sem-4_project/Chameleon-cybersecurity-ml")
DATASET_DIR = Path("/Users/rohit/Documents/Sem-4_project/Dataset")
CUSTOM_DATA = BASE_DIR / "custom_attack_data.csv"
FINAL_DATASET = BASE_DIR / "final_dataset.csv"

all_data = []
stats = {
    'xss': {'loaded': 0, 'valid': 0},
    'sqli': {'loaded': 0, 'valid': 0},
    'custom': {'loaded': 0, 'valid': 0}
}

print("\n[1] LOADING XSS DATASET")
print("-" * 50)

xss_path = DATASET_DIR / "XSS_dataset.csv"
if xss_path.exists():
    try:
        with open(xss_path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for row in reader:
                sentence = row.get('Sentence', '')
                label = row.get('Label', '')
                if sentence and label:
                    try:
                        all_data.append({
                            'command_sequence': str(sentence),
                            'label': int(float(label)),
                            'source': 'xss'
                        })
                        stats['xss']['loaded'] += 1
                    except:
                        pass
        print(f"   XSS dataset: {stats['xss']['loaded']} rows")
    except Exception as e:
        print(f"   ERROR: {e}")
else:
    print(f"   File not found: {xss_path}")

print("\n[2] LOADING SQL INJECTION DATASETS")
print("-" * 50)

sqli_dir = DATASET_DIR / "sql-injection"
if sqli_dir.exists():
    for filename in ['sqli.csv', 'sqliv2.csv', 'SQLiV3.csv']:
        filepath = sqli_dir / filename
        if not filepath.exists():
            continue
        
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        
        for enc in encodings:
            try:
                with open(filepath, 'r', encoding=enc, errors='ignore') as f:
                    reader = csv.DictReader(f)
                    rows_added = 0
                    for row in reader:
                        sentence = row.get('Sentence', '') or row.get('sentence', '') or row.get('query', '')
                        label = row.get('Label', '') or row.get('label', '')
                        
                        if sentence and label:
                            try:
                                all_data.append({
                                    'command_sequence': str(sentence),
                                    'label': int(float(label)),
                                    'source': 'sqli'
                                })
                                rows_added += 1
                            except:
                                pass
                    
                    if rows_added > 0:
                        print(f"   {filename}: {rows_added} rows (encoding: {enc})")
                        stats['sqli']['loaded'] += rows_added
                        break
            except:
                continue
else:
    print(f"   Directory not found: {sqli_dir}")

print("\n[3] LOADING CUSTOM LLM-GENERATED DATASET")
print("-" * 50)

if CUSTOM_DATA.exists():
    try:
        with open(CUSTOM_DATA, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cmd = row.get('command_sequence', '')
                label = row.get('label', '')
                if cmd and label:
                    all_data.append({
                        'command_sequence': str(cmd),
                        'label': int(label),
                        'source': 'custom'
                    })
                    stats['custom']['loaded'] += 1
        print(f"   Custom dataset: {stats['custom']['loaded']} rows")
    except Exception as e:
        print(f"   ERROR: {e}")
else:
    print(f"   File not found: {CUSTOM_DATA}")

print("\n[4] DATASET STATISTICS")
print("-" * 50)

print(f"\n   Raw total: {len(all_data)} rows")

unique_commands = set()
clean_data = []
for item in all_data:
    cmd = item['command_sequence'].strip()
    if len(cmd) > 3 and cmd not in unique_commands:
        unique_commands.add(cmd)
        clean_data.append(item)

print(f"   After deduplication: {len(clean_data)} rows")

benign = sum(1 for d in clean_data if d['label'] == 0)
malicious = sum(1 for d in clean_data if d['label'] == 1)

print(f"\n   Benign (0):     {benign:>6} ({benign/len(clean_data)*100:.1f}%)")
print(f"   Malicious (1):  {malicious:>6} ({malicious/len(clean_data)*100:.1f}%)")

print("\n[5] INTEGRITY HASH")
print("-" * 50)

content = json.dumps(clean_data[:1000], default=str)
dataset_hash = hashlib.sha256(content.encode()).hexdigest()
print(f"   SHA-256: {dataset_hash[:32]}...")

print("\n[6] SAMPLE DATA")
print("-" * 50)

print("\n   Benign samples:")
benign_samples = [d for d in clean_data if d['label'] == 0][:3]
for i, s in enumerate(benign_samples, 1):
    cmd = s['command_sequence'][:60]
    print(f"     {i}. {cmd}...")

print("\n   Malicious samples:")
malicious_samples = [d for d in clean_data if d['label'] == 1][:3]
for i, s in enumerate(malicious_samples, 1):
    cmd = s['command_sequence'][:60]
    print(f"     {i}. {cmd}...")

print("\n[7] SAVING FINAL DATASET")
print("-" * 50)

with open(FINAL_DATASET, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['command_sequence', 'label', 'source'])
    writer.writeheader()
    writer.writerows(clean_data)

print(f"   Saved to: {FINAL_DATASET}")
print(f"   Total rows: {len(clean_data)}")

integrity_record = {
    "timestamp": datetime.utcnow().isoformat(),
    "dataset_hash": dataset_hash,
    "total_rows": len(clean_data),
    "benign_count": benign,
    "malicious_count": malicious,
    "sources": stats
}

integrity_path = BASE_DIR / "Backend" / "dataset_integrity.json"
os.makedirs(BASE_DIR / "Backend", exist_ok=True)
with open(integrity_path, 'w') as f:
    json.dump(integrity_record, f, indent=2)

print(f"   Integrity record: {integrity_path}")

print("\n" + "=" * 70)
print(" DATASET MERGE COMPLETE")
print("=" * 70)
print(f"   XSS:      {stats['xss']['loaded']:>6} rows")
print(f"   SQLi:     {stats['sqli']['loaded']:>6} rows")
print(f"   Custom:   {stats['custom']['loaded']:>6} rows")
print(f"   Total:    {len(clean_data):>6} rows")
print("=" * 70)
