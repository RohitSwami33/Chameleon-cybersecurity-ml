# 🎯 Commands Summary - Quick Reference

## 📋 Main Commands

```
┌─────────────────────────────────────────────────────────────┐
│                    MAIN COMMANDS                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ./start.sh              Start everything (development)    │
│  ./stop.sh               Stop all servers                  │
│  ./build.sh              Build for production              │
│  ./test_integration.sh   Test integration                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Start Command

### `./start.sh`

**What it does:**
```
1. ✅ Checks Python 3.12, Node.js, npm, MongoDB
2. ✅ Creates Python virtual environment
3. ✅ Installs Python dependencies (pip install)
4. ✅ Installs Node.js dependencies (npm install)
5. ✅ Starts Backend on port 8000
6. ✅ Starts Frontend on port 5174
7. ✅ Verifies both servers are running
8. ✅ Shows access URLs
```

**Output:**
```
Backend:  http://localhost:8000
Frontend: http://localhost:5174
Chatbot:  http://localhost:5174/dashboard/chatbot
```

**Features:**
- 🔄 Hot reload enabled (auto-refresh on code changes)
- 📝 Real-time logs
- 🔍 Health checks
- ⚡ Fast startup

---

## 🏗️ Build Command

### `./build.sh`

**What it does:**
```
1. ✅ Installs all dependencies
2. ✅ Builds optimized frontend (npm run build)
3. ✅ Creates production-ready files
4. ✅ Outputs to frontend/dist/
```

**Output:**
```
frontend/dist/          Production frontend files
Backend/venv/           Python environment
```

**When to use:**
- Before deployment
- Performance testing
- Creating production bundle

---

## 🛑 Stop Command

### `./stop.sh`

**What it does:**
```
1. ✅ Stops Backend (uvicorn)
2. ✅ Stops Frontend (vite)
3. ✅ Clean shutdown
```

**When to use:**
- End of work
- Before restart
- Switching projects

---

## 🔄 Development Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                  DAILY WORKFLOW                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Morning:                                                   │
│  $ ./start.sh                                               │
│                                                             │
│  During Development:                                        │
│  - Edit code (auto-reloads)                                 │
│  - View logs: tail -f backend.log frontend.log              │
│  - Test: ./test_integration.sh                              │
│                                                             │
│  Evening:                                                   │
│  $ ./stop.sh                                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Individual Commands

### Backend

```bash
# Development (with hot reload)
cd Backend
source venv/bin/activate
python -m uvicorn main:app --reload

# Production (multiple workers)
python -m uvicorn main:app --workers 4
```

### Frontend

```bash
# Development (with hot reload)
cd frontend
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

---

## 🎯 Command Comparison

| Command | Mode | Hot Reload | Use Case |
|---------|------|------------|----------|
| `./start.sh` | Development | ✅ Yes | Daily coding |
| `./build.sh` | Production | ❌ No | Deployment |
| `npm run dev` | Development | ✅ Yes | Frontend only |
| `npm run build` | Production | ❌ No | Build only |

---

## 📊 What Each Command Installs

### `./start.sh` (Development)

**Backend:**
```bash
pip install -r requirements.txt
```
Installs:
- FastAPI, Uvicorn
- TensorFlow 2.16.1
- MongoDB drivers
- Gemini AI SDK
- DuckDuckGo search
- And more...

**Frontend:**
```bash
npm install
```
Installs:
- React 19
- Vite 7
- Material-UI
- Axios
- Framer Motion
- And more...

### `./build.sh` (Production)

**Backend:**
- Same as start.sh

**Frontend:**
```bash
npm run build
```
Creates:
- Minified JavaScript
- Optimized CSS
- Compressed assets
- Production bundle in `dist/`

---

## 🔍 Behind the Scenes

### `./start.sh` Process

```
1. Check Prerequisites
   ├─ Python 3.12? ✅
   ├─ Node.js? ✅
   ├─ npm? ✅
   └─ MongoDB? ✅

2. Setup Backend
   ├─ Create venv (if needed)
   ├─ Activate venv
   ├─ pip install -r requirements.txt
   └─ Start: uvicorn main:app --reload

3. Setup Frontend
   ├─ npm install (if needed)
   └─ Start: npm run dev

4. Verify
   ├─ Backend health check
   ├─ Frontend accessibility
   └─ Show URLs
```

### `./build.sh` Process

```
1. Check Prerequisites
   ├─ Python 3.12? ✅
   └─ Node.js? ✅

2. Build Backend
   ├─ Create venv (if needed)
   └─ pip install -r requirements.txt

3. Build Frontend
   ├─ npm install
   └─ npm run build
       ├─ Minify JS
       ├─ Optimize CSS
       ├─ Compress images
       └─ Output to dist/

4. Summary
   └─ Show build artifacts
```

---

## 💡 Quick Tips

### Fastest Start
```bash
./start.sh
```
That's it! Everything else is automatic.

### View Logs While Running
```bash
tail -f backend.log frontend.log
```

### Restart After Changes
```bash
./stop.sh && ./start.sh
```

### Clean Restart
```bash
./stop.sh
rm -f backend.log frontend.log
./start.sh
```

---

## 🆘 Troubleshooting

### If `./start.sh` fails:

```bash
# 1. Check prerequisites
python3.12 --version
node --version
npm --version

# 2. Clean and retry
./stop.sh
rm -f backend.log frontend.log
./start.sh

# 3. Manual cleanup
lsof -ti :8000 | xargs kill -9
lsof -ti :5174 | xargs kill -9
./start.sh
```

---

## 📚 More Information

- **Full Guide**: `QUICK_START.md`
- **All Commands**: `COMMANDS_REFERENCE.md`
- **CORS Details**: `CORS_INTEGRATION_GUIDE.md`
- **Architecture**: `INTEGRATION_ARCHITECTURE.md`

---

## ✨ Summary

**Start Development:**
```bash
./start.sh
```

**Build for Production:**
```bash
./build.sh
```

**Stop Everything:**
```bash
./stop.sh
```

**That's all you need to know!** 🚀

---

**Quick Access:**
- Frontend: http://localhost:5174
- Backend: http://localhost:8000
- Chatbot: http://localhost:5174/dashboard/chatbot
- Login: admin / chameleon2024
