import hashlib
import json
from typing import List, Optional, Dict
from datetime import datetime

class BlockchainLogger:
    def __init__(self):
        self.chain: List[Dict] = []

    def calculate_hash(self, data: dict, previous_hash: str) -> str:
        # Create a block structure to hash
        block_content = {
            "data": data,
            "previous_hash": previous_hash
        }
        # Sort keys to ensure consistent hashing
        block_string = json.dumps(block_content, sort_keys=True, default=str)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def add_block(self, log_data: dict) -> dict:
        previous_hash = "0" * 64
        if self.chain:
            previous_hash = self.chain[-1]["hash"]
            
        current_hash = self.calculate_hash(log_data, previous_hash)
        
        block = {
            "hash": current_hash,
            "previous_hash": previous_hash,
            "data": log_data
        }
        
        self.chain.append(block)
        return {"hash": current_hash, "previous_hash": previous_hash}

    def calculate_merkle_root(self, hashes: List[str]) -> Optional[str]:
        if not hashes:
            return None
        if len(hashes) == 1:
            return hashes[0]
            
        new_level = []
        # If odd number of hashes, duplicate the last one
        if len(hashes) % 2 != 0:
            hashes.append(hashes[-1])
            
        for i in range(0, len(hashes), 2):
            pair = hashes[i] + hashes[i+1]
            new_level.append(hashlib.sha256(pair.encode()).hexdigest())
            
        return self.calculate_merkle_root(new_level)

    def get_merkle_root_for_recent_logs(self, logs: List[dict]) -> Optional[str]:
        hashes = [log.get("hash") for log in logs if log.get("hash")]
        if not hashes:
            return None
        return self.calculate_merkle_root(hashes)

    def verify_chain_integrity(self) -> bool:
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            # Verify previous hash link
            if current_block["previous_hash"] != previous_block["hash"]:
                return False
                
            # Verify current hash
            recalculated_hash = self.calculate_hash(current_block["data"], current_block["previous_hash"])
            if recalculated_hash != current_block["hash"]:
                return False
                
        return True

blockchain_logger = BlockchainLogger()
