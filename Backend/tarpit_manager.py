import time
import random
from typing import Tuple, Dict, List
from config import settings
from datetime import datetime, timedelta

class TarpitManager:
    def __init__(self):
        self.request_timestamps: Dict[str, List[float]] = {}
        self.blocked_ips: Dict[str, datetime] = {}

    def clean_old_requests(self, ip: str):
        current_time = time.time()
        if ip in self.request_timestamps:
            # Keep only requests from the last 60 seconds
            self.request_timestamps[ip] = [
                ts for ts in self.request_timestamps[ip] 
                if current_time - ts <= 60
            ]
            if not self.request_timestamps[ip]:
                del self.request_timestamps[ip]

    def record_request(self, ip: str) -> Tuple[bool, float]:
        self.clean_old_requests(ip)
        
        current_time = time.time()
        if ip not in self.request_timestamps:
            self.request_timestamps[ip] = []
        
        self.request_timestamps[ip].append(current_time)
        
        count = len(self.request_timestamps[ip])
        
        if count > settings.TARPIT_THRESHOLD:
            excess_requests = count - settings.TARPIT_THRESHOLD
            delay = settings.TARPIT_DELAY_MIN + (excess_requests * 0.5)
            
            # Add random variation
            variation = random.uniform(-0.5, 0.5)
            delay += variation
            
            # Cap at max delay
            delay = min(delay, settings.TARPIT_DELAY_MAX)
            delay = max(delay, 0.0) # Ensure non-negative
            
            return True, delay
            
        return False, 0.0

    def is_blocked(self, ip: str) -> bool:
        if ip in self.blocked_ips:
            expiry = self.blocked_ips[ip]
            if datetime.utcnow() > expiry:
                del self.blocked_ips[ip]
                return False
            return True
        return False

    def block_ip(self, ip: str, duration_minutes: int):
        expiry = datetime.utcnow() + timedelta(minutes=duration_minutes)
        self.blocked_ips[ip] = expiry

tarpit_manager = TarpitManager()
