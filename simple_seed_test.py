#!/usr/bin/env python3
"""
Simple test for admin seed-demo endpoint with light size to avoid timeout
"""

import requests
import json
import time

# Configuration
BACKEND_URL = "https://taskpilot-2.preview.emergentagent.com/api"
TEST_USER_EMAIL = "marc.alleyne@aurumtechnologyltd.com"
TEST_USER_PASSWORD = "password123"

def test_simple_seed():
    session = requests.Session()
    
    # Login
    login_data = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    
    print("🔐 Logging in...")
    response = session.post(f"{BACKEND_URL}/auth/login", json=login_data, timeout=30)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return False
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Login successful")
    
    # Test with light size first
    print("🌱 Testing seed-demo with size=light...")
    params = {"size": "light", "include_streak": "false"}
    
    start_time = time.time()
    response = session.post(f"{BACKEND_URL}/admin/seed-demo", params=params, headers=headers, timeout=60)
    response_time = time.time() - start_time
    
    print(f"⏱️ Response time: {response_time:.2f}s")
    print(f"📊 Status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Seed demo successful!")
        print(f"📋 Response: {json.dumps(data, indent=2)}")
        return True
    else:
        print(f"❌ Seed demo failed: {response.text}")
        return False

if __name__ == "__main__":
    success = test_simple_seed()
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}")