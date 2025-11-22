#!/bin/bash

echo "=========================================="
echo "Testing Threat Score System"
echo "=========================================="
echo ""

echo "Submitting multiple attacks from same IP to lower threat score..."
echo ""

# Submit 5 SQLi attacks from same IP
for i in {1..5}; do
    echo "Attack $i from 45.33.32.156..."
    curl -s -X POST http://localhost:8000/api/trap/submit \
      -H "Content-Type: application/json" \
      -d '{"input_text":"SELECT * FROM users WHERE id=1 UNION SELECT password","ip_address":"45.33.32.156"}' > /dev/null
done

# Submit 3 XSS attacks from another IP
for i in {1..3}; do
    echo "Attack $i from 185.220.101.1..."
    curl -s -X POST http://localhost:8000/api/trap/submit \
      -H "Content-Type: application/json" \
      -d '{"input_text":"<script>alert(1)</script>","ip_address":"185.220.101.1"}' > /dev/null
done

# Submit 2 SSI attacks from another IP
for i in {1..2}; do
    echo "Attack $i from 104.16.132.229..."
    curl -s -X POST http://localhost:8000/api/trap/submit \
      -H "Content-Type: application/json" \
      -d '{"input_text":"<!--#exec cmd=\"ls\" -->","ip_address":"104.16.132.229"}' > /dev/null
done

echo ""
echo "Waiting for processing..."
sleep 3

echo ""
echo "=========================================="
echo "Checking Threat Scores"
echo "=========================================="
echo ""

# Get auth token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"chameleon2024"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "1. Top Threats:"
echo "-------------------------------------------"
curl -s http://localhost:8000/api/threat-scores/top-threats \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool

echo ""
echo "2. Flagged IPs:"
echo "-------------------------------------------"
curl -s http://localhost:8000/api/threat-scores/flagged \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool

echo ""
echo "3. Specific IP Score (45.33.32.156):"
echo "-------------------------------------------"
curl -s http://localhost:8000/api/threat-scores/45.33.32.156 \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -c "import sys, json; data=json.load(sys.stdin); rep=data['reputation']; print(f'IP: {rep[\"ip_address\"]}'); print(f'Score: {rep[\"score\"]}/100'); print(f'Level: {rep[\"level\"]}'); print(f'Total Attacks: {rep[\"total_attacks\"]}'); print(f'Flagged: {rep[\"is_flagged\"]}')"

echo ""
echo "4. Verify Score Chain Integrity:"
echo "-------------------------------------------"
curl -s http://localhost:8000/api/threat-scores/verify-chain \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool

echo ""
echo "=========================================="
echo "Dashboard Stats with Threat Scores:"
echo "=========================================="
curl -s http://localhost:8000/api/dashboard/stats \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -c "import sys, json; data=json.load(sys.stdin); print(f'Flagged IPs: {data.get(\"flagged_ips_count\", 0)}'); print(f'Top Threats: {len(data.get(\"top_threats\", []))}'); [print(f'  - {t[\"ip_address\"]}: Score {t[\"score\"]} ({t[\"level\"]})') for t in data.get('top_threats', [])[:5]]"

echo ""
echo "✅ Testing complete! Check dashboard at http://localhost:5174/dashboard"
