# 🚀 Quick Reference Card

## Access Points

| Service | URL | Credentials |
|---------|-----|-------------|
| **Dashboard** | http://localhost:5174/dashboard | admin / chameleon2024 |
| **API** | http://localhost:8000 | - |
| **API Docs** | http://localhost:8000/docs | - |
| **Health Check** | http://localhost:8000/api/health | - |

## Quick Test Commands

### Test SQLi (Context-Aware)
```bash
curl -X POST http://localhost:8000/api/trap/submit \
  -H "Content-Type: application/json" \
  -d '{"input_text":"SELECT * FROM users UNION SELECT password","ip_address":"8.8.8.8"}'
```
**Expected**: `"Error: UNION query with different number of columns"` (500)

### Test XSS
```bash
curl -X POST http://localhost:8000/api/trap/submit \
  -H "Content-Type: application/json" \
  -d '{"input_text":"<script>alert(1)</script>","ip_address":"1.1.1.1"}'
```
**Expected**: Fake success message (200)

### Test SSI
```bash
curl -X POST http://localhost:8000/api/trap/submit \
  -H "Content-Type: application/json" \
  -d '{"input_text":"<!--#exec cmd=\"ls\" -->","ip_address":"45.33.32.156"}'
```
**Expected**: `"SSI directives not allowed"` (403)

### Run Full Test Suite
```bash
./test_deception.sh
```

## Dashboard Features

### Stats Cards
- Total Attempts
- Malicious Attacks (with percentage)
- Benign Requests
- Chain Integrity

### Visualizations
- **Attack Distribution** (Pie/Bar Chart)
- **Geographic Origins** (Location Map)
- **System Health** (Status Panel)
- **Attack Logs** (Detailed Table)

### Filters
- Search by IP address
- Filter by attack type (All, SQLI, XSS, SSI, BRUTE_FORCE, BENIGN)
- Auto-refresh toggle (10s interval)

## Attack Types & Responses

| Type | HTTP Status | Example Response |
|------|-------------|------------------|
| **SQLI** | 500 | "MySQL Error 1064: Syntax error..." |
| **XSS** | 200 | "Input validated successfully..." |
| **SSI** | 403 | "SSI directives not allowed..." |
| **BRUTE_FORCE** | 401 | "Account locked..." |
| **BENIGN** | 200 | "Request processed successfully" |

## Context-Aware SQLi Responses

| Pattern | Response |
|---------|----------|
| Contains "UNION" | "UNION query with different number of columns" |
| Contains "DROP" | "DROP command denied to user 'webapp'" |
| Contains "information_schema" | "SELECT command denied on table..." |

## Geographic Data

### Tracked Information
- Country
- Region/State
- City
- Latitude/Longitude
- ISP

### Current Coverage
- 12+ unique locations
- 6+ countries
- 3 continents

## File Locations

### Backend
- `Backend/deception_engine.py` - Fake error messages
- `Backend/main.py` - API endpoints
- `Backend/database.py` - Geographic aggregation
- `Backend/models.py` - Data models

### Frontend
- `frontend/src/components/Dashboard.jsx` - Main dashboard
- `frontend/src/components/GeoMap.jsx` - Geographic map
- `frontend/src/components/AttackLogs.jsx` - Attack logs table

### Documentation
- `ADAPTIVE_DECEPTION_GUIDE.md` - Complete guide
- `TESTING_RESULTS.md` - Test results
- `FINAL_STATUS.md` - Current status
- `QUICK_REFERENCE.md` - This file

## Common Tasks

### Start Services
```bash
# Backend
cd Backend && uvicorn main:app --reload

# Frontend
cd frontend && npm run dev
```

### Check Logs
```bash
# Backend logs
tail -f Backend/data/mongod.log

# Check attack count
curl -s http://localhost:8000/api/dashboard/stats | python3 -m json.tool
```

### Generate Report
```bash
# Via API
curl -X POST http://localhost:8000/api/reports/generate/8.8.8.8 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output report.pdf

# Via Dashboard
Click PDF icon next to any IP in attack logs
```

## Troubleshooting

### No Geographic Data
**Issue**: "No geographic data available"
**Fix**: Submit attacks from external IPs (not 127.0.0.1)
```bash
curl -X POST http://localhost:8000/api/trap/submit \
  -H "Content-Type: application/json" \
  -d '{"input_text":"test","ip_address":"8.8.8.8"}'
```

### Dashboard Not Loading
**Fix**: 
1. Check backend is running: `curl http://localhost:8000/api/health`
2. Check frontend is running: `curl http://localhost:5174`
3. Clear browser cache
4. Check console for errors

### Fake Errors Not Showing
**Fix**:
1. Verify attack is detected: Check classification in logs
2. Check deception_engine.py is loaded
3. Restart backend service

## API Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/trap/submit` | POST | No | Submit attack |
| `/api/auth/login` | POST | No | Login |
| `/api/dashboard/stats` | GET | Yes | Get statistics |
| `/api/dashboard/logs` | GET | Yes | Get attack logs |
| `/api/reports/generate/{ip}` | POST | Yes | Generate PDF |
| `/api/health` | GET | No | Health check |

## Environment Variables

### Backend (.env)
```
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=chameleon_db
ADMIN_USERNAME=admin
ADMIN_PASSWORD=chameleon2024
JWT_SECRET_KEY=your-secret-key
```

### Frontend (.env)
```
VITE_API_BASE_URL=http://localhost:8000
```

## Performance

- **Response Time**: < 100ms
- **Geolocation**: < 500ms
- **Dashboard Load**: < 2s
- **Auto-refresh**: Every 10s

## Security Notes

✅ All attacks logged internally
✅ Fake errors don't reveal system info
✅ Real errors never sent to attacker
✅ Blockchain logging for integrity
✅ Rate limiting enabled
✅ JWT authentication for dashboard

## Support

📚 **Documentation**: See all .md files in root directory
🧪 **Testing**: Run `./test_deception.sh`
🐛 **Issues**: Check browser console and backend logs
📊 **Stats**: Visit dashboard or call `/api/dashboard/stats`

---

**Version**: 2.0.0
**Status**: ✅ Production Ready
**Last Updated**: November 22, 2025
