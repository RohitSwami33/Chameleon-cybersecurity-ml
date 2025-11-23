#!/bin/bash

# Chameleon Cybersecurity ML - Build Script
# This script builds the application for production

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     CHAMELEON ADAPTIVE DECEPTION SYSTEM - BUILD           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check prerequisites
echo -e "${BLUE}🔍 Checking prerequisites...${NC}"

if ! command -v python3.12 &> /dev/null; then
    echo -e "${RED}❌ Python 3.12 not found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python 3.12 found${NC}"

if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Node.js found${NC}"

echo ""

# Build Backend
echo -e "${BLUE}🔧 Building Backend...${NC}"
cd Backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creating Python virtual environment...${NC}"
    python3.12 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo -e "${GREEN}✅ Backend dependencies installed${NC}"

# Optional: Run tests
# echo -e "${YELLOW}🧪 Running backend tests...${NC}"
# python -m pytest tests/

cd ..

# Build Frontend
echo -e "${BLUE}🔧 Building Frontend...${NC}"
cd frontend

# Install dependencies
echo -e "${YELLOW}📦 Installing Node.js dependencies...${NC}"
npm install --silent

# Build for production
echo -e "${YELLOW}🏗️  Building frontend for production...${NC}"
npm run build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Frontend built successfully${NC}"
    echo -e "${GREEN}   Output: frontend/dist/${NC}"
else
    echo -e "${RED}❌ Frontend build failed${NC}"
    exit 1
fi

cd ..

# Summary
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    🎉 BUILD COMPLETE                       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}📦 Build Artifacts:${NC}"
echo -e "   Backend:  ${GREEN}Backend/venv/${NC}"
echo -e "   Frontend: ${GREEN}frontend/dist/${NC}"
echo ""
echo -e "${BLUE}📝 Next Steps:${NC}"
echo -e "   Development: ${YELLOW}./start.sh${NC}"
echo -e "   Production:  ${YELLOW}./deploy.sh${NC} (if available)"
echo ""
echo -e "${GREEN}✨ Ready for deployment!${NC}"
echo ""
