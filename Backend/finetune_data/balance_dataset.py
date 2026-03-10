"""
Balance the training dataset to 50/50 BLOCK/ALLOW
"""
import json
import random

# Read existing data
block_samples = []
allow_samples = []

with open('train.jsonl', 'r') as f:
    for line in f:
        data = json.loads(line)
        if 'VERDICT: BLOCK' in data['text']:
            block_samples.append(data)
        elif 'VERDICT: ALLOW' in data['text']:
            allow_samples.append(data)

print(f"Original: BLOCK={len(block_samples)}, ALLOW={len(allow_samples)}")

# Balance by undersampling BLOCK and augmenting ALLOW
min_count = min(len(block_samples), len(allow_samples))

# Take all ALLOW samples
balanced_allow = allow_samples.copy()

# Take equal number of BLOCK samples
balanced_block = random.sample(block_samples, min_count)

# Augment ALLOW samples with variations to reach target
target_per_class = 2000

# Augmentation strategies for ALLOW samples
allow_augmented = []
for sample in allow_samples:
    allow_augmented.append(sample)
    text = sample['text']
    
    # Add whitespace variations
    if 'COMMAND:' in text:
        # Add extra spaces
        augmented = text.replace('COMMAND:', 'COMMAND:  ')
        allow_augmented.append({'text': augmented})
        
        # Lowercase some commands
        if random.random() > 0.5:
            parts = text.split('\n')
            if len(parts) > 1:
                parts[0] = parts[0].lower()
                allow_augmented.append({'text': '\n'.join(parts)})

# Take target count from augmented
if len(allow_augmented) > target_per_class:
    allow_augmented = random.sample(allow_augmented, target_per_class)

# Take same count from BLOCK
if len(balanced_block) > target_per_class:
    balanced_block = random.sample(balanced_block, target_per_class)

# Combine and shuffle
balanced_samples = balanced_block + allow_augmented
random.shuffle(balanced_samples)

# Write balanced training data
with open('train_balanced.jsonl', 'w') as f:
    for sample in balanced_samples:
        f.write(json.dumps(sample) + '\n')

# Also balance validation data
block_valid = []
allow_valid = []

with open('valid.jsonl', 'r') as f:
    for line in f:
        data = json.loads(line)
        if 'VERDICT: BLOCK' in data['text']:
            block_valid.append(data)
        elif 'VERDICT: ALLOW' in data['text']:
            allow_valid.append(data)

min_valid = min(len(block_valid), len(allow_valid))
balanced_valid = random.sample(block_valid, min_valid) + random.sample(allow_valid, min_valid)
random.shuffle(balanced_valid)

with open('valid_balanced.jsonl', 'w') as f:
    for sample in balanced_valid:
        f.write(json.dumps(sample) + '\n')

print(f"Balanced: BLOCK={len(balanced_block)}, ALLOW={len(allow_augmented)}")
print(f"Validation: BLOCK={min_valid}, ALLOW={min_valid}")
print("Saved to train_balanced.jsonl and valid_balanced.jsonl")
