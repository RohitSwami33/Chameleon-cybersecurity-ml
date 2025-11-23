# 🚀 Quick Start Guide

## One Command to Rule Them All!

### Start Everything
```bash
./start.sh
```

This single command will:
- ✅ Check all prerequisites (Python 3.12, Node.js, npm)
- ✅ Check and start MongoDB if needed
- ✅ Create Python virtual environment (if not exists)
- ✅ Install all Python dependencies
- ✅ Install all Node.js dependencies
- ✅ Start Backend server on port 8000
- ✅ Start Frontend server on port 5174
- ✅ Verify both servers are running
- ✅ Display access URLs and credentials

### Stop Everything
```bash
./stop.sh
```

This will gracefully stop both backend and frontend servers.

## 📋 Prerequisites

Before running `./start.sh`, make sure you have:

1. **Python 3.12** installed
   ```bash
   python3.12 --version
   ```

2. **Node.js** installed
   ```bash
   node --version
   ```

3. **MongoDB** installed
   ```bash
   mongod --version
   ```

## 🎯 Access Points

After running `./start.sh`:

- **Frontend**: http://localhost:5174
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **AI Chatbot**: http://localhost:5174/dashboard/chatbot

## 🔐 Login Credentials

```
Username: admin
Password: chameleon2024
```

## 📊 Features

### Dashboard Pages
- **Overview** - Main dashboard with stats
- **Attack Globe** - 3D visualization of attacks
- **Analytics** - Detailed analytics and charts
- **Threat Intel** - Threat intelligence feed
- **AI Assistant** - AI-powered chatbot (NEW!)
- **Blockchain** - Blockchain explorer

### AI Chatbot Features
- 🤖 Powered by Gemini 2.5 Pro
- 🔍 Web search via DuckDuckGo
- 📊 Attack analysis
- 💡 Smart suggestions
- 📝 Chat history
- 🔗 Source citations

## 🛠️ Manual Setup (Alternative)

If you prefer to start services manually:

### Backend
```bash
cd Backend
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### MongoDB
```bash
mongod --dbpath ./Backend/data --logpath ./Backend/data/mongod.log
```

## 📝 Logs

View real-time logs:

```bash
# Backend logs
tail -f backend.log

# Frontend logs
tail -f frontend.log

# Both logs
tail -f backend.log frontend.log
```

## 🔧 Troubleshooting

### Port Already in Use
If you get "port already in use" errors:

```bash
# Kill backend (port 8000)
lsof -ti :8000 | xargs kill -9

# Kill frontend (port 5174)
lsof -ti :5174 | xargs kill -9
```

Or simply run:
```bash
./stop.sh
./start.sh
```

### MongoDB Not Starting
```bash
# Check if MongoDB is already running
pgrep mongod

# Start MongoDB manually
mongod --dbpath ./Backend/data --logpath ./Backend/data/mongod.log --fork
```

### Dependencies Issues
```bash
# Reinstall Python dependencies
cd Backend
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Reinstall Node dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Backend Not Responding
```bash
# Check backend logs
tail -50 backend.log

# Restart backend
pkill -f "uvicorn main:app"
cd Backend
source venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend Not Loading
```bash
# Check frontend logs
tail -50 frontend.log

# Restart frontend
pkill -f "vite"
cd frontend
npm run dev
```

## 🧪 Testing

### Integration Test
```bash
./test_integration.sh
```

This will test:
- Backend health
- CORS configuration
- Frontend accessibility
- Authentication
- Protected endpoints
- Chatbot API

### Manual API Test
```bash
# Health check
curl http://localhost:8000/api/health

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"chameleon2024"}'
```

## 📚 Documentation

- **CORS Integration**: See `CORS_INTEGRATION_GUIDE.md`
- **Architecture**: See `INTEGRATION_ARCHITECTURE.md`
- **Chatbot Guide**: See `AI_CHATBOT_GUIDE.md`
- **API Documentation**: http://localhost:8000/docs (when running)

## 🎨 Features Overview

### Security Features
- 🛡️ Adaptive deception system
- 🔍 ML-based attack classification
- 🌐 Geo-location tracking
- ⛓️ Blockchain logging
- 📊 Threat scoring
- 🎯 Tarpit management
- 🔐 JWT authentication

### AI Features
- 🤖 Gemini 2.5 Pro integration
- 🔍 Real-time web search
- 📊 Attack analysis
- 💡 Response suggestions
- 📝 Chat history
- 🔗 Source citations

### Visualization
- 🌍 3D attack globe
- 📈 Real-time charts
- 🗺️ Geographic maps
- 📊 Analytics dashboard
- ⛓️ Blockchain explorer

## 🚀 Production Deployment

For production deployment:

1. Update CORS origins in `Backend/main.py`
2. Set environment variables for API keys
3. Use HTTPS
4. Configure proper MongoDB instance
5. Set up reverse proxy (nginx)
6. Enable rate limiting
7. Configure firewall rules

## 💡 Tips

1. **First Time Setup**: The first run may take longer as it installs all dependencies
2. **Hot Reload**: Both frontend and backend support hot reload during development
3. **Logs**: Keep logs open in separate terminals for debugging
4. **MongoDB**: Make sure MongoDB is running before starting the application
5. **Ports**: Default ports are 8000 (backend) and 5174 (frontend)

## 🆘 Support

If you encounter issues:

1. Check logs: `tail -f backend.log frontend.log`
2. Run integration tests: `./test_integration.sh`
3. Restart services: `./stop.sh && ./start.sh`
4. Check prerequisites are installed
5. Verify MongoDB is running

## 📦 Project Structure

```
.
├── Backend/              # Python FastAPI backend
│   ├── main.py          # Main API endpoints
│   ├── chatbot_service.py  # AI chatbot service
│   ├── requirements.txt # Python dependencies
│   └── venv/           # Virtual environment
├── frontend/            # React + Vite frontend
│   ├── src/
│   │   ├── components/ # React components
│   │   ├── pages/      # Page components
│   │   └── services/   # API services
│   └── package.json    # Node dependencies
├── start.sh            # One-command startup
├── stop.sh             # Stop all services
└── test_integration.sh # Integration tests
```

## 🎉 Success!

If everything is working, you should see:

```
✅ Backend is responding on http://localhost:8000
✅ Frontend is responding on http://localhost:5174
✨ Ready to use! Open http://localhost:5174 in your browser
```

Now open your browser and start exploring! 🚀

---

**Quick Commands Summary:**
```bash
./start.sh              # Start everything
./stop.sh               # Stop everything
./test_integration.sh   # Test integration
tail -f backend.log     # View backend logs
tail -f frontend.log    # View frontend logs
```
