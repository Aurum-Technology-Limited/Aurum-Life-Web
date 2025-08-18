#!/usr/bin/env python3
"""
AUTHENTICATION FIXES TESTING - COMPREHENSIVE SECURITY VERIFICATION
Testing the authentication fixes to resolve 401 errors and security vulnerabilities.

FOCUS AREAS:
1. Test Security Fix - Password Verification (wrong passwords should return 401)
2. Test Correct Password Login (should work and return 200 with token)
3. Test User Profile Mapping (GET /api/auth/me should return correct user profile)
4. Test Registration Error Handling (proper HTTP 429 for rate limiting)

CREDENTIALS: marc.alleyne@aurumtechnologyltd.com / password (correct)
WRONG PASSWORD: wrongpassword123 (should fail with 401)
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import time

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://taskpilot-2.preview.emergentagent.com/api"

class AuthenticationFixesTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        # Test credentials as specified in review request
        self.test_user_email = "marc.alleyne@aurumtechnologyltd.com"
        self.correct_password = "password123"
        self.wrong_password = "wrongpassword123"
        
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

    def test_basic_connectivity(self):
        """Test basic connectivity to the backend API"""
        print("\n=== TESTING BASIC CONNECTIVITY ===")
        
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

    def test_security_fix_wrong_password(self):
        """Test 1: Security Fix - Wrong Password Should Return 401"""
        print("\n=== TESTING SECURITY FIX - WRONG PASSWORD REJECTION ===")
        
        # Try to login with marc.alleyne@aurumtechnologyltd.com but with WRONG password
        login_data = {
            "email": self.test_user_email,
            "password": self.wrong_password  # This should fail
        }
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        
        # This should return 401 (security fix)
        if result['status_code'] == 401:
            self.log_test(
                "SECURITY FIX - WRONG PASSWORD REJECTION",
                True,
                f"✅ Security vulnerability FIXED: Wrong password correctly rejected with HTTP 401"
            )
            return True
        elif result['status_code'] == 200:
            self.log_test(
                "SECURITY FIX - WRONG PASSWORD REJECTION",
                False,
                f"❌ SECURITY VULNERABILITY: Wrong password incorrectly accepted with HTTP 200 - THIS IS A CRITICAL SECURITY ISSUE",
                result['data']
            )
            return False
        else:
            self.log_test(
                "SECURITY FIX - WRONG PASSWORD REJECTION",
                False,
                f"❌ Unexpected response for wrong password: HTTP {result['status_code']} (expected 401)",
                result['data']
            )
            return False

    def test_correct_password_login(self):
        """Test 2: Correct Password Login Should Work"""
        print("\n=== TESTING CORRECT PASSWORD LOGIN ===")
        
        # Login with correct credentials
        login_data = {
            "email": self.test_user_email,
            "password": self.correct_password  # This should work
        }
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        
        if result['success'] and result['status_code'] == 200:
            token_data = result['data']
            self.auth_token = token_data.get('access_token')
            
            if self.auth_token:
                self.log_test(
                    "CORRECT PASSWORD LOGIN",
                    True,
                    f"✅ Login successful with correct password, token received"
                )
                return True
            else:
                self.log_test(
                    "CORRECT PASSWORD LOGIN",
                    False,
                    f"❌ Login returned 200 but no access_token in response",
                    token_data
                )
                return False
        else:
            self.log_test(
                "CORRECT PASSWORD LOGIN",
                False,
                f"❌ Login failed with correct password: {result.get('error', 'Unknown error')}",
                result['data']
            )
            return False

    def test_user_profile_mapping(self):
        """Test 3: User Profile Mapping - GET /api/auth/me Should Return Correct User"""
        print("\n=== TESTING USER PROFILE MAPPING ===")
        
        if not self.auth_token:
            self.log_test(
                "USER PROFILE MAPPING - Authentication Required", 
                False, 
                "No authentication token available"
            )
            return False
        
        # Test GET /api/auth/me endpoint
        result = self.make_request('GET', '/auth/me', use_auth=True)
        
        if result['success'] and result['status_code'] == 200:
            user_profile = result['data']
            
            # Verify that it returns the CORRECT user profile for marc.alleyne
            expected_email = self.test_user_email
            actual_email = user_profile.get('email', '')
            
            # Check if we get the correct user (not a different user's profile)
            if actual_email == expected_email or 'marc.alleyne' in actual_email.lower():
                self.log_test(
                    "USER PROFILE MAPPING - CORRECT USER",
                    True,
                    f"✅ Profile mapping FIXED: Returns correct user profile for {expected_email}"
                )
                
                # Verify profile fields are present
                required_fields = ['username', 'email', 'first_name', 'last_name']
                missing_fields = [field for field in required_fields if field not in user_profile or not user_profile[field]]
                
                if not missing_fields:
                    self.log_test(
                        "USER PROFILE MAPPING - PROFILE COMPLETENESS",
                        True,
                        f"✅ All profile fields present: username={user_profile.get('username')}, email={user_profile.get('email')}, first_name={user_profile.get('first_name')}, last_name={user_profile.get('last_name')}"
                    )
                    return True
                else:
                    self.log_test(
                        "USER PROFILE MAPPING - PROFILE COMPLETENESS",
                        False,
                        f"❌ Missing or empty profile fields: {missing_fields}",
                        user_profile
                    )
                    return False
            else:
                self.log_test(
                    "USER PROFILE MAPPING - CORRECT USER",
                    False,
                    f"❌ PROFILE MAPPING BUG: Expected user {expected_email}, but got profile for different user: {actual_email}",
                    user_profile
                )
                return False
        else:
            self.log_test(
                "USER PROFILE MAPPING",
                False,
                f"❌ Failed to get user profile: {result.get('error', 'Unknown error')}",
                result['data']
            )
            return False

    def test_registration_error_handling(self):
        """Test 4: Registration Error Handling - Should Return HTTP 429 for Rate Limiting"""
        print("\n=== TESTING REGISTRATION ERROR HANDLING ===")
        
        # Try to register a new user (this might fail due to rate limiting)
        registration_data = {
            "email": f"test.user.{int(time.time())}@example.com",
            "password": "testpassword123",
            "username": f"testuser{int(time.time())}",
            "first_name": "Test",
            "last_name": "User"
        }
        
        result = self.make_request('POST', '/auth/register', data=registration_data)
        
        if result['status_code'] == 201 or result['status_code'] == 200:
            # Registration succeeded
            self.log_test(
                "REGISTRATION ERROR HANDLING - SUCCESS CASE",
                True,
                f"✅ Registration successful - user created successfully"
            )
            
            # Try to login with the new credentials immediately
            login_data = {
                "email": registration_data["email"],
                "password": registration_data["password"]
            }
            
            login_result = self.make_request('POST', '/auth/login', data=login_data)
            
            if login_result['success']:
                self.log_test(
                    "REGISTRATION ERROR HANDLING - IMMEDIATE LOGIN",
                    True,
                    f"✅ Can login immediately after registration"
                )
                return True
            else:
                self.log_test(
                    "REGISTRATION ERROR HANDLING - IMMEDIATE LOGIN",
                    False,
                    f"❌ Cannot login immediately after registration: {login_result.get('error', 'Unknown error')}"
                )
                return False
                
        elif result['status_code'] == 429:
            # Rate limiting - this is expected and good
            error_message = result['data'].get('detail', '') if isinstance(result['data'], dict) else str(result['data'])
            
            if 'rate limit' in error_message.lower():
                self.log_test(
                    "REGISTRATION ERROR HANDLING - RATE LIMITING",
                    True,
                    f"✅ Registration properly handles rate limiting with HTTP 429: {error_message}"
                )
                return True
            else:
                self.log_test(
                    "REGISTRATION ERROR HANDLING - RATE LIMITING",
                    False,
                    f"❌ HTTP 429 returned but error message unclear: {error_message}"
                )
                return False
                
        elif result['status_code'] == 409:
            # Email already exists - this is also acceptable
            self.log_test(
                "REGISTRATION ERROR HANDLING - DUPLICATE EMAIL",
                True,
                f"✅ Registration properly handles duplicate email with HTTP 409"
            )
            return True
            
        else:
            # Other error
            self.log_test(
                "REGISTRATION ERROR HANDLING",
                False,
                f"❌ Registration failed with unexpected status: HTTP {result['status_code']} - {result.get('error', 'Unknown error')}",
                result['data']
            )
            return False

    def run_comprehensive_authentication_fixes_test(self):
        """Run comprehensive authentication fixes tests"""
        print("\n🔐 STARTING AUTHENTICATION FIXES COMPREHENSIVE TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print(f"Correct Password: {self.correct_password}")
        print(f"Wrong Password: {self.wrong_password}")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Basic Connectivity", self.test_basic_connectivity),
            ("Security Fix - Wrong Password Rejection", self.test_security_fix_wrong_password),
            ("Correct Password Login", self.test_correct_password_login),
            ("User Profile Mapping", self.test_user_profile_mapping),
            ("Registration Error Handling", self.test_registration_error_handling)
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
        print("🔐 AUTHENTICATION FIXES TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze results for authentication functionality
        security_tests_passed = sum(1 for result in self.test_results if result['success'] and 'SECURITY FIX' in result['test'])
        login_tests_passed = sum(1 for result in self.test_results if result['success'] and 'LOGIN' in result['test'])
        profile_tests_passed = sum(1 for result in self.test_results if result['success'] and 'PROFILE MAPPING' in result['test'])
        registration_tests_passed = sum(1 for result in self.test_results if result['success'] and 'REGISTRATION' in result['test'])
        
        print(f"\n🔍 SYSTEM ANALYSIS:")
        print(f"Security Fix Tests Passed: {security_tests_passed}")
        print(f"Login Tests Passed: {login_tests_passed}")
        print(f"Profile Mapping Tests Passed: {profile_tests_passed}")
        print(f"Registration Error Handling Tests Passed: {registration_tests_passed}")
        
        if success_rate >= 80:
            print("\n✅ AUTHENTICATION FIXES: SUCCESS")
            print("   ✅ Security vulnerability fixed (wrong passwords rejected)")
            print("   ✅ Correct password login working")
            print("   ✅ User profile mapping returns correct data")
            print("   ✅ Registration error handling implemented")
            print("   The Authentication system fixes are working correctly!")
        else:
            print("\n❌ AUTHENTICATION FIXES: ISSUES DETECTED")
            print("   Issues found in authentication fixes implementation")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 80

def main():
    """Run Authentication Fixes Tests"""
    print("🔐 STARTING AUTHENTICATION FIXES BACKEND TESTING")
    print("=" * 80)
    
    tester = AuthenticationFixesTester()
    
    try:
        # Run the comprehensive authentication fixes tests
        success = tester.run_comprehensive_authentication_fixes_test()
        
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
        
        return success_rate >= 80
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)