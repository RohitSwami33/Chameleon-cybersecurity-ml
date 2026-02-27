"""
Quick test script for Progressive Deception Engine
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_sql_injection_progression():
    """Test SQL injection 4-stage progression"""
    print("=" * 60)
    print("Testing SQL Injection Progression")
    print("=" * 60)
    
    ip = "192.168.1.100"
    user_agent = "TestBot/1.0"
    
    attacks = [
        ("Stage 1", "' OR 1=1--"),
        ("Stage 2", "' UNION SELECT * FROM users--"),
        ("Stage 3", "' UNION SELECT password FROM users--"),
        ("Stage 4", "' UNION SELECT passwd FROM users--"),
    ]
    
    for stage, payload in attacks:
        print(f"\n{stage}: {payload}")
        
        response = requests.post(
            f"{BASE_URL}/api/trap/submit",
            json={
                "input_text": payload,
                "ip_address": ip,
                "user_agent": user_agent
            }
        )
        
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {data['message'][:150]}...")
        print("-" * 60)

def test_xss_progression():
    """Test XSS 3-stage progression"""
    print("\n" + "=" * 60)
    print("Testing XSS Progression")
    print("=" * 60)
    
    ip = "10.0.0.50"
    user_agent = "XSSBot/1.0"
    
    attacks = [
        ("Stage 1", "<script>alert(1)</script>"),
        ("Stage 2", "<img src=x onerror=alert(1)>"),
        ("Stage 3", "&#60;script&#62;alert(1)&#60;/script&#62;"),
    ]
    
    for stage, payload in attacks:
        print(f"\n{stage}: {payload}")
        
        response = requests.post(
            f"{BASE_URL}/api/trap/submit",
            json={
                "input_text": payload,
                "ip_address": ip,
                "user_agent": user_agent
            }
        )
        
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {data['message'][:150]}...")
        print("-" * 60)

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Health check: {response.json()}")
    return response.status_code == 200

if __name__ == "__main__":
    print("Progressive Deception Engine - Test Suite")
    print("=" * 60)
    
    # Test health first
    if not test_health():
        print("❌ Server is not running!")
        exit(1)
    
    print("✅ Server is running\n")
    
    # Test SQL injection progression
    test_sql_injection_progression()
    
    # Test XSS progression
    test_xss_progression()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
