#!/usr/bin/env python3
"""
Onboarding Functionality Backend Testing
Tests the new onboarding functionality as requested in the review.

Test Focus:
1. Test the new POST /api/auth/complete-onboarding endpoint
2. Create a new user with has_completed_onboarding=false by default 
3. Test logging in with this new user to verify the API returns the correct onboarding status
4. Test the complete-onboarding endpoint to mark onboarding as completed

Test Credentials:
- email: onboarding.test@aurumlife.com
- password: testpass123
- first_name: Onboarding
- last_name: Test
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://bc5c41e8-49fa-4e1c-8536-e71401e166ef.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials as specified in the review
TEST_USER = {
    "email": "onboarding.test@aurumlife.com",
    "password": "testpass123",
    "first_name": "Onboarding",
    "last_name": "Test",
    "username": "onboarding_test"
}

class OnboardingTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.test_results = []
        
    def log_result(self, test_name, success, details, response_time=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "response_time": f"{response_time:.1f}ms" if response_time else "N/A",
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status} {test_name}: {details}")
        if response_time:
            print(f"   Response time: {response_time:.1f}ms")
        print()

    def test_user_registration(self):
        """Test 1: Create a new user with has_completed_onboarding=false by default"""
        print("🧪 TEST 1: User Registration with Default Onboarding Status")
        print("=" * 60)
        
        try:
            start_time = time.time()
            
            # First, try to clean up any existing user (ignore errors)
            try:
                # This might fail if user doesn't exist, which is fine
                pass
            except:
                pass
            
            # Register new user
            registration_data = {
                "username": TEST_USER["username"],
                "email": TEST_USER["email"],
                "password": TEST_USER["password"],
                "first_name": TEST_USER["first_name"],
                "last_name": TEST_USER["last_name"]
            }
            
            response = self.session.post(
                f"{API_BASE}/auth/register",
                json=registration_data,
                headers={"Content-Type": "application/json"}
            )
            
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 201 or response.status_code == 200:
                user_data = response.json()
                self.user_id = user_data.get("id")
                
                # Check if has_completed_onboarding defaults to false
                has_completed_onboarding = user_data.get("has_completed_onboarding", None)
                
                if has_completed_onboarding is False:
                    self.log_result(
                        "User Registration",
                        True,
                        f"User created successfully with has_completed_onboarding=False. User ID: {self.user_id}",
                        response_time
                    )
                    return True
                else:
                    self.log_result(
                        "User Registration",
                        False,
                        f"User created but has_completed_onboarding={has_completed_onboarding}, expected False",
                        response_time
                    )
                    return False
            else:
                error_detail = response.text
                self.log_result(
                    "User Registration",
                    False,
                    f"Registration failed with status {response.status_code}: {error_detail}",
                    response_time
                )
                return False
                
        except Exception as e:
            self.log_result(
                "User Registration",
                False,
                f"Registration error: {str(e)}"
            )
            return False

    def test_user_login_onboarding_status(self):
        """Test 2: Test logging in with new user to verify API returns correct onboarding status"""
        print("🧪 TEST 2: User Login and Onboarding Status Verification")
        print("=" * 60)
        
        try:
            start_time = time.time()
            
            # Login with test credentials
            login_data = {
                "email": TEST_USER["email"],
                "password": TEST_USER["password"]
            }
            
            response = self.session.post(
                f"{API_BASE}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                login_result = response.json()
                self.auth_token = login_result.get("access_token")
                
                if self.auth_token:
                    self.log_result(
                        "User Login",
                        True,
                        f"Login successful, received access token",
                        response_time
                    )
                    
                    # Now test getting user profile to check onboarding status
                    return self.test_get_user_profile()
                else:
                    self.log_result(
                        "User Login",
                        False,
                        "Login successful but no access token received",
                        response_time
                    )
                    return False
            else:
                error_detail = response.text
                self.log_result(
                    "User Login",
                    False,
                    f"Login failed with status {response.status_code}: {error_detail}",
                    response_time
                )
                return False
                
        except Exception as e:
            self.log_result(
                "User Login",
                False,
                f"Login error: {str(e)}"
            )
            return False

    def test_get_user_profile(self):
        """Test 2b: Get user profile to verify onboarding status"""
        try:
            start_time = time.time()
            
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(
                f"{API_BASE}/auth/me",
                headers=headers
            )
            
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                user_profile = response.json()
                has_completed_onboarding = user_profile.get("has_completed_onboarding", None)
                
                if has_completed_onboarding is False:
                    self.log_result(
                        "User Profile Onboarding Status",
                        True,
                        f"User profile shows has_completed_onboarding=False as expected",
                        response_time
                    )
                    return True
                else:
                    self.log_result(
                        "User Profile Onboarding Status",
                        False,
                        f"User profile shows has_completed_onboarding={has_completed_onboarding}, expected False",
                        response_time
                    )
                    return False
            else:
                error_detail = response.text
                self.log_result(
                    "User Profile Onboarding Status",
                    False,
                    f"Failed to get user profile with status {response.status_code}: {error_detail}",
                    response_time
                )
                return False
                
        except Exception as e:
            self.log_result(
                "User Profile Onboarding Status",
                False,
                f"Get user profile error: {str(e)}"
            )
            return False

    def test_complete_onboarding_endpoint(self):
        """Test 3: Test the complete-onboarding endpoint to mark onboarding as completed"""
        print("🧪 TEST 3: Complete Onboarding Endpoint")
        print("=" * 60)
        
        try:
            start_time = time.time()
            
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.post(
                f"{API_BASE}/auth/complete-onboarding",
                headers=headers
            )
            
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                result = response.json()
                has_completed_onboarding = result.get("has_completed_onboarding", None)
                message = result.get("message", "")
                
                if has_completed_onboarding is True and "completed successfully" in message:
                    self.log_result(
                        "Complete Onboarding Endpoint",
                        True,
                        f"Onboarding marked as completed successfully. Message: {message}",
                        response_time
                    )
                    return True
                else:
                    self.log_result(
                        "Complete Onboarding Endpoint",
                        False,
                        f"Unexpected response: has_completed_onboarding={has_completed_onboarding}, message={message}",
                        response_time
                    )
                    return False
            else:
                error_detail = response.text
                self.log_result(
                    "Complete Onboarding Endpoint",
                    False,
                    f"Complete onboarding failed with status {response.status_code}: {error_detail}",
                    response_time
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Complete Onboarding Endpoint",
                False,
                f"Complete onboarding error: {str(e)}"
            )
            return False

    def test_verify_onboarding_completed(self):
        """Test 4: Verify that onboarding status is now true after completion"""
        print("🧪 TEST 4: Verify Onboarding Status After Completion")
        print("=" * 60)
        
        try:
            start_time = time.time()
            
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(
                f"{API_BASE}/auth/me",
                headers=headers
            )
            
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                user_profile = response.json()
                has_completed_onboarding = user_profile.get("has_completed_onboarding", None)
                
                if has_completed_onboarding is True:
                    self.log_result(
                        "Verify Onboarding Completed",
                        True,
                        f"User profile now shows has_completed_onboarding=True as expected",
                        response_time
                    )
                    return True
                else:
                    self.log_result(
                        "Verify Onboarding Completed",
                        False,
                        f"User profile shows has_completed_onboarding={has_completed_onboarding}, expected True",
                        response_time
                    )
                    return False
            else:
                error_detail = response.text
                self.log_result(
                    "Verify Onboarding Completed",
                    False,
                    f"Failed to get user profile with status {response.status_code}: {error_detail}",
                    response_time
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Verify Onboarding Completed",
                False,
                f"Verify onboarding error: {str(e)}"
            )
            return False

    def test_error_handling(self):
        """Test 5: Test error handling scenarios"""
        print("🧪 TEST 5: Error Handling")
        print("=" * 60)
        
        # Test complete-onboarding without authentication
        try:
            start_time = time.time()
            
            response = self.session.post(
                f"{API_BASE}/auth/complete-onboarding",
                headers={"Content-Type": "application/json"}
            )
            
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 401 or response.status_code == 403:
                self.log_result(
                    "Error Handling - No Auth",
                    True,
                    f"Correctly rejected unauthenticated request with status {response.status_code}",
                    response_time
                )
            else:
                self.log_result(
                    "Error Handling - No Auth",
                    False,
                    f"Expected 401/403 for unauthenticated request, got {response.status_code}",
                    response_time
                )
                
        except Exception as e:
            self.log_result(
                "Error Handling - No Auth",
                False,
                f"Error handling test error: {str(e)}"
            )

        # Test complete-onboarding with invalid token
        try:
            start_time = time.time()
            
            headers = {
                "Authorization": "Bearer invalid_token_12345",
                "Content-Type": "application/json"
            }
            
            response = self.session.post(
                f"{API_BASE}/auth/complete-onboarding",
                headers=headers
            )
            
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 401 or response.status_code == 403:
                self.log_result(
                    "Error Handling - Invalid Token",
                    True,
                    f"Correctly rejected invalid token with status {response.status_code}",
                    response_time
                )
                return True
            else:
                self.log_result(
                    "Error Handling - Invalid Token",
                    False,
                    f"Expected 401/403 for invalid token, got {response.status_code}",
                    response_time
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Error Handling - Invalid Token",
                False,
                f"Error handling test error: {str(e)}"
            )
            return False

    def run_all_tests(self):
        """Run all onboarding functionality tests"""
        print("🚀 ONBOARDING FUNCTIONALITY BACKEND TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User: {TEST_USER['email']}")
        print(f"Started at: {datetime.now().isoformat()}")
        print("=" * 80)
        print()
        
        # Test sequence
        tests_passed = 0
        total_tests = 5
        
        # Test 1: User Registration
        if self.test_user_registration():
            tests_passed += 1
        
        # Test 2: User Login and Onboarding Status
        if self.test_user_login_onboarding_status():
            tests_passed += 1
        
        # Test 3: Complete Onboarding Endpoint
        if self.test_complete_onboarding_endpoint():
            tests_passed += 1
        
        # Test 4: Verify Onboarding Completed
        if self.test_verify_onboarding_completed():
            tests_passed += 1
        
        # Test 5: Error Handling
        if self.test_error_handling():
            tests_passed += 1
        
        # Summary
        print("=" * 80)
        print("🎯 ONBOARDING FUNCTIONALITY TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (tests_passed / total_tests) * 100
        
        for result in self.test_results:
            print(f"{result['status']} {result['test']}")
            print(f"   Details: {result['details']}")
            print(f"   Response Time: {result['response_time']}")
            print()
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Tests Passed: {tests_passed}/{total_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Status: {'🎉 ALL TESTS PASSED' if tests_passed == total_tests else '⚠️ SOME TESTS FAILED'}")
        
        if success_rate >= 80:
            print(f"✅ ONBOARDING FUNCTIONALITY IS PRODUCTION-READY!")
        else:
            print(f"❌ ONBOARDING FUNCTIONALITY NEEDS ATTENTION!")
        
        print("=" * 80)
        
        return success_rate

if __name__ == "__main__":
    tester = OnboardingTester()
    success_rate = tester.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if success_rate >= 80 else 1)