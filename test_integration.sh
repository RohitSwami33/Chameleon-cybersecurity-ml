#!/bin/bash

# Integration Test Script for Frontend-Backend Communication
# Tests CORS, API endpoints, and chatbot functionality

echo "🔍 Testing Frontend-Backend Integration"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Backend Health Check
echo "1️⃣  Testing Backend Health..."
HEALTH_RESPONSE=$(curl -s http://localhost:8000/api/health)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Backend is running${NC}"
    echo "   Response: $HEALTH_RESPONSE"
else
    echo -e "${RED}❌ Backend is not responding${NC}"
    exit 1
fi
echo ""

# Test 2: CORS Headers
echo "2️⃣  Testing CORS Configuration..."
CORS_RESPONSE=$(curl -s -I -X OPTIONS http://localhost:8000/api/health \
    -H "Origin: http://localhost:5174" \
    -H "Access-Control-Request-Method: GET")

if echo "$CORS_RESPONSE" | grep -q "access-control-allow-origin"; then
    echo -e "${GREEN}✅ CORS headers present${NC}"
    echo "$CORS_RESPONSE" | grep -i "access-control"
else
    echo -e "${RED}❌ CORS headers missing${NC}"
fi
echo ""

# Test 3: Frontend Accessibility
echo "3️⃣  Testing Frontend Server..."
FRONTEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5174)
if [ "$FRONTEND_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✅ Frontend is accessible${NC}"
    echo "   Status Code: $FRONTEND_RESPONSE"
else
    echo -e "${RED}❌ Frontend is not accessible${NC}"
    echo "   Status Code: $FRONTEND_RESPONSE"
fi
echo ""

# Test 4: Login Endpoint
echo "4️⃣  Testing Login Endpoint..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"chameleon2024"}')

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo -e "${GREEN}✅ Login endpoint working${NC}"
    TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    echo "   Token received: ${TOKEN:0:20}..."
else
    echo -e "${RED}❌ Login endpoint failed${NC}"
    echo "   Response: $LOGIN_RESPONSE"
fi
echo ""

# Test 5: Protected Endpoint (Dashboard Stats)
echo "5️⃣  Testing Protected Endpoint..."
if [ -n "$TOKEN" ]; then
    STATS_RESPONSE=$(curl -s http://localhost:8000/api/dashboard/stats \
        -H "Authorization: Bearer $TOKEN")
    
    if echo "$STATS_RESPONSE" | grep -q "total_attempts"; then
        echo -e "${GREEN}✅ Protected endpoint accessible with token${NC}"
        echo "   Response contains dashboard stats"
    else
        echo -e "${RED}❌ Protected endpoint failed${NC}"
        echo "   Response: $STATS_RESPONSE"
    fi
else
    echo -e "${YELLOW}⚠️  Skipping (no token available)${NC}"
fi
echo ""

# Test 6: Chatbot Endpoint
echo "6️⃣  Testing Chatbot Endpoint..."
if [ -n "$TOKEN" ]; then
    CHATBOT_RESPONSE=$(curl -s -X POST http://localhost:8000/api/chatbot/chat \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"message":"test","use_search":false}')
    
    if echo "$CHATBOT_RESPONSE" | grep -q "response"; then
        echo -e "${GREEN}✅ Chatbot endpoint working${NC}"
        echo "   Response received from AI"
    else
        echo -e "${RED}❌ Chatbot endpoint failed${NC}"
        echo "   Response: $CHATBOT_RESPONSE"
    fi
else
    echo -e "${YELLOW}⚠️  Skipping (no token available)${NC}"
fi
echo ""

# Test 7: WebSocket Support (if applicable)
echo "7️⃣  Testing WebSocket Support..."
if command -v wscat &> /dev/null; then
    echo -e "${YELLOW}⚠️  WebSocket test requires wscat (npm install -g wscat)${NC}"
else
    echo -e "${YELLOW}⚠️  wscat not installed, skipping WebSocket test${NC}"
fi
echo ""

# Summary
echo "========================================"
echo "📊 Integration Test Summary"
echo "========================================"
echo ""
echo "Backend URL: http://localhost:8000"
echo "Frontend URL: http://localhost:5174"
echo "Chatbot Page: http://localhost:5174/dashboard/chatbot"
echo ""
echo -e "${GREEN}✅ Integration tests completed!${NC}"
echo ""
echo "Next steps:"
echo "1. Open http://localhost:5174 in your browser"
echo "2. Login with admin/chameleon2024"
echo "3. Navigate to AI Assistant page"
echo "4. Test the chatbot functionality"
