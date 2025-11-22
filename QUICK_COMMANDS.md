# Chameleon Quick Commands Reference

## 🚀 Development

### Start Everything (Dev Mode)
```bash
npm start
```
- Starts both frontend and backend
- Hot reload enabled
- Frontend: http://localhost:5173
- Backend: http://localhost:8000

---

## 🏗️ Build for Production

### Single Build Command
```bash
npm run build
```
**OR**
```bash
build.bat          # Windows
./build.sh         # Linux/macOS
```

**Output:**
- Frontend: `frontend/dist/` (ready to deploy)
- Backend: `Backend/` (runs from source)

---

## 📦 Installation

### Install All Dependencies
```bash
npm run install:all
```

### Individual Installation
```bash
npm run install:backend    # Python dependencies
npm run install:frontend   # Node dependencies
```

---

## 🎯 Individual Commands

### Start Individual Services
```bash
npm run start:backend      # Backend only
npm run start:frontend     # Frontend only
```

### Build Individual Components
```bash
npm run build:frontend     # Frontend only
npm run build:backend      # Backend check
```

---

## 🌐 Access Points

| Service | URL | Credentials |
|---------|-----|-------------|
| Frontend | http://localhost:5173 | admin / chameleon2024 |
| Backend API | http://localhost:8000 | - |
| API Docs | http://localhost:8000/docs | - |

---

## 📋 Complete Command List

| Command | Description |
|---------|-------------|
| `npm start` | Start dev servers (both) |
| `npm run build` | Build for production |
| `npm run install:all` | Install all dependencies |
| `npm run start:backend` | Start backend only |
| `npm run start:frontend` | Start frontend only |
| `npm run build:frontend` | Build frontend only |
| `npm run build:backend` | Check backend |
| `npm run install:backend` | Install backend deps |
| `npm run install:frontend` | Install frontend deps |

---

## 🚢 Production Deployment

### Quick Deploy
```bash
# 1. Build
npm run build

# 2. Deploy frontend/dist/ to your web server

# 3. Start backend
cd Backend
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## ⚡ Quick Start (First Time)

```bash
# 1. Install everything
npm run install:all

# 2. Start development
npm start

# 3. Open browser
# http://localhost:5173
```

---

## 🛑 Stop Servers

Press `Ctrl+C` in the terminal running `npm start`

---

**Status:** ✅ All commands operational
**Last Updated:** 2025-11-23
