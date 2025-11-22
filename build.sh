#!/bin/bash

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "========================================"
echo "Chameleon Build Script"
echo "========================================"
echo

echo -e "${BLUE}[1/2] Building Frontend...${NC}"
cd frontend
npm run build
if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Frontend build failed!${NC}"
    cd ..
    exit 1
fi
cd ..
echo -e "${GREEN}✓ Frontend built successfully${NC}"
echo

echo -e "${BLUE}[2/2] Backend Check...${NC}"
echo "Backend is Python-based and runs from source"
echo "No build step required"
echo -e "${GREEN}✓ Backend ready${NC}"
echo

echo "========================================"
echo "Build Complete!"
echo "========================================"
echo
echo "Frontend Output: frontend/dist/"
echo "Backend Source: Backend/"
echo
echo "To deploy:"
echo "1. Deploy frontend/dist/ to your web server"
echo "2. Run backend with: cd Backend && uvicorn main:app --host 0.0.0.0 --port 8000"
echo
