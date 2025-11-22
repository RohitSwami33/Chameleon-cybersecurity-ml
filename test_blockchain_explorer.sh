#!/bin/bash

echo "🔗 Testing Blockchain Explorer"
echo "=============================="
echo ""

# Test attacks to populate blockchain
echo "1️⃣ Submitting test attacks to populate blockchain..."
echo ""

# Submit various attacks
curl -s -X POST http://localhost:8000/api/trap/submit \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "SELECT * FROM users WHERE id=1 OR 1=1",
    "ip_address": "45.33.32.156"
  }' > /dev/null

curl -s -X POST http://localhost:8000/api/trap/submit \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "<script>alert(\"XSS\")</script>",
    "ip_address": "185.220.101.1"
  }' > /dev/null

curl -s -X POST http://localhost:8000/api/trap/submit \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "<!--#exec cmd=\"/bin/ls\" -->",
    "ip_address": "104.16.132.229"
  }' > /dev/null

curl -s -X POST http://localhost:8000/api/trap/submit \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "Hello, this is a normal request",
    "ip_address": "8.8.8.8"
  }' > /dev/null

echo "✅ Submitted 4 test attacks"
echo ""

# Login
echo "2️⃣ Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"chameleon2024"}')

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [[ -z "$TOKEN" ]]; then
    echo "❌ Login failed"
    exit 1
fi

echo "✅ Login successful"
echo ""

# Test blockchain endpoint
echo "3️⃣ Testing Blockchain API..."
echo ""

echo "📊 Analytics:"
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/threat-scores/analytics" | python3 -m json.tool
echo ""

echo "🔗 Blockchain Records (first 5):"
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/threat-scores/blockchain?skip=0&limit=5" | python3 -m json.tool
echo ""

echo "🎯 Top Threats:"
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/threat-scores/top-threats" | python3 -m json.tool
echo ""

echo "✅ Blockchain Explorer API is working!"
echo ""
echo "🌐 Access the UI at:"
echo "   http://localhost:5174/blockchain"
echo ""
echo "🔑 Login credentials:"
echo "   Username: admin"
echo "   Password: chameleon2024"
echo ""
