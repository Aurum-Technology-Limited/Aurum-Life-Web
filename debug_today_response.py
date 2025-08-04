#!/usr/bin/env python3
"""
Debug script to see the actual Today API response structure
"""

import requests
import json
import uuid

BACKEND_URL = "https://1b0a62f2-f882-476f-afb6-6747b2b238a1.preview.emergentagent.com/api"

def get_auth_token():
    """Register and login to get auth token"""
    # Register user
    test_user_data = {
        "username": f"debug_user_{uuid.uuid4().hex[:8]}",
        "email": f"debug.user_{uuid.uuid4().hex[:8]}@aurumlife.com",
        "first_name": "Debug",
        "last_name": "User",
        "password": "DebugTest2025!"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/register", json=test_user_data)
    if not response.ok:
        print(f"Registration failed: {response.text}")
        return None
    
    # Login
    login_data = {
        "email": test_user_data['email'],
        "password": test_user_data['password']
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
    if not response.ok:
        print(f"Login failed: {response.text}")
        return None
    
    return response.json()['access_token']

def test_today_endpoint():
    """Test the Today endpoint and show actual response"""
    token = get_auth_token()
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test GET /api/today
    response = requests.get(f"{BACKEND_URL}/today", headers=headers)
    
    print("=== GET /api/today Response ===")
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.ok:
        data = response.json()
        print(f"Response Structure:")
        print(json.dumps(data, indent=2, default=str))
        
        print(f"\nField Analysis:")
        for key, value in data.items():
            print(f"  {key}: {type(value)} - {len(value) if isinstance(value, (list, dict, str)) else value}")
    else:
        print(f"Error Response: {response.text}")

if __name__ == "__main__":
    test_today_endpoint()