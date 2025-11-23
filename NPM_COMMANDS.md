# 🚀 NPM Commands Guide

## ⚡ Single Commands to Build and Start

### 🎯 Quick Start (One Command)

```bash
npm run setup && npm start
```

This will:
1. Install all dependencies (backend + frontend)
2. Start both servers
3. Open on http://localhost:8000 (backend) and http://localhost:5174 (frontend)

---

## 📋 Available NPM Commands

### Start Commands

#### Start Everything (Backend + Frontend)
```bash
npm start
```
or
```bash
npm run dev
```

**What it does:**
- Starts Backend on port 8000 (with hot reload)
- Starts Frontend on port 5174 (with hot reload)
- Runs both concurrently

---

#### Start Backend Only
```bash
npm run start:backend
```

**What it does:**
- Activates Python virtual environment
- Starts uvicorn with hot reload
- Runs on http://localhost:8000

---

#### Start Frontend Only
```bash
npm run start:frontend
```

**What it does:**
- Starts Vite dev server
- Runs on http://localhost:5174

---

### Build Commands

#### Build Everything
```bash
npm run build
```

**What it does:**
1. Creates Python virtual environment
2. Installs all Python dependencies
3. Installs all Node.js dependencies
4. Builds frontend for production

---

#### Build Backend Only
```bash
npm run build:backend
```

**What it does:**
- Creates Python virtual environment
- Upgrades pip
- Installs all Python dependencies from requirements.txt

---

#### Build Frontend Only
```bash
npm run build:frontend
```

**What it does:**
- Installs Node.js dependencies
- Builds optimized production bundle
- Outputs to `frontend/dist/`

---

### Install Commands

#### Install All Dependencies
```bash
npm run install:all
```

**What it does:**
- Installs Python dependencies (Backend)
- Installs Node.js dependencies (Frontend)

---

#### Install Backend Dependencies
```bash
npm run install:backend
```

**What it does:**
- Activates virtual environment
- Installs Python packages from requirements.txt

---

#### Install Frontend Dependencies
```bash
npm run install:frontend
```

**What it does:**
- Installs Node.js packages from package.json

---

### Setup Command

#### Complete Setup (First Time)
```bash
npm run setup
```

**What it does:**
1. Installs root dependencies (concurrently)
2. Creates Python virtual environment
3. Installs all Python dependencies
4. Installs all Node.js dependencies

**Use this for first-time setup!**

---

## 🎯 Common Workflows

### First Time Setup
```bash
npm run setup
npm start
```

### Daily Development
```bash
npm start
```

### Build for Production
```bash
npm run build
```

### After Pulling Changes
```bash
npm run install:all
npm start
```

---

## 📊 Command Reference Table

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `npm run setup` | Complete first-time setup | First time only |
| `npm start` | Start both servers | Daily development |
| `npm run dev` | Same as start | Daily development |
| `npm run build` | Build everything | Before deployment |
| `npm run install:all` | Install all dependencies | After git pull |
| `npm run start:backend` | Start backend only | Backend development |
| `npm run start:frontend` | Start frontend only | Frontend development |

---

## 🔧 What Each Script Does

### `npm start`
```json
"start": "concurrently \"npm run start:backend\" \"npm run start:frontend\""
```
Runs both backend and frontend simultaneously using concurrently.

### `npm run start:backend`
```json
"start:backend": "cd Backend && source venv/bin/activate && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
```
- Changes to Backend directory
- Activates Python virtual environment
- Starts uvicorn with hot reload

### `npm run start:frontend`
```json
"start:frontend": "cd frontend && npm run dev"
```
- Changes to frontend directory
- Runs Vite dev server

### `npm run build`
```json
"build": "npm run build:backend && npm run build:frontend"
```
Builds both backend and frontend sequentially.

### `npm run build:backend`
```json
"build:backend": "cd Backend && python3.12 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"
```
- Creates virtual environment
- Upgrades pip
- Installs all Python dependencies

### `npm run build:frontend`
```json
"build:frontend": "cd frontend && npm install && npm run build"
```
- Installs Node.js dependencies
- Builds production bundle

### `npm run setup`
```json
"setup": "npm install && npm run build:backend && npm run install:frontend"
```
Complete setup for first-time use.

---

## 🎨 Output Examples

### When you run `npm start`:
```
[0] INFO:     Uvicorn running on http://0.0.0.0:8000
[0] INFO:     Application startup complete.
[1] VITE v7.2.4  ready in 311 ms
[1] ➜  Local:   http://localhost:5174/
```

### When you run `npm run build`:
```
> Backend: Creating virtual environment...
> Backend: Installing dependencies...
> Frontend: Building for production...
> ✓ built in 11.92s
```

---

## 🚀 Quick Start Guide

### For First Time:
```bash
# 1. Clone repository
git clone https://github.com/RohitSwami33/Chameleon-cybersecurity-ml.git
cd Chameleon-cybersecurity-ml

# 2. Setup everything
npm run setup

# 3. Start development servers
npm start
```

### For Daily Development:
```bash
npm start
```

### For Production Build:
```bash
npm run build
```

---

## 🔍 Troubleshooting

### If `npm start` fails:

1. **Run setup first:**
   ```bash
   npm run setup
   ```

2. **Check if MongoDB is running:**
   ```bash
   mongod --version
   ```

3. **Check if Python 3.12 is installed:**
   ```bash
   python3.12 --version
   ```

4. **Reinstall dependencies:**
   ```bash
   npm run install:all
   ```

---

## 💡 Pro Tips

1. **Use `npm start` for development** - It has hot reload enabled

2. **Use `npm run build` before deployment** - Creates optimized builds

3. **Run `npm run setup` only once** - After that, just use `npm start`

4. **Keep terminal open** - You'll see logs from both servers

5. **Press Ctrl+C to stop** - Stops both servers

---

## 📝 Package.json Scripts

```json
{
  "scripts": {
    "start": "concurrently \"npm run start:backend\" \"npm run start:frontend\"",
    "start:backend": "cd Backend && source venv/bin/activate && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000",
    "start:frontend": "cd frontend && npm run dev",
    "build": "npm run build:backend && npm run build:frontend",
    "build:backend": "cd Backend && python3.12 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt",
    "build:frontend": "cd frontend && npm install && npm run build",
    "dev": "npm run start",
    "install:all": "npm run build:backend && npm run install:frontend",
    "install:backend": "cd Backend && source venv/bin/activate && pip install -r requirements.txt",
    "install:frontend": "cd frontend && npm install",
    "setup": "npm install && npm run build:backend && npm run install:frontend"
  }
}
```

---

## ✅ Summary

**Single command to setup and start:**
```bash
npm run setup && npm start
```

**Single command to start (after setup):**
```bash
npm start
```

**Single command to build:**
```bash
npm run build
```

**That's it!** 🎉

---

## 🌐 Access Points

After running `npm start`:

- **Frontend:** http://localhost:5174
- **Backend:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Chatbot:** http://localhost:5174/dashboard/chatbot

**Login:**
- Username: `admin`
- Password: `chameleon2024`

---

**Quick Reference:**
- Setup: `npm run setup`
- Start: `npm start`
- Build: `npm run build`
- Stop: `Ctrl+C`
