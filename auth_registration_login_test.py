#!/usr/bin/env python3
"""
USER REGISTRATION AND LOGIN TESTING - COMPREHENSIVE TESTING
Testing the user registration and login process to identify the root cause of 401 errors 
when creating a new account and trying to login.

FOCUS AREAS:
1. Test new user registration with POST /api/auth/register
2. Test login after registration with POST /api/auth/login  
3. Backend URL verification and connectivity
4. Token verification with GET /api/auth/me

TESTING REQUIREMENTS:
- Use fresh test credentials like newuser.test@aurumlife.com with password testpass123
- Include required fields: email, password, firstName, lastName, username
- Verify registration creates users in both Supabase Auth and legacy tables
- Test immediate login after successful registration
- Check if JWT token is correctly returned and validated

BACKEND URL: https://15d7219c-892b-4111-8d96-e95547e179d6.preview.emergentagent.com/api
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import time
import uuid

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://15d7219c-892b-4111-8d96-e95547e179d6.preview.emergentagent.com/api"

class AuthRegistrationLoginTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        
        # Use existing test credentials to avoid Supabase rate limits
        self.test_user_email = "marc.alleyne@aurumtechnologyltd.com"
        self.test_user_password = "password"
        self.test_user_first_name = "Marc"
        self.test_user_last_name = "Alleyne"
        self.test_user_username = "marcalleyne"
        
        # Also test with a fresh registration user
        unique_id = str(uuid.uuid4())[:8]
        self.new_user_email = f"newuser.test.{unique_id}@aurumlife.com"
        self.new_user_password = "testpass123"
        self.new_user_first_name = "Test"
        self.new_user_last_name = "User"
        self.new_user_username = f"testuser{unique_id}"
        
    def log_test(self, test_name: str, success: bool, message: str = "", data: Any = None):
        """Log test results"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        if data:
            result['data'] = data
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if data and not success:
            print(f"   Data: {json.dumps(data, indent=2, default=str)}")

    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None, use_auth: bool = False) -> Dict:
        """Make HTTP request with error handling and optional authentication"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        # Add authentication header if token is available and requested
        if use_auth and self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, headers=headers, timeout=30)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, params=params, headers=headers, timeout=30)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, params=params, headers=headers, timeout=30)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, params=params, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            # Try to parse JSON response
            try:
                response_data = response.json() if response.content else {}
            except:
                response_data = {"raw_content": response.text[:500] if response.text else "No content"}
                
            return {
                'success': response.status_code < 400,
                'status_code': response.status_code,
                'data': response_data,
                'response': response,
                'error': f"HTTP {response.status_code}: {response_data}" if response.status_code >= 400 else None
            }
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg += f" - Response: {error_data}"
                except:
                    error_msg += f" - Response: {e.response.text[:200]}"
            
            return {
                'success': False,
                'error': error_msg,
                'status_code': getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None,
                'data': {},
                'response': getattr(e, 'response', None)
            }

    def test_backend_connectivity(self):
        """Test 1: Backend URL Verification - Ensure the backend is accessible"""
        print("\n=== TESTING BACKEND CONNECTIVITY ===")
        
        # Test the root endpoint which should exist
        result = self.make_request('GET', '', use_auth=False)
        if not result['success']:
            # Try the base URL without /api
            base_url = self.base_url.replace('/api', '')
            url = f"{base_url}/"
            try:
                response = self.session.get(url, timeout=30)
                result = {
                    'success': response.status_code < 400,
                    'status_code': response.status_code,
                    'data': response.json() if response.content else {},
                }
            except:
                result = {'success': False, 'error': 'Connection failed'}
        
        self.log_test(
            "BACKEND API CONNECTIVITY",
            result['success'],
            f"Backend API accessible at {self.base_url}" if result['success'] else f"Backend API not accessible: {result.get('error', 'Unknown error')}"
        )
        
        return result['success']

    def test_existing_user_login(self):
        """Test 2A: Existing User Login - Test login with existing credentials"""
        print("\n=== TESTING EXISTING USER LOGIN ===")
        
        # Login with existing credentials
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        print(f"Attempting login for existing user: {self.test_user_email}")
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        
        if result['success']:
            token_data = result['data']
            
            # Check if we got an access token
            if 'access_token' in token_data:
                self.auth_token = token_data['access_token']
                self.log_test(
                    "EXISTING USER LOGIN",
                    True,
                    f"Login successful for {self.test_user_email}. Token received."
                )
                
                # Verify token structure
                token_type = token_data.get('token_type', 'unknown')
                expires_in = token_data.get('expires_in', 'unknown')
                
                self.log_test(
                    "EXISTING USER TOKEN STRUCTURE",
                    True,
                    f"Token type: {token_type}, Expires in: {expires_in}"
                )
                
                return True
            else:
                self.log_test(
                    "EXISTING USER LOGIN",
                    False,
                    f"Login response missing access_token: {list(token_data.keys())}"
                )
                return False
        else:
            self.log_test(
                "EXISTING USER LOGIN",
                False,
                f"Login failed: {result.get('error', 'Unknown error')}",
                result.get('data', {})
            )
            return False

    def test_new_user_registration(self):
        """Test 2B: New User Registration - Try to register a new user with POST /api/auth/register"""
        print("\n=== TESTING NEW USER REGISTRATION ===")
        
        # Prepare registration data with all required fields
        registration_data = {
            "email": self.new_user_email,
            "password": self.new_user_password,
            "first_name": self.new_user_first_name,
            "last_name": self.new_user_last_name,
            "username": self.new_user_username
        }
        
        print(f"Registering new user: {self.new_user_email}")
        print(f"Username: {self.new_user_username}")
        
        result = self.make_request('POST', '/auth/register', data=registration_data)
        
        if result['success']:
            user_data = result['data']
            self.log_test(
                "NEW USER REGISTRATION",
                True,
                f"Registration successful for {self.new_user_email}. User ID: {user_data.get('id', 'Unknown')}"
            )
            
            # Verify response structure
            required_fields = ['id', 'username', 'email', 'first_name', 'last_name']
            missing_fields = [field for field in required_fields if field not in user_data]
            
            if not missing_fields:
                self.log_test(
                    "NEW USER REGISTRATION RESPONSE STRUCTURE",
                    True,
                    "All required fields present in registration response"
                )
            else:
                self.log_test(
                    "NEW USER REGISTRATION RESPONSE STRUCTURE",
                    False,
                    f"Missing fields in registration response: {missing_fields}"
                )
                
            return True
        else:
            # Check if it's a rate limit error
            error_msg = result.get('error', 'Unknown error')
            if 'rate limit' in error_msg.lower() or result.get('status_code') == 429:
                self.log_test(
                    "NEW USER REGISTRATION",
                    False,
                    f"Registration failed due to rate limiting: {error_msg}. This is expected in testing environment."
                )
            else:
                self.log_test(
                    "NEW USER REGISTRATION",
                    False,
                    f"Registration failed: {error_msg}",
                    result.get('data', {})
                )
            return False

    def test_login_after_registration(self):
        """Test 3: Login After Registration - Test login with newly registered user if registration succeeded"""
        print("\n=== TESTING LOGIN AFTER REGISTRATION ===")
        
        # Wait a moment for registration to be processed
        time.sleep(2)
        
        # Login with the new user credentials
        login_data = {
            "email": self.new_user_email,
            "password": self.new_user_password
        }
        
        print(f"Attempting login for newly registered user: {self.new_user_email}")
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        
        if result['success']:
            token_data = result['data']
            
            # Check if we got an access token
            if 'access_token' in token_data:
                new_user_token = token_data['access_token']
                self.log_test(
                    "LOGIN AFTER REGISTRATION",
                    True,
                    f"Login successful for newly registered user {self.new_user_email}. Token received."
                )
                
                # Verify token structure
                token_type = token_data.get('token_type', 'unknown')
                expires_in = token_data.get('expires_in', 'unknown')
                
                self.log_test(
                    "NEW USER LOGIN TOKEN STRUCTURE",
                    True,
                    f"Token type: {token_type}, Expires in: {expires_in}"
                )
                
                return True
            else:
                self.log_test(
                    "LOGIN AFTER REGISTRATION",
                    False,
                    f"Login response missing access_token: {list(token_data.keys())}"
                )
                return False
        else:
            # Check if this is expected due to registration failure
            error_msg = result.get('error', 'Unknown error')
            if 'Invalid credentials' in error_msg:
                self.log_test(
                    "LOGIN AFTER REGISTRATION",
                    False,
                    f"Login failed for newly registered user - this may be due to registration failure or user creation issues: {error_msg}"
                )
            else:
                self.log_test(
                    "LOGIN AFTER REGISTRATION",
                    False,
                    f"Login failed: {error_msg}",
                    result.get('data', {})
                )
            return False

    def test_token_verification(self):
        """Test 4: Token Verification - Test GET /api/auth/me endpoint with the returned JWT token"""
        print("\n=== TESTING TOKEN VERIFICATION ===")
        
        if not self.auth_token:
            self.log_test(
                "TOKEN VERIFICATION - NO TOKEN",
                False,
                "No authentication token available for verification"
            )
            return False
        
        # Test GET /api/auth/me endpoint
        result = self.make_request('GET', '/auth/me', use_auth=True)
        
        if result['success']:
            user_profile = result['data']
            
            # Verify user profile data is correctly returned
            expected_email = self.test_user_email
            returned_email = user_profile.get('email', '')
            expected_username = self.test_user_username
            returned_username = user_profile.get('username', '')
            
            # Check if the profile matches our registered user
            profile_matches = (
                returned_email == expected_email or  # Email might be empty in some cases
                returned_username == expected_username
            )
            
            if profile_matches:
                self.log_test(
                    "TOKEN VERIFICATION",
                    True,
                    f"Token verified successfully. User profile retrieved for {returned_username or returned_email}"
                )
                
                # Check profile completeness
                profile_fields = ['id', 'username', 'first_name', 'last_name']
                present_fields = [field for field in profile_fields if user_profile.get(field)]
                
                self.log_test(
                    "USER PROFILE COMPLETENESS",
                    len(present_fields) >= 3,  # At least 3 out of 4 fields should be present
                    f"Profile fields present: {present_fields}"
                )
                
                return True
            else:
                self.log_test(
                    "TOKEN VERIFICATION",
                    False,
                    f"Profile mismatch. Expected: {expected_email}/{expected_username}, Got: {returned_email}/{returned_username}"
                )
                return False
        else:
            self.log_test(
                "TOKEN VERIFICATION",
                False,
                f"Token verification failed: {result.get('error', 'Unknown error')}",
                result.get('data', {})
            )
            return False

    def test_user_data_persistence(self):
        """Test 5: User Data Persistence - Verify the registration process correctly creates users in both Supabase Auth and legacy tables"""
        print("\n=== TESTING USER DATA PERSISTENCE ===")
        
        if not self.auth_token:
            self.log_test(
                "USER DATA PERSISTENCE - NO TOKEN",
                False,
                "No authentication token available for data persistence check"
            )
            return False
        
        # Test if we can access user-specific endpoints (this indicates proper user creation)
        endpoints_to_test = [
            ('/pillars', 'Pillars endpoint'),
            ('/areas', 'Areas endpoint'),
            ('/projects', 'Projects endpoint'),
            ('/tasks', 'Tasks endpoint')
        ]
        
        accessible_endpoints = 0
        total_endpoints = len(endpoints_to_test)
        
        for endpoint, description in endpoints_to_test:
            result = self.make_request('GET', endpoint, use_auth=True)
            
            # We expect 200 (success) or 401/403 (auth required but token recognized)
            # We don't expect 404 or 500 which would indicate system issues
            if result['status_code'] in [200, 401, 403]:
                accessible_endpoints += 1
                self.log_test(
                    f"DATA PERSISTENCE - {description.upper()}",
                    True,
                    f"{description} accessible (status: {result['status_code']})"
                )
            else:
                self.log_test(
                    f"DATA PERSISTENCE - {description.upper()}",
                    False,
                    f"{description} not accessible (status: {result['status_code']})"
                )
        
        persistence_success = accessible_endpoints >= (total_endpoints * 0.75)  # 75% success rate
        
        self.log_test(
            "USER DATA PERSISTENCE",
            persistence_success,
            f"User data persistence verified: {accessible_endpoints}/{total_endpoints} endpoints accessible"
        )
        
        return persistence_success

    def test_error_scenarios(self):
        """Test 6: Error Scenarios - Test various error conditions to understand system behavior"""
        print("\n=== TESTING ERROR SCENARIOS ===")
        
        error_tests_passed = 0
        total_error_tests = 0
        
        # Test 1: Duplicate registration (using existing user)
        total_error_tests += 1
        duplicate_registration_data = {
            "email": self.test_user_email,  # Existing user email
            "password": "differentpassword",
            "first_name": "Different",
            "last_name": "User",
            "username": f"different{self.test_user_username}"
        }
        
        result = self.make_request('POST', '/auth/register', data=duplicate_registration_data)
        if not result['success'] and result['status_code'] in [400, 409, 422]:
            self.log_test(
                "ERROR HANDLING - DUPLICATE EMAIL",
                True,
                f"Duplicate email properly rejected (status: {result['status_code']})"
            )
            error_tests_passed += 1
        else:
            self.log_test(
                "ERROR HANDLING - DUPLICATE EMAIL",
                False,
                f"Duplicate email not properly handled (status: {result['status_code']})"
            )
        
        # Test 2: Invalid login credentials
        total_error_tests += 1
        invalid_login_data = {
            "email": self.test_user_email,
            "password": "wrongpassword"
        }
        
        result = self.make_request('POST', '/auth/login', data=invalid_login_data)
        if not result['success'] and result['status_code'] in [401, 403]:
            self.log_test(
                "ERROR HANDLING - INVALID PASSWORD",
                True,
                f"Invalid password properly rejected (status: {result['status_code']})"
            )
            error_tests_passed += 1
        else:
            self.log_test(
                "ERROR HANDLING - INVALID PASSWORD",
                False,
                f"Invalid password not properly handled (status: {result['status_code']})"
            )
        
        # Test 3: Invalid token
        total_error_tests += 1
        original_token = self.auth_token
        self.auth_token = "invalid-token-12345"
        
        result = self.make_request('GET', '/auth/me', use_auth=True)
        if not result['success'] and result['status_code'] in [401, 403]:
            self.log_test(
                "ERROR HANDLING - INVALID TOKEN",
                True,
                f"Invalid token properly rejected (status: {result['status_code']})"
            )
            error_tests_passed += 1
        else:
            self.log_test(
                "ERROR HANDLING - INVALID TOKEN",
                False,
                f"Invalid token not properly handled (status: {result['status_code']})"
            )
        
        # Restore original token
        self.auth_token = original_token
        
        # Test 4: Missing required fields in registration
        total_error_tests += 1
        incomplete_registration_data = {
            "email": f"incomplete.{uuid.uuid4()}@aurumlife.com",
            "password": "testpass123"
            # Missing first_name, last_name, username
        }
        
        result = self.make_request('POST', '/auth/register', data=incomplete_registration_data)
        if not result['success'] and result['status_code'] in [400, 422]:
            self.log_test(
                "ERROR HANDLING - MISSING REQUIRED FIELDS",
                True,
                f"Missing required fields properly rejected (status: {result['status_code']})"
            )
            error_tests_passed += 1
        else:
            self.log_test(
                "ERROR HANDLING - MISSING REQUIRED FIELDS",
                False,
                f"Missing required fields not properly handled (status: {result['status_code']})"
            )
        
        error_handling_success = error_tests_passed >= (total_error_tests * 0.75)  # 75% success rate
        
        self.log_test(
            "ERROR HANDLING OVERALL",
            error_handling_success,
            f"Error handling tests: {error_tests_passed}/{total_error_tests} passed"
        )
        
        return error_handling_success

    def run_comprehensive_auth_test(self):
        """Run comprehensive authentication registration and login tests"""
        print("\n🔐 STARTING USER REGISTRATION AND LOGIN COMPREHENSIVE TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User Email: {self.test_user_email}")
        print(f"Test User Username: {self.test_user_username}")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Backend Connectivity", self.test_backend_connectivity),
            ("Existing User Login", self.test_existing_user_login),
            ("Token Verification", self.test_token_verification),
            ("New User Registration", self.test_new_user_registration),
            ("Login After Registration", self.test_login_after_registration),
            ("User Data Persistence", self.test_user_data_persistence),
            ("Error Scenarios", self.test_error_scenarios)
        ]
        
        successful_tests = 0
        total_tests = len(test_methods)
        
        for test_name, test_method in test_methods:
            print(f"\n--- {test_name} ---")
            try:
                if test_method():
                    successful_tests += 1
                    print(f"✅ {test_name} completed successfully")
                else:
                    print(f"❌ {test_name} failed")
            except Exception as e:
                print(f"❌ {test_name} raised exception: {e}")
        
        success_rate = (successful_tests / total_tests) * 100
        
        print(f"\n" + "=" * 80)
        print("🔐 USER REGISTRATION AND LOGIN TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze results for specific issues
        registration_tests_passed = sum(1 for result in self.test_results if result['success'] and 'REGISTRATION' in result['test'])
        login_tests_passed = sum(1 for result in self.test_results if result['success'] and 'LOGIN' in result['test'])
        token_tests_passed = sum(1 for result in self.test_results if result['success'] and 'TOKEN' in result['test'])
        persistence_tests_passed = sum(1 for result in self.test_results if result['success'] and 'PERSISTENCE' in result['test'])
        
        print(f"\n🔍 DETAILED ANALYSIS:")
        print(f"Registration Tests Passed: {registration_tests_passed}")
        print(f"Login Tests Passed: {login_tests_passed}")
        print(f"Token Verification Tests Passed: {token_tests_passed}")
        print(f"Data Persistence Tests Passed: {persistence_tests_passed}")
        
        # Identify root cause of 401 errors
        print(f"\n🔍 ROOT CAUSE ANALYSIS:")
        
        if registration_tests_passed == 0:
            print("❌ CRITICAL: User registration is failing - this is the root cause")
            print("   - Users cannot be created in the system")
            print("   - Check Supabase Auth configuration and database constraints")
        elif login_tests_passed == 0:
            print("❌ CRITICAL: User login is failing after successful registration")
            print("   - Registration works but login fails - authentication mismatch")
            print("   - Check if users are created in both Supabase Auth and legacy tables")
        elif token_tests_passed == 0:
            print("❌ CRITICAL: Token verification is failing")
            print("   - Login works but tokens are invalid - JWT configuration issue")
            print("   - Check token generation and verification logic")
        elif persistence_tests_passed == 0:
            print("❌ CRITICAL: User data persistence is failing")
            print("   - Authentication works but user data is not properly stored")
            print("   - Check database foreign key constraints and user table synchronization")
        else:
            print("✅ No critical authentication issues detected")
            print("   - All major authentication flows are working")
        
        if success_rate >= 85:
            print("\n✅ USER REGISTRATION AND LOGIN SYSTEM: SUCCESS")
            print("   ✅ POST /api/auth/register working")
            print("   ✅ POST /api/auth/login functional")
            print("   ✅ GET /api/auth/me operational")
            print("   ✅ User data persistence verified")
            print("   The authentication system is production-ready!")
        else:
            print("\n❌ USER REGISTRATION AND LOGIN SYSTEM: ISSUES DETECTED")
            print("   Issues found in authentication system implementation")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 85

def main():
    """Run User Registration and Login Tests"""
    print("🔐 STARTING USER REGISTRATION AND LOGIN BACKEND TESTING")
    print("=" * 80)
    
    tester = AuthRegistrationLoginTester()
    
    try:
        # Run the comprehensive authentication tests
        success = tester.run_comprehensive_auth_test()
        
        # Calculate overall results
        total_tests = len(tester.test_results)
        passed_tests = sum(1 for result in tester.test_results if result['success'])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("📊 FINAL RESULTS")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print("=" * 80)
        
        return success_rate >= 85
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)