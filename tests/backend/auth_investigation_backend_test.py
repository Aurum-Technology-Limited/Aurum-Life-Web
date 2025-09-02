#!/usr/bin/env python3
"""
Authentication Investigation Backend Test
Focused test to investigate 401 authentication errors as reported by user
"""

import requests
import json
import time
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://smart-life-os.preview.emergentagent.com/api"
TEST_EMAIL = "marc.alleyne@aurumtechnologyltd.com"
TEST_PASSWORD = "password123"

def log_test(message):
    """Log test messages with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] {message}")

def test_health_check():
    """Test if backend is accessible"""
    log_test("🔍 Testing backend health check...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        log_test(f"Health check: {response.status_code} - {response.text}")
        return response.status_code == 200
    except Exception as e:
        log_test(f"❌ Health check failed: {e}")
        return False

def test_login_endpoint():
    """Test the login endpoint with known credentials"""
    log_test("🔍 Testing login endpoint with known credentials...")
    
    login_payload = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
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

def test_auth_me_endpoint(token):
    """Test the /auth/me endpoint with token"""
    log_test("🔍 Testing /auth/me endpoint...")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        start_time = time.time()
        response = requests.get(
            f"{BACKEND_URL}/auth/me",
            headers=headers,
            timeout=30
        )
        end_time = time.time()
        
        log_test(f"/auth/me response: {response.status_code} ({(end_time - start_time) * 1000:.1f}ms)")
        
        if response.status_code == 200:
            data = response.json()
            log_test(f"✅ User profile retrieved: {data.get('email', 'N/A')}")
            return True
        else:
            log_test(f"❌ /auth/me failed: {response.text}")
            return False
            
    except Exception as e:
        log_test(f"❌ /auth/me request failed: {e}")
        return False

def test_protected_endpoint(token):
    """Test a protected endpoint to verify token works"""
    log_test("🔍 Testing protected endpoint /pillars...")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        start_time = time.time()
        response = requests.get(
            f"{BACKEND_URL}/pillars",
            headers=headers,
            timeout=30
        )
        end_time = time.time()
        
        log_test(f"/pillars response: {response.status_code} ({(end_time - start_time) * 1000:.1f}ms)")
        
        if response.status_code == 200:
            data = response.json()
            log_test(f"✅ Protected endpoint accessible! Pillars count: {len(data) if isinstance(data, list) else 'N/A'}")
            return True
        else:
            log_test(f"❌ Protected endpoint failed: {response.text}")
            return False
            
    except Exception as e:
        log_test(f"❌ Protected endpoint request failed: {e}")
        return False

def test_debug_supabase_config():
    """Test debug endpoint to check Supabase configuration"""
    log_test("🔍 Testing Supabase debug configuration...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/auth/debug-supabase-config", timeout=10)
        log_test(f"Debug config response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            log_test(f"✅ Supabase URL: {data.get('supabase_url', 'N/A')}")
            log_test(f"✅ Expected site URL: {data.get('expected_site_url', 'N/A')}")
            return True
        else:
            log_test(f"❌ Debug config failed: {response.text}")
            return False
            
    except Exception as e:
        log_test(f"❌ Debug config request failed: {e}")
        return False

def test_invalid_credentials():
    """Test with invalid credentials to verify error handling"""
    log_test("🔍 Testing with invalid credentials...")
    
    invalid_payload = {
        "email": "invalid@test.com",
        "password": "wrongpassword"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json=invalid_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        log_test(f"Invalid credentials response: {response.status_code}")
        
        if response.status_code == 401:
            log_test("✅ Invalid credentials properly rejected with 401")
            return True
        else:
            log_test(f"❌ Unexpected response for invalid credentials: {response.text}")
            return False
            
    except Exception as e:
        log_test(f"❌ Invalid credentials test failed: {e}")
        return False

def main():
    """Main test execution"""
    log_test("🎯 AUTHENTICATION INVESTIGATION BACKEND TEST STARTED")
    log_test(f"Backend URL: {BACKEND_URL}")
    log_test(f"Test credentials: {TEST_EMAIL}")
    
    results = {
        "health_check": False,
        "debug_config": False,
        "invalid_credentials": False,
        "login_success": False,
        "auth_me": False,
        "protected_endpoint": False
    }
    
    # Test 1: Health check
    results["health_check"] = test_health_check()
    
    # Test 2: Debug Supabase configuration
    results["debug_config"] = test_debug_supabase_config()
    
    # Test 3: Invalid credentials handling
    results["invalid_credentials"] = test_invalid_credentials()
    
    # Test 4: Login with known credentials
    token = test_login_endpoint()
    results["login_success"] = token is not None
    
    if token:
        # Test 5: /auth/me endpoint
        results["auth_me"] = test_auth_me_endpoint(token)
        
        # Test 6: Protected endpoint access
        results["protected_endpoint"] = test_protected_endpoint(token)
    else:
        log_test("⚠️ Skipping authenticated endpoint tests due to login failure")
    
    # Summary
    log_test("\n" + "="*60)
    log_test("🎯 AUTHENTICATION INVESTIGATION TEST SUMMARY")
    log_test("="*60)
    
    success_count = sum(1 for result in results.values() if result)
    total_tests = len(results)
    success_rate = (success_count / total_tests) * 100
    
    log_test(f"Overall Success Rate: {success_rate:.1f}% ({success_count}/{total_tests})")
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        log_test(f"{status}: {test_name}")
    
    # Critical findings
    if not results["login_success"]:
        log_test("\n🚨 CRITICAL ISSUE: Login endpoint failing with known credentials!")
        log_test("This matches the user's reported 401 authentication error.")
        log_test("Possible causes:")
        log_test("- Account may be disabled or deleted")
        log_test("- Password may have been changed")
        log_test("- Supabase Auth configuration issues")
        log_test("- Backend authentication logic problems")
    
    if results["login_success"] and not results["auth_me"]:
        log_test("\n🚨 CRITICAL ISSUE: Login works but /auth/me fails!")
        log_test("This indicates token validation problems in the backend.")
    
    if results["login_success"] and not results["protected_endpoint"]:
        log_test("\n🚨 CRITICAL ISSUE: Login works but protected endpoints fail!")
        log_test("This indicates authentication dependency problems.")
    
    log_test("\n🎯 Authentication investigation completed!")

if __name__ == "__main__":
    main()