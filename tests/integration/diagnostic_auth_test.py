#!/usr/bin/env python3
"""
Diagnostic Authentication Test
Tests Supabase authentication and provides detailed error information
"""

import requests
import json
import time

# Configuration
BACKEND_URL = "https://auth-flow-master.preview.emergentagent.com/api"
TEST_EMAIL = "marc.alleyne@aurumtechnologyltd.com"
TEST_PASSWORD = "password123"

def test_health():
    """Test health endpoint"""
    print("🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        print(f"Health Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Health Response: {response.json()}")
            return True
        else:
            print(f"Health Error: {response.text}")
            return False
    except Exception as e:
        print(f"Health Exception: {e}")
        return False

def test_register():
    """Try to register the test account"""
    print("📝 Testing registration...")
    payload = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "first_name": "Marc",
        "last_name": "Alleyne",
        "username": "marc_test"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/register", json=payload, timeout=30)
        print(f"Register Status: {response.status_code}")
        print(f"Register Response: {response.text[:500]}")
        
        if response.status_code == 200:
            print("✅ Registration successful")
            return True
        elif response.status_code == 409:
            print("ℹ️ Account already exists (expected)")
            return True
        else:
            print("❌ Registration failed")
            return False
    except Exception as e:
        print(f"Register Exception: {e}")
        return False

def test_login():
    """Test login with detailed error reporting"""
    print("🔐 Testing login...")
    payload = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/login", json=payload, timeout=30)
        print(f"Login Status: {response.status_code}")
        print(f"Login Response: {response.text[:500]}")
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                print("✅ Login successful")
                print(f"Token length: {len(data['access_token'])}")
                return data["access_token"]
            else:
                print("❌ No access token in response")
                return None
        else:
            print("❌ Login failed")
            return None
    except Exception as e:
        print(f"Login Exception: {e}")
        return None

def test_auth_me(token):
    """Test /auth/me endpoint"""
    if not token:
        print("❌ No token available for /auth/me test")
        return False
        
    print("👤 Testing /auth/me...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BACKEND_URL}/auth/me", headers=headers, timeout=30)
        print(f"Auth/me Status: {response.status_code}")
        print(f"Auth/me Response: {response.text[:500]}")
        
        if response.status_code == 200:
            print("✅ Auth/me successful")
            return True
        else:
            print("❌ Auth/me failed")
            return False
    except Exception as e:
        print(f"Auth/me Exception: {e}")
        return False

def main():
    print("🚀 Starting Diagnostic Authentication Test")
    print("=" * 60)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Email: {TEST_EMAIL}")
    print("=" * 60)
    print()
    
    # Test sequence
    health_ok = test_health()
    print()
    
    if not health_ok:
        print("❌ Health check failed, stopping tests")
        return
    
    register_ok = test_register()
    print()
    
    token = test_login()
    print()
    
    if token:
        auth_me_ok = test_auth_me(token)
        print()
        
        if auth_me_ok:
            print("🎉 All authentication tests passed!")
        else:
            print("⚠️ Login works but /auth/me failed")
    else:
        print("❌ Login failed, cannot test further")
    
    print("=" * 60)

if __name__ == "__main__":
    main()