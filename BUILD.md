# Chameleon Build Commands

## ⚡ Single Command - Build Everything

```bash
npm run build
```

This single command builds the entire Chameleon system for production!

**What it does:**
- ✅ Builds frontend (optimized production bundle)
- ✅ Confirms backend is ready (Python runs from source)
- ✅ Creates deployable assets

---

## Alternative Build Methods

### Windows Batch Script
```bash
build.bat
```

### Linux/macOS Shell Script
```bash
chmod +x build.sh
./build.sh
```

---

## Build Output

### Frontend
- **Location**: `frontend/dist/`
- **Contents**: 
  - `index.html` - Entry point
  - `assets/` - Optimized JS and CSS files
- **Size**: ~1.2 MB JS (381 KB gzipped) + 17 KB CSS (3.7 KB gzipped)

### Backend
- **Location**: `Backend/` (source files)
- **Note**: Python-based, runs directly from source
- **No build step required**

---

## Deployment

### Frontend Deployment
```bash
# After building
npm run build

# Deploy the frontend/dist/ folder to:
# - Static hosting (Netlify, Vercel, AWS S3)
# - CDN
# - Nginx/Apache server
```

### Backend Deployment
```bash
cd Backend
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## All Available Commands

| Command | Description |
|---------|-------------|
| `npm run build` | **Build everything (frontend + backend check)** |
| `npm run build:frontend` | Build frontend only |
| `npm run build:backend` | Check backend (no build needed) |
| `npm start` | Start dev servers (both) |
| `npm run start:backend` | Start backend dev server |
| `npm run start:frontend` | Start frontend dev server |
| `npm run install:all` | Install all dependencies |
| `npm run install:backend` | Install backend dependencies |
| `npm run install:frontend` | Install frontend dependencies |

---

## Quick Start Guide

### First Time Setup
```bash
# 1. Install dependencies
npm run install:all

# 2. Start development
npm start
```

### Production Build
```bash
# 1. Build for production
npm run build

# 2. Deploy frontend/dist/ to web server

# 3. Start backend in production mode
cd Backend && uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## Testing the Build

### Test Frontend Build Locally
```bash
# Build
npm run build

# Preview
cd frontend && npm run preview

# Access at http://localhost:4173
```

### Test Backend
```bash
cd Backend
uvicorn main:app --host 127.0.0.1 --port 8000

# Test API
curl http://localhost:8000/api/health
```

---

## Build Performance

- **Frontend Build Time**: ~10 seconds
- **Backend Prep Time**: Instant (no build needed)
- **Total Build Time**: ~10 seconds

---

## Environment Configuration

### Backend (.env)
```env
MONGODB_URL=mongodb+srv://...
DATABASE_NAME=chameleon_db
JWT_SECRET_KEY=your-secret-key
```

### Frontend (.env)
```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## Status: ✅ READY

Single command build system is fully operational!

```bash
npm run build
```

**Last Updated:** 2025-11-23
