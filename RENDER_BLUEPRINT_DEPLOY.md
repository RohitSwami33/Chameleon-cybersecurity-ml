# 🚀 Render Blueprint Deployment Guide

## ✅ Your Project is Ready!

The `render.yaml` file is configured to deploy **both backend and frontend** as separate services using Render's Blueprint feature.

---

## 📋 What's Configured

### Backend Service
- **Name:** chameleon-backend
- **Runtime:** Python 3.11
- **Build:** `pip install -r Backend/requirements.txt`
- **Start:** `cd Backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT`

### Frontend Service
- **Name:** chameleon-frontend
- **Runtime:** Node 18
- **Build:** `cd frontend && npm install && npm run build`
- **Start:** `cd frontend && npm run preview -- --host 0.0.0.0 --port $PORT`

---

## 🎯 Deploy Using Blueprint (Single Click!)

### Step 1: Push to GitHub

```bash
git add .
git commit -m "Add Render Blueprint configuration"
git push origin main
```

### Step 2: Deploy on Render

1. **Go to Render Dashboard:** https://dashboard.render.com

2. **Click:** "New" → "Blueprint"

3. **Connect Repository:**
   - Select: `RohitSwami33/Chameleon-cybersecurity-ml`
   - Branch: `main`

4. **Render Detects render.yaml:**
   - Shows 2 services to be created
   - Backend (Python)
   - Frontend (Node)

5. **Add Secret Environment Variable:**
   - `MONGODB_URL`: `mongodb+srv://privatestudent33_db_user:hk3rc71C0GsEoJf4@cluster0.uiklaos.mongodb.net/?appName=Cluster0`

6. **Click:** "Apply"

7. **Wait:** 10-15 minutes for both services to deploy

8. **Done!** Both services will be live

---

## 🔐 Environment Variables

### Already Configured in render.yaml:

**Backend:**
- ✅ `PYTHON_VERSION=3.11.0`
- ✅ `GEMINI_API_KEY=AIzaSyB7w5tQXvg1D7cVuqpeR6cZ5OMzNKCqguY`
- ✅ `JWT_SECRET_KEY` (auto-generated)
- ✅ `DATABASE_NAME=chameleon_db`

**Frontend:**
- ✅ `NODE_VERSION=18.17.0`
- ✅ `VITE_API_BASE_URL` (auto-linked to backend)

### You Need to Add:

**MONGODB_URL** (marked as `sync: false` for security):
```
mongodb+srv://privatestudent33_db_user:hk3rc71C0GsEoJf4@cluster0.uiklaos.mongodb.net/?appName=Cluster0
```

---

## 📊 Deployment Flow

```
1. Push to GitHub
   └─> git push origin main

2. Render Blueprint
   └─> Detects render.yaml
       ├─> Creates Backend Service (Python)
       │   ├─> Installs dependencies
       │   ├─> Starts uvicorn
       │   └─> URL: https://chameleon-backend.onrender.com
       │
       └─> Creates Frontend Service (Node)
           ├─> Builds production bundle
           ├─> Starts preview server
           ├─> Auto-links to backend URL
           └─> URL: https://chameleon-frontend.onrender.com

3. Services Communicate
   └─> Frontend → Backend via VITE_API_BASE_URL
```

---

## 🎯 After Deployment

### Your URLs:

**Frontend:**
```
https://chameleon-frontend.onrender.com
```

**Backend:**
```
https://chameleon-backend.onrender.com
```

**API Docs:**
```
https://chameleon-backend.onrender.com/docs
```

**Health Check:**
```
https://chameleon-backend.onrender.com/api/health
```

---

## 🧪 Test Deployment

### Test Backend:
```bash
curl https://chameleon-backend.onrender.com/api/health
```

Expected:
```json
{"status":"healthy","timestamp":"2025-11-23T..."}
```

### Test Frontend:
Open in browser:
```
https://chameleon-frontend.onrender.com
```

Login:
- Username: `admin`
- Password: `chameleon2024`

---

## 📝 Files Updated

1. ✅ `render.yaml` - Blueprint configuration
2. ✅ `frontend/vite.config.js` - Preview server config
3. ✅ `frontend/package.json` - Preview command
4. ✅ `Backend/config.py` - Already uses env vars

---

## 🔧 Configuration Details

### render.yaml Features

**Auto-linking:**
```yaml
VITE_API_BASE_URL:
  fromService:
    type: web
    name: chameleon-backend
    envVarKey: RENDER_EXTERNAL_URL
```
This automatically sets the frontend's API URL to the backend's URL!

**Auto-generated secrets:**
```yaml
JWT_SECRET_KEY:
  generateValue: true
```
Render generates a secure random secret automatically!

---

## 🎨 Blueprint Advantages

### Single Click Deployment
- ✅ Creates both services at once
- ✅ Auto-links services
- ✅ Manages dependencies
- ✅ Handles environment variables

### Auto-Deploy
- ✅ Push to GitHub → Auto-deploy
- ✅ Zero-downtime updates
- ✅ Rollback support

### Service Discovery
- ✅ Frontend automatically knows backend URL
- ✅ No manual URL configuration
- ✅ Works across environments

---

## 🚀 Deployment Steps (Summary)

### 1. Push to GitHub
```bash
git add .
git commit -m "Add Render Blueprint"
git push origin main
```

### 2. Deploy on Render
```
1. Dashboard → New → Blueprint
2. Select repository
3. Add MONGODB_URL
4. Click Apply
5. Wait 10-15 minutes
6. Done!
```

### 3. Access Your App
```
https://chameleon-frontend.onrender.com
```

---

## 🔐 Environment Variables to Add

When deploying via Blueprint, you'll be prompted to add:

**MONGODB_URL:**
```
mongodb+srv://privatestudent33_db_user:hk3rc71C0GsEoJf4@cluster0.uiklaos.mongodb.net/?appName=Cluster0
```

All other variables are already configured in `render.yaml`!

---

## 📊 Service Configuration

### Backend (chameleon-backend)

| Setting | Value |
|---------|-------|
| **Environment** | Python 3.11 |
| **Build** | `pip install -r Backend/requirements.txt` |
| **Start** | `cd Backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Health Check** | `/api/health` |

### Frontend (chameleon-frontend)

| Setting | Value |
|---------|-------|
| **Environment** | Node 18 |
| **Build** | `cd frontend && npm install && npm run build` |
| **Start** | `cd frontend && npm run preview -- --host 0.0.0.0 --port $PORT` |
| **Health Check** | `/` |

---

## 🎉 Benefits of Blueprint

1. **Single Configuration:** One `render.yaml` file
2. **Auto-Deploy:** Push to GitHub → Auto-deploy
3. **Service Linking:** Frontend auto-discovers backend
4. **Version Control:** Infrastructure as code
5. **Easy Rollback:** Revert to previous version
6. **Consistent:** Same config for all environments

---

## 🛠️ Troubleshooting

### If Deployment Fails:

1. **Check Logs:**
   - Go to service in Render Dashboard
   - Click "Logs" tab
   - Look for errors

2. **Verify render.yaml:**
   - Check syntax
   - Verify paths
   - Ensure commands are correct

3. **Test Locally:**
   ```bash
   npm run build
   cd frontend && npm run preview
   ```

4. **Redeploy:**
   - Dashboard → Service → Manual Deploy
   - Or push a new commit

---

## 📚 Documentation

- **Complete Guide:** `RENDER_DEPLOYMENT.md`
- **Environment Variables:** `ENVIRONMENT_VARIABLES.md`
- **Blueprint Guide:** This file

---

## ✅ Summary

**Configuration:** ✅ Complete
**render.yaml:** ✅ Ready
**Environment Variables:** ✅ Set
**Commands:** ✅ Correct

**Next Step:**
1. Push to GitHub
2. Deploy via Blueprint
3. Add MongoDB URL
4. Wait for deployment
5. Access your app!

---

## 🎯 Quick Deploy

```bash
# 1. Commit and push
git add .
git commit -m "Ready for Render Blueprint deployment"
git push origin main

# 2. Go to Render
# Dashboard → New → Blueprint → Select repo → Apply

# 3. Add MongoDB URL when prompted
# mongodb+srv://privatestudent33_db_user:hk3rc71C0GsEoJf4@cluster0.uiklaos.mongodb.net/?appName=Cluster0

# 4. Done!
```

**Your app will be live in 10-15 minutes!** 🚀

---

**All environment variables are configured in render.yaml!**
**Just add MONGODB_URL when deploying and you're done!** 🎉
