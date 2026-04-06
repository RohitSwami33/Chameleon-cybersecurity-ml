import urllib.request
import json
import time
import subprocess
import statistics
import threading

API_URL = "http://localhost:8000/api/trap/submit"
NUM_REQUESTS = 100

PAYLOADS = [
    {"input_text": "admin' OR '1'='1", "ip_address": "10.0.0.1", "user_agent": "Sim-1"},
    {"input_text": "hello system status", "ip_address": "10.0.0.2", "user_agent": "Sim-2"},
    {"input_text": "<script>alert(1)</script>", "ip_address": "10.0.0.3", "user_agent": "Sim-3"},
    {"input_text": "../../../etc/passwd", "ip_address": "10.0.0.4", "user_agent": "Sim-4"},
    {"input_text": "SELECT * FROM users", "ip_address": "10.0.0.5", "user_agent": "Sim-5"},
]

metrics = {
    "latencies": [],
    "success": 0,
    "failed": 0,
    "peak_ram_mb": 0.0,
    "peak_cpu_percent": 0.0
}

is_running = True

def get_server_pids():
    try:
        res = subprocess.check_output(['pgrep', '-f', 'uvicorn src.api.main'], text=True)
        return [pid.strip() for pid in res.strip().split('\n') if pid.strip()]
    except subprocess.CalledProcessError:
        return []

def monitor_system():
    pids = get_server_pids()
    if not pids:
        print("Warning: Could not find uvicorn process for metrics!")
        
    while is_running:
        if pids:
            try:
                # ps -o rss,pcpu -p PID
                # Flatten the list
                flat_cmd = ['ps', '-o', 'rss,pcpu', '-p', ','.join(pids)]
                out = subprocess.check_output(flat_cmd, text=True).strip().split('\n')
                
                total_ram = 0.0
                total_cpu = 0.0
                
                for line in out[1:]: # skip header
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        rss_kb = float(parts[0])
                        cpu_p = float(parts[1])
                        total_ram += rss_kb / 1024.0 # convert to MB
                        total_cpu += cpu_p
                        
                if total_ram > metrics["peak_ram_mb"]:
                    metrics["peak_ram_mb"] = total_ram
                if total_cpu > metrics["peak_cpu_percent"]:
                    metrics["peak_cpu_percent"] = total_cpu
            except Exception:
                pass
        time.sleep(0.5)

def fire_request(payload):
    start_time = time.time()
    try:
        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(API_URL, data=req_data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=30) as response:
            if response.status == 200:
                metrics["success"] += 1
            else:
                metrics["failed"] += 1
    except Exception as e:
        metrics["failed"] += 1
    finally:
        latency = (time.time() - start_time) * 1000
        metrics["latencies"].append(latency)

def run_load_test():
    print(f"🔥 Starting Concurrency Benchmark: {NUM_REQUESTS} simultaneous requests...")
    
    # Start monitor thread
    monitor_thread = threading.Thread(target=monitor_system)
    monitor_thread.start()
    
    start_test = time.time()
    
    threads = []
    # Launch threads
    for i in range(NUM_REQUESTS):
        payload = PAYLOADS[i % len(PAYLOADS)]
        t = threading.Thread(target=fire_request, args=(payload,))
        t.start()
        threads.append(t)
        
    # Join threads
    for t in threads:
        t.join()
        
    total_time = time.time() - start_test
    global is_running
    is_running = False
    monitor_thread.join()
    
    print("\n" + "="*50)
    print("📊 CONCURRENCY BENCHMARK RESULTS")
    print("="*50)
    print(f"Total Requests  : {NUM_REQUESTS}")
    print(f"Successful (200): {metrics['success']}")
    print(f"Failed/Errors   : {metrics['failed']}")
    print("-" * 50)
    if metrics["latencies"]:
        avg_lat = statistics.mean(metrics["latencies"])
        max_lat = max(metrics["latencies"])
        min_lat = min(metrics["latencies"])
        print(f"Avg Latency     : {avg_lat:.2f} ms")
        print(f"Min Latency     : {min_lat:.2f} ms")
        print(f"Max Latency     : {max_lat:.2f} ms")
        print(f"Throughput      : {(NUM_REQUESTS / total_time):.2f} req/sec")
    print("-" * 50)
    print(f"Server Peak RAM : {metrics['peak_ram_mb']:.2f} MB")
    print(f"Server Peak CPU : {metrics['peak_cpu_percent']:.1f}%")
    print("="*50)

if __name__ == "__main__":
    run_load_test()
