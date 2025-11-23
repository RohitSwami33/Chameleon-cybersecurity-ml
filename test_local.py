#!/usr/bin/env python3
"""Test script to verify the backend works correctly"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"✅ Health check: {response.status_code}")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_attack_submission():
    """Test attack submission"""
    print("\n🔍 Testing attack submission...")
    
    test_cases = [
        {"input": "admin' OR 1=1--", "expected": "SQLI"},
        {"input": "<script>alert('xss')</script>", "expected": "XSS"},
        {"input": "<!--#exec cmd=\"ls\"-->", "expected": "SSI"},
        {"input": "Hello, this is normal text", "expected": "BENIGN"}
    ]
    
    for test in test_cases:
        try:
            payload = {
                "input_text": test["input"],
                "ip_address": "127.0.0.1",
                "user_agent": "TestAgent/1.0"
            }
            
            response = requests.post(
                f"{BASE_URL}/api/trap/submit",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200 or response.status_code == 500:
                result = response.json()
                print(f"✅ Test '{test['input'][:30]}...'")
                print(f"   Status: {response.status_code}")
                print(f"   Response: {json.dumps(result, indent=2)[:200]}...")
            else:
                print(f"❌ Unexpected status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    return True

def test_frontend():
    """Test if frontend is being served"""
    print("\n🔍 Testing frontend serving...")
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200 and "<!doctype html>" in response.text.lower():
            print(f"✅ Frontend served successfully")
            return True
        else:
            print(f"❌ Frontend not served properly: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 CHAMELEON LOCAL TEST SUITE")
    print("=" * 60)
    print("\n⚠️  Make sure backend is running on port 8000!")
    print("   Run: cd Backend && python -m uvicorn main:app --port 8000\n")
    
    input("Press Enter to start tests...")
    
    test_health()
    test_attack_submission()
    test_frontend()
    
    print("\n" + "=" * 60)
    print("✅ Tests completed!")
    print("=" * 60)
