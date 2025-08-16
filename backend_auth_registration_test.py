#!/usr/bin/env python3
"""
Backend Authentication Flow with Registration Test
Re-run Backend auth flow smoke test with actual registration to verify 400/401 issues are resolved
"""

import requests
import json
import time
import uuid
from datetime import datetime
import sys

# Configuration
BASE_URL = "https://datahierarchy-app.preview.emergentagent.com"
TIMEOUT = 30

def log_test_step(step, message):
    """Log test step with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] {step}: {message}")

def make_request(method, url, **kwargs):
    """Make HTTP request with timing and error handling"""
    start_time = time.time()
    try:
        response = requests.request(method, url, timeout=TIMEOUT, **kwargs)
        duration = (time.time() - start_time) * 1000
        
        log_test_step("REQUEST", f"{method} {url} -> {response.status_code} ({duration:.0f}ms)")
        
        # Log response details for debugging
        if response.status_code >= 400:
            try:
                error_data = response.json()
                log_test_step("ERROR", f"Response: {json.dumps(error_data, indent=2)}")
            except:
                log_test_step("ERROR", f"Response text: {response.text[:500]}")
        
        return response, duration
    except requests.exceptions.Timeout:
        duration = (time.time() - start_time) * 1000
        log_test_step("ERROR", f"{method} {url} -> TIMEOUT after {duration:.0f}ms")
        return None, duration
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        log_test_step("ERROR", f"{method} {url} -> EXCEPTION: {str(e)} ({duration:.0f}ms)")
        return None, duration

def test_backend_auth_registration_flow():
    """Test complete backend authentication flow with new user registration"""
    
    print("=" * 80)
    print("🚀 BACKEND AUTHENTICATION FLOW WITH REGISTRATION TEST")
    print("=" * 80)
    
    # Generate unique test credentials
    timestamp = int(time.time())
    test_email = f"e2e.auth+{timestamp}@emergent.test"
    test_password = "P@ssw0rd123"
    test_username = f"e2e_{timestamp}"
    
    log_test_step("SETUP", f"Generated test credentials:")
    log_test_step("SETUP", f"  Email: {test_email}")
    log_test_step("SETUP", f"  Password: {test_password}")
    log_test_step("SETUP", f"  Username: {test_username}")
    
    total_start_time = time.time()
    test_results = {
        "backend_health": {"status": "pending", "duration_ms": 0},
        "user_registration": {"status": "pending", "duration_ms": 0, "user_id": None},
        "user_login": {"status": "pending", "duration_ms": 0, "access_token": None},
        "profile_retrieval": {"status": "pending", "duration_ms": 0, "has_completed_onboarding": None},
        "onboarding_completion": {"status": "pending", "duration_ms": 0},
        "profile_verification": {"status": "pending", "duration_ms": 0},
        "pillars_access": {"status": "pending", "duration_ms": 0},
        "areas_access": {"status": "pending", "duration_ms": 0}
    }
    
    # Step 1: Backend Health Check
    log_test_step("STEP 1", "Backend Health Check")
    response, duration = make_request("GET", f"{BASE_URL}/")
    test_results["backend_health"]["duration_ms"] = duration
    
    if response and response.status_code == 200:
        test_results["backend_health"]["status"] = "success"
        log_test_step("SUCCESS", f"Backend is accessible and responding correctly")
        try:
            health_data = response.json()
            log_test_step("INFO", f"Backend response: {json.dumps(health_data, indent=2)}")
        except:
            pass
    else:
        test_results["backend_health"]["status"] = "failed"
        log_test_step("FAILED", "Backend health check failed")
        return test_results
    
    # Step 2: User Registration
    log_test_step("STEP 2", "User Registration")
    registration_data = {
        "email": test_email,
        "password": test_password,
        "first_name": "E2E",
        "last_name": "User",
        "username": test_username
    }
    
    response, duration = make_request(
        "POST", 
        f"{BASE_URL}/api/auth/register",
        json=registration_data,
        headers={"Content-Type": "application/json"}
    )
    test_results["user_registration"]["duration_ms"] = duration
    
    if response and response.status_code in [200, 201]:
        test_results["user_registration"]["status"] = "success"
        try:
            reg_data = response.json()
            user_id = reg_data.get("id") or reg_data.get("user", {}).get("id")
            test_results["user_registration"]["user_id"] = user_id
            
            log_test_step("SUCCESS", f"User registration successful")
            log_test_step("INFO", f"Registration response: {json.dumps(reg_data, indent=2)}")
            
            if user_id:
                log_test_step("VERIFIED", f"User ID present: {user_id}")
            else:
                log_test_step("WARNING", "User ID not found in response")
                
        except Exception as e:
            log_test_step("ERROR", f"Failed to parse registration response: {e}")
            test_results["user_registration"]["status"] = "failed"
            return test_results
    else:
        test_results["user_registration"]["status"] = "failed"
        log_test_step("FAILED", f"User registration failed with status {response.status_code if response else 'None'}")
        return test_results
    
    # Step 3: User Login (immediately after registration)
    log_test_step("STEP 3", "User Login (immediate after registration)")
    login_data = {
        "email": test_email,
        "password": test_password
    }
    
    response, duration = make_request(
        "POST",
        f"{BASE_URL}/api/auth/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    test_results["user_login"]["duration_ms"] = duration
    
    access_token = None
    if response and response.status_code == 200:
        test_results["user_login"]["status"] = "success"
        try:
            login_data = response.json()
            access_token = login_data.get("access_token")
            test_results["user_login"]["access_token"] = access_token
            
            log_test_step("SUCCESS", f"User login successful")
            log_test_step("INFO", f"Login response: {json.dumps(login_data, indent=2)}")
            
            if access_token:
                log_test_step("VERIFIED", f"Access token received: {access_token[:20]}...")
            else:
                log_test_step("WARNING", "Access token not found in response")
                
        except Exception as e:
            log_test_step("ERROR", f"Failed to parse login response: {e}")
            test_results["user_login"]["status"] = "failed"
            return test_results
    else:
        test_results["user_login"]["status"] = "failed"
        log_test_step("FAILED", f"User login failed with status {response.status_code if response else 'None'}")
        return test_results
    
    if not access_token:
        log_test_step("FAILED", "Cannot proceed without access token")
        return test_results
    
    # Prepare authorization header
    auth_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Step 4: Profile Retrieval (check onboarding status)
    log_test_step("STEP 4", "Profile Retrieval (check onboarding status)")
    response, duration = make_request(
        "GET",
        f"{BASE_URL}/api/auth/me",
        headers=auth_headers
    )
    test_results["profile_retrieval"]["duration_ms"] = duration
    
    if response and response.status_code == 200:
        test_results["profile_retrieval"]["status"] = "success"
        try:
            profile_data = response.json()
            has_completed_onboarding = profile_data.get("has_completed_onboarding")
            test_results["profile_retrieval"]["has_completed_onboarding"] = has_completed_onboarding
            
            log_test_step("SUCCESS", f"Profile retrieval successful")
            log_test_step("INFO", f"Profile response: {json.dumps(profile_data, indent=2)}")
            log_test_step("VERIFIED", f"has_completed_onboarding: {has_completed_onboarding}")
            
        except Exception as e:
            log_test_step("ERROR", f"Failed to parse profile response: {e}")
            test_results["profile_retrieval"]["status"] = "failed"
            return test_results
    else:
        test_results["profile_retrieval"]["status"] = "failed"
        log_test_step("FAILED", f"Profile retrieval failed with status {response.status_code if response else 'None'}")
        return test_results
    
    # Step 5: Complete Onboarding
    log_test_step("STEP 5", "Complete Onboarding")
    response, duration = make_request(
        "POST",
        f"{BASE_URL}/api/auth/complete-onboarding",
        headers=auth_headers,
        json={}
    )
    test_results["onboarding_completion"]["duration_ms"] = duration
    
    if response and response.status_code == 200:
        test_results["onboarding_completion"]["status"] = "success"
        try:
            onboarding_data = response.json()
            log_test_step("SUCCESS", f"Onboarding completion successful")
            log_test_step("INFO", f"Onboarding response: {json.dumps(onboarding_data, indent=2)}")
            
            # Check if response indicates success
            if onboarding_data.get("has_completed_onboarding") == True or "completed successfully" in str(onboarding_data).lower():
                log_test_step("VERIFIED", "Onboarding marked as completed")
            else:
                log_test_step("WARNING", "Onboarding completion status unclear")
                
        except Exception as e:
            log_test_step("ERROR", f"Failed to parse onboarding response: {e}")
            test_results["onboarding_completion"]["status"] = "failed"
            return test_results
    else:
        test_results["onboarding_completion"]["status"] = "failed"
        log_test_step("FAILED", f"Onboarding completion failed with status {response.status_code if response else 'None'}")
        return test_results
    
    # Step 6: Profile Verification (confirm onboarding status changed)
    log_test_step("STEP 6", "Profile Verification (confirm onboarding status)")
    response, duration = make_request(
        "GET",
        f"{BASE_URL}/api/auth/me",
        headers=auth_headers
    )
    test_results["profile_verification"]["duration_ms"] = duration
    
    if response and response.status_code == 200:
        test_results["profile_verification"]["status"] = "success"
        try:
            profile_data = response.json()
            has_completed_onboarding = profile_data.get("has_completed_onboarding")
            
            log_test_step("SUCCESS", f"Profile verification successful")
            log_test_step("INFO", f"Updated profile response: {json.dumps(profile_data, indent=2)}")
            log_test_step("VERIFIED", f"has_completed_onboarding now: {has_completed_onboarding}")
            
            if has_completed_onboarding == True:
                log_test_step("VERIFIED", "Onboarding status successfully updated to true")
            else:
                log_test_step("WARNING", f"Onboarding status is {has_completed_onboarding}, expected true")
                
        except Exception as e:
            log_test_step("ERROR", f"Failed to parse profile verification response: {e}")
            test_results["profile_verification"]["status"] = "failed"
            return test_results
    else:
        test_results["profile_verification"]["status"] = "failed"
        log_test_step("FAILED", f"Profile verification failed with status {response.status_code if response else 'None'}")
        return test_results
    
    # Step 7: Test Pillars Access
    log_test_step("STEP 7", "Test Pillars Access")
    response, duration = make_request(
        "GET",
        f"{BASE_URL}/api/pillars",
        headers=auth_headers
    )
    test_results["pillars_access"]["duration_ms"] = duration
    
    if response and response.status_code == 200:
        test_results["pillars_access"]["status"] = "success"
        try:
            pillars_data = response.json()
            log_test_step("SUCCESS", f"Pillars access successful")
            log_test_step("INFO", f"Pillars response: {json.dumps(pillars_data, indent=2)}")
            log_test_step("VERIFIED", f"Retrieved {len(pillars_data)} pillars")
            
        except Exception as e:
            log_test_step("ERROR", f"Failed to parse pillars response: {e}")
            test_results["pillars_access"]["status"] = "failed"
    else:
        test_results["pillars_access"]["status"] = "failed"
        log_test_step("FAILED", f"Pillars access failed with status {response.status_code if response else 'None'}")
    
    # Step 8: Test Areas Access
    log_test_step("STEP 8", "Test Areas Access")
    response, duration = make_request(
        "GET",
        f"{BASE_URL}/api/areas",
        headers=auth_headers
    )
    test_results["areas_access"]["duration_ms"] = duration
    
    if response and response.status_code == 200:
        test_results["areas_access"]["status"] = "success"
        try:
            areas_data = response.json()
            log_test_step("SUCCESS", f"Areas access successful")
            log_test_step("INFO", f"Areas response: {json.dumps(areas_data, indent=2)}")
            log_test_step("VERIFIED", f"Retrieved {len(areas_data)} areas")
            
        except Exception as e:
            log_test_step("ERROR", f"Failed to parse areas response: {e}")
            test_results["areas_access"]["status"] = "failed"
    else:
        test_results["areas_access"]["status"] = "failed"
        log_test_step("FAILED", f"Areas access failed with status {response.status_code if response else 'None'}")
    
    # Calculate total test time
    total_duration = (time.time() - total_start_time) * 1000
    
    # Print comprehensive results
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 80)
    
    success_count = sum(1 for result in test_results.values() if result["status"] == "success")
    total_tests = len(test_results)
    success_rate = (success_count / total_tests) * 100
    
    print(f"🎯 Overall Success Rate: {success_count}/{total_tests} ({success_rate:.1f}%)")
    print(f"⏱️  Total Test Duration: {total_duration:.0f}ms")
    
    print(f"\n📋 Detailed Results:")
    for test_name, result in test_results.items():
        status_emoji = "✅" if result["status"] == "success" else "❌" if result["status"] == "failed" else "⏳"
        print(f"  {status_emoji} {test_name.replace('_', ' ').title()}: {result['status']} ({result['duration_ms']:.0f}ms)")
    
    print(f"\n🔍 Performance Metrics:")
    avg_response_time = sum(result["duration_ms"] for result in test_results.values()) / len(test_results)
    print(f"  Average API Response Time: {avg_response_time:.0f}ms")
    
    # Print success criteria analysis
    print(f"\n✅ Success Criteria Analysis:")
    criteria = [
        ("Backend health check working", test_results["backend_health"]["status"] == "success"),
        ("User registration with 200/201 and ID present", test_results["user_registration"]["status"] == "success" and test_results["user_registration"]["user_id"]),
        ("User login with access_token", test_results["user_login"]["status"] == "success" and test_results["user_login"]["access_token"]),
        ("Profile endpoint accessible", test_results["profile_retrieval"]["status"] == "success"),
        ("Onboarding completion working", test_results["onboarding_completion"]["status"] == "success"),
        ("Profile persistence verified", test_results["profile_verification"]["status"] == "success"),
        ("Pillars access confirmed", test_results["pillars_access"]["status"] == "success"),
        ("Areas access confirmed", test_results["areas_access"]["status"] == "success")
    ]
    
    for criterion, passed in criteria:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {criterion}")
    
    print("\n" + "=" * 80)
    
    if success_rate == 100:
        print("🎉 BACKEND AUTHENTICATION FLOW WITH REGISTRATION - 100% SUCCESS!")
        print("All authentication endpoints working correctly with new user registration.")
    elif success_rate >= 75:
        print("⚠️  BACKEND AUTHENTICATION FLOW - MOSTLY SUCCESSFUL")
        print("Core authentication working but some issues detected.")
    else:
        print("🚨 BACKEND AUTHENTICATION FLOW - CRITICAL ISSUES DETECTED")
        print("Multiple authentication endpoints failing.")
    
    print("=" * 80)
    
    return test_results

if __name__ == "__main__":
    try:
        results = test_backend_auth_registration_flow()
        
        # Exit with appropriate code
        success_count = sum(1 for result in results.values() if result["status"] == "success")
        total_tests = len(results)
        
        if success_count == total_tests:
            sys.exit(0)  # All tests passed
        else:
            sys.exit(1)  # Some tests failed
            
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        sys.exit(1)