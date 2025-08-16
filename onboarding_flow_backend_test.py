#!/usr/bin/env python3
"""
Backend-only validation for onboarding endpoints to ensure new-user flow completes after login.

Test Steps:
1) Create a fresh account via /api/auth/register with unique email
2) Login via /api/auth/login  
3) GET /api/auth/me -> expect has_completed_onboarding=false
4) POST /api/auth/complete-onboarding
5) GET /api/auth/me -> expect has_completed_onboarding=true
6) Optionally, seed demo for this user size=light include_streak=false

Base URL: https://datahierarchy-app.preview.emergentagent.com
"""

import requests
import json
import time
import uuid
from datetime import datetime
import sys

# Configuration
BASE_URL = "https://datahierarchy-app.preview.emergentagent.com"
API_BASE = f"{BASE_URL}/api"

class OnboardingBackendTest:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.access_token = None
        self.user_email = None
        self.test_results = []
        
    def log_result(self, test_name, success, details, response_time=None):
        """Log test result with details"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'response_time': response_time,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        time_info = f" ({response_time:.3f}s)" if response_time else ""
        print(f"{status}: {test_name}{time_info}")
        print(f"   Details: {details}")
        print()
        
    def make_request(self, method, endpoint, data=None, auth_required=False):
        """Make HTTP request with error handling and timing"""
        url = f"{API_BASE}{endpoint}"
        headers = {}
        
        if auth_required and self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
            
        start_time = time.time()
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, headers=headers)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, headers=headers)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, headers=headers)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            response_time = time.time() - start_time
            return response, response_time
            
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            return None, response_time
            
    def test_1_create_fresh_account(self):
        """Step 1: Create a fresh account via /api/auth/register with unique email"""
        timestamp = int(time.time())
        self.user_email = f"onboarding.test.{timestamp}@aurumlife.com"
        
        user_data = {
            "email": self.user_email,
            "password": "TestPassword123!",
            "first_name": "Onboarding",
            "last_name": "Test",
            "username": f"onboarding_test_{timestamp}"
        }
        
        response, response_time = self.make_request('POST', '/auth/register', user_data)
        
        if response is None:
            self.log_result(
                "Create Fresh Account", 
                False, 
                "Network error during registration request",
                response_time
            )
            return False
            
        if response.status_code == 200:
            try:
                response_data = response.json()
                self.log_result(
                    "Create Fresh Account", 
                    True, 
                    f"Successfully created account for {self.user_email}. Response: {response_data}",
                    response_time
                )
                return True
            except json.JSONDecodeError:
                self.log_result(
                    "Create Fresh Account", 
                    False, 
                    f"Registration returned 200 but invalid JSON. Response text: {response.text[:200]}",
                    response_time
                )
                return False
        else:
            try:
                error_data = response.json()
                self.log_result(
                    "Create Fresh Account", 
                    False, 
                    f"Registration failed with status {response.status_code}. Error: {error_data}",
                    response_time
                )
            except json.JSONDecodeError:
                self.log_result(
                    "Create Fresh Account", 
                    False, 
                    f"Registration failed with status {response.status_code}. Response: {response.text[:200]}",
                    response_time
                )
            return False
            
    def test_2_login_user(self):
        """Step 2: Login via /api/auth/login"""
        if not self.user_email:
            self.log_result("Login User", False, "No user email available from registration")
            return False
            
        login_data = {
            "email": self.user_email,
            "password": "TestPassword123!"
        }
        
        response, response_time = self.make_request('POST', '/auth/login', login_data)
        
        if response is None:
            self.log_result("Login User", False, "Network error during login request", response_time)
            return False
            
        if response.status_code == 200:
            try:
                response_data = response.json()
                if 'access_token' in response_data:
                    self.access_token = response_data['access_token']
                    self.log_result(
                        "Login User", 
                        True, 
                        f"Successfully logged in. Token type: {response_data.get('token_type', 'unknown')}",
                        response_time
                    )
                    return True
                else:
                    self.log_result(
                        "Login User", 
                        False, 
                        f"Login successful but no access_token in response: {response_data}",
                        response_time
                    )
                    return False
            except json.JSONDecodeError:
                self.log_result(
                    "Login User", 
                    False, 
                    f"Login returned 200 but invalid JSON. Response: {response.text[:200]}",
                    response_time
                )
                return False
        else:
            try:
                error_data = response.json()
                self.log_result(
                    "Login User", 
                    False, 
                    f"Login failed with status {response.status_code}. Error: {error_data}",
                    response_time
                )
            except json.JSONDecodeError:
                self.log_result(
                    "Login User", 
                    False, 
                    f"Login failed with status {response.status_code}. Response: {response.text[:200]}",
                    response_time
                )
            return False
            
    def test_3_check_initial_onboarding_status(self):
        """Step 3: GET /api/auth/me -> expect has_completed_onboarding=false"""
        if not self.access_token:
            self.log_result("Check Initial Onboarding Status", False, "No access token available")
            return False
            
        response, response_time = self.make_request('GET', '/auth/me', auth_required=True)
        
        if response is None:
            self.log_result(
                "Check Initial Onboarding Status", 
                False, 
                "Network error during /auth/me request", 
                response_time
            )
            return False
            
        if response.status_code == 200:
            try:
                user_data = response.json()
                has_completed_onboarding = user_data.get('has_completed_onboarding')
                
                if has_completed_onboarding is False:
                    self.log_result(
                        "Check Initial Onboarding Status", 
                        True, 
                        f"Correct initial state: has_completed_onboarding=false. User data: {user_data}",
                        response_time
                    )
                    return True
                else:
                    self.log_result(
                        "Check Initial Onboarding Status", 
                        False, 
                        f"Expected has_completed_onboarding=false, got {has_completed_onboarding}. User data: {user_data}",
                        response_time
                    )
                    return False
            except json.JSONDecodeError:
                self.log_result(
                    "Check Initial Onboarding Status", 
                    False, 
                    f"/auth/me returned 200 but invalid JSON. Response: {response.text[:200]}",
                    response_time
                )
                return False
        else:
            try:
                error_data = response.json()
                self.log_result(
                    "Check Initial Onboarding Status", 
                    False, 
                    f"/auth/me failed with status {response.status_code}. Error: {error_data}",
                    response_time
                )
            except json.JSONDecodeError:
                self.log_result(
                    "Check Initial Onboarding Status", 
                    False, 
                    f"/auth/me failed with status {response.status_code}. Response: {response.text[:200]}",
                    response_time
                )
            return False
            
    def test_4_complete_onboarding(self):
        """Step 4: POST /api/auth/complete-onboarding"""
        if not self.access_token:
            self.log_result("Complete Onboarding", False, "No access token available")
            return False
            
        response, response_time = self.make_request('POST', '/auth/complete-onboarding', {}, auth_required=True)
        
        if response is None:
            self.log_result(
                "Complete Onboarding", 
                False, 
                "Network error during complete-onboarding request", 
                response_time
            )
            return False
            
        if response.status_code == 200:
            try:
                response_data = response.json()
                if response_data.get('has_completed_onboarding') is True:
                    self.log_result(
                        "Complete Onboarding", 
                        True, 
                        f"Successfully completed onboarding. Response: {response_data}",
                        response_time
                    )
                    return True
                else:
                    self.log_result(
                        "Complete Onboarding", 
                        False, 
                        f"Onboarding completion returned 200 but has_completed_onboarding not true: {response_data}",
                        response_time
                    )
                    return False
            except json.JSONDecodeError:
                self.log_result(
                    "Complete Onboarding", 
                    False, 
                    f"Complete onboarding returned 200 but invalid JSON. Response: {response.text[:200]}",
                    response_time
                )
                return False
        else:
            try:
                error_data = response.json()
                self.log_result(
                    "Complete Onboarding", 
                    False, 
                    f"Complete onboarding failed with status {response.status_code}. Error: {error_data}",
                    response_time
                )
            except json.JSONDecodeError:
                self.log_result(
                    "Complete Onboarding", 
                    False, 
                    f"Complete onboarding failed with status {response.status_code}. Response: {response.text[:200]}",
                    response_time
                )
            return False
            
    def test_5_verify_onboarding_completion(self):
        """Step 5: GET /api/auth/me -> expect has_completed_onboarding=true"""
        if not self.access_token:
            self.log_result("Verify Onboarding Completion", False, "No access token available")
            return False
            
        response, response_time = self.make_request('GET', '/auth/me', auth_required=True)
        
        if response is None:
            self.log_result(
                "Verify Onboarding Completion", 
                False, 
                "Network error during /auth/me verification request", 
                response_time
            )
            return False
            
        if response.status_code == 200:
            try:
                user_data = response.json()
                has_completed_onboarding = user_data.get('has_completed_onboarding')
                
                if has_completed_onboarding is True:
                    self.log_result(
                        "Verify Onboarding Completion", 
                        True, 
                        f"Correct final state: has_completed_onboarding=true. User data: {user_data}",
                        response_time
                    )
                    return True
                else:
                    self.log_result(
                        "Verify Onboarding Completion", 
                        False, 
                        f"Expected has_completed_onboarding=true, got {has_completed_onboarding}. User data: {user_data}",
                        response_time
                    )
                    return False
            except json.JSONDecodeError:
                self.log_result(
                    "Verify Onboarding Completion", 
                    False, 
                    f"/auth/me verification returned 200 but invalid JSON. Response: {response.text[:200]}",
                    response_time
                )
                return False
        else:
            try:
                error_data = response.json()
                self.log_result(
                    "Verify Onboarding Completion", 
                    False, 
                    f"/auth/me verification failed with status {response.status_code}. Error: {error_data}",
                    response_time
                )
            except json.JSONDecodeError:
                self.log_result(
                    "Verify Onboarding Completion", 
                    False, 
                    f"/auth/me verification failed with status {response.status_code}. Response: {response.text[:200]}",
                    response_time
                )
            return False
            
    def test_6_optional_seed_demo(self):
        """Step 6: Optionally, seed demo for this user size=light include_streak=false"""
        if not self.access_token:
            self.log_result("Optional Seed Demo", False, "No access token available")
            return False
            
        seed_data = {
            "size": "light",
            "include_streak": False
        }
        
        response, response_time = self.make_request('POST', '/admin/seed-demo', seed_data, auth_required=True)
        
        if response is None:
            self.log_result(
                "Optional Seed Demo", 
                False, 
                "Network error during seed-demo request", 
                response_time
            )
            return False
            
        if response.status_code == 200:
            try:
                response_data = response.json()
                self.log_result(
                    "Optional Seed Demo", 
                    True, 
                    f"Successfully seeded demo data. Response: {response_data}",
                    response_time
                )
                return True
            except json.JSONDecodeError:
                self.log_result(
                    "Optional Seed Demo", 
                    True, 
                    f"Seed demo returned 200. Response text: {response.text[:200]}",
                    response_time
                )
                return True
        else:
            try:
                error_data = response.json()
                # Seed demo is optional, so we'll log as warning but not fail
                self.log_result(
                    "Optional Seed Demo", 
                    False, 
                    f"Seed demo failed with status {response.status_code} (optional). Error: {error_data}",
                    response_time
                )
            except json.JSONDecodeError:
                self.log_result(
                    "Optional Seed Demo", 
                    False, 
                    f"Seed demo failed with status {response.status_code} (optional). Response: {response.text[:200]}",
                    response_time
                )
            return False
            
    def run_all_tests(self):
        """Run all onboarding backend tests in sequence"""
        print("🚀 STARTING BACKEND ONBOARDING ENDPOINT VALIDATION")
        print(f"Base URL: {BASE_URL}")
        print(f"Test started at: {datetime.now().isoformat()}")
        print("=" * 80)
        print()
        
        # Run tests in sequence
        tests = [
            self.test_1_create_fresh_account,
            self.test_2_login_user,
            self.test_3_check_initial_onboarding_status,
            self.test_4_complete_onboarding,
            self.test_5_verify_onboarding_completion,
            self.test_6_optional_seed_demo
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                self.log_result(
                    test_func.__name__, 
                    False, 
                    f"Test threw exception: {str(e)}"
                )
                
        # Print summary
        print("=" * 80)
        print("🎯 TEST SUMMARY")
        print(f"Tests passed: {passed_tests}/{total_tests}")
        print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"User email: {self.user_email}")
        print(f"Test completed at: {datetime.now().isoformat()}")
        
        if self.access_token:
            print(f"Access token available: Yes (length: {len(self.access_token)})")
        else:
            print("Access token available: No")
            
        print()
        print("📊 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            time_info = f" ({result['response_time']:.3f}s)" if result['response_time'] else ""
            print(f"{status} {result['test']}{time_info}")
            
        return passed_tests, total_tests

def main():
    """Main function to run the onboarding backend tests"""
    tester = OnboardingBackendTest()
    passed, total = tester.run_all_tests()
    
    # Exit with appropriate code
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - Onboarding endpoints working correctly!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total - passed} TEST(S) FAILED - Issues found in onboarding flow")
        sys.exit(1)

if __name__ == "__main__":
    main()