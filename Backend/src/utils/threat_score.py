"""
Threat Score System - Blockchain-based IP Reputation Tracking
Assigns reputation scores to IPs based on attack patterns
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
import hashlib
import json

class ThreatScoreSystem:
    def __init__(self):
        # IP reputation scores: {ip_address: score}
        # Score ranges: 0-100 (100 = clean, 0 = highly malicious)
        self.ip_scores: Dict[str, int] = defaultdict(lambda: 100)
        
        # Attack history: {ip_address: [attack_records]}
        self.attack_history: Dict[str, List[dict]] = defaultdict(list)
        
        # Score penalties per attack type
        self.penalties = {
            "SQLI": 15,
            "XSS": 12,
            "SSI": 10,
            "BRUTE_FORCE": 8,
            "BENIGN": 0
        }
        
        # Reputation levels
        self.reputation_levels = {
            "TRUSTED": (90, 100),      # Green
            "NEUTRAL": (70, 89),        # Yellow
            "SUSPICIOUS": (40, 69),     # Orange
            "MALICIOUS": (20, 39),      # Red
            "CRITICAL": (0, 19)         # Dark Red
        }
        
        # Blockchain-like hash chain for immutability
        self.score_chain: List[dict] = []
        
    def calculate_threat_score(self, ip_address: str, attack_type: str, is_malicious: bool) -> int:
        """
        Calculate and update threat score for an IP address
        
        Args:
            ip_address: IP address to score
            attack_type: Type of attack detected
            is_malicious: Whether the attack was malicious
            
        Returns:
            Updated threat score (0-100)
        """
        current_score = self.ip_scores[ip_address]
        
        if not is_malicious:
            # Benign request - slowly improve score (max 100)
            new_score = min(100, current_score + 1)
        else:
            # Malicious attack - apply penalty
            penalty = self.penalties.get(attack_type, 10)
            new_score = max(0, current_score - penalty)
        
        # Record the score change
        self._record_score_change(ip_address, current_score, new_score, attack_type, is_malicious)
        
        # Update score
        self.ip_scores[ip_address] = new_score
        
        return new_score
    
    def _record_score_change(self, ip_address: str, old_score: int, new_score: int, 
                            attack_type: str, is_malicious: bool):
        """Record score change in blockchain-like chain"""
        timestamp = datetime.utcnow()
        
        # Create record
        record = {
            "ip_address": ip_address,
            "old_score": old_score,
            "new_score": new_score,
            "attack_type": attack_type,
            "is_malicious": is_malicious,
            "timestamp": timestamp.isoformat(),
            "previous_hash": self.score_chain[-1]["hash"] if self.score_chain else "0" * 64
        }
        
        # Calculate hash
        record_str = json.dumps(record, sort_keys=True)
        record["hash"] = hashlib.sha256(record_str.encode()).hexdigest()
        
        # Add to chain
        self.score_chain.append(record)
        
        # Add to attack history
        self.attack_history[ip_address].append({
            "timestamp": timestamp,
            "attack_type": attack_type,
            "score_change": new_score - old_score,
            "new_score": new_score
        })
    
    def get_reputation_level(self, score: int) -> str:
        """Get reputation level name from score"""
        for level, (min_score, max_score) in self.reputation_levels.items():
            if min_score <= score <= max_score:
                return level
        return "UNKNOWN"
    
    def get_reputation_color(self, score: int) -> str:
        """Get color code for reputation level"""
        level = self.get_reputation_level(score)
        colors = {
            "TRUSTED": "#4CAF50",      # Green
            "NEUTRAL": "#FFC107",       # Yellow
            "SUSPICIOUS": "#FF9800",    # Orange
            "MALICIOUS": "#F44336",     # Red
            "CRITICAL": "#B71C1C"       # Dark Red
        }
        return colors.get(level, "#757575")
    
    def get_ip_score(self, ip_address: str) -> int:
        """Get current threat score for an IP"""
        return self.ip_scores.get(ip_address, 100)
    
    def get_ip_reputation(self, ip_address: str) -> dict:
        """Get complete reputation info for an IP"""
        score = self.get_ip_score(ip_address)
        level = self.get_reputation_level(score)
        color = self.get_reputation_color(score)
        
        # Get attack statistics
        history = self.attack_history.get(ip_address, [])
        total_attacks = len([h for h in history if h.get("attack_type") != "BENIGN"])
        
        # Get recent attacks (last 24 hours)
        cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_attacks = len([h for h in history if h["timestamp"] > cutoff])
        
        return {
            "ip_address": ip_address,
            "score": score,
            "level": level,
            "color": color,
            "total_attacks": total_attacks,
            "recent_attacks": recent_attacks,
            "first_seen": history[0]["timestamp"].isoformat() if history else None,
            "last_seen": history[-1]["timestamp"].isoformat() if history else None,
            "is_flagged": score < 40  # Flag if suspicious or worse
        }
    
    def get_flagged_ips(self, threshold: int = 40) -> List[dict]:
        """Get all IPs with score below threshold (flagged as malicious)"""
        flagged = []
        for ip, score in self.ip_scores.items():
            if score < threshold:
                flagged.append(self.get_ip_reputation(ip))
        
        # Sort by score (lowest first)
        flagged.sort(key=lambda x: x["score"])
        return flagged
    
    def get_top_threats(self, limit: int = 10) -> List[dict]:
        """Get top threat IPs (lowest scores)"""
        all_ips = [(ip, score) for ip, score in self.ip_scores.items() if score < 100]
        all_ips.sort(key=lambda x: x[1])  # Sort by score ascending
        
        return [self.get_ip_reputation(ip) for ip, _ in all_ips[:limit]]
    
    def verify_chain_integrity(self) -> bool:
        """Verify the integrity of the score chain"""
        if not self.score_chain:
            return True
        
        for i in range(1, len(self.score_chain)):
            current = self.score_chain[i]
            previous = self.score_chain[i - 1]
            
            # Verify previous hash
            if current["previous_hash"] != previous["hash"]:
                return False
            
            # Verify current hash
            record_copy = current.copy()
            stored_hash = record_copy.pop("hash")
            record_str = json.dumps(record_copy, sort_keys=True)
            calculated_hash = hashlib.sha256(record_str.encode()).hexdigest()
            
            if stored_hash != calculated_hash:
                return False
        
        return True
    
    def get_score_history(self, ip_address: str) -> List[dict]:
        """Get score change history for an IP"""
        return self.attack_history.get(ip_address, [])
    
    def reset_score(self, ip_address: str):
        """Reset score for an IP (admin function)"""
        if ip_address in self.ip_scores:
            old_score = self.ip_scores[ip_address]
            self._record_score_change(ip_address, old_score, 100, "RESET", False)
            self.ip_scores[ip_address] = 100

# Global instance
threat_score_system = ThreatScoreSystem()
