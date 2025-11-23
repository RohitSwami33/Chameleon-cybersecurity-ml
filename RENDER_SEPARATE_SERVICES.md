# 🚀 Render Deployment - Separate Services

## ⚠️ Important: Deploy as TWO Separate Services

You need to create **TWO separate web services** on Render:
1. Backend (Python)
2. Frontend (Node)

**DO NOT** use the root `package.json` for deployment!

---

## 📋 Step-by-Step Deployment

### 1️⃣ Deploy Backend Service

**Go to Render Dashboard:** https://dashboard.render.com

**Click:** New + → Web Service

**Configure:**
```
Name: chameleon-backend
Environment: Python 3
Region: Oregon (US West)
Branch: main
Root Directory: (leave empty)

Build Command:
pip install --upgrade pip && pip install -r Backend/requirements.txt

Start Command:
cd Backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT

Instance Type: Free
```

**Environment Variables:**
```
PYTHON_VERSION=3.12.0
MONGODB_URL=mongodb+srv://privatestudent33_db_user:hk3rc71C0GsEoJf4@cluster0.uiklaos.mongodb.net/?appName=Cluster0
DATABASE_NAME=chameleon_db
JWT_SECRET_KEY=your-secret-key-change-in-production-2024
GEMINI_API_KEY=AIzaSyB7w5tQXvg1D7cVuqpeR6cZ5OMzNKCqguY
```

**Click:** Create Web Service

**Wait:** 5-10 minutes for deployment

**Copy Backend URL:** e.g., `https://chameleon-backend.onrender.com`

---

### 2️⃣ Deploy Frontend Service

**Click:** New + → Web Service

**Configure:**
```
Name: chameleon-frontend
Environment: Node
Region: Oregon (US West)
Branch: main
Root Directory: (leave empty)

Build Command:
cd frontend && npm install && npm run build

Start Command:
cd frontend && npm start

Instance Type: Free
```

**Environment Variables:**
```
NODE_VERSION=18.17.0
VITE_API_BASE_URL=https://chameleon-backend.onrender.com
```
*(Replace with your actual backend URL from step 1)*

**Click:** Create Web Service

**Wait:** 5-10 minutes for deployment

---

## 🎯 Key Points

### ❌ Don't Do This:
- Don't deploy using root `package.json`
- Don't try to run both in one service
- Don't use `npm run build` for backend

### ✅ Do This:
- Create TWO separate services
- Backend = Python environment
- Frontend = Node environment
- Use correct build/start commands for each

---

## 📊 Service Configuration Summary

### Backend Service

| Setting | Value |
|---------|-------|
| **Name** | chameleon-backend |
| **Environment** | Python 3 |
| **Build Command** | `pip install --upgrade pip && pip install -r Backend/requirements.txt` |
| **Start Command** | `cd Backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Root Directory** | (empty) |

### Frontend Service

| Setting | Value |
|---------|-------|
| **Name** | chameleon-frontend |
| **Environment** | Node |
| **Build Command** | `cd frontend && npm install && npm run build` |
| **Start Command** | `cd frontend && npm start` |
| **Root Directory** | (empty) |

---

## 🔧 Why This Failed

**Error:** `sh: 1: python3.12: not found`

**Reason:** You deployed to a **Node service** but the root `package.json` has a build script that tries to run Python commands.

**Solution:** Deploy backend and frontend as **separate services** with correct environments.

---

## 🎨 Visual Guide

```
GitHub Repository
       │
       ├─── Backend/          → Deploy as Python Service
       │    ├── main.py
       │    └── requirements.txt
       │
       └─── frontend/         → Deploy as Node Service
            ├── package.json
            └── src/

❌ WRONG: Deploy root as Node service (tries to run Python)
✅ RIGHT: Deploy Backend as Python, Frontend as Node
```

---

## 📝 Correct Deployment Steps

1. **Create Backend Service**
   - Environment: Python 3
   - Build: `pip install -r Backend/requirements.txt`
   - Start: `cd Backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT`

2. **Wait for Backend to Deploy**
   - Get backend URL

3. **Create Frontend Service**
   - Environment: Node
   - Build: `cd frontend && npm install && npm run build`
   - Start: `cd frontend && npm start`
   - Add env var: `VITE_API_BASE_URL=<backend-url>`

4. **Done!**
   - Frontend talks to Backend
   - Both services running

---

## 🚀 Quick Deploy Checklist

### Backend Service
- [ ] New Web Service created
- [ ] Environment: Python 3
- [ ] Build command correct
- [ ] Start command correct
- [ ] Environment variables added
- [ ] Deployed successfully
- [ ] Backend URL copied

### Frontend Service
- [ ] New Web Service created
- [ ] Environment: Node
- [ ] Build command correct
- [ ] Start command correct
- [ ] Backend URL added to env vars
- [ ] Deployed successfully
- [ ] Frontend accessible

---

## 🔗 After Deployment

**Your URLs:**
- Backend: `https://chameleon-backend.onrender.com`
- Frontend: `https://chameleon-frontend.onrender.com`
- API Docs: `https://chameleon-backend.onrender.com/docs`

**Test:**
```bash
curl https://chameleon-backend.onrender.com/api/health
```

**Access:**
```
https://chameleon-frontend.onrender.com
```

**Login:**
- Username: `admin`
- Password: `chameleon2024`

---

## 💡 Pro Tip

The root `package.json` is for **local development only** (using `npm start`).

For Render deployment, **ignore it** and deploy services separately!

---

## 🆘 If You Already Created a Service

1. **Delete the failed service**
2. **Create TWO new services** as described above
3. **Follow the correct configuration**

---

## ✅ Summary

**Problem:** Tried to deploy as one Node service

**Solution:** Deploy as TWO separate services:
1. Backend (Python)
2. Frontend (Node)

**Result:** Both services work independently and communicate via API

---

**Follow the steps above to deploy correctly!** 🚀
