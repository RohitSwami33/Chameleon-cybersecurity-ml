# Chameleon Frontend-Backend Integration

## Integration Status ✅

The Chameleon frontend and backend are now successfully integrated and running!

### Running Services

1. **Frontend**: http://localhost:5173/
   - TrapInterface (Honeypot): http://localhost:5173/
   - Forensic Dashboard: http://localhost:5173/dashboard

2. **Backend API**: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/api/health

3. **Database**: MongoDB running on localhost:27017

## Integration Test Results

### Backend API Test
```bash
$ curl http://localhost:8000/api/health
{"status":"healthy","timestamp":"2025-11-22T10:26:42.892204"}
```

### Honeypot Test
Submitted a SQL injection attack:
```bash
$ curl -X POST http://localhost:8000/api/trap/submit \
  -H "Content-Type: application/json" \
  -d '{"input_text":"admin OR 1=1","user_agent":"Mozilla/5.0"}'
```

Response:
```json
{
  "message":"Error: You have an error in your SQL syntax...",
  "delay_applied":0.0,
  "http_status":500
}
```

### Dashboard Stats
After the attack, the dashboard shows:
```json
{
  "total_attempts": 1,
  "malicious_attempts": 1,
  "benign_attempts": 0,
  "attack_distribution": {
    "SQLI": 1
  },
  "top_attackers": [
    {
      "ip": "127.0.0.1",
      "count": 1,
      "last_seen": "2025-11-22T10:27:09.486000"
    }
  ],
  "merkle_root": "2fbd935c91adee4bf119c39b171268d0c7a6364cfaed8246ee82cbcb3f125bfe"
}
```

## Changes Made for Integration

### 1. Backend Configuration
- **File**: `/Backend/.env`
- **Change**: Switched from MongoDB Atlas to local MongoDB
  ```
  MONGODB_URL=mongodb://localhost:27017
  ```

### 2. Database Connection
- **File**: `/Backend/database.py`
- **Change**: Removed TLS certificate requirement for local MongoDB
  ```python
  db.client = AsyncIOMotorClient(settings.MONGODB_URL)  # Removed tlsCAFile parameter
  ```

### 3. MongoDB Service
- Started local MongoDB service:
  ```bash
  brew services start mongodb-community
  ```

### 4. Backend Dependencies
- Recreated virtual environment and installed dependencies
- Backend now running with uvicorn on port 8000

### 5. Frontend Configuration
- **File**: `/frontend/.env`
- Already configured to point to http://localhost:8000

## How to Use

### Start Backend
```bash
cd /Users/rohit/Desktop/Projects/hackathon/project/Backend
source .venv/bin/activate
uvicorn main:app --reload --port 8000
```

### Start Frontend
```bash
cd /Users/rohit/Desktop/Projects/hackathon/project/frontend
npm run dev
```

### Test the System

1. **Access the Trap Interface**: 
   - Open http://localhost:5173/ in your browser
   - Try logging in with malicious input like `' OR '1'='1`
   - The system will detect and log the attack

2. **View the Dashboard**:
   - Navigate to http://localhost:5173/dashboard
   - See real-time statistics and attack logs
   - Auto-refresh is enabled by default

3. **Generate Reports**:
   - In the attack logs table, click the PDF icon
   - Download incident reports for specific IP addresses

## CORS Configuration
The backend is configured to accept requests from any origin:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## API Endpoints Being Used

- `POST /api/trap/submit` - Submit user input for analysis
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/dashboard/logs` - Get attack logs with pagination
- `POST /api/reports/generate/{ip}` - Generate PDF report
- `GET /api/blockchain/verify` - Verify blockchain integrity

## Next Steps

You can now:
- ✅ Test the honeypot by submitting various attack patterns
- ✅ Monitor attacks in real-time via the dashboard
- ✅ Generate incident reports for analysis
- ✅ Verify blockchain integrity of logged attacks
