# 🚀 Render Quick Deploy - Copy & Paste

## ✅ Ready to Deploy!

Your project is now configured for Render deployment with:
- ✅ `npm run build` for building
- ✅ `npm start` for starting
- ✅ CORS configured for Render URLs

---

## 📋 Quick Deploy Steps

### 1️⃣ Setup MongoDB Atlas (5 minutes)

1. Go to: https://www.mongodb.com/cloud/atlas
2. Create free cluster
3. Create database user
4. Whitelist IP: `0.0.0.0/0`
5. Copy connection string:
   ```
   mongodb+srv://username:password@cluster.mongodb.net/chameleon_db
   ```

---

### 2️⃣ Deploy Backend (10 minutes)

**Render Dashboard:** https://dashboard.render.com

**Create Web Service:**

```
Name: chameleon-backend
Runtime: Python 3
Branch: main

Build Command:
cd Backend && pip install --upgrade pip && pip install -r requirements.txt

Start Command:
cd Backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Environment Variables:**
```
PYTHON_VERSION=3.12.0
GEMINI_API_KEY=AIzaSyB7w5tQXvg1D7cVuqpeR6cZ5OMzNKCqguY
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/chameleon_db
JWT_SECRET_KEY=your-secret-key-change-this-in-production
```

**Click:** Create Web Service

**Copy Backend URL:** `https://chameleon-backend.onrender.com`

---

### 3️⃣ Deploy Frontend (10 minutes)

**Create Web Service:**

```
Name: chameleon-frontend
Runtime: Node
Branch: main

Build Command:
cd frontend && npm install && npm run build

Start Command:
cd frontend && npm start
```

**Environment Variables:**
```
NODE_VERSION=18.17.0
VITE_API_BASE_URL=https://chameleon-backend.onrender.com
```

**Click:** Create Web Service

**Your App URL:** `https://chameleon-frontend.onrender.com`

---

## 🎯 Copy-Paste Configuration

### Backend Service

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
MONGODB_URL=<YOUR_MONGODB_ATLAS_URL>
JWT_SECRET_KEY=<GENERATE_RANDOM_SECRET>
```

---

### Frontend Service

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
NODE_VERSION=18.17.0
VITE_API_BASE_URL=https://chameleon-backend.onrender.com
```

---

## 🔑 Generate JWT Secret

Run this locally to generate a secure secret:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and use it as `JWT_SECRET_KEY`

---

## ✅ Deployment Checklist

- [ ] MongoDB Atlas cluster created
- [ ] Database user created with password
- [ ] IP whitelist set to 0.0.0.0/0
- [ ] Connection string copied
- [ ] Code pushed to GitHub
- [ ] Backend service created on Render
- [ ] Backend environment variables added
- [ ] Backend deployed (wait 5-10 min)
- [ ] Backend URL copied
- [ ] Frontend service created on Render
- [ ] Frontend environment variables added (with backend URL)
- [ ] Frontend deployed (wait 5-10 min)
- [ ] Test backend: `https://your-backend.onrender.com/api/health`
- [ ] Test frontend: `https://your-frontend.onrender.com`
- [ ] Login works (admin/chameleon2024)
- [ ] Chatbot works

---

## 🧪 Test Your Deployment

### Test Backend
```bash
curl https://chameleon-backend.onrender.com/api/health
```

Expected response:
```json
{"status":"healthy","timestamp":"2025-11-23T..."}
```

### Test Frontend
Open in browser:
```
https://chameleon-frontend.onrender.com
```

Login:
- Username: `admin`
- Password: `chameleon2024`

---

## 🎨 What's Configured

### package.json (Frontend)
```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "start": "vite preview --host 0.0.0.0 --port $PORT"
  }
}
```

### CORS (Backend)
```python
allow_origins=[
    "https://*.onrender.com",
    "https://chameleon-frontend.onrender.com",
    "*"
]
```

---

## 🚨 Important Notes

### Free Tier
- Services sleep after 15 minutes of inactivity
- First request after sleep takes 30-60 seconds
- 500 build minutes/month
- 100 GB bandwidth/month

### Keep Awake
Use UptimeRobot (free) to ping every 14 minutes:
- https://uptimerobot.com
- Add monitor for: `https://chameleon-backend.onrender.com/api/health`

---

## 🔄 Auto-Deploy

Push to GitHub to auto-deploy:

```bash
git add .
git commit -m "Deploy to Render"
git push origin main
```

Render will automatically:
1. Detect the push
2. Run build commands
3. Deploy new version

---

## 🛠️ Troubleshooting

### Build Fails
- Check build logs in Render dashboard
- Verify all dependencies are in requirements.txt/package.json
- Test build locally: `./build.sh`

### Service Won't Start
- Check start command is correct
- Verify environment variables are set
- Check logs for errors

### CORS Errors
- Verify backend URL in frontend env vars
- Check CORS configuration in Backend/main.py
- Ensure URLs match exactly

### MongoDB Connection Failed
- Verify connection string format
- Check database user permissions
- Ensure IP whitelist includes 0.0.0.0/0

---

## 📊 Service URLs

After deployment, you'll have:

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | `https://chameleon-frontend.onrender.com` | Main app |
| Backend | `https://chameleon-backend.onrender.com` | API |
| API Docs | `https://chameleon-backend.onrender.com/docs` | Swagger UI |
| Health | `https://chameleon-backend.onrender.com/api/health` | Status check |

---

## 🎉 Success!

Once deployed, your app will be live at:

**🌐 https://chameleon-frontend.onrender.com**

Login with:
- Username: `admin`
- Password: `chameleon2024`

Navigate to "AI Assistant" to use the chatbot!

---

## 📚 Full Documentation

For detailed information, see:
- `RENDER_DEPLOYMENT.md` - Complete deployment guide
- `QUICK_START.md` - Local development guide
- `COMMANDS_REFERENCE.md` - All commands

---

**Need Help?**

1. Check Render logs
2. Review `RENDER_DEPLOYMENT.md`
3. Test locally with `./start.sh`
4. Verify environment variables

---

**Quick Deploy:** Just follow the 3 steps above! 🚀
