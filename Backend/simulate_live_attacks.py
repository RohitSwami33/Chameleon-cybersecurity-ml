import urllib.request
import urllib.error
import json
import time

API_URL = "http://localhost:8000/api/trap/submit"
STATS_URL = "http://localhost:8000/api/meta-heuristics/stats"

payloads = [
    {"type": "SQLI", "text": "admin' OR '1'='1", "expected": True},
    {"type": "SQLI", "text": "SELECT * FROM users WHERE id=1 UNION SELECT null, version()", "expected": True},
    {"type": "BENIGN", "text": "john.doe password123", "expected": False},
    {"type": "XSS", "text": "<script>alert(document.cookie)</script>", "expected": True},
    {"type": "PATH_TRAVERSAL", "text": "../../../etc/passwd", "expected": True},
    {"type": "BENIGN", "text": "hello system status", "expected": False},
    {"type": "RCE", "text": "; rm -rf /; echo hack", "expected": True},
    {"type": "SSI", "text": "<!--#exec cmd='ls -l'-->", "expected": True},
    {"type": "BENIGN", "text": "my_email@nexacorp.io P@ssw0rd2025", "expected": False},
    {"type": "SQLI", "text": "DROP TABLE users;--", "expected": True},
]

print("=== CHAMELEON LIVE ATTACK SIMULATION ===")
print("Sending payloads to deception layer API...\n")

correct = 0
total = len(payloads)

for idx, p in enumerate(payloads):
    req_data = {
        "input_text": p["text"],
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0 (Kali Linux) AttackSim/1.0"
    }
    
    jsondata = json.dumps(req_data).encode("utf-8")
    req = urllib.request.Request(API_URL, data=jsondata, headers={'Content-Type': 'application/json'})
    
    start_time = time.time()
    try:
        with urllib.request.urlopen(req) as response:
            resp_body = response.read()
            latency = (time.time() - start_time) * 1000
            data = json.loads(resp_body)
            
            is_malicious = data.get("is_malicious", False)
            status = data.get("status", "unknown")
            
            if is_malicious == p["expected"]:
                correct += 1
                result = "✅ PASS"
            else:
                result = "❌ FAIL"
                
            print(f"[{idx+1}/{total}] {p['type']} Payload: {p['text'][:30]}...")
            print(f"   -> Result: {result} (Expected Malicious: {p['expected']}, Got: {is_malicious})")
            print(f"   -> Latency: {latency:.2f}ms | Assigned Status: {status}")
            print("-" * 50)
    except Exception as e:
        print(f"[{idx+1}/{total}] {p['type']} Payload FAILED TO SEND: {e}")

accuracy = (correct / total) * 100
print(f"\n=== OVERALL PREDICTION ACCURACY: {accuracy:.2f}% ===")

print("\nFetching updated TC-PSO / S-RRT metrics:")
try:
    req_stats = urllib.request.Request(STATS_URL)
    with urllib.request.urlopen(req_stats) as response:
        stats_body = response.read()
        stats_data = json.loads(stats_body)
        
        tc_pso = stats_data.get("tc_pso", stats_data.get("pso", {}))
        srrt_stats = stats_data.get("srrt", {})
        
        print("\nTC-PSO Dynamic Target Delays vs Original Static (3.0s):")
        for category, sd in tc_pso.items():
            delay = sd.get("global_best_delay", 3.0)
            iter_count = sd.get("iterations", 0)
            improvement = ((delay - 3.0) / 3.0 * 100) if delay != 3.0 else 0
            print(f"  - {category}: {delay:.2f}s (Iterations: {iter_count}) -> Adjusted by {improvement:+.1f}% from baseline")
            
        print("\nS-RRT Memory Metrics vs Unbounded RRT:")
        print(f"  - Generations: {srrt_stats.get('generation')}")
        print(f"  - Mean Nodes generated: {srrt_stats.get('mean_nodes')} vs ~300+ in baseline")
        print(f"  - Max Depth strictly capped to: {srrt_stats.get('max_depth')} (Limit: 6)")
except Exception as e:
    print(f"Failed to fetch stats: {e}")
