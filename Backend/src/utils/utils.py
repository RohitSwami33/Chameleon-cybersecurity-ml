from datetime import datetime, timezone, timedelta
from ipaddress import ip_address, ip_network
import re

# Indian Standard Time (IST) is UTC+5:30
IST = timezone(timedelta(hours=5, minutes=30))

# Trusted proxy CIDRs (private IP ranges)
TRUSTED_PROXY_CIDRS = [
    ip_network("127.0.0.0/8"),
    ip_network("10.0.0.0/8"),
    ip_network("172.16.0.0/12"),
    ip_network("192.168.0.0/16"),
]

# IP validation regex patterns (EC-023)
_IPV4_RE = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
_IPV6_RE = re.compile(r'^[0-9a-fA-F:]{2,45}$')


def validate_ip(ip: str) -> str:
    """
    Validate and sanitise IP address to prevent 2MB string injection.
    EC-023: Limits IP to 45 chars max and validates format.
    """
    if not ip:
        raise ValueError("Empty IP")
    ip = ip.strip()[:45]
    if _IPV4_RE.match(ip) or _IPV6_RE.match(ip):
        return ip
    raise ValueError(f"Invalid IP: {ip[:20]!r}")


def real_ip(request) -> str:
    """Extract the real client IP, ignoring spoofed X-Forwarded-For headers."""
    socket_ip = request.client.host if request.client else "0.0.0.0"
    xff = request.headers.get("x-forwarded-for", "")
    if not xff:
        return socket_ip
    candidates = [x.strip() for x in xff.split(",")][::-1]
    for candidate in candidates:
        try:
            addr = ip_address(candidate)
            if not any(addr in net for net in TRUSTED_PROXY_CIDRS):
                return candidate
        except ValueError:
            continue
    return socket_ip


def get_current_time():
    """Get current time in IST timezone"""
    return datetime.now(IST)

def get_utc_time():
    """Get current time in UTC (for backward compatibility)"""
    return datetime.utcnow()
