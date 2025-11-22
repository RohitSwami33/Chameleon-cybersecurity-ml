# 🔗 Blockchain Explorer - NFT-Style Threat Score Tracking

## Overview

The Blockchain Explorer provides a comprehensive, immutable tracking system for IP reputation scores. Each score change is recorded as a "block" in a blockchain-like structure, similar to NFT ownership records, ensuring complete transparency and auditability.

## Features

### 🎯 Core Capabilities

1. **Immutable Record Keeping**
   - Every threat score change is recorded as a blockchain block
   - Each block contains cryptographic hash linking to previous block
   - Chain integrity verification ensures no tampering

2. **NFT-Style Reputation Tracking**
   - Each IP address has a unique reputation "NFT"
   - Score ranges from 0-100 (like a credit score)
   - Complete history of all score changes
   - Transparent and auditable

3. **Comprehensive Analytics**
   - Total IPs tracked
   - Total blockchain blocks
   - Score distribution across reputation levels
   - Attack type distribution
   - Most active IPs

4. **Advanced Search & Filtering**
   - Filter by IP address
   - View complete history for specific IPs
   - Export blockchain data as JSON

## API Endpoints

### 1. Get Blockchain Data
```
GET /api/threat-scores/blockchain
```

**Parameters:**
- `skip` (int): Pagination offset (default: 0)
- `limit` (int): Number of records (default: 100)
- `ip_address` (string, optional): Filter by specific IP

**Response:**
```json
{
  "total": 150,
  "skip": 0,
  "limit": 100,
  "records": [
    {
      "ip_address": "45.33.32.156",
      "old_score": 40,
      "new_score": 25,
      "attack_type": "SQLI",
      "is_malicious": true,
      "timestamp": "2025-11-22T16:10:45.385951",
      "hash": "a3f5d8c9e2b1...",
      "previous_hash": "b2e4c7a8d1f3..."
    }
  ],
  "chain_integrity": true
}
```

### 2. Get Specific Block
```
GET /api/threat-scores/blockchain/block/{block_index}
```

**Response:**
```json
{
  "block_index": 42,
  "block": {
    "ip_address": "185.220.101.1",
    "old_score": 76,
    "new_score": 64,
    "attack_type": "XSS",
    "is_malicious": true,
    "timestamp": "2025-11-22T16:10:49.719390",
    "hash": "c4d6e8f9a2b3...",
    "previous_hash": "d5e7f9a1b4c6..."
  },
  "is_valid": true,
  "total_blocks": 150
}
```

### 3. Export Blockchain
```
GET /api/threat-scores/blockchain/export
```

**Parameters:**
- `format` (string): Export format (default: "json")
- `ip_address` (string, optional): Filter by specific IP

**Response:**
```json
{
  "blockchain": [...],
  "metadata": {
    "total_blocks": 150,
    "chain_integrity": true,
    "exported_at": "2025-11-22T16:15:00.000000",
    "filter_ip": null
  }
}
```

### 4. Get Analytics
```
GET /api/threat-scores/analytics
```

**Response:**
```json
{
  "total_ips_tracked": 12,
  "total_score_changes": 150,
  "score_distribution": {
    "TRUSTED": 2,
    "NEUTRAL": 5,
    "SUSPICIOUS": 3,
    "MALICIOUS": 1,
    "CRITICAL": 1
  },
  "attack_type_distribution": {
    "SQLI": 45,
    "XSS": 38,
    "SSI": 22,
    "BENIGN": 45
  },
  "most_active_ips": [
    {
      "ip": "45.33.32.156",
      "activity_count": 25
    }
  ],
  "chain_integrity": true
}
```

## UI Components

### Blockchain Explorer Page

Access at: `http://localhost:5174/blockchain`

**Features:**

1. **Analytics Dashboard**
   - Total IPs tracked
   - Total blockchain blocks
   - Chain integrity status
   - Malicious IP count

2. **Search & Filter**
   - Filter by IP address
   - Real-time search
   - Clear filters option

3. **Blockchain Table**
   - Block number
   - Timestamp
   - IP address
   - Attack type
   - Score change (with color coding)
   - New score
   - Block hash (truncated, hover for full)
   - Actions (view details)

4. **Block Details Dialog**
   - Complete block information
   - Full hash values
   - Previous hash link
   - Score change details

5. **Export Functionality**
   - Export entire blockchain as JSON
   - Export filtered data
   - Download to local file

## How It Works

### Blockchain Structure

Each block contains:
```javascript
{
  ip_address: "45.33.32.156",
  old_score: 40,
  new_score: 25,
  attack_type: "SQLI",
  is_malicious: true,
  timestamp: "2025-11-22T16:10:45.385951",
  hash: "SHA256 hash of this block",
  previous_hash: "SHA256 hash of previous block"
}
```

### Score Calculation

**Starting Score:** 100 (clean)

**Penalties:**
- SQL Injection (SQLI): -15
- Cross-Site Scripting (XSS): -12
- Server-Side Injection (SSI): -10
- Brute Force: -8
- Benign Request: +1 (recovery)

**Reputation Levels:**
- 🟢 TRUSTED (90-100): Clean IPs
- 🟡 NEUTRAL (70-89): Normal activity
- 🟠 SUSPICIOUS (40-69): Questionable behavior
- 🔴 MALICIOUS (20-39): Active threats
- ⚫ CRITICAL (0-19): Severe threats

### Chain Integrity

The system verifies:
1. Each block's hash matches its content
2. Each block's previous_hash matches the previous block's hash
3. No blocks have been modified or removed

## Usage Examples

### 1. View All Blockchain Records
```bash
# Login first
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"chameleon2024"}'

# Get blockchain data
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/threat-scores/blockchain?skip=0&limit=50"
```

### 2. Track Specific IP
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/threat-scores/blockchain?ip_address=45.33.32.156"
```

### 3. Export Blockchain
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/threat-scores/blockchain/export" \
  -o blockchain_export.json
```

### 4. Get Analytics
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/threat-scores/analytics"
```

### 5. Verify Chain Integrity
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/threat-scores/verify-chain"
```

## UI Navigation

### From Dashboard
1. Login at `http://localhost:5174/login`
2. Click "Blockchain" button in top navigation
3. Explore blockchain records

### From Blockchain Explorer
1. Click "Dashboard" button to return
2. Or click back arrow icon

## Data Extraction

### Export Options

1. **Full Export**
   - Click "Export JSON" button
   - Downloads complete blockchain
   - Includes metadata and integrity status

2. **Filtered Export**
   - Enter IP address in search
   - Click "Search"
   - Click "Export JSON"
   - Downloads only records for that IP

3. **Programmatic Export**
   ```javascript
   // Using the API
   const response = await api.get('/api/threat-scores/blockchain/export', {
     params: { ip_address: '45.33.32.156' }
   });
   
   // Save to file
   const dataStr = JSON.stringify(response.data, null, 2);
   const blob = new Blob([dataStr], { type: 'application/json' });
   // ... download logic
   ```

## Use Cases

### 1. Forensic Analysis
- Track complete attack history for an IP
- Identify attack patterns
- Generate evidence for incident reports

### 2. Compliance & Auditing
- Prove immutability of records
- Verify chain integrity
- Export for compliance reports

### 3. Threat Intelligence
- Identify most active attackers
- Analyze attack type distribution
- Track reputation changes over time

### 4. Research & Analytics
- Study attack patterns
- Analyze score recovery rates
- Identify trends in malicious activity

## Security Features

1. **Immutability**
   - Cryptographic hashing prevents tampering
   - Chain verification detects modifications
   - Blockchain structure ensures auditability

2. **Authentication**
   - All endpoints require JWT token
   - Protected routes in UI
   - Session management

3. **Data Integrity**
   - SHA-256 hashing
   - Previous hash linking
   - Automatic verification

## Benefits

### For Security Teams
- Complete audit trail
- Transparent reputation system
- Easy forensic analysis
- Exportable evidence

### For Compliance
- Immutable records
- Verifiable integrity
- Comprehensive logging
- Audit-ready exports

### For Research
- Rich dataset
- Historical tracking
- Pattern analysis
- Exportable data

## Future Enhancements

Potential additions:
- Real-time blockchain visualization
- Advanced analytics dashboard
- Machine learning insights
- Integration with threat intelligence feeds
- Multi-chain support for different attack types
- Smart contract-like rules for automatic actions

## Troubleshooting

### Chain Integrity Failed
If chain integrity shows as compromised:
1. Check for system errors in logs
2. Verify no manual database modifications
3. Review recent system changes
4. Contact system administrator

### Missing Records
If records are missing:
1. Check filter settings
2. Verify pagination parameters
3. Ensure proper authentication
4. Check backend logs for errors

### Export Issues
If export fails:
1. Check browser console for errors
2. Verify sufficient disk space
3. Try smaller date ranges
4. Check network connectivity

## Summary

The Blockchain Explorer provides a robust, transparent, and immutable system for tracking IP reputation scores. Like NFTs track digital asset ownership, this system tracks IP reputation changes with complete auditability and transparency. All data can be extracted, verified, and used for forensic analysis, compliance, or research purposes.
