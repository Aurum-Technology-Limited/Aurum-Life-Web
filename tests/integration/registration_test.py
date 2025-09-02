#!/usr/bin/env python3
"""
Registration and Alternative Authentication Test
Test user registration and try alternative authentication methods
"""

import requests
import json
import time
import os
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://aurum-life-os.preview.emergentagent.com/api"

def log_test(message):
    """Log test messages with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] {message}")

def test_user_registration():
    """Test user registration to create a working test account"""
    log_test("🔍 Testing user registration...")
    
    # Generate unique test user
    unique_id = str(uuid.uuid4())[:8]
    test_email = f"authtest_{unique_id}@aurumtechnologyltd.com"
    
    registration_payload = {
        "email": test_email,
        "password": "TestPassword123!",
        "first_name": "Auth",
        "last_name": "Test",
        "username": f"authtest_{unique_id}"
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BACKEND_URL}/auth/register",
            json=registration_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        end_time = time.time()
        
        log_test(f"Registration response: {response.status_code} ({(end_time - start_time) * 1000:.1f}ms)")
        log_test(f"Registration response body: {response.text}")
        
        if response.status_code == 200:
            log_test(f"✅ Registration successful for: {test_email}")
            return test_email, "TestPassword123!"
        else:
            log_test(f"❌ Registration failed: {response.text}")
            return None, None
            
    except Exception as e:
        log_test(f"❌ Registration request failed: {e}")
        return None, None

def test_login_with_credentials(email, password):
    """Test login with specific credentials"""
    log_test(f"🔍 Testing login with: {email}")
    
    login_payload = {
        "email": email,
        "password": password
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json=login_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        end_time = time.time()
        
        log_test(f"Login response: {response.status_code} ({(end_time - start_time) * 1000:.1f}ms)")
        
        if response.status_code == 200:
            data = response.json()
            log_test(f"✅ Login successful! Token length: {len(data.get('access_token', ''))}")
            return data.get('access_token')
        else:
            log_test(f"❌ Login failed: {response.text}")
            return None
            
    except Exception as e:
        log_test(f"❌ Login request failed: {e}")
        return None

def test_alternative_accounts():
    """Test with alternative known accounts from test history"""
    log_test("🔍 Testing alternative known accounts...")
    
    # Alternative accounts mentioned in test history
    alternative_accounts = [
        ("smoketest_e0742f61@aurumtechnologyltd.com", "TestPassword123!"),
        ("marc.alleyne@gmail.com", "Test$1920"),
    ]
    
    for email, password in alternative_accounts:
        log_test(f"Trying alternative account: {email}")
        token = test_login_with_credentials(email, password)
        if token:
            return email, password, token
    
    return None, None, None

def main():
    """Main test execution"""
    log_test("🎯 REGISTRATION AND ALTERNATIVE AUTHENTICATION TEST STARTED")
    log_test(f"Backend URL: {BACKEND_URL}")
    
    # Test 1: Try user registration
    new_email, new_password = test_user_registration()
    
    if new_email:
        # Test login with newly created account
        log_test("🔍 Testing login with newly created account...")
        token = test_login_with_credentials(new_email, new_password)
        
        if token:
            log_test("✅ NEW ACCOUNT AUTHENTICATION WORKING!")
            log_test("This indicates the authentication system is functional.")
            log_test("The issue is specifically with the marc.alleyne@aurumtechnologyltd.com account.")
            return
    
    # Test 2: Try alternative accounts
    alt_email, alt_password, alt_token = test_alternative_accounts()
    
    if alt_token:
        log_test(f"✅ ALTERNATIVE ACCOUNT WORKING: {alt_email}")
        log_test("This indicates the authentication system is functional.")
        log_test("The issue is specifically with the marc.alleyne@aurumtechnologyltd.com account.")
        return
    
    # If we reach here, there's a broader authentication issue
    log_test("\n🚨 CRITICAL FINDING:")
    log_test("- Cannot create new accounts (registration blocked)")
    log_test("- Cannot login with known alternative accounts")
    log_test("- This suggests a system-wide authentication issue")
    log_test("- The 401 error is not account-specific but system-wide")

if __name__ == "__main__":
    main()