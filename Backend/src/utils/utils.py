from datetime import datetime, timezone, timedelta

# Indian Standard Time (IST) is UTC+5:30
IST = timezone(timedelta(hours=5, minutes=30))

def get_current_time():
    """Get current time in IST timezone"""
    return datetime.now(IST)

def get_utc_time():
    """Get current time in UTC (for backward compatibility)"""
    return datetime.utcnow()
