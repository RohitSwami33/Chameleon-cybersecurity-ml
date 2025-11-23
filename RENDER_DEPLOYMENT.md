# 🚀 Render Deployment Guide

## 📋 Overview

This guide will help you deploy the Chameleon Adaptive Deception System on Render.com with the correct build and start commands.

---

## 🎯 Deployment Configuration

### Frontend (React + Vite)

**Service Type:** Web Service

**Build Command:**
```bash
cd frontend && npm install && npm run build
```

**Start Command:**
```bash
cd frontend && npm start
```

**Environment Variables:**
```
VITE_API_BASE_URL=https://your-backend-url.onrender.com
NODE_VERSION=18.17.0
```

**Port:** Render will provide `$PORT` automatically

---

### Backend (FastAPI + Python)

**Service Type:** Web Service

**Build Command:**
```bash
cd Backend && pip install --upgrade pip && pip install -r requirements.txt
```

**Start Command:**
```bash
cd Backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Environment Variables:**
```
PYTHON_VERSION=3.12.0
GEMINI_API_KEY=AIzaSyB7w5tQXvg1D7cVuqpeR6cZ5OMzNKCqguY
MONGODB_URL=your_mongodb_atlas_connection_string
JWT_SECRET_KEY=your_secret_key_here
```

---

## 📝 Step-by-Step Deployment

### Prerequisites

1. ✅ GitHub account
2. ✅ Render account (https://render.com)
3. ✅ MongoDB Atlas account (for database)
4. ✅ Push your code to GitHub

---

### Step 1: Setup MongoDB Atlas

1. Go to https://www.mongodb.com/cloud/atlas
2. Create a free cluster
3. Create a database user
4. Whitelist all IPs (0.0.0.0/0) for Render
5. Get your connection string:
   ```
   mongodb+srv://username:password@cluster.mongodb.net/chameleon_db
   ```

---

### Step 2: Deploy Backend

1. **Login to Render**
   - Go to https://dashboard.render.com

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select your repository

3. **Configure Backend Service**
   ```
   Name: chameleon-backend
   Region: Oregon (US West)
   Branch: main
   Root Directory: (leave empty)
   Runtime: Python 3
   
   Build Command:
   cd Backend && pip install --upgrade pip && pip install -r requirements.txt
   
   Start Command:
   cd Backend && uvicorn main:app --host 0.0.0.0 --port $PORT
   
   Plan: Free
   ```

4. **Add Environment Variables**
   ```
   PYTHON_VERSION = 3.12.0
   GEMINI_API_KEY = AIzaSyB7w5tQXvg1D7cVuqpeR6cZ5OMzNKCqguY
   MONGODB_URL = mongodb+srv://username:password@cluster.mongodb.net/chameleon_db
   JWT_SECRET_KEY = your-secret-key-change-this
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)
   - Note your backend URL: `https://chameleon-backend.onrender.com`

---

### Step 3: Deploy Frontend

1. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect same GitHub repository

2. **Configure Frontend Service**
   ```
   Name: chameleon-frontend
   Region: Oregon (US West)
   Branch: main
   Root Directory: (leave empty)
   Runtime: Node
   
   Build Command:
   cd frontend && npm install && npm run build
   
   Start Command:
   cd frontend && npm start
   
   Plan: Free
   ```

3. **Add Environment Variables**
   ```
   NODE_VERSION = 18.17.0
   VITE_API_BASE_URL = https://chameleon-backend.onrender.com
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)
   - Your app will be live at: `https://chameleon-frontend.onrender.com`

---

## 🔧 Configuration Files

### package.json (Frontend)

The `start` script has been updated:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "start": "vite preview --host 0.0.0.0 --port $PORT",
    "preview": "vite preview"
  }
}
```

### Backend CORS Configuration

Update `Backend/main.py` to include your Render URLs:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "https://chameleon-frontend.onrender.com",  # Add this
        "https://*.onrender.com",  # Add this
        "*"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)
```

---

## 🎯 Render Dashboard Configuration

### Backend Service Settings

```yaml
Name: chameleon-backend
Environment: Python 3
Region: Oregon (US West)
Branch: main

Build Command:
cd Backend && pip install --upgrade pip && pip install -r requirements.txt

Start Command:
cd Backend && uvicorn main:app --host 0.0.0.0 --port $PORT

Environment Variables:
- PYTHON_VERSION: 3.12.0
- GEMINI_API_KEY: AIzaSyB7w5tQXvg1D7cVuqpeR6cZ5OMzNKCqguY
- MONGODB_URL: mongodb+srv://...
- JWT_SECRET_KEY: your-secret-key

Health Check Path: /api/health
```

### Frontend Service Settings

```yaml
Name: chameleon-frontend
Environment: Node
Region: Oregon (US West)
Branch: main

Build Command:
cd frontend && npm install && npm run build

Start Command:
cd frontend && npm start

Environment Variables:
- NODE_VERSION: 18.17.0
- VITE_API_BASE_URL: https://chameleon-backend.onrender.com

Health Check Path: /
```

---

## 🔐 Environment Variables

### Backend Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `PYTHON_VERSION` | `3.12.0` | Python version |
| `GEMINI_API_KEY` | Your API key | Gemini AI API key |
| `MONGODB_URL` | MongoDB connection string | Database URL |
| `JWT_SECRET_KEY` | Random secret | JWT token secret |

### Frontend Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `NODE_VERSION` | `18.17.0` | Node.js version |
| `VITE_API_BASE_URL` | Backend URL | API endpoint |

---

## 🧪 Testing Deployment

### Test Backend

```bash
# Health check
curl https://chameleon-backend.onrender.com/api/health

# Login
curl -X POST https://chameleon-backend.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"chameleon2024"}'
```

### Test Frontend

Open in browser:
```
https://chameleon-frontend.onrender.com
```

Login with:
- Username: `admin`
- Password: `chameleon2024`

---

## 🚨 Important Notes

### Free Tier Limitations

1. **Sleep Mode**: Services sleep after 15 minutes of inactivity
2. **Cold Start**: First request may take 30-60 seconds
3. **Build Time**: Limited to 15 minutes
4. **Bandwidth**: 100 GB/month
5. **Build Minutes**: 500 minutes/month

### Keeping Services Awake

Use a service like UptimeRobot to ping your app every 14 minutes:
```
https://chameleon-backend.onrender.com/api/health
https://chameleon-frontend.onrender.com
```

---

## 🔄 Auto-Deploy

Render automatically deploys when you push to GitHub:

```bash
git add .
git commit -m "Update deployment"
git push origin main
```

Render will:
1. Detect the push
2. Run build commands
3. Deploy new version
4. Zero-downtime deployment

---

## 📊 Monitoring

### View Logs

1. Go to Render Dashboard
2. Select your service
3. Click "Logs" tab
4. View real-time logs

### Check Status

- **Backend**: https://chameleon-backend.onrender.com/api/health
- **Frontend**: https://chameleon-frontend.onrender.com

---

## 🛠️ Troubleshooting

### Build Fails

**Check:**
1. Build command is correct
2. All dependencies in requirements.txt/package.json
3. Python/Node version is correct
4. Build logs for errors

**Solution:**
```bash
# Test locally first
cd Backend && pip install -r requirements.txt
cd frontend && npm install && npm run build
```

### Service Won't Start

**Check:**
1. Start command is correct
2. Port is set to `$PORT`
3. Environment variables are set
4. MongoDB connection string is correct

**Solution:**
- Check logs in Render dashboard
- Verify environment variables
- Test MongoDB connection

### CORS Errors

**Check:**
1. Frontend URL is in CORS origins
2. Backend URL is correct in frontend env

**Solution:**
Update `Backend/main.py`:
```python
allow_origins=[
    "https://chameleon-frontend.onrender.com",
    "https://*.onrender.com",
]
```

### MongoDB Connection Failed

**Check:**
1. Connection string is correct
2. Database user has permissions
3. IP whitelist includes 0.0.0.0/0

**Solution:**
- Verify MongoDB Atlas settings
- Check connection string format
- Test connection locally

---

## 📝 Deployment Checklist

- [ ] MongoDB Atlas cluster created
- [ ] Database user created
- [ ] IP whitelist configured (0.0.0.0/0)
- [ ] Code pushed to GitHub
- [ ] Backend service created on Render
- [ ] Backend environment variables set
- [ ] Backend deployed successfully
- [ ] Frontend service created on Render
- [ ] Frontend environment variables set
- [ ] Frontend deployed successfully
- [ ] CORS configured with production URLs
- [ ] Health checks passing
- [ ] Login works
- [ ] Chatbot works
- [ ] All features tested

---

## 🎉 Success!

Your application should now be live at:

- **Frontend**: https://chameleon-frontend.onrender.com
- **Backend**: https://chameleon-backend.onrender.com
- **API Docs**: https://chameleon-backend.onrender.com/docs

---

## 📚 Additional Resources

- [Render Documentation](https://render.com/docs)
- [MongoDB Atlas Documentation](https://docs.atlas.mongodb.com/)
- [Vite Deployment Guide](https://vitejs.dev/guide/static-deploy.html)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

---

## 🆘 Support

If you encounter issues:

1. Check Render logs
2. Verify environment variables
3. Test locally first
4. Check MongoDB connection
5. Review CORS configuration

---

**Quick Commands:**

```bash
# Local testing
./start.sh

# Build test
./build.sh

# Deploy
git push origin main
```

**Render will auto-deploy!** 🚀
