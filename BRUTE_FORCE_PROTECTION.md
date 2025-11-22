# Brute Force Protection - Updated Settings

## ✅ Configuration Updated

### New Settings
- **Max Attempts**: 3 unsuccessful login attempts
- **Time Window**: 20 seconds
- **Trigger**: Exactly at the 3rd attempt (changed from 4th)

### What Changed

**File**: `login_rate_limiter.py`

1. **Time Window**: Increased from 10 to 20 seconds
   ```python
   self.time_window = 20  # seconds (was 10)
   ```

2. **Trigger Logic**: Changed from `>` to `>=`
   ```python
   # Before: triggered at 4+ attempts
   if len(self.login_attempts[ip_address]) > self.max_attempts:
   
   # After: triggers at exactly 3 attempts  
   if len(self.login_attempts[ip_address]) >= self.max_attempts:
   ```

### Behavior

**Timeline Example:**
- **0s**: Attempt 1 - Failed (401)
- **5s**: Attempt 2 - Failed (401)  
- **10s**: Attempt 3 - **BLOCKED** (429 - Brute Force Detected)
- **10s-30s**: All attempts blocked (429)
- **After 30s**: Window reset, can try again

### Test Results

```bash
Attempt 1: HTTP 401 - "Incorrect username or password"
Attempt 2: HTTP 401 - "Incorrect username or password"
Attempt 3: HTTP 429 - "Brute force attack detected. Account temporarily locked."
```

### What Gets Logged to Database

1. **Attempt 1-2**: Each logged as BENIGN with 0.5 confidence
2. **Attempt 3**: Logged as BRUTE_FORCE with 1.0 confidence
3. **Further attempts**: Logged as BRUTE_FORCE (blocked)

### Dashboard Display

All brute force attempts will appear in the dashboard with:
- **Attack Type**: BRUTE_FORCE (purple chip)
- **Confidence**: 100%
- **Status**: Visible in attack logs table
- **Filter**: Can filter by "Brute Force" type
