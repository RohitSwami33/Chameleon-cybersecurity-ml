#!/bin/bash

# Chameleon Cybersecurity ML - Stop Script
# This script stops both backend and frontend servers

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     CHAMELEON ADAPTIVE DECEPTION SYSTEM - SHUTDOWN        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${YELLOW}🛑 Stopping servers...${NC}"
echo ""

# Stop Backend
echo -e "${BLUE}Stopping Backend (uvicorn)...${NC}"
pkill -f "uvicorn main:app" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Backend stopped${NC}"
else
    echo -e "${YELLOW}⚠️  No backend process found${NC}"
fi

# Stop Frontend
echo -e "${BLUE}Stopping Frontend (vite)...${NC}"
pkill -f "vite" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Frontend stopped${NC}"
else
    echo -e "${YELLOW}⚠️  No frontend process found${NC}"
fi

# Optional: Stop MongoDB (commented out by default)
# echo -e "${BLUE}Stopping MongoDB...${NC}"
# pkill -f "mongod" 2>/dev/null
# if [ $? -eq 0 ]; then
#     echo -e "${GREEN}✅ MongoDB stopped${NC}"
# else
#     echo -e "${YELLOW}⚠️  No MongoDB process found${NC}"
# fi

echo ""
echo -e "${GREEN}✅ All servers stopped${NC}"
echo ""
