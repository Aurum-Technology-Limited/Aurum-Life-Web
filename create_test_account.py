#!/usr/bin/env python3
"""
Create Test Account for Smoke Testing
Creates a new test account if the existing one is not working
"""

import requests
import json
import uuid
import time

# Configuration
BACKEND_URL = "https://auth-wizard-2.preview.emergentagent.com/api"

def create_new_test_account():
    """Create a new test account with unique email"""
    unique_id = str(uuid.uuid4())[:8]
    test_email = f"smoketest_{unique_id}@aurumtechnologyltd.com"
    test_password = "password123"
    
    print(f"🔧 Creating new test account: {test_email}")
    
    payload = {
        "email": test_email,
        "password": test_password,
        "first_name": "Smoke",
        "last_name": "Test",
        "username": f"smoketest_{unique_id}"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/register", json=payload, timeout=30)
        print(f"Register Status: {response.status_code}")
        print(f"Register Response: {response.text[:500]}")
        
        if response.status_code == 200:
            print("✅ New test account created successfully")
            return test_email, test_password
        else:
            print("❌ Failed to create new test account")
            return None, None
    except Exception as e:
        print(f"Register Exception: {e}")
        return None, None

def test_login_with_account(email, password):
    """Test login with given credentials"""
    print(f"🔐 Testing login with {email}")
    
    payload = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/login", json=payload, timeout=30)
        print(f"Login Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                print("✅ Login successful")
                return data["access_token"]
            else:
                print("❌ No access token in response")
                return None
        else:
            print(f"❌ Login failed: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"Login Exception: {e}")
        return None

def main():
    print("🚀 Creating Test Account for Smoke Testing")
    print("=" * 60)
    
    # Try original account first
    print("1. Testing original account...")
    original_token = test_login_with_account("marc.alleyne@aurumtechnologyltd.com", "password123")
    
    if original_token:
        print("✅ Original account works fine!")
        print(f"Credentials: marc.alleyne@aurumtechnologyltd.com / password123")
        return
    
    print("\n2. Original account failed, creating new test account...")
    new_email, new_password = create_new_test_account()
    
    if new_email:
        print("\n3. Testing new account...")
        new_token = test_login_with_account(new_email, new_password)
        
        if new_token:
            print("✅ New test account works!")
            print(f"New credentials: {new_email} / {new_password}")
            print("\nUpdate your smoke test to use these credentials:")
            print(f'TEST_EMAIL = "{new_email}"')
            print(f'TEST_PASSWORD = "{new_password}"')
        else:
            print("❌ New test account also failed")
    else:
        print("❌ Could not create new test account")
    
    print("=" * 60)

if __name__ == "__main__":
    main()