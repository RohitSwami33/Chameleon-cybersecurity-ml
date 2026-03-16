"""
Threat Intelligence Service
Privacy-preserving threat intelligence sharing using cryptographic commitments
"""
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from models import AttackType

class ThreatIntelligenceService:
    """
    Service for detecting novel attacks and creating privacy-preserving threat intelligence.
    Uses cryptographic hashing to share attack patterns without revealing sensitive data.
    """
    
    def __init__(self):
        # Cache of recent attack pattern hashes (last 24 hours)
        self._known_patterns: Set[str] = set()
        self._pattern_timestamps: Dict[str, datetime] = {}
        
        # Threat intelligence reports
        self._threat_reports: List[Dict] = []
        
        # Known attack patterns (for detection)
        self.sqli_patterns = [
            "' OR '1'='1",
            "' OR 1=1--",
            "UNION SELECT",
            "DROP TABLE",
            "'; DROP",
            "admin'--",
            "1' AND '1'='1",
        ]
        
        self.xss_patterns = [
            "<script>",
            "javascript:",
            "onerror=",
            "onload=",
            "<iframe",
            "document.cookie",
        ]
    
    def _create_pattern_hash(self, raw_input: str, attack_type: str) -> str:
        """
        Create a cryptographic hash of the attack pattern.
        This allows sharing without revealing the actual payload.
        
        Args:
            raw_input: The attack payload
            attack_type: Type of attack (SQLI, XSS, etc.)
            
        Returns:
            SHA-256 hash of the pattern
        """
        # Normalize the input (lowercase, remove extra spaces)
        normalized = ' '.join(raw_input.lower().split())
        
        # Create a pattern signature
        pattern_data = f"{attack_type}:{normalized}"
        
        # Generate SHA-256 hash
        return hashlib.sha256(pattern_data.encode()).hexdigest()
    
    def _extract_attack_signature(self, raw_input: str, attack_type: AttackType) -> Optional[str]:
        """
        Extract a generalized signature from the attack.
        This identifies the attack technique without revealing specifics.
        
        Args:
            raw_input: The attack payload
            attack_type: Type of attack
            
        Returns:
            Attack signature or None
        """
        input_lower = raw_input.lower()
        
        if attack_type == AttackType.SQLI:
            for pattern in self.sqli_patterns:
                if pattern.lower() in input_lower:
                    return f"SQLi:{pattern}"
        
        elif attack_type == AttackType.XSS:
            for pattern in self.xss_patterns:
                if pattern.lower() in input_lower:
                    return f"XSS:{pattern}"
        
        return None
    
    def is_novel_attack(self, raw_input: str, attack_type: AttackType) -> bool:
        """
        Determine if this is a novel attack pattern we haven't seen recently.
        
        Args:
            raw_input: The attack payload
            attack_type: Type of attack
            
        Returns:
            True if this is a novel pattern
        """
        # Only consider malicious attacks
        if attack_type == AttackType.BENIGN:
            return False
        
        # Create pattern hash
        pattern_hash = self._create_pattern_hash(raw_input, attack_type.value)
        
        # Clean up old patterns (older than 24 hours)
        self._cleanup_old_patterns()
        
        # Check if we've seen this pattern recently
        if pattern_hash in self._known_patterns:
            return False
        
        # This is a novel pattern
        self._known_patterns.add(pattern_hash)
        self._pattern_timestamps[pattern_hash] = datetime.utcnow()
        
        return True
    
    def _cleanup_old_patterns(self):
        """Remove patterns older than 24 hours from the cache."""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        patterns_to_remove = [
            pattern_hash 
            for pattern_hash, timestamp in self._pattern_timestamps.items()
            if timestamp < cutoff_time
        ]
        
        for pattern_hash in patterns_to_remove:
            self._known_patterns.discard(pattern_hash)
            self._pattern_timestamps.pop(pattern_hash, None)
    
    def create_threat_report(
        self, 
        raw_input: str, 
        attack_type: AttackType,
        ip_address: str,
        confidence: float
    ) -> Optional[Dict]:
        """
        Create a privacy-preserving threat intelligence report.
        
        Args:
            raw_input: The attack payload
            attack_type: Type of attack
            ip_address: Attacker IP (will be hashed)
            confidence: Classification confidence
            
        Returns:
            Threat report dictionary or None
        """
        # Extract attack signature
        signature = self._extract_attack_signature(raw_input, attack_type)
        if not signature:
            return None
        
        # Create pattern hash (public commitment)
        pattern_hash = self._create_pattern_hash(raw_input, attack_type.value)
        
        # Create IP hash (privacy-preserving)
        ip_hash = hashlib.sha256(ip_address.encode()).hexdigest()[:16]
        
        # Create threat report
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "attack_type": attack_type.value,
            "pattern_hash": pattern_hash,
            "signature": signature,
            "ip_hash": ip_hash,
            "confidence": confidence,
            "severity": self._calculate_severity(attack_type, confidence)
        }
        
        # Add to local reports
        self._threat_reports.append(report)
        
        # Keep only last 100 reports
        if len(self._threat_reports) > 100:
            self._threat_reports = self._threat_reports[-100:]
        
        return report
    
    def _calculate_severity(self, attack_type: AttackType, confidence: float) -> str:
        """
        Calculate threat severity based on attack type and confidence.
        
        Args:
            attack_type: Type of attack
            confidence: Classification confidence
            
        Returns:
            Severity level (LOW, MEDIUM, HIGH, CRITICAL)
        """
        # Base severity by attack type
        severity_map = {
            AttackType.SQLI: 3,  # High
            AttackType.XSS: 2,   # Medium
            AttackType.SSI: 3,   # High
            AttackType.BRUTE_FORCE: 2,  # Medium
            AttackType.BENIGN: 0  # None
        }
        
        base_severity = severity_map.get(attack_type, 1)
        
        # Adjust by confidence
        if confidence >= 0.9:
            base_severity += 1
        elif confidence < 0.7:
            base_severity -= 1
        
        # Map to severity levels
        if base_severity >= 4:
            return "CRITICAL"
        elif base_severity == 3:
            return "HIGH"
        elif base_severity == 2:
            return "MEDIUM"
        else:
            return "LOW"
    
    def get_threat_reports(self, limit: int = 50) -> List[Dict]:
        """
        Get recent threat intelligence reports.
        
        Args:
            limit: Maximum number of reports to return
            
        Returns:
            List of threat reports
        """
        return self._threat_reports[-limit:]
    
    def get_statistics(self) -> Dict:
        """
        Get threat intelligence statistics.
        
        Returns:
            Statistics dictionary
        """
        total_patterns = len(self._known_patterns)
        total_reports = len(self._threat_reports)
        
        # Count by attack type
        attack_type_counts = {}
        for report in self._threat_reports:
            attack_type = report["attack_type"]
            attack_type_counts[attack_type] = attack_type_counts.get(attack_type, 0) + 1
        
        # Count by severity
        severity_counts = {}
        for report in self._threat_reports:
            severity = report["severity"]
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Recent attacks (last hour)
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_attacks = sum(
            1 for report in self._threat_reports
            if datetime.fromisoformat(report["timestamp"]) > one_hour_ago
        )
        
        return {
            "total_patterns": total_patterns,
            "total_reports": total_reports,
            "recent_attacks": recent_attacks,
            "attack_type_distribution": attack_type_counts,
            "severity_distribution": severity_counts
        }

# Global instance
threat_intel_service = ThreatIntelligenceService()
