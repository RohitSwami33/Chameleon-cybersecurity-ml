"""
Merkle Tree Integrity Module for Chameleon Honeypot System
===========================================================

This module provides cryptographic integrity verification for honeypot logs
using Merkle Trees. It enables tamper-proof logging and verification that
log entries have not been modified after being recorded.

Key Features:
- SHA-256 hashing of individual log entries
- Merkle Tree construction for efficient verification
- Merkle proof generation and verification
- Integration with ReputationScores table for data integrity

How Merkle Trees Work for Log Integrity:
1. Each log entry is hashed using SHA-256
2. Pairs of hashes are combined and hashed again
3. This process repeats until a single "root hash" is produced
4. The root hash is stored in ReputationScores.merkle_root
5. Any modification to logs would change the root hash, detecting tampering

Author: Chameleon Security Team
"""

import hashlib
import json
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


# ============================================================
# Log Entry Hashing
# ============================================================

def hash_log_entry(log_data: Dict[str, Any]) -> str:
    """
    Hash a single log entry using SHA-256.
    
    This function creates a deterministic hash of a log entry by:
    1. Sorting keys alphabetically for consistent ordering
    2. Converting to JSON string with sorted keys
    3. Encoding to UTF-8 bytes
    4. Applying SHA-256 hash
    
    Args:
        log_data: Dictionary containing log entry data.
                  Expected keys: id, timestamp, attacker_ip, command_entered,
                                 response_sent, metadata (optional)
    
    Returns:
        Hexadecimal string representation of the SHA-256 hash (64 characters)
    
    Example:
        >>> log = {
        ...     "id": "abc123",
        ...     "timestamp": "2024-01-15T10:30:00Z",
        ...     "attacker_ip": "192.168.1.100",
        ...     "command_entered": "ls -la",
        ...     "response_sent": "total 48..."
        ... }
        >>> hash_log_entry(log)
        'a1b2c3d4e5f6...7890abcdef'
    """
    # Create a copy to avoid modifying the original
    data = log_data.copy()
    
    # Ensure consistent serialization
    # Remove any non-serializable fields
    serializable_data = {}
    for key, value in sorted(data.items()):
        if isinstance(value, datetime):
            serializable_data[key] = value.isoformat()
        elif isinstance(value, dict):
            # Recursively handle nested dicts
            serializable_data[key] = _make_serializable(value)
        elif value is not None:
            serializable_data[key] = value
    
    # Convert to JSON string with sorted keys
    json_string = json.dumps(serializable_data, sort_keys=True, separators=(',', ':'))
    
    # Encode and hash
    encoded = json_string.encode('utf-8')
    hash_object = hashlib.sha256(encoded)
    
    return hash_object.hexdigest()


def _make_serializable(data: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively convert a dictionary to be JSON serializable."""
    result = {}
    for key, value in sorted(data.items()):
        if isinstance(value, datetime):
            result[key] = value.isoformat()
        elif isinstance(value, dict):
            result[key] = _make_serializable(value)
        elif isinstance(value, (list, tuple)):
            result[key] = [
                item.isoformat() if isinstance(item, datetime) else item
                for item in value
            ]
        elif value is not None:
            result[key] = value
    return result


def hash_pair(left: str, right: str) -> str:
    """
    Hash a pair of hashes together.
    
    Args:
        left: Left hash (hexadecimal string)
        right: Right hash (hexadecimal string)
    
    Returns:
        Combined hash (hexadecimal string)
    """
    combined = left + right
    return hashlib.sha256(combined.encode('utf-8')).hexdigest()


# ============================================================
# Merkle Tree Implementation
# ============================================================

@dataclass
class MerkleNode:
    """Represents a node in the Merkle Tree."""
    
    hash: str
    left: Optional['MerkleNode'] = None
    right: Optional['MerkleNode'] = None
    is_leaf: bool = True
    data: Optional[Dict[str, Any]] = None  # Original data for leaf nodes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary representation."""
        result = {"hash": self.hash, "is_leaf": self.is_leaf}
        if self.left:
            result["left"] = self.left.to_dict()
        if self.right:
            result["right"] = self.right.to_dict()
        return result


class MerkleTree:
    """
    Merkle Tree implementation for log integrity verification.
    
    The tree is built from the bottom up:
    1. Leaf nodes contain hashes of individual log entries
    2. Parent nodes contain hashes of their children combined
    3. The root node's hash represents the entire dataset
    
    Attributes:
        leaves: List of leaf node hashes
        root: Root node of the tree
        tree: Complete tree structure for proof generation
    """
    
    def __init__(self, log_entries: List[Dict[str, Any]]):
        """
        Initialize Merkle Tree from log entries.
        
        Args:
            log_entries: List of log entry dictionaries
        """
        self.log_entries = log_entries
        self.leaf_hashes: List[str] = []
        self.nodes: List[List[MerkleNode]] = []
        self.root: Optional[MerkleNode] = None
        
        if log_entries:
            self._build_tree()
    
    def _build_tree(self) -> None:
        """Build the Merkle Tree from log entries."""
        # Step 1: Create leaf nodes by hashing each log entry
        leaf_nodes = []
        for entry in self.log_entries:
            entry_hash = hash_log_entry(entry)
            self.leaf_hashes.append(entry_hash)
            node = MerkleNode(hash=entry_hash, is_leaf=True, data=entry)
            leaf_nodes.append(node)
        
        self.nodes.append(leaf_nodes)
        
        # Step 2: Build tree levels from bottom up
        current_level = leaf_nodes
        while len(current_level) > 1:
            next_level = []
            
            # Process pairs of nodes
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                
                if i + 1 < len(current_level):
                    right = current_level[i + 1]
                else:
                    # Odd number of nodes - duplicate the last one
                    right = MerkleNode(hash=left.hash, is_leaf=True)
                
                # Create parent node
                parent_hash = hash_pair(left.hash, right.hash)
                parent = MerkleNode(
                    hash=parent_hash,
                    left=left,
                    right=right,
                    is_leaf=False
                )
                next_level.append(parent)
            
            self.nodes.append(next_level)
            current_level = next_level
        
        # The last remaining node is the root
        if current_level:
            self.root = current_level[0]
    
    @property
    def root_hash(self) -> Optional[str]:
        """Get the root hash of the tree."""
        return self.root.hash if self.root else None
    
    def get_proof(self, index: int) -> List[Dict[str, str]]:
        """
        Generate a Merkle proof for a specific leaf node.
        
        A Merkle proof consists of the sibling hashes needed to
        verify that a leaf is part of the tree without needing
        all other leaves.
        
        Args:
            index: Index of the leaf node to prove
        
        Returns:
            List of proof steps, each containing:
            - "hash": The sibling hash
            - "position": "left" or "right" indicating sibling position
        
        Example:
            >>> tree = MerkleTree([log1, log2, log3, log4])
            >>> proof = tree.get_proof(0)
            >>> # proof = [{"hash": "hash_of_log2", "position": "right"}, ...]
        """
        if not self.root or index < 0 or index >= len(self.leaf_hashes):
            return []
        
        proof = []
        current_index = index
        
        # Traverse from leaves to root
        for level in range(len(self.nodes) - 1):
            current_level = self.nodes[level]
            
            # Find sibling
            if current_index % 2 == 0:
                # Current is left child, sibling is right
                sibling_index = current_index + 1
                position = "right"
            else:
                # Current is right child, sibling is left
                sibling_index = current_index - 1
                position = "left"
            
            # Get sibling hash (or duplicate if out of bounds)
            if sibling_index < len(current_level):
                sibling_hash = current_level[sibling_index].hash
            else:
                # No sibling - use self hash (for odd-length levels)
                sibling_hash = current_level[current_index].hash
            
            proof.append({
                "hash": sibling_hash,
                "position": position
            })
            
            # Move to parent level
            current_index = current_index // 2
        
        return proof
    
    @staticmethod
    def verify_proof(
        leaf_hash: str,
        proof: List[Dict[str, str]],
        root_hash: str
    ) -> bool:
        """
        Verify a Merkle proof.
        
        This allows verification that a leaf node is part of a tree
        without having access to the entire tree.
        
        Args:
            leaf_hash: Hash of the leaf node to verify
            proof: Merkle proof (list of sibling hashes and positions)
            root_hash: Expected root hash
        
        Returns:
            True if the proof is valid, False otherwise
        
        Example:
            >>> leaf_hash = hash_log_entry(log_entry)
            >>> proof = tree.get_proof(0)
            >>> root_hash = tree.root_hash
            >>> MerkleTree.verify_proof(leaf_hash, proof, root_hash)
            True
        """
        current_hash = leaf_hash
        
        for step in proof:
            sibling_hash = step["hash"]
            position = step["position"]
            
            if position == "right":
                # Sibling is on the right
                current_hash = hash_pair(current_hash, sibling_hash)
            else:
                # Sibling is on the left
                current_hash = hash_pair(sibling_hash, current_hash)
        
        return current_hash == root_hash
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tree to dictionary representation."""
        return {
            "root_hash": self.root_hash,
            "leaf_count": len(self.leaf_hashes),
            "leaf_hashes": self.leaf_hashes,
            "tree": self.root.to_dict() if self.root else None
        }


# ============================================================
# Merkle Logger Class
# ============================================================

class MerkleLogger:
    """
    High-level Merkle Tree logger for honeypot logs.
    
    This class provides a convenient interface for:
    - Hashing log entries
    - Building Merkle Trees
    - Storing and verifying log integrity
    - Integration with the ReputationScores table
    
    Usage:
        logger = MerkleLogger()
        
        # Add logs
        logger.add_log(log_entry_1)
        logger.add_log(log_entry_2)
        
        # Build tree and get root
        root_hash = logger.build_tree()
        
        # Store root hash in ReputationScores
        await update_reputation_score(session, ip, merkle_root=root_hash)
        
        # Later, verify integrity
        is_valid = logger.verify_integrity(stored_root_hash)
    """
    
    def __init__(self):
        """Initialize the Merkle Logger."""
        self.logs: List[Dict[str, Any]] = []
        self.log_hashes: List[str] = []
        self._tree: Optional[MerkleTree] = None
        self._root_hash: Optional[str] = None
    
    def add_log(self, log_entry: Dict[str, Any]) -> str:
        """
        Add a log entry to the logger.
        
        Args:
            log_entry: Log entry dictionary
        
        Returns:
            Hash of the log entry
        """
        entry_hash = hash_log_entry(log_entry)
        self.logs.append(log_entry)
        self.log_hashes.append(entry_hash)
        
        # Invalidate cached tree
        self._tree = None
        self._root_hash = None
        
        return entry_hash
    
    def add_logs(self, log_entries) -> List[str]:
        """
        Add multiple log entries.
        
        Args:
            log_entries: List of log entry dictionaries or SQLAlchemy objects
        
        Returns:
            List of hashes for the entries
        """
        hashes = []
        for entry in log_entries:
            if hasattr(entry, 'to_dict'):
                entry_dict = entry.to_dict()
            elif isinstance(entry, dict):
                entry_dict = entry
            else:
                entry_dict = {
                    "id": str(getattr(entry, 'id', '')),
                    "timestamp": str(getattr(entry, 'timestamp', '')),
                    "attacker_ip": getattr(entry, 'attacker_ip', ''),
                    "command_entered": getattr(entry, 'command_entered', ''),
                    "response_sent": getattr(entry, 'response_sent', ''),
                    "metadata": getattr(entry, 'metadata', {})
                }
            entry_hash = self.add_log(entry_dict)
            hashes.append(entry_hash)
        return hashes
    
    def build_tree(self) -> Optional[str]:
        """
        Build Merkle Tree from collected logs.
        
        Returns:
            Root hash of the tree, or None if no logs
        """
        if not self.logs:
            return None
        
        self._tree = MerkleTree(self.logs)
        self._root_hash = self._tree.root_hash
        
        if self._root_hash:
            logger.info(f"Built Merkle Tree with {len(self.logs)} logs, root: {self._root_hash[:16]}...")
        
        return self._root_hash
    
    @property
    def root_hash(self) -> Optional[str]:
        """Get the current root hash (builds tree if needed)."""
        if self._root_hash is None and self.logs:
            self.build_tree()
        return self._root_hash
    
    @property
    def tree(self) -> Optional[MerkleTree]:
        """Get the current Merkle Tree (builds if needed)."""
        if self._tree is None and self.logs:
            self.build_tree()
        return self._tree
    
    def get_proof_for_log(self, log_index: int) -> Optional[List[Dict[str, str]]]:
        """
        Get Merkle proof for a specific log entry.
        
        Args:
            log_index: Index of the log entry
        
        Returns:
            Merkle proof, or None if tree not built
        """
        if self.tree is None:
            return None
        return self.tree.get_proof(log_index)
    
    def verify_log(
        self,
        log_entry: Dict[str, Any],
        proof: List[Dict[str, str]],
        root_hash: str
    ) -> bool:
        """
        Verify a log entry against a known root hash.
        
        Args:
            log_entry: The log entry to verify
            proof: Merkle proof for the entry
            root_hash: Expected root hash
        
        Returns:
            True if verification succeeds
        """
        leaf_hash = hash_log_entry(log_entry)
        return MerkleTree.verify_proof(leaf_hash, proof, root_hash)
    
    def verify_integrity(self, stored_root_hash: str) -> bool:
        """
        Verify that current logs match a stored root hash.
        
        This is used to detect tampering - if any log has been
        modified, added, or removed, the root hash will differ.
        
        Args:
            stored_root_hash: Previously stored root hash
        
        Returns:
            True if integrity is verified, False if tampering detected
        """
        current_root = self.root_hash
        if current_root is None:
            return stored_root_hash is None
        
        is_valid = current_root == stored_root_hash
        
        if is_valid:
            logger.info("Log integrity verified successfully")
        else:
            logger.warning(
                f"Log integrity check FAILED! "
                f"Expected: {stored_root_hash[:16]}... "
                f"Got: {current_root[:16]}..."
            )
        
        return is_valid
    
    def clear(self) -> None:
        """Clear all logs and reset the logger."""
        self.logs.clear()
        self.log_hashes.clear()
        self._tree = None
        self._root_hash = None
        logger.info("Merkle Logger cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the logger."""
        return {
            "log_count": len(self.logs),
            "root_hash": self.root_hash,
            "has_tree": self._tree is not None
        }


# ============================================================
# Integration with ReputationScores
# ============================================================

async def update_reputation_merkle_root(
    session,
    ip_address: str,
    logs
) -> Tuple[str, str]:
    """
    Update the Merkle root in ReputationScores for an IP address.
    
    This function:
    1. Builds a Merkle Tree from the logs
    2. Stores the root hash in ReputationScores.merkle_root
    3. Returns both the root hash and behavior hash
    
    Args:
        session: SQLAlchemy async session
        ip_address: IP address to update
        logs: List of log entries (can be HoneypotLog objects or dicts)
    
    Returns:
        Tuple of (merkle_root, behavior_hash)
    
    Example:
        >>> logs = await get_logs_by_ip(session, "192.168.1.100")
        >>> merkle_root, behavior_hash = await update_reputation_merkle_root(
        ...     session, "192.168.1.100", logs
        ... )
    """
    from database_postgres import update_reputation_score
    
    log_dicts = []
    for log in logs:
        if hasattr(log, 'to_dict'):
            log_dicts.append(log.to_dict())
        elif isinstance(log, dict):
            log_dicts.append(log)
        else:
            log_dicts.append({
                "id": str(getattr(log, 'id', '')),
                "timestamp": str(getattr(log, 'timestamp', '')),
                "attacker_ip": getattr(log, 'attacker_ip', ''),
                "command_entered": getattr(log, 'command_entered', ''),
                "response_sent": getattr(log, 'response_sent', ''),
                "metadata": getattr(log, 'metadata', {})
            })
    
    merkle_logger = MerkleLogger()
    merkle_logger.add_logs(log_dicts)
    merkle_root = merkle_logger.build_tree()
    
    behavior_data = {
        "ip": ip_address,
        "commands": [log.get("command_entered", "") for log in log_dicts],
        "count": len(log_dicts)
    }
    behavior_hash = hash_log_entry(behavior_data)
    
    if merkle_root:
        await update_reputation_score(
            session,
            ip_address,
            score_delta=0,
            merkle_root=merkle_root
        )
    
    return merkle_root or "", behavior_hash


async def verify_ip_log_integrity(
    session,  # AsyncSession from SQLAlchemy
    ip_address: str,
    stored_root_hash: str
) -> Dict[str, Any]:
    """
    Verify the integrity of logs for a specific IP address.
    
    This function retrieves all logs for an IP, rebuilds the Merkle Tree,
    and compares the root hash with the stored value.
    
    Args:
        session: SQLAlchemy async session
        ip_address: IP address to verify
        stored_root_hash: Previously stored Merkle root hash
    
    Returns:
        Dictionary with verification results:
        {
            "valid": bool,
            "merkle_root": str,
            "log_count": int,
            "verified_at": str
        }
    """
    from database_postgres import get_logs_by_ip
    
    # Get all logs for this IP
    logs = await get_logs_by_ip(session, ip_address)
    
    # Build Merkle Tree
    merkle_logger = MerkleLogger()
    merkle_logger.add_logs(logs)
    current_root = merkle_logger.build_tree()
    
    # Verify
    is_valid = current_root == stored_root_hash if current_root else stored_root_hash is None
    
    return {
        "valid": is_valid,
        "merkle_root": current_root,
        "log_count": len(logs),
        "verified_at": datetime.utcnow().isoformat(),
        "ip_address": ip_address
    }


# ============================================================
# Global Merkle Logger Instance
# ============================================================

# Global instance for use across the application
merkle_logger = MerkleLogger()


# ============================================================
# Convenience Functions
# ============================================================

def hash_entry(log_data: Dict[str, Any]) -> str:
    """Convenience function to hash a single log entry."""
    return hash_log_entry(log_data)


def build_merkle_tree(logs: List[Dict[str, Any]]) -> Optional[str]:
    """Convenience function to build a Merkle Tree and return root hash."""
    tree = MerkleTree(logs)
    return tree.root_hash


def verify_merkle_proof(
    leaf_hash: str,
    proof: List[Dict[str, str]],
    root_hash: str
) -> bool:
    """Convenience function to verify a Merkle proof."""
    return MerkleTree.verify_proof(leaf_hash, proof, root_hash)