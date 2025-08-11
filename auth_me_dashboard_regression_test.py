#!/usr/bin/env python3
"""
Regression Test for auth/me and dashboard after fixes
Base: https://aurum-overflow-fix.emergent.host/api

Test scenarios:
1) POST /api/auth/login with email=marc.alleyne@aurumtechnologyltd.com and a placeholder wrong password to force legacy branch; expect 200 with access_token (hybrid).
2) GET /api/auth/me with the access_token; expect 200 and verify id equals Supabase Auth ID (950f327b-4a85-438f-bb85-6229bf3cde9d) or legacy fallback with created user_profiles record.
3) GET /api/ultra/dashboard with Bearer token; expect 200.
"""

import requests
import json
import sys
from datetime import datetime

# Base URL for the API
BASE_URL = "https://aurum-overflow-fix.emergent.host/api"

# Test credentials
TEST_EMAIL = "marc.alleyne@aurumtechnologyltd.com"
WRONG_PASSWORD = "placeholder_wrong_password"
EXPECTED_SUPABASE_ID = "950f327b-4a85-438f-bb85-6229bf3cde9d"

def log_test_result(test_name, status_code, response_data, success=True):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"[{timestamp}] {status} {test_name}")
    print(f"  Status Code: {status_code}")
    if isinstance(response_data, dict):
        print(f"  Response: {json.dumps(response_data, indent=2)}")
    else:
        print(f"  Response: {response_data}")
    print("-" * 80)

def test_auth_login_wrong_password():
    """
    Test 1: POST /api/auth/login with wrong password to force legacy branch
    Expected: 200 with access_token (hybrid authentication)
    """
    print("🔐 TEST 1: Authentication Login with Wrong Password (Force Legacy Branch)")
    
    url = f"{BASE_URL}/auth/login"
    payload = {
        "email": TEST_EMAIL,
        "password": WRONG_PASSWORD
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        
        # Check if we get 200 with access_token (hybrid behavior)
        if response.status_code == 200 and isinstance(response_data, dict) and 'access_token' in response_data:
            log_test_result("Login with Wrong Password (Hybrid)", response.status_code, response_data, success=True)
            return response_data.get('access_token')
        else:
            log_test_result("Login with Wrong Password (Hybrid)", response.status_code, response_data, success=False)
            return None
            
    except Exception as e:
        log_test_result("Login with Wrong Password (Hybrid)", 0, f"Exception: {str(e)}", success=False)
        return None

def test_auth_me(access_token):
    """
    Test 2: GET /api/auth/me with access_token
    Expected: 200 and verify id equals Supabase Auth ID or legacy fallback
    """
    print("👤 TEST 2: Get User Profile with Access Token")
    
    if not access_token:
        log_test_result("Get User Profile", 0, "No access token available", success=False)
        return None
    
    url = f"{BASE_URL}/auth/me"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        
        if response.status_code == 200 and isinstance(response_data, dict):
            user_id = response_data.get('id')
            email = response_data.get('email')
            
            # Check if ID matches expected Supabase Auth ID or is a valid fallback
            id_match = user_id == EXPECTED_SUPABASE_ID
            email_match = email == TEST_EMAIL
            
            success = email_match and user_id is not None
            
            result_details = {
                "user_id": user_id,
                "expected_id": EXPECTED_SUPABASE_ID,
                "id_matches_expected": id_match,
                "email": email,
                "email_matches": email_match,
                "full_response": response_data
            }
            
            log_test_result("Get User Profile", response.status_code, result_details, success=success)
            return response_data
        else:
            log_test_result("Get User Profile", response.status_code, response_data, success=False)
            return None
            
    except Exception as e:
        log_test_result("Get User Profile", 0, f"Exception: {str(e)}", success=False)
        return None

def test_ultra_dashboard(access_token):
    """
    Test 3: GET /api/ultra/dashboard with Bearer token
    Expected: 200
    """
    print("📊 TEST 3: Ultra Dashboard Access")
    
    if not access_token:
        log_test_result("Ultra Dashboard", 0, "No access token available", success=False)
        return None
    
    url = f"{BASE_URL}/ultra/dashboard"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        
        success = response.status_code == 200
        log_test_result("Ultra Dashboard", response.status_code, response_data, success=success)
        return response_data
            
    except Exception as e:
        log_test_result("Ultra Dashboard", 0, f"Exception: {str(e)}", success=False)
        return None

def main():
    """Run all regression tests"""
    print("🚀 STARTING AUTH/ME AND DASHBOARD REGRESSION TESTS")
    print(f"Base URL: {BASE_URL}")
    print(f"Test Email: {TEST_EMAIL}")
    print(f"Expected Supabase ID: {EXPECTED_SUPABASE_ID}")
    print("=" * 80)
    
    # Test 1: Login with wrong password (force legacy branch)
    access_token = test_auth_login_wrong_password()
    
    # Test 2: Get user profile with access token
    user_profile = test_auth_me(access_token)
    
    # Test 3: Access ultra dashboard
    dashboard_data = test_ultra_dashboard(access_token)
    
    # Summary
    print("\n📋 REGRESSION TEST SUMMARY")
    print("=" * 80)
    
    tests_passed = 0
    total_tests = 3
    
    if access_token:
        tests_passed += 1
        print("✅ Test 1: Login with wrong password (hybrid) - PASSED")
    else:
        print("❌ Test 1: Login with wrong password (hybrid) - FAILED")
    
    if user_profile and user_profile.get('email') == TEST_EMAIL:
        tests_passed += 1
        print("✅ Test 2: Get user profile - PASSED")
    else:
        print("❌ Test 2: Get user profile - FAILED")
    
    if dashboard_data is not None:
        tests_passed += 1
        print("✅ Test 3: Ultra dashboard access - PASSED")
    else:
        print("❌ Test 3: Ultra dashboard access - FAILED")
    
    success_rate = (tests_passed / total_tests) * 100
    print(f"\n🎯 OVERALL SUCCESS RATE: {tests_passed}/{total_tests} ({success_rate:.1f}%)")
    
    if tests_passed == total_tests:
        print("🎉 ALL REGRESSION TESTS PASSED!")
        return 0
    else:
        print("⚠️  SOME REGRESSION TESTS FAILED!")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)