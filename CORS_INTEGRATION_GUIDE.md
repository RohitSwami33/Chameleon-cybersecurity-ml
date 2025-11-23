# Frontend-Backend CORS Integration Guide

## ✅ Integration Status: FULLY CONFIGURED

All integration tests passed successfully! The frontend and backend are properly connected with CORS configured.

## 🔧 Configuration Details

### Backend CORS Configuration
**File**: `Backend/main.py`

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default dev server
        "http://localhost:5174",  # Alternative Vite port
        "http://localhost:3000",  # React default
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:3000",
        "*"  # Allow all origins (for development)
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)
```

### Frontend API Configuration
**File**: `frontend/src/services/api.js`

```javascript
const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

### Environment Variables
**File**: `frontend/.env`

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## 🧪 Integration Tests

Run the integration test script:

```bash
./test_integration.sh
```

### Test Results (All Passed ✅)

1. ✅ **Backend Health Check** - Backend responding correctly
2. ✅ **CORS Headers** - Proper CORS headers configured
3. ✅ **Frontend Accessibility** - Frontend server running
4. ✅ **Login Endpoint** - Authentication working
5. ✅ **Protected Endpoints** - JWT token authentication working
6. ✅ **Chatbot Endpoint** - AI chatbot API responding

## 🌐 API Endpoints

### Public Endpoints
- `GET /api/health` - Health check
- `POST /api/auth/login` - User authentication
- `POST /api/trap/submit` - Honeypot trap submission

### Protected Endpoints (Require JWT Token)
- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/dashboard/logs` - Attack logs
- `POST /api/chatbot/chat` - AI chatbot
- `GET /api/chatbot/history` - Chat history
- `POST /api/chatbot/clear-history` - Clear chat
- `POST /api/chatbot/analyze-attack/{log_id}` - AI attack analysis
- `GET /api/threat-intel/reports` - Threat intelligence
- `GET /api/blockchain/verify` - Blockchain verification

## 🔐 Authentication Flow

### 1. Login Request
```javascript
const response = await api.post('/api/auth/login', {
  username: 'admin',
  password: 'chameleon2024'
});
```

### 2. Store Token
```javascript
localStorage.setItem('authToken', response.data.access_token);
```

### 3. Automatic Token Injection
The axios interceptor automatically adds the token to all requests:

```javascript
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### 4. Automatic Logout on 401
```javascript
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

## 📡 Request/Response Flow

### Example: Chatbot Request

**Frontend**:
```javascript
const response = await api.post('/api/chatbot/chat', {
  message: 'What is SQL injection?',
  use_search: false
});
```

**Backend Receives**:
```
POST http://localhost:8000/api/chatbot/chat
Headers:
  Content-Type: application/json
  Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
  Origin: http://localhost:5174
Body:
  {
    "message": "What is SQL injection?",
    "use_search": false
  }
```

**Backend Responds**:
```json
{
  "success": true,
  "response": "SQL injection is a code injection technique...",
  "search_results": [],
  "timestamp": "2025-11-23T00:10:00.000Z"
}
```

**CORS Headers Included**:
```
Access-Control-Allow-Origin: http://localhost:5174
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS, PATCH
```

## 🚀 Running the Application

### Start Backend
```bash
cd Backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### Start Frontend
```bash
cd frontend
npm run dev
```

### Access Points
- **Frontend**: http://localhost:5174
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Chatbot Page**: http://localhost:5174/dashboard/chatbot

## 🔍 Debugging CORS Issues

### Check CORS Headers
```bash
curl -I -X OPTIONS http://localhost:8000/api/health \
  -H "Origin: http://localhost:5174" \
  -H "Access-Control-Request-Method: GET"
```

### Expected Response
```
HTTP/1.1 200 OK
access-control-allow-origin: http://localhost:5174
access-control-allow-credentials: true
access-control-allow-methods: DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT
```

### Browser Console
Open DevTools → Network tab → Check request headers:
- ✅ `Origin: http://localhost:5174`
- ✅ `Authorization: Bearer <token>`

Check response headers:
- ✅ `Access-Control-Allow-Origin: http://localhost:5174`
- ✅ `Access-Control-Allow-Credentials: true`

## 🛠️ Common Issues & Solutions

### Issue 1: CORS Error in Browser
**Error**: "Access to XMLHttpRequest has been blocked by CORS policy"

**Solution**:
1. Verify backend is running: `curl http://localhost:8000/api/health`
2. Check CORS configuration in `Backend/main.py`
3. Restart backend server
4. Clear browser cache

### Issue 2: 401 Unauthorized
**Error**: "Request failed with status code 401"

**Solution**:
1. Check if token exists: `localStorage.getItem('authToken')`
2. Login again to get fresh token
3. Verify token is being sent in headers

### Issue 3: Network Error
**Error**: "Network Error" or "ERR_CONNECTION_REFUSED"

**Solution**:
1. Verify backend is running on port 8000
2. Check firewall settings
3. Verify API_URL in frontend/.env

### Issue 4: Preflight Request Failed
**Error**: "Response to preflight request doesn't pass access control check"

**Solution**:
1. Ensure OPTIONS method is allowed in CORS config
2. Check `allow_credentials` is set to `true`
3. Verify origin is in `allow_origins` list

## 📊 Network Traffic Example

### Successful Request Flow

1. **Preflight Request** (OPTIONS)
```
OPTIONS /api/chatbot/chat HTTP/1.1
Host: localhost:8000
Origin: http://localhost:5174
Access-Control-Request-Method: POST
Access-Control-Request-Headers: authorization,content-type
```

2. **Preflight Response**
```
HTTP/1.1 200 OK
Access-Control-Allow-Origin: http://localhost:5174
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS, PATCH
Access-Control-Allow-Headers: *
Access-Control-Allow-Credentials: true
```

3. **Actual Request** (POST)
```
POST /api/chatbot/chat HTTP/1.1
Host: localhost:8000
Origin: http://localhost:5174
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Content-Type: application/json

{"message":"test","use_search":false}
```

4. **Actual Response**
```
HTTP/1.1 200 OK
Access-Control-Allow-Origin: http://localhost:5174
Access-Control-Allow-Credentials: true
Content-Type: application/json

{"success":true,"response":"...","timestamp":"..."}
```

## 🔒 Security Considerations

### Development vs Production

**Development** (Current):
```python
allow_origins=["*"]  # Allows all origins
```

**Production** (Recommended):
```python
allow_origins=[
    "https://yourdomain.com",
    "https://www.yourdomain.com"
]
```

### Best Practices

1. ✅ Use specific origins in production
2. ✅ Enable credentials only when needed
3. ✅ Limit allowed methods to what's necessary
4. ✅ Use HTTPS in production
5. ✅ Implement rate limiting
6. ✅ Validate JWT tokens properly
7. ✅ Set appropriate token expiration

## 📝 Environment Configuration

### Development
```env
# frontend/.env
VITE_API_BASE_URL=http://localhost:8000
```

### Production
```env
# frontend/.env.production
VITE_API_BASE_URL=https://api.yourdomain.com
```

## ✅ Verification Checklist

- [x] Backend running on port 8000
- [x] Frontend running on port 5174
- [x] CORS headers configured
- [x] Authentication working
- [x] Protected endpoints accessible
- [x] Chatbot API responding
- [x] Token refresh working
- [x] Error handling implemented
- [x] Integration tests passing

## 🎯 Quick Test Commands

```bash
# Test backend health
curl http://localhost:8000/api/health

# Test login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"chameleon2024"}'

# Test CORS
curl -I -X OPTIONS http://localhost:8000/api/health \
  -H "Origin: http://localhost:5174"

# Run full integration test
./test_integration.sh
```

## 📚 Additional Resources

- [FastAPI CORS Documentation](https://fastapi.tiangolo.com/tutorial/cors/)
- [MDN CORS Guide](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [Axios Documentation](https://axios-http.com/docs/intro)

---

**Status**: ✅ Fully Integrated and Working
**Last Updated**: November 23, 2025
**Test Results**: All Passed ✅
