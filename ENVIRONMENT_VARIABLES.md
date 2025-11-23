# 🔐 Environment Variables Guide

## 📋 All Environment Variables

### Backend Environment Variables

#### Required Variables

```env
# MongoDB Configuration
MONGODB_URL=mongodb+srv://privatestudent33_db_user:hk3rc71C0GsEoJf4@cluster0.uiklaos.mongodb.net/?appName=Cluster0
DATABASE_NAME=chameleon_db

# JWT Authentication
JWT_SECRET_KEY=your-secret-key-change-in-production-2024
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Gemini AI Configuration
GEMINI_API_KEY=AIzaSyB7w5tQXvg1D7cVuqpeR6cZ5OMzNKCqguY

# API Configuration
GEOIP_API_URL=http://ip-api.com/json/

# Security Settings
TARPIT_THRESHOLD=5
TARPIT_DELAY_MIN=2.0
TARPIT_DELAY_MAX=10.0
CONFIDENCE_THRESHOLD=0.7
MAX_INPUT_LENGTH=200
```

#### Optional Variables (with defaults)

```env
# Python Version (for Render)
PYTHON_VERSION=3.12.0

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

---

### Frontend Environment Variables

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000

# For Production (Render)
VITE_API_BASE_URL=https://chameleon-backend.onrender.com

# Node Version (for Render)
NODE_VERSION=18.17.0
```

---

## 📁 File Structure

### Backend `.env` File

Create `Backend/.env`:

```env
# MongoDB Configuration
MONGODB_URL=mongodb+srv://privatestudent33_db_user:hk3rc71C0GsEoJf4@cluster0.uiklaos.mongodb.net/?appName=Cluster0
DATABASE_NAME=chameleon_db

# JWT Authentication
JWT_SECRET_KEY=your-secret-key-change-in-production-2024
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Gemini AI
GEMINI_API_KEY=AIzaSyB7w5tQXvg1D7cVuqpeR6cZ5OMzNKCqguY

# API Settings
GEOIP_API_URL=http://ip-api.com/json/
TARPIT_THRESHOLD=5
TARPIT_DELAY_MIN=2.0
TARPIT_DELAY_MAX=10.0
CONFIDENCE_THRESHOLD=0.7
MAX_INPUT_LENGTH=200
```

### Frontend `.env` File

Create `frontend/.env`:

```env
# Development
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000

# Production (uncomment for production)
# VITE_API_BASE_URL=https://chameleon-backend.onrender.com
```

---

## 🚀 Render Deployment Variables

### Backend Service Environment Variables

```
PYTHON_VERSION=3.12.0
MONGODB_URL=mongodb+srv://privatestudent33_db_user:hk3rc71C0GsEoJf4@cluster0.uiklaos.mongodb.net/?appName=Cluster0
DATABASE_NAME=chameleon_db
JWT_SECRET_KEY=your-secret-key-change-in-production-2024
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
GEMINI_API_KEY=AIzaSyB7w5tQXvg1D7cVuqpeR6cZ5OMzNKCqguY
GEOIP_API_URL=http://ip-api.com/json/
TARPIT_THRESHOLD=5
TARPIT_DELAY_MIN=2.0
TARPIT_DELAY_MAX=10.0
CONFIDENCE_THRESHOLD=0.7
MAX_INPUT_LENGTH=200
```

### Frontend Service Environment Variables

```
NODE_VERSION=18.17.0
VITE_API_BASE_URL=https://chameleon-backend.onrender.com
```

---

## 📝 Variable Descriptions

### MongoDB Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `MONGODB_URL` | `mongodb+srv://...` | MongoDB Atlas connection string |
| `DATABASE_NAME` | `chameleon_db` | Database name |

### Authentication Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `JWT_SECRET_KEY` | Random string | Secret key for JWT tokens |
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Token expiration time |

### AI Configuration

| Variable | Value | Description |
|----------|-------|-------------|
| `GEMINI_API_KEY` | Your API key | Google Gemini AI API key |

### API Settings

| Variable | Value | Description |
|----------|-------|-------------|
| `GEOIP_API_URL` | `http://ip-api.com/json/` | Geo-location API endpoint |
| `VITE_API_BASE_URL` | Backend URL | Frontend API endpoint |

### Security Settings

| Variable | Value | Description |
|----------|-------|-------------|
| `TARPIT_THRESHOLD` | `5` | Requests before tarpit activation |
| `TARPIT_DELAY_MIN` | `2.0` | Minimum delay in seconds |
| `TARPIT_DELAY_MAX` | `10.0` | Maximum delay in seconds |
| `CONFIDENCE_THRESHOLD` | `0.7` | ML confidence threshold |
| `MAX_INPUT_LENGTH` | `200` | Maximum input length |

---

## 🔧 How to Set Environment Variables

### Local Development

1. **Create Backend `.env`:**
   ```bash
   touch Backend/.env
   ```

2. **Add variables:**
   ```env
   MONGODB_URL=mongodb+srv://privatestudent33_db_user:hk3rc71C0GsEoJf4@cluster0.uiklaos.mongodb.net/?appName=Cluster0
   DATABASE_NAME=chameleon_db
   JWT_SECRET_KEY=your-secret-key-change-in-production-2024
   GEMINI_API_KEY=AIzaSyB7w5tQXvg1D7cVuqpeR6cZ5OMzNKCqguY
   ```

3. **Create Frontend `.env`:**
   ```bash
   touch frontend/.env
   ```

4. **Add variables:**
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   ```

---

### Render Deployment

1. **Go to Service Settings**
2. **Click "Environment"**
3. **Add each variable:**
   - Click "Add Environment Variable"
   - Enter Key and Value
   - Click "Save"

---

## 🔐 Security Best Practices

### For Production:

1. **Generate New JWT Secret:**
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Use Environment Variables:**
   - Never commit `.env` files
   - Use Render's secret management
   - Rotate keys regularly

3. **Update MongoDB:**
   - Use strong passwords
   - Whitelist specific IPs (not 0.0.0.0/0)
   - Enable authentication

4. **Protect API Keys:**
   - Don't commit to Git
   - Use different keys for dev/prod
   - Monitor usage

---

## 📋 Copy-Paste Templates

### Backend `.env` (Local Development)

```env
MONGODB_URL=mongodb+srv://privatestudent33_db_user:hk3rc71C0GsEoJf4@cluster0.uiklaos.mongodb.net/?appName=Cluster0
DATABASE_NAME=chameleon_db
JWT_SECRET_KEY=your-secret-key-change-in-production-2024
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
GEMINI_API_KEY=AIzaSyB7w5tQXvg1D7cVuqpeR6cZ5OMzNKCqguY
GEOIP_API_URL=http://ip-api.com/json/
TARPIT_THRESHOLD=5
TARPIT_DELAY_MIN=2.0
TARPIT_DELAY_MAX=10.0
CONFIDENCE_THRESHOLD=0.7
MAX_INPUT_LENGTH=200
```

### Frontend `.env` (Local Development)

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

### Backend `.env` (Production)

```env
MONGODB_URL=mongodb+srv://privatestudent33_db_user:hk3rc71C0GsEoJf4@cluster0.uiklaos.mongodb.net/?appName=Cluster0
DATABASE_NAME=chameleon_db
JWT_SECRET_KEY=<GENERATE_NEW_SECRET>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
GEMINI_API_KEY=AIzaSyB7w5tQXvg1D7cVuqpeR6cZ5OMzNKCqguY
GEOIP_API_URL=http://ip-api.com/json/
TARPIT_THRESHOLD=5
TARPIT_DELAY_MIN=2.0
TARPIT_DELAY_MAX=10.0
CONFIDENCE_THRESHOLD=0.7
MAX_INPUT_LENGTH=200
```

### Frontend `.env` (Production)

```env
VITE_API_BASE_URL=https://chameleon-backend.onrender.com
```

---

## 🧪 Testing Environment Variables

### Check if variables are loaded:

**Backend:**
```python
from config import settings
print(settings.MONGODB_URL)
print(settings.GEMINI_API_KEY)
```

**Frontend:**
```javascript
console.log(import.meta.env.VITE_API_BASE_URL);
```

---

## 🔄 Environment-Specific Configuration

### Development
```env
VITE_API_BASE_URL=http://localhost:8000
```

### Staging
```env
VITE_API_BASE_URL=https://chameleon-backend-staging.onrender.com
```

### Production
```env
VITE_API_BASE_URL=https://chameleon-backend.onrender.com
```

---

## 📊 Complete Variable List

### Backend (17 variables)

1. `MONGODB_URL` - Database connection
2. `DATABASE_NAME` - Database name
3. `JWT_SECRET_KEY` - JWT secret
4. `JWT_ALGORITHM` - JWT algorithm
5. `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiry
6. `GEMINI_API_KEY` - AI API key
7. `GEOIP_API_URL` - Geo API endpoint
8. `TARPIT_THRESHOLD` - Security threshold
9. `TARPIT_DELAY_MIN` - Min delay
10. `TARPIT_DELAY_MAX` - Max delay
11. `CONFIDENCE_THRESHOLD` - ML threshold
12. `MAX_INPUT_LENGTH` - Input limit
13. `PYTHON_VERSION` - Python version (Render)
14. `HOST` - Server host
15. `PORT` - Server port
16. `MODEL_PATH` - ML model path (hardcoded)
17. `ADMIN_USERNAME` - Admin user (hardcoded)

### Frontend (3 variables)

1. `VITE_API_BASE_URL` - Backend API URL
2. `VITE_WS_URL` - WebSocket URL
3. `NODE_VERSION` - Node version (Render)

---

## ✅ Quick Setup

1. **Copy Backend template:**
   ```bash
   cp Backend/.env.example Backend/.env
   ```

2. **Copy Frontend template:**
   ```bash
   cp frontend/.env.example frontend/.env
   ```

3. **Update values:**
   - Edit `Backend/.env`
   - Edit `frontend/.env`

4. **Start application:**
   ```bash
   npm start
   ```

---

## 🎯 Summary

**Your MongoDB URL:**
```
mongodb+srv://privatestudent33_db_user:hk3rc71C0GsEoJf4@cluster0.uiklaos.mongodb.net/?appName=Cluster0
```

**Your Database Name:**
```
chameleon_db
```

**Your JWT Secret:**
```
your-secret-key-change-in-production-2024
```

**Your Gemini API Key:**
```
AIzaSyB7w5tQXvg1D7cVuqpeR6cZ5OMzNKCqguY
```

**All set!** 🎉
