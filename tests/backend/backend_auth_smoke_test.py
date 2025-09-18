#!/usr/bin/env python3
"""
Backend Auth Smoke Test for Aurum Life API
Testing authentication endpoints at https://aurum-overflow-fix.emergent.host/api

Test Scenarios:
1) POST /api/auth/register with disposable email: e2e.autotest+<timestamp>@emergent.test
2) POST /api/auth/login with same email/password; expect 200 with access_token  
3) GET /api/auth/me with Bearer token; expect 200 with id and email

Returns status codes and response bodies or errors.
"""

import requests
import json
import time
import sys
from datetime import datetime
import traceback

# Configuration
BASE_URL = "https://aurum-overflow-fix.emergent.host/api"
TIMEOUT = 30

def log_test_result(test_name, status_code, response_data, error=None):
    """Log test results in a structured format"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"TIME: {timestamp}")
    print(f"STATUS CODE: {status_code}")
    
    if error:
        print(f"ERROR: {error}")
    
    if response_data:
        print(f"RESPONSE: {json.dumps(response_data, indent=2)}")
    
    print(f"{'='*60}")

def test_auth_smoke():
    """Execute the complete auth smoke test as requested"""
    
    print("🚀 STARTING BACKEND AUTH SMOKE TEST")
    print(f"Target URL: {BASE_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Generate unique timestamp for disposable email
    timestamp = str(int(time.time()))
    test_email = f"e2e.autotest+{timestamp}@emergent.test"
    test_password = "StrongPass!234"
    test_username = f"e2e_autotest_{timestamp}"
    
    print(f"\n📧 Test Credentials:")
    print(f"Email: {test_email}")
    print(f"Password: {test_password}")
    print(f"Username: {test_username}")
    
    results = {
        "registration": {"success": False, "status_code": None, "response": None, "error": None},
        "login": {"success": False, "status_code": None, "response": None, "error": None, "access_token": None},
        "profile": {"success": False, "status_code": None, "response": None, "error": None}
    }
    
    # Test 1: User Registration
    print(f"\n🔐 TEST 1: POST /api/auth/register")
    try:
        registration_data = {
            "email": test_email,
            "password": test_password,
            "username": test_username,
            "first_name": "E2E",
            "last_name": "Bot"
        }
        
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=registration_data,
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        
        results["registration"]["status_code"] = response.status_code
        
        try:
            response_data = response.json()
            results["registration"]["response"] = response_data
        except:
            results["registration"]["response"] = {"raw_text": response.text}
        
        # Accept 201/200 as success, or 400/409 to continue as requested
        if response.status_code in [200, 201]:
            results["registration"]["success"] = True
            log_test_result("User Registration", response.status_code, results["registration"]["response"])
            print("✅ Registration successful")
        elif response.status_code in [400, 409]:
            results["registration"]["success"] = True  # Continue as requested
            log_test_result("User Registration", response.status_code, results["registration"]["response"])
            print("⚠️ Registration returned 400/409 - continuing as requested")
        else:
            results["registration"]["error"] = f"Unexpected status code: {response.status_code}"
            log_test_result("User Registration", response.status_code, results["registration"]["response"], results["registration"]["error"])
            print(f"❌ Registration failed with status {response.status_code}")
            
    except Exception as e:
        results["registration"]["error"] = str(e)
        log_test_result("User Registration", None, None, str(e))
        print(f"❌ Registration error: {e}")
    
    # Test 2: User Login
    print(f"\n🔑 TEST 2: POST /api/auth/login")
    try:
        login_data = {
            "email": test_email,
            "password": test_password
        }
        
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        
        results["login"]["status_code"] = response.status_code
        
        try:
            response_data = response.json()
            results["login"]["response"] = response_data
        except:
            results["login"]["response"] = {"raw_text": response.text}
        
        # Expect 200 with access_token
        if response.status_code == 200:
            if isinstance(results["login"]["response"], dict) and "access_token" in results["login"]["response"]:
                results["login"]["success"] = True
                results["login"]["access_token"] = results["login"]["response"]["access_token"]
                log_test_result("User Login", response.status_code, results["login"]["response"])
                print("✅ Login successful with access_token")
            else:
                results["login"]["error"] = "Login successful but no access_token in response"
                log_test_result("User Login", response.status_code, results["login"]["response"], results["login"]["error"])
                print("❌ Login missing access_token")
        else:
            results["login"]["error"] = f"Login failed with status code: {response.status_code}"
            log_test_result("User Login", response.status_code, results["login"]["response"], results["login"]["error"])
            print(f"❌ Login failed with status {response.status_code}")
            
    except Exception as e:
        results["login"]["error"] = str(e)
        log_test_result("User Login", None, None, str(e))
        print(f"❌ Login error: {e}")
    
    # Test 3: Get User Profile
    print(f"\n👤 TEST 3: GET /api/auth/me")
    if results["login"]["success"] and results["login"]["access_token"]:
        try:
            headers = {
                "Authorization": f"Bearer {results['login']['access_token']}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{BASE_URL}/auth/me",
                headers=headers,
                timeout=TIMEOUT
            )
            
            results["profile"]["status_code"] = response.status_code
            
            try:
                response_data = response.json()
                results["profile"]["response"] = response_data
            except:
                results["profile"]["response"] = {"raw_text": response.text}
            
            # Expect 200 with id and email
            if response.status_code == 200:
                if isinstance(results["profile"]["response"], dict):
                    has_id = "id" in results["profile"]["response"]
                    has_email = "email" in results["profile"]["response"]
                    
                    if has_id and has_email:
                        results["profile"]["success"] = True
                        log_test_result("Get User Profile", response.status_code, results["profile"]["response"])
                        print("✅ Profile retrieval successful with id and email")
                    else:
                        missing_fields = []
                        if not has_id:
                            missing_fields.append("id")
                        if not has_email:
                            missing_fields.append("email")
                        results["profile"]["error"] = f"Profile missing required fields: {', '.join(missing_fields)}"
                        log_test_result("Get User Profile", response.status_code, results["profile"]["response"], results["profile"]["error"])
                        print(f"❌ Profile missing fields: {', '.join(missing_fields)}")
                else:
                    results["profile"]["error"] = "Profile response is not a valid JSON object"
                    log_test_result("Get User Profile", response.status_code, results["profile"]["response"], results["profile"]["error"])
                    print("❌ Profile response invalid")
            else:
                results["profile"]["error"] = f"Profile request failed with status code: {response.status_code}"
                log_test_result("Get User Profile", response.status_code, results["profile"]["response"], results["profile"]["error"])
                print(f"❌ Profile failed with status {response.status_code}")
                
        except Exception as e:
            results["profile"]["error"] = str(e)
            log_test_result("Get User Profile", None, None, str(e))
            print(f"❌ Profile error: {e}")
    else:
        results["profile"]["error"] = "Skipped - no valid access token from login"
        log_test_result("Get User Profile", None, None, results["profile"]["error"])
        print("⏭️ Profile test skipped - no access token")
    
    # Final Summary
    print(f"\n{'='*80}")
    print("🎯 BACKEND AUTH SMOKE TEST SUMMARY")
    print(f"{'='*80}")
    
    total_tests = 3
    successful_tests = sum(1 for test in results.values() if test["success"])
    
    print(f"📊 Overall Success Rate: {successful_tests}/{total_tests} ({(successful_tests/total_tests)*100:.1f}%)")
    
    print(f"\n📋 Detailed Results:")
    
    # Registration Summary
    reg_status = "✅ PASS" if results["registration"]["success"] else "❌ FAIL"
    print(f"1. Registration: {reg_status} (Status: {results['registration']['status_code']})")
    if results["registration"]["error"]:
        print(f"   Error: {results['registration']['error']}")
    
    # Login Summary  
    login_status = "✅ PASS" if results["login"]["success"] else "❌ FAIL"
    print(f"2. Login: {login_status} (Status: {results['login']['status_code']})")
    if results["login"]["error"]:
        print(f"   Error: {results['login']['error']}")
    elif results["login"]["success"]:
        print(f"   Access Token: {results['login']['access_token'][:20]}..." if results['login']['access_token'] else "None")
    
    # Profile Summary
    profile_status = "✅ PASS" if results["profile"]["success"] else "❌ FAIL"
    print(f"3. Profile: {profile_status} (Status: {results['profile']['status_code']})")
    if results["profile"]["error"]:
        print(f"   Error: {results['profile']['error']}")
    elif results["profile"]["success"]:
        profile_data = results["profile"]["response"]
        if isinstance(profile_data, dict):
            print(f"   User ID: {profile_data.get('id', 'N/A')}")
            print(f"   Email: {profile_data.get('email', 'N/A')}")
    
    print(f"\n🏁 Test completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Return results for further processing
    return results

if __name__ == "__main__":
    try:
        results = test_auth_smoke()
        
        # Exit with appropriate code
        all_successful = all(test["success"] for test in results.values())
        sys.exit(0 if all_successful else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        traceback.print_exc()
        sys.exit(1)