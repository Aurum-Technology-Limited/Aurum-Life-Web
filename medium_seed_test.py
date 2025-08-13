#!/usr/bin/env python3
"""
Test for admin seed-demo endpoint with medium size and include_streak=true
"""

import requests
import json
import time

# Configuration
BACKEND_URL = "https://hierarchy-enforcer.preview.emergentagent.com/api"
TEST_USER_EMAIL = "marc.alleyne@aurumtechnologyltd.com"
TEST_USER_PASSWORD = "password123"

def test_medium_seed():
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
    
    # Test with medium size and include_streak=true
    print("🌱 Testing seed-demo with size=medium and include_streak=true...")
    params = {"size": "medium", "include_streak": "true"}
    
    start_time = time.time()
    try:
        response = session.post(f"{BACKEND_URL}/admin/seed-demo", params=params, headers=headers, timeout=120)  # 2 minute timeout
        response_time = time.time() - start_time
        
        print(f"⏱️ Response time: {response_time:.2f}s")
        print(f"📊 Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Seed demo successful!")
            
            # Verify required response structure
            required_keys = ['message', 'size', 'include_streak', 'created']
            missing_keys = [key for key in required_keys if key not in data]
            
            if missing_keys:
                print(f"❌ Missing required keys: {missing_keys}")
                return False
            
            # Verify specific values
            if (data.get('message') == 'Demo data seeded' and 
                data.get('size') == 'medium' and 
                data.get('include_streak') == True):
                print("✅ Response structure and values correct")
            else:
                print(f"❌ Response values incorrect: {data}")
                return False
            
            # Verify created counts
            created = data.get('created', {})
            if (created.get('pillars', 0) > 0 and 
                created.get('areas', 0) > 0 and 
                created.get('projects', 0) > 0 and 
                created.get('tasks', 0) > 0):
                print(f"✅ Created counts valid: {created}")
            else:
                print(f"❌ Created counts invalid: {created}")
                return False
            
            print(f"📋 Full response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ Seed demo failed: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        response_time = time.time() - start_time
        print(f"⏱️ Request timed out after {response_time:.2f}s")
        print("❌ Seed demo timed out - this indicates the endpoint may be working but is slow")
        return False
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def test_ultra_endpoints():
    """Test the ultra endpoints to verify data exists"""
    session = requests.Session()
    
    # Login
    login_data = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    
    response = session.post(f"{BACKEND_URL}/auth/login", json=login_data, timeout=30)
    if response.status_code != 200:
        print(f"❌ Login failed for ultra endpoints test")
        return False
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🚀 Testing ultra endpoints...")
    
    ultra_endpoints = [
        ('/ultra/pillars', 'pillars'),
        ('/ultra/areas', 'areas'),
        ('/ultra/projects', 'projects')
    ]
    
    all_valid = True
    
    for endpoint, entity_name in ultra_endpoints:
        try:
            start_time = time.time()
            response = session.get(f"{BACKEND_URL}{endpoint}", headers=headers, timeout=30)
            response_time = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    print(f"✅ GET {endpoint}: Retrieved {len(data)} {entity_name} ({response_time}ms)")
                else:
                    print(f"❌ GET {endpoint}: Empty or invalid response")
                    all_valid = False
            else:
                print(f"❌ GET {endpoint}: Failed with status {response.status_code}")
                all_valid = False
        except Exception as e:
            print(f"❌ GET {endpoint}: Exception - {e}")
            all_valid = False
    
    return all_valid

if __name__ == "__main__":
    print("🧪 TESTING ADMIN SEED-DEMO WITH MEDIUM SIZE AND INCLUDE_STREAK=TRUE")
    print("=" * 80)
    
    # Test the seed endpoint
    seed_success = test_medium_seed()
    
    # Test ultra endpoints regardless of seed result
    ultra_success = test_ultra_endpoints()
    
    overall_success = seed_success and ultra_success
    
    print("\n" + "=" * 80)
    print("📊 FINAL RESULTS")
    print("=" * 80)
    print(f"Seed Demo Test: {'✅ PASS' if seed_success else '❌ FAIL'}")
    print(f"Ultra Endpoints Test: {'✅ PASS' if ultra_success else '❌ FAIL'}")
    print(f"Overall: {'✅ SUCCESS' if overall_success else '❌ FAILED'}")
    print("=" * 80)