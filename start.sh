#!/bin/bash

# Chameleon Cybersecurity ML - One Command Startup Script
# This script starts both backend and frontend servers

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     CHAMELEON ADAPTIVE DECEPTION SYSTEM - STARTUP        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    lsof -i :"$1" >/dev/null 2>&1
}

# Function to kill process on port
kill_port() {
    local port=$1
    echo -e "${YELLOW}⚠️  Port $port is in use. Killing existing process...${NC}"
    lsof -ti :$port | xargs kill -9 2>/dev/null || true
    sleep 2
}

# Check prerequisites
echo -e "${BLUE}🔍 Checking prerequisites...${NC}"

if ! command_exists python3.12; then
    echo -e "${RED}❌ Python 3.12 not found. Please install Python 3.12${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python 3.12 found${NC}"

if ! command_exists node; then
    echo -e "${RED}❌ Node.js not found. Please install Node.js${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Node.js found ($(node --version))${NC}"

if ! command_exists npm; then
    echo -e "${RED}❌ npm not found. Please install npm${NC}"
    exit 1
fi
echo -e "${GREEN}✅ npm found ($(npm --version))${NC}"

echo ""

# Check if MongoDB is running
echo -e "${BLUE}🔍 Checking MongoDB...${NC}"
if ! pgrep -x mongod > /dev/null; then
    echo -e "${YELLOW}⚠️  MongoDB is not running${NC}"
    echo -e "${YELLOW}   Starting MongoDB...${NC}"
    mongod --dbpath ./Backend/data --logpath ./Backend/data/mongod.log --fork 2>/dev/null || {
        echo -e "${YELLOW}   Note: MongoDB may already be running as a service${NC}"
    }
else
    echo -e "${GREEN}✅ MongoDB is running${NC}"
fi

echo ""

# Setup Backend
echo -e "${BLUE}🔧 Setting up Backend...${NC}"
cd Backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creating Python virtual environment...${NC}"
    python3.12 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/Update dependencies
echo -e "${YELLOW}📦 Installing/Updating Python dependencies...${NC}"
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo -e "${GREEN}✅ Backend dependencies installed${NC}"

# Kill existing backend process
if port_in_use 8000; then
    kill_port 8000
fi

# Start Backend
echo -e "${BLUE}🚀 Starting Backend Server...${NC}"
python -m uvicorn main:app --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"

cd ..

# Setup Frontend
echo -e "${BLUE}🔧 Setting up Frontend...${NC}"
cd frontend

# Install/Update dependencies
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Installing Node.js dependencies (this may take a while)...${NC}"
    npm install
else
    echo -e "${YELLOW}📦 Checking Node.js dependencies...${NC}"
    npm install --silent
fi

echo -e "${GREEN}✅ Frontend dependencies installed${NC}"

# Kill existing frontend process
if port_in_use 5173; then
    kill_port 5173
fi
if port_in_use 5174; then
    kill_port 5174
fi

# Start Frontend
echo -e "${BLUE}🚀 Starting Frontend Server...${NC}"
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"

cd ..

# Wait for servers to start
echo ""
echo -e "${YELLOW}⏳ Waiting for servers to initialize...${NC}"
sleep 5

# Check if servers are running
echo ""
echo -e "${BLUE}🔍 Verifying servers...${NC}"

# Check Backend
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is responding on http://localhost:8000${NC}"
else
    echo -e "${RED}❌ Backend is not responding${NC}"
    echo -e "${YELLOW}   Check backend.log for errors${NC}"
fi

# Check Frontend
if curl -s http://localhost:5174 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend is responding on http://localhost:5174${NC}"
elif curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend is responding on http://localhost:5173${NC}"
else
    echo -e "${RED}❌ Frontend is not responding${NC}"
    echo -e "${YELLOW}   Check frontend.log for errors${NC}"
fi

# Display summary
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    🎉 STARTUP COMPLETE                     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}📊 Application Status:${NC}"
echo -e "   Backend:  ${GREEN}http://localhost:8000${NC}"
echo -e "   Frontend: ${GREEN}http://localhost:5174${NC} (or 5173)"
echo -e "   API Docs: ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo -e "${GREEN}🤖 AI Chatbot:${NC}"
echo -e "   ${GREEN}http://localhost:5174/dashboard/chatbot${NC}"
echo ""
echo -e "${GREEN}🔐 Login Credentials:${NC}"
echo -e "   Username: ${YELLOW}admin${NC}"
echo -e "   Password: ${YELLOW}chameleon2024${NC}"
echo ""
echo -e "${BLUE}📝 Logs:${NC}"
echo -e "   Backend:  ${YELLOW}tail -f backend.log${NC}"
echo -e "   Frontend: ${YELLOW}tail -f frontend.log${NC}"
echo ""
echo -e "${BLUE}🛑 To stop servers:${NC}"
echo -e "   ${YELLOW}./stop.sh${NC}"
echo -e "   or"
echo -e "   ${YELLOW}pkill -f 'uvicorn main:app'${NC}"
echo -e "   ${YELLOW}pkill -f 'vite'${NC}"
echo ""
echo -e "${GREEN}✨ Ready to use! Open http://localhost:5174 in your browser${NC}"
echo ""

# Keep script running to show logs
echo -e "${BLUE}Press Ctrl+C to stop watching logs (servers will continue running)${NC}"
echo ""
tail -f backend.log frontend.log
