# 📚 Commands Reference Guide

## 🎯 Quick Commands

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `./start.sh` | Start development servers | Daily development |
| `./stop.sh` | Stop all servers | End of work |
| `./build.sh` | Build for production | Before deployment |
| `./test_integration.sh` | Test integration | After changes |

---

## 🚀 Development Commands

### Start Everything (Development Mode)
```bash
./start.sh
```

**What it does:**
- Installs dependencies (if needed)
- Starts Backend in development mode (hot reload)
- Starts Frontend in development mode (hot reload)
- Shows real-time logs

**When to use:**
- Daily development
- Testing features
- Debugging

**Ports:**
- Backend: http://localhost:8000
- Frontend: http://localhost:5174

---

### Stop Everything
```bash
./stop.sh
```

**What it does:**
- Stops Backend server
- Stops Frontend server
- Clean shutdown

**When to use:**
- End of work session
- Before system restart
- When switching projects

---

### Build for Production
```bash
./build.sh
```

**What it does:**
- Installs all dependencies
- Builds optimized frontend bundle
- Prepares backend for production
- Creates `frontend/dist/` folder

**When to use:**
- Before deployment
- Creating production build
- Performance testing

**Output:**
- `frontend/dist/` - Production-ready frontend
- `Backend/venv/` - Python environment

---

## 📦 Individual Component Commands

### Backend Commands

#### Start Backend (Development)
```bash
cd Backend
source venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Options:**
- `--reload` - Auto-reload on code changes
- `--host 0.0.0.0` - Listen on all interfaces
- `--port 8000` - Port number

#### Start Backend (Production)
```bash
cd Backend
source venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Options:**
- `--workers 4` - Multiple worker processes
- No `--reload` for production

#### Install Backend Dependencies
```bash
cd Backend
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Update Backend Dependencies
```bash
cd Backend
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

---

### Frontend Commands

#### Start Frontend (Development)
```bash
cd frontend
npm run dev
```

**What it does:**
- Starts Vite dev server
- Enables hot module replacement (HMR)
- Opens on http://localhost:5174

#### Build Frontend (Production)
```bash
cd frontend
npm run build
```

**What it does:**
- Creates optimized production build
- Minifies JavaScript and CSS
- Outputs to `dist/` folder

#### Preview Production Build
```bash
cd frontend
npm run preview
```

**What it does:**
- Serves the production build locally
- Tests production build before deployment

#### Install Frontend Dependencies
```bash
cd frontend
npm install
```

#### Update Frontend Dependencies
```bash
cd frontend
npm update
```

#### Clean Install (Fix Issues)
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

## 🧪 Testing Commands

### Integration Tests
```bash
./test_integration.sh
```

**Tests:**
- Backend health
- CORS configuration
- Frontend accessibility
- Authentication
- Protected endpoints
- Chatbot API

### Manual API Tests
```bash
# Health check
curl http://localhost:8000/api/health

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"chameleon2024"}'

# Dashboard stats (requires token)
curl http://localhost:8000/api/dashboard/stats \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 📝 Log Commands

### View Backend Logs
```bash
tail -f backend.log
```

### View Frontend Logs
```bash
tail -f frontend.log
```

### View Both Logs
```bash
tail -f backend.log frontend.log
```

### View Last 100 Lines
```bash
tail -100 backend.log
tail -100 frontend.log
```

### Search Logs for Errors
```bash
grep -i error backend.log
grep -i error frontend.log
```

---

## 🗄️ Database Commands

### Start MongoDB
```bash
mongod --dbpath ./Backend/data --logpath ./Backend/data/mongod.log --fork
```

### Stop MongoDB
```bash
pkill mongod
```

### MongoDB Shell
```bash
mongosh
use chameleon_db
db.attack_logs.find().limit(10)
```

### Backup Database
```bash
mongodump --db chameleon_db --out ./backup
```

### Restore Database
```bash
mongorestore --db chameleon_db ./backup/chameleon_db
```

---

## 🔧 Troubleshooting Commands

### Kill Process on Port
```bash
# Kill backend (port 8000)
lsof -ti :8000 | xargs kill -9

# Kill frontend (port 5174)
lsof -ti :5174 | xargs kill -9

# Kill MongoDB (port 27017)
lsof -ti :27017 | xargs kill -9
```

### Check What's Running on Port
```bash
lsof -i :8000  # Backend
lsof -i :5174  # Frontend
lsof -i :27017 # MongoDB
```

### Check Running Processes
```bash
ps aux | grep uvicorn  # Backend
ps aux | grep vite     # Frontend
ps aux | grep mongod   # MongoDB
```

### Clean Everything
```bash
./stop.sh
pkill -f mongod
rm -f backend.log frontend.log
rm -rf Backend/venv
rm -rf frontend/node_modules
```

### Fresh Start
```bash
./stop.sh
rm -f backend.log frontend.log
./start.sh
```

---

## 🎨 Package Management

### Backend (Python)

#### List Installed Packages
```bash
cd Backend
source venv/bin/activate
pip list
```

#### Install New Package
```bash
cd Backend
source venv/bin/activate
pip install package-name
pip freeze > requirements.txt
```

#### Uninstall Package
```bash
cd Backend
source venv/bin/activate
pip uninstall package-name
```

### Frontend (Node.js)

#### List Installed Packages
```bash
cd frontend
npm list --depth=0
```

#### Install New Package
```bash
cd frontend
npm install package-name
```

#### Install Dev Dependency
```bash
cd frontend
npm install --save-dev package-name
```

#### Uninstall Package
```bash
cd frontend
npm uninstall package-name
```

---

## 🚀 Deployment Commands

### Build for Production
```bash
./build.sh
```

### Deploy Frontend (Example with Netlify)
```bash
cd frontend
npm run build
netlify deploy --prod --dir=dist
```

### Deploy Backend (Example with Docker)
```bash
cd Backend
docker build -t chameleon-backend .
docker run -p 8000:8000 chameleon-backend
```

---

## 📊 Monitoring Commands

### Check System Resources
```bash
# CPU and Memory usage
top

# Disk usage
df -h

# Process-specific resources
ps aux | grep uvicorn
ps aux | grep node
```

### Monitor Logs in Real-Time
```bash
# With colors
tail -f backend.log | grep --color=auto -E 'ERROR|WARNING|INFO'

# Multiple files
multitail backend.log frontend.log
```

---

## 🔐 Security Commands

### Generate New JWT Secret
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Check Open Ports
```bash
netstat -tuln | grep LISTEN
```

### Test CORS
```bash
curl -I -X OPTIONS http://localhost:8000/api/health \
  -H "Origin: http://localhost:5174" \
  -H "Access-Control-Request-Method: GET"
```

---

## 📚 Documentation Commands

### View API Documentation
```bash
# Start backend first, then open:
open http://localhost:8000/docs
```

### Generate API Documentation
```bash
cd Backend
source venv/bin/activate
python -c "from main import app; import json; print(json.dumps(app.openapi(), indent=2))" > api-docs.json
```

---

## 🎯 Common Workflows

### Daily Development
```bash
./start.sh
# ... do your work ...
./stop.sh
```

### After Pulling Changes
```bash
./stop.sh
git pull
cd Backend && source venv/bin/activate && pip install -r requirements.txt && cd ..
cd frontend && npm install && cd ..
./start.sh
```

### Before Committing
```bash
./test_integration.sh
# If tests pass:
git add .
git commit -m "Your message"
git push
```

### Preparing for Deployment
```bash
./build.sh
./test_integration.sh
# If everything passes, deploy
```

---

## 📋 Command Cheat Sheet

```bash
# Quick Start
./start.sh              # Start everything
./stop.sh               # Stop everything
./build.sh              # Build for production
./test_integration.sh   # Run tests

# Backend
cd Backend && source venv/bin/activate
python -m uvicorn main:app --reload
pip install -r requirements.txt

# Frontend
cd frontend
npm run dev             # Development
npm run build           # Production build
npm run preview         # Preview build
npm install             # Install dependencies

# Logs
tail -f backend.log
tail -f frontend.log

# Database
mongod --dbpath ./Backend/data --fork
mongosh

# Troubleshooting
lsof -ti :8000 | xargs kill -9
lsof -ti :5174 | xargs kill -9
./stop.sh && ./start.sh
```

---

## 🆘 Help Commands

### Get Help
```bash
# Backend
cd Backend
source venv/bin/activate
python -m uvicorn --help

# Frontend
cd frontend
npm run dev -- --help
```

### Check Versions
```bash
python3.12 --version
node --version
npm --version
mongod --version
```

---

## 💡 Pro Tips

1. **Use aliases** in your `.bashrc` or `.zshrc`:
   ```bash
   alias cham-start='cd ~/path/to/project && ./start.sh'
   alias cham-stop='cd ~/path/to/project && ./stop.sh'
   alias cham-logs='cd ~/path/to/project && tail -f backend.log frontend.log'
   ```

2. **Keep logs open** in separate terminal windows

3. **Use tmux** for managing multiple terminals:
   ```bash
   tmux new -s chameleon
   # Split panes and run different commands
   ```

4. **Create shortcuts** for common tasks

5. **Monitor resources** during development

---

**Quick Reference:**
- Start: `./start.sh`
- Stop: `./stop.sh`
- Build: `./build.sh`
- Test: `./test_integration.sh`
- Logs: `tail -f backend.log frontend.log`

**Need help?** Check `QUICK_START.md` for detailed guide!
