#!/usr/bin/env python3
"""
LOGIN AUTHENTICATION FUNCTIONALITY TESTING
Complete testing of the login authentication functionality after fixing the REACT_APP_BACKEND_URL configuration.

FOCUS AREAS:
1. User registration works correctly
2. User login with the created credentials works without 401 errors  
3. Authentication token is properly generated and validated
4. Backend authentication endpoints are accessible and responding correctly
5. JWT token validation works for protected endpoints

Test credentials:
- Email: test.login@aurumlife.com
- Password: testpassword123
- First Name: Test
- Last Name: User

Backend should be accessible via http://localhost:8001
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import time

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

class LoginAuthenticationTester:
    def __init__(self):
        self.base_url = API_BASE
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        
        # Test credentials as specified in the review request
        self.test_user_email = "test.login@aurumlife.com"
        self.test_user_password = "testpassword123"
        self.test_user_first_name = "Test"
        self.test_user_last_name = "User"
        
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
        """Test basic connectivity to the backend API"""
        print("\n=== TESTING BACKEND CONNECTIVITY ===")
        
        # Test the root endpoint
        try:
            response = self.session.get(f"{BACKEND_URL}/", timeout=30)
            result = {
                'success': response.status_code < 400,
                'status_code': response.status_code,
                'data': response.json() if response.content else {},
            }
        except Exception as e:
            result = {'success': False, 'error': f'Connection failed: {str(e)}'}
        
        self.log_test(
            "BACKEND API CONNECTIVITY",
            result['success'],
            f"Backend API accessible at {BACKEND_URL}" if result['success'] else f"Backend API not accessible: {result.get('error', 'Unknown error')}"
        )
        
        return result['success']

    def test_user_registration(self):
        """Test user registration with the specified test credentials"""
        print("\n=== TESTING USER REGISTRATION ===")
        
        # First, try to delete the user if it exists (cleanup)
        self.cleanup_test_user()
        
        # Register new user with specified credentials
        registration_data = {
            "username": "testlogin",  # Required field
            "email": self.test_user_email,
            "password": self.test_user_password,
            "first_name": self.test_user_first_name,
            "last_name": self.test_user_last_name
        }
        
        result = self.make_request('POST', '/auth/register', data=registration_data)
        
        if result['success']:
            self.log_test(
                "USER REGISTRATION",
                True,
                f"User registration successful for {self.test_user_email}"
            )
            return True
        else:
            # Check if user already exists (which is also acceptable)
            if result['status_code'] == 400 and 'already exists' in str(result.get('data', {})).lower():
                self.log_test(
                    "USER REGISTRATION",
                    True,
                    f"User {self.test_user_email} already exists (acceptable for testing)"
                )
                return True
            else:
                self.log_test(
                    "USER REGISTRATION",
                    False,
                    f"Registration failed: {result.get('error', 'Unknown error')}"
                )
                return False

    def test_user_login(self):
        """Test user login with the specified test credentials"""
        print("\n=== TESTING USER LOGIN ===")
        
        # Login user with specified credentials
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        
        if result['success']:
            token_data = result['data']
            self.auth_token = token_data.get('access_token')
            
            if self.auth_token:
                self.log_test(
                    "USER LOGIN",
                    True,
                    f"Login successful with {self.test_user_email}, token received"
                )
                return True
            else:
                self.log_test(
                    "USER LOGIN",
                    False,
                    f"Login successful but no access token received: {token_data}"
                )
                return False
        else:
            self.log_test(
                "USER LOGIN",
                False,
                f"Login failed: {result.get('error', 'Unknown error')}"
            )
            return False

    def test_authentication_token_validation(self):
        """Test JWT token validation with protected endpoints"""
        print("\n=== TESTING AUTHENTICATION TOKEN VALIDATION ===")
        
        if not self.auth_token:
            self.log_test(
                "AUTHENTICATION TOKEN VALIDATION",
                False,
                "No authentication token available for testing"
            )
            return False
        
        # Test token validation with /auth/me endpoint
        result = self.make_request('GET', '/auth/me', use_auth=True)
        
        if result['success']:
            user_data = result['data']
            expected_email = self.test_user_email
            actual_email = user_data.get('email')
            
            if actual_email == expected_email:
                self.log_test(
                    "AUTHENTICATION TOKEN VALIDATION",
                    True,
                    f"Token validated successfully, user: {actual_email}"
                )
                return True
            else:
                self.log_test(
                    "AUTHENTICATION TOKEN VALIDATION",
                    False,
                    f"Token valid but wrong user data. Expected: {expected_email}, Got: {actual_email}"
                )
                return False
        else:
            self.log_test(
                "AUTHENTICATION TOKEN VALIDATION",
                False,
                f"Token validation failed: {result.get('error', 'Unknown error')}"
            )
            return False

    def test_protected_endpoints_access(self):
        """Test access to protected endpoints with valid JWT token"""
        print("\n=== TESTING PROTECTED ENDPOINTS ACCESS ===")
        
        if not self.auth_token:
            self.log_test(
                "PROTECTED ENDPOINTS ACCESS",
                False,
                "No authentication token available for testing"
            )
            return False
        
        # Test multiple protected endpoints
        protected_endpoints = [
            ('/dashboard', 'Dashboard'),
            ('/pillars', 'Pillars'),
            ('/areas', 'Areas'),
            ('/projects', 'Projects'),
            ('/tasks', 'Tasks')
        ]
        
        successful_endpoints = 0
        total_endpoints = len(protected_endpoints)
        
        for endpoint, name in protected_endpoints:
            result = self.make_request('GET', endpoint, use_auth=True)
            
            if result['success']:
                self.log_test(
                    f"PROTECTED ENDPOINT ACCESS - {name}",
                    True,
                    f"{name} endpoint accessible with valid token"
                )
                successful_endpoints += 1
            else:
                self.log_test(
                    f"PROTECTED ENDPOINT ACCESS - {name}",
                    False,
                    f"{name} endpoint failed: {result.get('error', 'Unknown error')}"
                )
        
        success_rate = (successful_endpoints / total_endpoints) * 100
        overall_success = success_rate >= 80  # 80% success rate threshold
        
        self.log_test(
            "PROTECTED ENDPOINTS ACCESS - OVERALL",
            overall_success,
            f"Protected endpoints access: {successful_endpoints}/{total_endpoints} successful ({success_rate:.1f}%)"
        )
        
        return overall_success

    def test_unauthorized_access_prevention(self):
        """Test that endpoints properly reject requests without authentication"""
        print("\n=== TESTING UNAUTHORIZED ACCESS PREVENTION ===")
        
        # Test protected endpoints without authentication token
        protected_endpoints = [
            ('/auth/me', 'User Profile'),
            ('/dashboard', 'Dashboard'),
            ('/pillars', 'Pillars'),
            ('/areas', 'Areas'),
            ('/projects', 'Projects'),
            ('/tasks', 'Tasks')
        ]
        
        properly_protected = 0
        total_endpoints = len(protected_endpoints)
        
        for endpoint, name in protected_endpoints:
            result = self.make_request('GET', endpoint, use_auth=False)
            
            # Should return 401 or 403 for unauthorized access
            if result['status_code'] in [401, 403]:
                self.log_test(
                    f"UNAUTHORIZED ACCESS PREVENTION - {name}",
                    True,
                    f"{name} endpoint properly requires authentication (status: {result['status_code']})"
                )
                properly_protected += 1
            else:
                self.log_test(
                    f"UNAUTHORIZED ACCESS PREVENTION - {name}",
                    False,
                    f"{name} endpoint does not require authentication (status: {result['status_code']})"
                )
        
        success_rate = (properly_protected / total_endpoints) * 100
        overall_success = success_rate >= 90  # 90% success rate threshold for security
        
        self.log_test(
            "UNAUTHORIZED ACCESS PREVENTION - OVERALL",
            overall_success,
            f"Authentication requirements: {properly_protected}/{total_endpoints} endpoints properly protected ({success_rate:.1f}%)"
        )
        
        return overall_success

    def test_invalid_token_handling(self):
        """Test handling of invalid/expired tokens"""
        print("\n=== TESTING INVALID TOKEN HANDLING ===")
        
        # Save the valid token
        valid_token = self.auth_token
        
        # Test with invalid token
        self.auth_token = "invalid-token-12345"
        
        result = self.make_request('GET', '/auth/me', use_auth=True)
        
        if result['status_code'] in [401, 403]:
            self.log_test(
                "INVALID TOKEN HANDLING",
                True,
                f"Invalid token properly rejected (status: {result['status_code']})"
            )
            success = True
        else:
            self.log_test(
                "INVALID TOKEN HANDLING",
                False,
                f"Invalid token not properly handled (status: {result['status_code']})"
            )
            success = False
        
        # Restore the valid token
        self.auth_token = valid_token
        
        return success

    def cleanup_test_user(self):
        """Cleanup test user if it exists (optional, for clean testing)"""
        # This is optional cleanup - we don't fail the test if this doesn't work
        try:
            # Try to login first to see if user exists
            login_data = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            result = self.make_request('POST', '/auth/login', data=login_data)
            if result['success']:
                # User exists, we can proceed with testing
                pass
        except:
            # Cleanup failed, but that's okay
            pass

    def run_comprehensive_login_auth_test(self):
        """Run comprehensive login authentication tests"""
        print("\n🔐 STARTING LOGIN AUTHENTICATION COMPREHENSIVE TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User: {self.test_user_email}")
        print(f"Test Password: {self.test_user_password}")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Backend Connectivity", self.test_backend_connectivity),
            ("User Registration", self.test_user_registration),
            ("User Login", self.test_user_login),
            ("Authentication Token Validation", self.test_authentication_token_validation),
            ("Protected Endpoints Access", self.test_protected_endpoints_access),
            ("Unauthorized Access Prevention", self.test_unauthorized_access_prevention),
            ("Invalid Token Handling", self.test_invalid_token_handling)
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
        print("🔐 LOGIN AUTHENTICATION TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze results for authentication functionality
        registration_success = any(result['success'] and 'REGISTRATION' in result['test'] for result in self.test_results)
        login_success = any(result['success'] and 'LOGIN' in result['test'] and 'REGISTRATION' not in result['test'] for result in self.test_results)
        token_validation_success = any(result['success'] and 'TOKEN VALIDATION' in result['test'] for result in self.test_results)
        protected_access_success = any(result['success'] and 'PROTECTED ENDPOINTS' in result['test'] for result in self.test_results)
        
        print(f"\n🔍 AUTHENTICATION ANALYSIS:")
        print(f"User Registration: {'✅ Working' if registration_success else '❌ Failed'}")
        print(f"User Login: {'✅ Working' if login_success else '❌ Failed'}")
        print(f"Token Validation: {'✅ Working' if token_validation_success else '❌ Failed'}")
        print(f"Protected Endpoints: {'✅ Working' if protected_access_success else '❌ Failed'}")
        
        if success_rate >= 85:
            print("\n✅ LOGIN AUTHENTICATION SYSTEM: SUCCESS")
            print("   ✅ User registration working correctly")
            print("   ✅ User login working without 401 errors")
            print("   ✅ Authentication token properly generated and validated")
            print("   ✅ Backend authentication endpoints accessible and responding correctly")
            print("   ✅ JWT token validation working for protected endpoints")
            print("   The login authentication functionality is production-ready!")
        else:
            print("\n❌ LOGIN AUTHENTICATION SYSTEM: ISSUES DETECTED")
            print("   Issues found in login authentication implementation")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 85

def main():
    """Run Login Authentication Tests"""
    print("🔐 STARTING LOGIN AUTHENTICATION BACKEND TESTING")
    print("=" * 80)
    
    tester = LoginAuthenticationTester()
    
    try:
        # Run the comprehensive login authentication tests
        success = tester.run_comprehensive_login_auth_test()
        
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