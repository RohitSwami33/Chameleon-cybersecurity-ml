#!/bin/bash

echo "=========================================="
echo "Testing Adaptive Deception Engine"
echo "=========================================="
echo ""

echo "1. Testing SQLi with UNION (Context-Aware)"
echo "-------------------------------------------"
curl -s -X POST http://localhost:8000/api/trap/submit \
  -H "Content-Type: application/json" \
  -d '{"input_text":"SELECT * FROM users UNION SELECT password FROM admin","ip_address":"51.15.43.205"}' | python3 -m json.tool
echo ""

echo "2. Testing SQLi with DROP (Context-Aware)"
echo "-------------------------------------------"
curl -s -X POST http://localhost:8000/api/trap/submit \
  -H "Content-Type: application/json" \
  -d '{"input_text":"DROP TABLE users CASCADE","ip_address":"80.67.169.12"}' | python3 -m json.tool
echo ""

echo "3. Testing SQLi with information_schema (Context-Aware)"
echo "-------------------------------------------"
curl -s -X POST http://localhost:8000/api/trap/submit \
  -H "Content-Type: application/json" \
  -d '{"input_text":"SELECT * FROM information_schema.columns","ip_address":"195.154.133.20"}' | python3 -m json.tool
echo ""

echo "4. Testing Regular SQLi"
echo "-------------------------------------------"
curl -s -X POST http://localhost:8000/api/trap/submit \
  -H "Content-Type: application/json" \
  -d '{"input_text":"admin OR 1=1 --","ip_address":"91.121.161.184"}' | python3 -m json.tool
echo ""

echo "5. Testing XSS with <script>"
echo "-------------------------------------------"
curl -s -X POST http://localhost:8000/api/trap/submit \
  -H "Content-Type: application/json" \
  -d '{"input_text":"<script>alert(document.cookie)</script>","ip_address":"139.162.130.8"}' | python3 -m json.tool
echo ""

echo "6. Testing XSS with javascript:"
echo "-------------------------------------------"
curl -s -X POST http://localhost:8000/api/trap/submit \
  -H "Content-Type: application/json" \
  -d '{"input_text":"<img src=x onerror=alert(1)>","ip_address":"172.104.136.243"}' | python3 -m json.tool
echo ""

echo "7. Testing SSI Attack"
echo "-------------------------------------------"
curl -s -X POST http://localhost:8000/api/trap/submit \
  -H "Content-Type: application/json" \
  -d '{"input_text":"<!--#exec cmd=\"whoami\" -->","ip_address":"178.62.214.105"}' | python3 -m json.tool
echo ""

echo "8. Testing SSI with include"
echo "-------------------------------------------"
curl -s -X POST http://localhost:8000/api/trap/submit \
  -H "Content-Type: application/json" \
  -d '{"input_text":"<!--#include virtual=\"/etc/passwd\" -->","ip_address":"46.101.169.79"}' | python3 -m json.tool
echo ""

echo "9. Testing Benign Request"
echo "-------------------------------------------"
curl -s -X POST http://localhost:8000/api/trap/submit \
  -H "Content-Type: application/json" \
  -d '{"input_text":"Hello, this is a normal message","ip_address":"188.166.149.57"}' | python3 -m json.tool
echo ""

echo "=========================================="
echo "Testing Complete!"
echo "=========================================="
echo ""
echo "Now checking dashboard stats..."
sleep 3

curl -s http://localhost:8000/api/dashboard/stats \
  -H "Authorization: Bearer $(curl -s -X POST http://localhost:8000/api/auth/login -H "Content-Type: application/json" -d '{"username":"admin","password":"chameleon2024"}' | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")" \
  | python3 -c "import sys, json; data=json.load(sys.stdin); print(f'\nTotal Attempts: {data[\"total_attempts\"]}'); print(f'Malicious: {data[\"malicious_attempts\"]}'); print(f'Benign: {data[\"benign_attempts\"]}'); print(f'\nAttack Distribution:'); [print(f'  {k}: {v}') for k,v in data['attack_distribution'].items()]; print(f'\nGeographic Locations: {len(data[\"geo_locations\"])} unique locations'); [print(f'  📍 {loc[\"city\"]}, {loc[\"country\"]}: {loc[\"count\"]} attacks') for loc in data['geo_locations'][:10]]"

echo ""
echo "✅ All tests complete! Check the dashboard at http://localhost:5174/dashboard"
