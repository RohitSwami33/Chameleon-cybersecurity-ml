#!/bin/bash

echo "🔍 Testing Dashboard Access Flow"
echo "================================"
echo ""

# Test 1: Health Check
echo "1️⃣ Testing Backend Health..."
HEALTH=$(curl -s http://localhost:8000/api/health)
if [[ $HEALTH == *"healthy"* ]]; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend is not responding"
    exit 1
fi
echo ""

# Test 2: Login
echo "2️⃣ Testing Login..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"chameleon2024"}')

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [[ -n "$TOKEN" ]]; then
    echo "✅ Login successful"
    echo "   Token: ${TOKEN:0:50}..."
else
    echo "❌ Login failed"
    echo "   Response: $LOGIN_RESPONSE"
    exit 1
fi
echo ""

# Test 3: Dashboard Stats
echo "3️⃣ Testing Dashboard Stats..."
STATS=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/dashboard/stats)

if [[ $STATS == *"total_attempts"* ]]; then
    echo "✅ Dashboard stats retrieved successfully"
    
    # Parse some stats
    TOTAL=$(echo $STATS | grep -o '"total_attempts":[0-9]*' | cut -d':' -f2)
    MALICIOUS=$(echo $STATS | grep -o '"malicious_attempts":[0-9]*' | cut -d':' -f2)
    BENIGN=$(echo $STATS | grep -o '"benign_attempts":[0-9]*' | cut -d':' -f2)
    
    echo "   📊 Total Attempts: $TOTAL"
    echo "   🔴 Malicious: $MALICIOUS"
    echo "   🟢 Benign: $BENIGN"
else
    echo "❌ Failed to retrieve dashboard stats"
    echo "   Response: ${STATS:0:200}..."
    exit 1
fi
echo ""

# Test 4: Dashboard Logs
echo "4️⃣ Testing Dashboard Logs..."
LOGS=$(curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/dashboard/logs?skip=0&limit=5")

if [[ $LOGS == *"["* ]]; then
    echo "✅ Dashboard logs retrieved successfully"
    LOG_COUNT=$(echo $LOGS | grep -o '"ip_address"' | wc -l | tr -d ' ')
    echo "   📝 Retrieved $LOG_COUNT logs"
else
    echo "❌ Failed to retrieve dashboard logs"
    exit 1
fi
echo ""

# Test 5: Threat Scores
echo "5️⃣ Testing Threat Scores..."
THREATS=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/threat-scores/top-threats)

if [[ $THREATS == *"top_threats"* ]]; then
    echo "✅ Threat scores retrieved successfully"
    THREAT_COUNT=$(echo $THREATS | grep -o '"count":[0-9]*' | head -1 | cut -d':' -f2)
    echo "   ⚠️  Top Threats: $THREAT_COUNT"
else
    echo "❌ Failed to retrieve threat scores"
    exit 1
fi
echo ""

echo "================================"
echo "✅ All tests passed!"
echo ""
echo "🌐 Access the dashboard at:"
echo "   http://localhost:5174/login"
echo ""
echo "🔑 Credentials:"
echo "   Username: admin"
echo "   Password: chameleon2024"
echo ""
