#!/usr/bin/env python3
"""
Authentication Diagnosis Test
Diagnose authentication issues with the refactored endpoints
"""

import requests
import json
import time
from datetime import datetime

BACKEND_URL = "https://aurum-life-os.preview.emergentagent.com/api"

def test_auth_diagnosis():
    print("🔍 AUTHENTICATION DIAGNOSIS TEST")
    print("=" * 50)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Started at: {datetime.utcnow().isoformat()}")
    print()
    
    # Test 1: Health check
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Test 2: Debug config
    print("2. Testing debug config...")
    try:
        response = requests.get(f"{BACKEND_URL}/auth/debug-supabase-config", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Test 3: Try creating a new test user
    print("3. Testing user registration...")
    test_user = {
        "username": f"diagtest_{int(time.time())}",
        "email": f"diagtest_{int(time.time())}@example.com",
        "first_name": "Diag",
        "last_name": "Test",
        "password": "DiagTest123!"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/register", 
                               json=test_user, 
                               headers={"Content-Type": "application/json"},
                               timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 201:
            # Try to login with the new user
            print("\n4. Testing login with new user...")
            login_data = {
                "email": test_user["email"],
                "password": test_user["password"]
            }
            
            login_response = requests.post(f"{BACKEND_URL}/auth/login",
                                         json=login_data,
                                         headers={"Content-Type": "application/json"},
                                         timeout=10)
            print(f"   Status: {login_response.status_code}")
            print(f"   Response: {login_response.json()}")
            
            if login_response.status_code == 200:
                token_data = login_response.json()
                access_token = token_data.get("access_token")
                
                # Test /auth/me endpoint
                print("\n5. Testing /auth/me endpoint...")
                me_response = requests.get(f"{BACKEND_URL}/auth/me",
                                         headers={"Authorization": f"Bearer {access_token}"},
                                         timeout=10)
                print(f"   Status: {me_response.status_code}")
                print(f"   Response: {me_response.json()}")
                
                return True
                
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Try with known credentials from test_result.md
    print("\n6. Testing with known credentials from test_result.md...")
    known_credentials = [
        {"email": "marc.alleyne@aurumtechnologyltd.com", "password": "password123"},
        {"email": "smoketest_e0742f61@aurumtechnologyltd.com", "password": "password123"}
    ]
    
    for creds in known_credentials:
        print(f"   Trying: {creds['email']}")
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login",
                                   json=creds,
                                   headers={"Content-Type": "application/json"},
                                   timeout=10)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   SUCCESS! Token received")
                return True
            else:
                print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")
    
    print("\n❌ DIAGNOSIS COMPLETE: Authentication system appears to have issues")
    return False

if __name__ == "__main__":
    test_auth_diagnosis()