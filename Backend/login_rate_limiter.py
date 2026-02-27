from datetime import datetime, timedelta
from typing import Dict, List
from collections import defaultdict

class LoginRateLimiter:
    def __init__(self):
        # Store login attempts: {ip_address: [timestamp1, timestamp2, ...]}
        self.login_attempts: Dict[str, List[datetime]] = defaultdict(list)
        self.max_attempts = 3
        self.time_window = 20  # seconds
        
    def record_attempt(self, ip_address: str) -> bool:
        """
        Record a login attempt and check if it's a brute force attack.
        Returns True if brute force detected (3 or more attempts within 20 seconds), False otherwise.
        """
        current_time = datetime.utcnow()
        
        # Get attempts for this IP
        attempts = self.login_attempts[ip_address]
        
        # Remove old attempts outside the time window
        cutoff_time = current_time - timedelta(seconds=self.time_window)
        self.login_attempts[ip_address] = [
            attempt_time for attempt_time in attempts 
            if attempt_time > cutoff_time
        ]
        
        # Add current attempt
        self.login_attempts[ip_address].append(current_time)
        
        # Check if brute force (3 or more attempts in time_window)
        # This means if this is the 3rd attempt within 20 seconds, it's brute force
        if len(self.login_attempts[ip_address]) >= self.max_attempts:
            return True
        
        return False
    
    def is_rate_limited(self, ip_address: str) -> bool:
        """
        Check if an IP is currently rate limited.
        """
        current_time = datetime.utcnow()
        cutoff_time = current_time - timedelta(seconds=self.time_window)
        
        attempts = self.login_attempts.get(ip_address, [])
        recent_attempts = [t for t in attempts if t > cutoff_time]
        
        return len(recent_attempts) >= self.max_attempts
    
    def reset_attempts(self, ip_address: str):
        """
        Reset login attempts for an IP (e.g., after successful login).
        """
        if ip_address in self.login_attempts:
            del self.login_attempts[ip_address]

# Global instance
login_limiter = LoginRateLimiter()
