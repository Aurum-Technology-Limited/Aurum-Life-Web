#!/usr/bin/env python3
"""
Account Status Investigation Test
Check if the marc.alleyne@aurumtechnologyltd.com account exists and its status
"""

import requests
import json
import time
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://journal-analytics-1.preview.emergentagent.com/api"
PROBLEM_EMAIL = "marc.alleyne@aurumtechnologyltd.com"
WORKING_EMAIL = "authtest_ad92d043@aurumtechnologyltd.com"
WORKING_PASSWORD = "TestPassword123!"

def log_test(message):
    """Log test messages with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] {message}")

def get_working_token():
    """Get a working authentication token"""
    log_test("🔍 Getting working authentication token...")
    
    login_payload = {
        "email": WORKING_EMAIL,
        "password": WORKING_PASSWORD
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json=login_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            log_test(f"✅ Working token obtained (length: {len(token)})")
            return token
        else:
            log_test(f"❌ Failed to get working token: {response.text}")
            return None
            
    except Exception as e:
        log_test(f"❌ Token request failed: {e}")
        return None

def test_password_reset_for_problem_account():
    """Test password reset for the problem account"""
    log_test("🔍 Testing password reset for problem account...")
    
    reset_payload = {
        "email": PROBLEM_EMAIL
    }
    
    headers = {
        "Content-Type": "application/json",
        "Origin": "https://journal-analytics-1.preview.emergentagent.com"
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BACKEND_URL}/auth/forgot-password",
            json=reset_payload,
            headers=headers,
            timeout=30
        )
        end_time = time.time()
        
        log_test(f"Password reset: {response.status_code} ({(end_time - start_time) * 1000:.1f}ms)")
        log_test(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                log_test("✅ Password reset request accepted")
                if 'recovery_url' in data:
                    log_test(f"✅ Recovery URL provided: {data['recovery_url'][:100]}...")
                return True
            else:
                log_test("❌ Password reset not successful")
                return False
        else:
            log_test(f"❌ Password reset failed: {response.text}")
            return False
            
    except Exception as e:
        log_test(f"❌ Password reset request failed: {e}")
        return False

def test_registration_with_problem_email():
    """Test if we can register with the problem email (to check if account exists)"""
    log_test("🔍 Testing registration with problem email...")
    
    registration_payload = {
        "email": PROBLEM_EMAIL,
        "password": "NewTestPassword123!",
        "first_name": "Marc",
        "last_name": "Alleyne",
        "username": "marc_alleyne"
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
        
        log_test(f"Registration attempt: {response.status_code} ({(end_time - start_time) * 1000:.1f}ms)")
        log_test(f"Response: {response.text}")
        
        if response.status_code == 409:
            log_test("✅ Account exists (409 conflict - email already registered)")
            return "exists"
        elif response.status_code == 200:
            log_test("✅ Account created successfully (was not existing)")
            return "created"
        else:
            log_test(f"❌ Registration failed: {response.text}")
            return "failed"
            
    except Exception as e:
        log_test(f"❌ Registration request failed: {e}")
        return "error"

def test_different_password_variations():
    """Test different password variations for the problem account"""
    log_test("🔍 Testing different password variations...")
    
    password_variations = [
        "password123",  # Original
        "Password123",  # Capitalized
        "Password123!",  # With special char
        "Test$1920",    # Alternative from test history
    ]
    
    for password in password_variations:
        log_test(f"Trying password variation: {password}")
        
        login_payload = {
            "email": PROBLEM_EMAIL,
            "password": password
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=login_payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            log_test(f"Password '{password}': {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                log_test(f"✅ SUCCESS! Working password found: {password}")
                log_test(f"Token length: {len(token)}")
                return password, token
            
        except Exception as e:
            log_test(f"❌ Request failed for password '{password}': {e}")
    
    log_test("❌ No working password variations found")
    return None, None

def main():
    """Main test execution"""
    log_test("🎯 ACCOUNT STATUS INVESTIGATION TEST STARTED")
    log_test(f"Problem account: {PROBLEM_EMAIL}")
    log_test(f"Backend URL: {BACKEND_URL}")
    
    # Test 1: Check if account exists via registration attempt
    account_status = test_registration_with_problem_email()
    
    # Test 2: Try password reset
    reset_success = test_password_reset_for_problem_account()
    
    # Test 3: Try different password variations
    working_password, working_token = test_different_password_variations()
    
    # Summary and diagnosis
    log_test("\n" + "="*60)
    log_test("🎯 ACCOUNT STATUS INVESTIGATION SUMMARY")
    log_test("="*60)
    
    log_test(f"Account existence: {account_status}")
    log_test(f"Password reset: {'✅ Working' if reset_success else '❌ Failed'}")
    log_test(f"Password variations: {'✅ Found working' if working_password else '❌ None work'}")
    
    if working_password:
        log_test(f"\n🎉 SOLUTION FOUND!")
        log_test(f"Working password for {PROBLEM_EMAIL}: {working_password}")
        log_test("The user should use this password for authentication.")
    else:
        log_test(f"\n🚨 DIAGNOSIS:")
        if account_status == "exists":
            log_test("- Account exists in Supabase")
            log_test("- Password is incorrect or account is disabled")
            log_test("- Password reset should be used to regain access")
        elif account_status == "created":
            log_test("- Account did not exist and was just created")
            log_test("- Original account may have been deleted")
        else:
            log_test("- Unable to determine account status")
            log_test("- May be a system-wide issue")

if __name__ == "__main__":
    main()