#!/usr/bin/env python3
"""
Final test to confirm Today API endpoints are working correctly
"""

import requests
import json
import uuid

BACKEND_URL = "https://15d7219c-892b-4111-8d96-e95547e179d6.preview.emergentagent.com/api"

def get_auth_token():
    """Register and login to get auth token"""
    test_user_data = {
        "username": f"final_test_{uuid.uuid4().hex[:8]}",
        "email": f"final.test_{uuid.uuid4().hex[:8]}@aurumlife.com",
        "first_name": "Final",
        "last_name": "Test",
        "password": "FinalTest2025!"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/register", json=test_user_data)
    if not response.ok:
        print(f"❌ Registration failed: {response.text}")
        return None
    
    login_data = {
        "email": test_user_data['email'],
        "password": test_user_data['password']
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
    if not response.ok:
        print(f"❌ Login failed: {response.text}")
        return None
    
    return response.json()['access_token']

def test_endpoints():
    """Test both Today endpoints"""
    print("🧪 FINAL TODAY API ENDPOINTS TEST")
    print("=" * 50)
    
    token = get_auth_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: GET /api/today
    print("\n1. Testing GET /api/today")
    response = requests.get(f"{BACKEND_URL}/today", headers=headers)
    
    if response.ok:
        data = response.json()
        required_fields = ['date', 'tasks', 'total_tasks', 'completed_tasks', 'estimated_duration']
        missing_fields = [field for field in required_fields if field not in data]
        
        if not missing_fields:
            print("✅ GET /api/today - SUCCESS")
            print(f"   - Status: {response.status_code}")
            print(f"   - All required fields present: {required_fields}")
            print(f"   - Total tasks: {data['total_tasks']}")
            print(f"   - Completed tasks: {data['completed_tasks']}")
            today_success = True
        else:
            print("❌ GET /api/today - MISSING FIELDS")
            print(f"   - Missing: {missing_fields}")
            today_success = False
    else:
        print(f"❌ GET /api/today - FAILED")
        print(f"   - Status: {response.status_code}")
        print(f"   - Error: {response.text}")
        today_success = False
    
    # Test 2: GET /api/today/available-tasks
    print("\n2. Testing GET /api/today/available-tasks")
    response = requests.get(f"{BACKEND_URL}/today/available-tasks", headers=headers)
    
    if response.ok:
        data = response.json()
        if isinstance(data, list):
            print("✅ GET /api/today/available-tasks - SUCCESS")
            print(f"   - Status: {response.status_code}")
            print(f"   - Response type: list")
            print(f"   - Available tasks count: {len(data)}")
            available_success = True
        else:
            print("❌ GET /api/today/available-tasks - WRONG TYPE")
            print(f"   - Expected list, got: {type(data)}")
            available_success = False
    else:
        print(f"❌ GET /api/today/available-tasks - FAILED")
        print(f"   - Status: {response.status_code}")
        print(f"   - Error: {response.text}")
        available_success = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 FINAL TEST RESULTS")
    print("=" * 50)
    
    if today_success and available_success:
        print("✅ ALL TESTS PASSED")
        print("   - Today API endpoints are working correctly")
        print("   - Frontend 'Failed to load today's data' error should be resolved")
        return True
    else:
        print("❌ SOME TESTS FAILED")
        print(f"   - GET /api/today: {'✅' if today_success else '❌'}")
        print(f"   - GET /api/today/available-tasks: {'✅' if available_success else '❌'}")
        return False

if __name__ == "__main__":
    success = test_endpoints()
    exit(0 if success else 1)