#!/usr/bin/env python3
"""
SIMPLE PILLAR CREATION TEST - DEBUGGING USER ID MISMATCH
Testing to understand the user ID mismatch issue after database fixes.

The issue appears to be:
- User can login successfully 
- But the user ID from authentication (6848f065-2d12-4c4e-88c4-80f375358d7b) 
- Doesn't match the user ID created in public.users table (272edb74-8be3-4504-818c-b1dd42c63ebe)

CREDENTIALS: marc.alleyne@aurumtechnologyltd.com / password
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://b7ef6377-f814-4d39-824c-6237cb92693c.preview.emergentagent.com/api"

def test_authentication_and_user_info():
    """Test authentication and get user information"""
    print("🔍 DEBUGGING USER ID MISMATCH ISSUE")
    print("=" * 60)
    
    session = requests.Session()
    
    # Step 1: Login
    print("\n1. Testing Login...")
    login_data = {
        "email": "marc.alleyne@aurumtechnologyltd.com",
        "password": "password"
    }
    
    try:
        response = session.post(f"{BACKEND_URL}/auth/login", json=login_data, timeout=30)
        print(f"   Login Status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            print(f"   ✅ Login successful")
            print(f"   Token received: {access_token[:50]}..." if access_token else "   ❌ No token received")
            
            # Step 2: Get user info
            print("\n2. Testing User Info Retrieval...")
            headers = {"Authorization": f"Bearer {access_token}"}
            
            response = session.get(f"{BACKEND_URL}/auth/me", headers=headers, timeout=30)
            print(f"   User Info Status: {response.status_code}")
            
            if response.status_code == 200:
                user_data = response.json()
                print(f"   ✅ User info retrieved successfully")
                print(f"   User ID: {user_data.get('id')}")
                print(f"   Email: {user_data.get('email')}")
                print(f"   Username: {user_data.get('username')}")
                
                # Step 3: Try to create a pillar
                print("\n3. Testing Pillar Creation...")
                pillar_data = {
                    "name": "Test Pillar",
                    "description": "Testing pillar creation after database fixes",
                    "icon": "🧪",
                    "color": "#10B981",
                    "time_allocation_percentage": 25.0
                }
                
                response = session.post(f"{BACKEND_URL}/pillars", json=pillar_data, headers=headers, timeout=30)
                print(f"   Pillar Creation Status: {response.status_code}")
                
                if response.status_code == 200:
                    pillar = response.json()
                    print(f"   ✅ Pillar created successfully!")
                    print(f"   Pillar ID: {pillar.get('id')}")
                    print(f"   Pillar Name: {pillar.get('name')}")
                    return True
                else:
                    error_data = response.json() if response.content else {"error": "No content"}
                    print(f"   ❌ Pillar creation failed")
                    print(f"   Error: {error_data}")
                    
                    # Check if it's a foreign key constraint error
                    error_str = str(error_data).lower()
                    if 'foreign key' in error_str or 'violates' in error_str:
                        print(f"   🚨 FOREIGN KEY CONSTRAINT ERROR DETECTED!")
                        print(f"   This suggests the user ID mismatch issue is still present")
                    
                    return False
            else:
                error_data = response.json() if response.content else {"error": "No content"}
                print(f"   ❌ User info retrieval failed")
                print(f"   Error: {error_data}")
                return False
        else:
            error_data = response.json() if response.content else {"error": "No content"}
            print(f"   ❌ Login failed")
            print(f"   Error: {error_data}")
            return False
            
    except Exception as e:
        print(f"   ❌ Request failed: {str(e)}")
        return False

def main():
    """Run the simple pillar creation test"""
    print("🧪 SIMPLE PILLAR CREATION TEST - DEBUGGING USER ID MISMATCH")
    print("=" * 70)
    print("Expected User ID in public.users: 272edb74-8be3-4504-818c-b1dd42c63ebe")
    print("Actual User ID from auth: Will be shown below")
    print("=" * 70)
    
    success = test_authentication_and_user_info()
    
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS")
    print("=" * 70)
    
    if success:
        print("✅ SUCCESS: Pillar creation working - database fixes successful!")
        print("   The foreign key constraint issue has been resolved.")
        print("   User ID mismatch has been fixed.")
    else:
        print("❌ FAILURE: Pillar creation still failing")
        print("   Possible causes:")
        print("   1. User ID mismatch between auth system and public.users table")
        print("   2. Foreign key constraints still referencing wrong table")
        print("   3. User record missing in public.users table")
        print("   4. Other database configuration issues")
    
    print("=" * 70)
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)