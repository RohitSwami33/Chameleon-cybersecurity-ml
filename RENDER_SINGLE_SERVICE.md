# 🚀 Render Single Service Deployment

## 📋 Deploy Frontend Only (Recommended for Free Tier)

Since you can only create one service, deploy the **frontend** and use a **free MongoDB Atlas** for the database. The backend can run locally or on another free service later.

---

## Option 1: Frontend Only (Simplest)

### Step 1: Deploy Frontend

**Render Configuration:**

```
Name: chameleon-frontend
Environment: Node
Branch: main
Root Directory: (empty)

Build Command:
cd frontend && npm install && npm run build

Start Command:
cd frontend && npm start

Environment Variables:
NODE_VERSION=18.17.0
VITE_API_BASE_URL=http://localhost:8000
```

**Note:** This will deploy only the frontend. You'll need to run the backend locally.

---

## Option 2: Use Docker (Single Service)

### Step 1: Create Dockerfile

A `Dockerfile` has been created that combines both frontend and backend.

### Step 2: Deploy with Docker

**Render Configuration:**

```
Name: chameleon-app
Environment: Docker
Branch: main
Root Directory: (empty)

Dockerfile Path: ./Dockerfile

Environment Variables:
PORT=10000
MONGODB_URL=mongodb+srv://privatestudent33_db_user:hk3rc71C0GsEoJf4@cluster0.uiklaos.mongodb.net/?appName=Cluster0
DATABASE_NAME=chameleon_db
JWT_SECRET_KEY=your-secret-key-change-in-production-2024
GEMINI_API_KEY=AIzaSyB7w5tQXvg1D7cVuqpeR6cZ5OMzNKCqguY
```

**Note:** Docker deployment is available on paid plans.

---

## Option 3: Static Site + Serverless Backend

### Deploy Frontend as Static Site

**Render Configuration:**

```
Name: chameleon-frontend
Environment: Static Site
Branch: main
Root Directory: frontend

Build Command:
npm install && npm run build

Publish Directory:
dist
```

**Cost:** Free!

---

## 🎯 Recommended Solution for Free Tier

### Deploy Frontend on Render (Free)

1. **Go to Render Dashboard**
2. **New Static Site**
3. **Connect GitHub repo**
4. **Configure:**
   ```
   Name: chameleon-frontend
   Branch: main
   Root Directory: frontend
   Build Command: npm install && npm run build
   Publish Directory: dist
   ```
5. **Deploy**

### Run Backend Locally

```bash
cd Backend
source venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### Or Deploy Backend on Railway/Fly.io (Free)

These platforms offer free tiers for Python apps:
- Railway: https://railway.app
- Fly.io: https://fly.io

---

## 📦 Alternative: Combine into Single Node Service

If you want everything in one Node service, here's how:

### Step 1: Update package.json

Already done! The package.json now has:

```json
{
  "scripts": {
    "build": "cd frontend && npm install && npm run build",
    "start:render": "cd frontend && npm start"
  }
}
```

### Step 2: Deploy on Render

**Configuration:**

```
Name: chameleon-app
Environment: Node
Branch: main
Root Directory: (empty)

Build Command:
npm run build

Start Command:
npm run start:render

Environment Variables:
NODE_VERSION=18.17.0
VITE_API_BASE_URL=https://your-backend-url.com
```

**Note:** You'll still need to deploy the backend separately or run it locally.

---

## 🔧 Docker Deployment (Paid Plans)

### Dockerfile Created

A `Dockerfile` has been created that:
1. Builds the frontend
2. Sets up Python backend
3. Serves both from one container

### Deploy with Docker

**Render Configuration:**

```
Name: chameleon-app
Environment: Docker
Branch: main

Environment Variables:
PORT=10000
MONGODB_URL=mongodb+srv://privatestudent33_db_user:hk3rc71C0GsEoJf4@cluster0.uiklaos.mongodb.net/?appName=Cluster0
DATABASE_NAME=chameleon_db
JWT_SECRET_KEY=your-secret-key-change-in-production-2024
GEMINI_API_KEY=AIzaSyB7w5tQXvg1D7cVuqpeR6cZ5OMzNKCqguY
```

---

## 💡 Best Solution for Your Case

### Option A: Frontend on Render (Free) + Backend Locally

**Pros:**
- Free
- Simple
- Works immediately

**Steps:**
1. Deploy frontend as Static Site on Render
2. Run backend locally
3. Update frontend env to point to localhost

### Option B: Frontend on Render + Backend on Railway

**Pros:**
- Both deployed
- Both free tier
- Professional setup

**Steps:**
1. Deploy frontend on Render (Static Site)
2. Deploy backend on Railway (Free tier)
3. Update frontend env to point to Railway backend

### Option C: Everything on Vercel (Free)

**Pros:**
- Single platform
- Free tier
- Easy deployment

**Steps:**
1. Deploy to Vercel
2. Frontend as static site
3. Backend as serverless functions

---

## 🎯 Quick Deploy: Frontend Only

**For immediate deployment:**

```
1. Go to Render Dashboard
2. New → Static Site
3. Connect GitHub repo
4. Configure:
   - Root Directory: frontend
   - Build Command: npm install && npm run build
   - Publish Directory: dist
5. Deploy
```

**Run backend locally:**
```bash
npm run start:backend
```

---

## 📊 Comparison

| Option | Frontend | Backend | Cost | Complexity |
|--------|----------|---------|------|------------|
| Static Site + Local | Render | Local | Free | Easy |
| Static Site + Railway | Render | Railway | Free | Medium |
| Docker | Render | Render | Paid | Easy |
| Vercel | Vercel | Vercel | Free | Medium |

---

## ✅ Recommended: Deploy Frontend Only

**Since you can only create one service:**

1. **Deploy frontend as Static Site** (Free)
2. **Run backend locally** for development
3. **Later:** Deploy backend on Railway/Fly.io (Free)

**Configuration:**

```
Type: Static Site
Root Directory: frontend
Build Command: npm install && npm run build
Publish Directory: dist
```

---

## 🚀 Quick Start

**Deploy Frontend:**
```
1. Render Dashboard → New Static Site
2. Root: frontend
3. Build: npm install && npm run build
4. Publish: dist
5. Deploy
```

**Run Backend:**
```bash
cd Backend
source venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

**Done!** 🎉

---

## 📝 Files Created

- ✅ `Dockerfile` - For Docker deployment (paid plans)
- ✅ `package.json` - Updated for single service
- ✅ `RENDER_SINGLE_SERVICE.md` - This guide

---

**Choose the option that works best for you!** 🚀
