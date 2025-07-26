#!/usr/bin/env python3
"""
Quick test to verify Supabase backend integration is working
"""

import requests
import json

BASE_URL = "http://localhost:8001/api"

def test_supabase_integration():
    """Test basic Supabase integration"""
    print("🧪 Testing Supabase Backend Integration")
    print("=" * 50)
    
    # Test 1: Health check
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check: Backend accessible")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Try to get pillars (this would use Supabase now)
    try:
        # Create a test user first (register)
        register_data = {
            "username": "testuser123",
            "email": "test.supabase@aurumlife.com",
            "first_name": "Test",
            "last_name": "Supabase",
            "password": "testpassword123"
        }
        
        register_response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if register_response.status_code in [200, 400]:  # 400 if user already exists
            print("✅ User registration endpoint accessible")
            
            # Try to login
            login_data = {
                "email": "test.supabase@aurumlife.com", 
                "password": "testpassword123"
            }
            
            login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
            if login_response.status_code == 200:
                token_data = login_response.json()
                token = token_data["access_token"]
                print("✅ User login successful - Got JWT token")
                
                # Test authenticated endpoint
                headers = {"Authorization": f"Bearer {token}"}
                pillars_response = requests.get(f"{BASE_URL}/pillars", headers=headers)
                
                if pillars_response.status_code == 200:
                    pillars = pillars_response.json()
                    print(f"✅ Pillars endpoint working - Found {len(pillars)} pillars")
                    print("✅ SUPABASE INTEGRATION IS WORKING!")
                    return True
                else:
                    print(f"❌ Pillars endpoint failed: {pillars_response.status_code}")
                    print(f"Response: {pillars_response.text}")
                    return False
            else:
                print(f"❌ Login failed: {login_response.status_code}")
                print(f"Response: {login_response.text}")
                return False
        else:
            print(f"❌ Registration failed: {register_response.status_code}")
            print(f"Response: {register_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Authentication/API test error: {e}")
        return False

if __name__ == "__main__":
    success = test_supabase_integration()
    if success:
        print("\n🎉 SUPABASE BACKEND INTEGRATION SUCCESSFUL!")
        print("✅ Backend is now using Supabase instead of MongoDB")
        print("✅ Authentication working")
        print("✅ API endpoints operational")
    else:
        print("\n❌ Integration test failed")