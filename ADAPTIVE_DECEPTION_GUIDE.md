# Adaptive Deception & Geolocation Features Guide

## Overview

This guide documents the enhanced adaptive deception system and IP geolocation features added to the Chameleon Cybersecurity ML system.

## 🎭 Adaptive Deception Engine

### What is Adaptive Deception?

The Adaptive Deception Engine generates fake error messages tailored to the specific type of attack detected. This misleads attackers into thinking their attacks are failing for technical reasons, while the system logs the real attack internally.

### How It Works

1. **Attack Detection**: The ML classifier identifies the attack type (SQLi, XSS, SSI, Brute Force, or Benign)
2. **Context Analysis**: The system analyzes the attack input for specific patterns
3. **Deceptive Response**: A fake error message is generated that matches the attack type
4. **Internal Logging**: The real attack is logged to the database and blockchain
5. **Attacker Receives**: Only the fake error message, not the real system response

### Attack-Specific Deception

#### SQL Injection (SQLi)
**HTTP Status**: 500 (Internal Server Error)

**Fake Error Messages**:
- "Error: You have an error in your SQL syntax..."
- "MySQL Error 1064: Syntax error near 'SELECT' at line 1"
- "Table 'users' doesn't exist in database 'production_db'"
- "Access denied for user 'root'@'localhost'"
- "Unknown column 'admin' in 'field list'"

**Context-Aware Responses**:
- If input contains "UNION" → "Error: UNION query with different number of columns"
- If input contains "DROP" → "Error: DROP command denied to user 'webapp'@'localhost'"
- If input contains "information_schema" → "Error: SELECT command denied on table 'information_schema.tables'"

#### Cross-Site Scripting (XSS)
**HTTP Status**: 200 (Success - to make attacker think it worked)

**Fake Error Messages**:
- "Input validated successfully. Content sanitized."
- "Form submitted. Thank you for your feedback."
- "Error: Invalid HTML detected. Content has been escaped."
- "Content-Security-Policy violation detected and blocked."
- "Script execution blocked by XSS protection."

#### Server-Side Includes (SSI)
**HTTP Status**: 403 (Forbidden)

**Fake Error Messages**:
- "Server-side includes are disabled on this server."
- "Error: SSI directives not allowed in user input."
- "Apache SSI module not enabled."
- "SSI parsing disabled for security reasons."

#### Brute Force
**HTTP Status**: 401 (Unauthorized)

**Fake Error Messages**:
- "Invalid credentials. Please try again."
- "Login failed. 2 attempts remaining."
- "Account locked due to suspicious activity."
- "Too many failed login attempts. Please try again in 15 minutes."

#### Benign Requests
**HTTP Status**: 200 (Success)

**Responses**:
- "Request processed successfully."
- "Operation completed."
- "Data retrieved successfully."

### Implementation Details

#### File: `Backend/deception_engine.py`

```python
class DeceptionEngine:
    def get_deceptive_error(self, attack_type: AttackType, input_snippet: str = "") -> str:
        """Generate context-aware fake error message"""
        
    def generate_response(self, attack_type: AttackType, apply_delay: float, input_snippet: str = "") -> DeceptionResponse:
        """Generate complete deception response with HTTP status"""
```

#### Usage in Main API

```python
# In Backend/main.py
deception = deception_engine.generate_response(
    classification.attack_type, 
    delay,
    user_input.input_text[:100]  # Pass first 100 chars for context
)
```

## 🌍 IP Geolocation Features

### Geographic Attack Tracking

The system now tracks and visualizes the geographic origin of attacks using IP geolocation.

### Features

1. **Automatic IP Geolocation**: Every attack is geolocated using the ip-api.com service
2. **Geographic Dashboard**: Visual display of top attack origins
3. **Location Details in Logs**: Each log entry shows city, region, country, and ISP
4. **Attack Heatmap Data**: Aggregated data for geographic analysis

### Data Collected

For each IP address:
- **Country**: Country name
- **Region**: State/Province
- **City**: City name
- **Latitude/Longitude**: Geographic coordinates
- **ISP**: Internet Service Provider

### Dashboard Components

#### GeoMap Component (`frontend/src/components/GeoMap.jsx`)

Displays:
- Top 10 attack origin locations
- Attack count per location
- Geographic coordinates
- Visual indicators with location pins

#### Enhanced Attack Logs

Each log entry now shows:
- IP Address
- Location: "City, Region, Country (ISP)"
- Example: "Mumbai, Maharashtra, India (Reliance Jio)"

### Database Aggregation

The system aggregates geographic data:

```python
# In Backend/database.py
geo_pipeline = [
    {"$match": {"geo_location": {"$ne": None}, "classification.is_malicious": True}},
    {"$group": {
        "_id": {
            "country": "$geo_location.country",
            "city": "$geo_location.city",
            "latitude": "$geo_location.latitude",
            "longitude": "$geo_location.longitude"
        },
        "count": {"$sum": 1}
    }},
    {"$sort": {"count": -1}},
    {"$limit": 50}
]
```

## 📊 Dashboard Layout

### New Layout Structure

1. **Stats Cards** (Top Row)
   - Total Attempts
   - Malicious Attacks
   - Benign Requests
   - Chain Integrity

2. **Visualization Row** (Middle)
   - **Left**: Attack Distribution Chart (Pie/Bar)
   - **Right**: Geographic Attack Origins Map

3. **System Health** (Below Charts)
   - Deception Engine Status
   - Blockchain Node Status
   - Tarpit Status

4. **Attack Logs Table** (Bottom)
   - Expandable rows with location details
   - Filter by attack type and IP
   - Generate reports per IP

## 🔧 Configuration

### Environment Variables

No additional configuration needed. The system uses:
- **GeoIP API**: `http://ip-api.com/json/` (free, no API key required)
- **Rate Limit**: Automatic (45 requests/minute)

### Customization

#### Add More Deceptive Messages

Edit `Backend/deception_engine.py`:

```python
self.sql_errors = [
    "Your custom SQL error message here",
    # ... more messages
]
```

#### Change Geolocation Provider

Edit `Backend/main.py`:

```python
async def fetch_geo_location(ip: str) -> Optional[GeoLocation]:
    # Replace with your preferred geolocation API
    response = await client.get(f"https://your-api.com/{ip}")
```

## 🧪 Testing

### Test Adaptive Deception

```bash
# Test SQLi deception
curl -X POST http://localhost:8000/api/trap/submit \
  -H "Content-Type: application/json" \
  -d '{"input_text":"' OR 1=1 --"}'

# Expected: 500 status with fake SQL error

# Test XSS deception
curl -X POST http://localhost:8000/api/trap/submit \
  -H "Content-Type: application/json" \
  -d '{"input_text":"<script>alert(1)</script>"}'

# Expected: 200 status with fake success message

# Test SSI deception
curl -X POST http://localhost:8000/api/trap/submit \
  -H "Content-Type: application/json" \
  -d '{"input_text":"<!--#exec cmd=\"ls\" -->"}'

# Expected: 403 status with SSI disabled message
```

### Test Geolocation

```bash
# Submit attack from external IP (not localhost)
curl -X POST http://your-server:8000/api/trap/submit \
  -H "Content-Type: application/json" \
  -d '{"input_text":"malicious input"}'

# Check dashboard for geographic data
# Visit: http://localhost:5174/dashboard
```

## 📈 Benefits

### Security Benefits

1. **Attacker Confusion**: Fake errors mislead attackers about system vulnerabilities
2. **Time Wasting**: Attackers spend time debugging fake errors
3. **False Confidence**: XSS attackers think their attacks succeeded (but they didn't)
4. **Intelligence Gathering**: System learns attack patterns while appearing vulnerable

### Operational Benefits

1. **Geographic Insights**: Identify attack origin countries and regions
2. **ISP Tracking**: Identify malicious ISPs or hosting providers
3. **Pattern Recognition**: Correlate attack types with geographic locations
4. **Threat Intelligence**: Build database of malicious IPs and locations

## 🔒 Security Considerations

1. **Real Logging**: All attacks are logged internally regardless of deceptive response
2. **Blockchain Integrity**: Attack logs are immutably stored on blockchain
3. **No Information Leakage**: Fake errors don't reveal real system information
4. **Tarpit Integration**: Deception works with tarpit delays to slow attackers

## 📝 Summary

The enhanced Chameleon system now provides:

✅ **Adaptive Deception**: Context-aware fake error messages per attack type
✅ **Geographic Tracking**: IP geolocation for all attacks
✅ **Visual Dashboard**: Geographic attack origin visualization
✅ **Enhanced Logging**: Location details in attack logs
✅ **Intelligence Gathering**: Build threat intelligence database

All while maintaining the core security features:
- ML-based attack classification
- Blockchain logging
- Tarpit delays
- Real-time monitoring
