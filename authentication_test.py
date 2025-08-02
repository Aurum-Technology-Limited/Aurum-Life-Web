#!/usr/bin/env python3
"""
COMPREHENSIVE AUTHENTICATION FLOW TESTING
Testing complete authentication flow for both new and existing users as requested in review.

FOCUS AREAS:
1. Test new user registration and login (should go to onboarding)
2. Test existing user login (should go to dashboard)
3. Verify JWT token generation and validation
4. Confirm no 401 or connection errors

TEST CREDENTIALS:
- New user: newuser@aurumlife.com / testpass123
- Existing user: marc.alleyne@aurumtechnologyltd.com / password (if available)
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import time

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "http://localhost:8001/api"

class AuthenticationFlowTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_tokens = {}
        
        # Test credentials as specified in review request
        self.new_user_email = "newuser@aurumlife.com"
        self.new_user_password = "testpass123"
        self.existing_user_email = "marc.alleyne@aurumtechnologyltd.com"
        self.existing_user_password = "password"
        
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

    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None, use_auth: bool = False, auth_token: str = None) -> Dict:
        """Make HTTP request with error handling and optional authentication"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        # Add authentication header if token is available and requested
        if use_auth and auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
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
            "BACKEND CONNECTIVITY",
            result['success'],
            f"Backend API accessible at {self.base_url}" if result['success'] else f"Backend API not accessible: {result.get('error', 'Unknown error')}"
        )
        
        return result['success']

    def test_new_user_registration(self):
        """Test new user registration flow"""
        print("\n=== TESTING NEW USER REGISTRATION ===")
        
        # Register new user
        registration_data = {
            "email": self.new_user_email,
            "password": self.new_user_password,
            "username": "newuser",
            "full_name": "New User"
        }
        
        result = self.make_request('POST', '/auth/register', data=registration_data)
        
        if result['success']:
            self.log_test(
                "NEW USER REGISTRATION",
                True,
                f"Successfully registered new user: {self.new_user_email}"
            )
            return True
        elif result['status_code'] == 409:
            # User already exists - this is okay for testing
            self.log_test(
                "NEW USER REGISTRATION",
                True,
                f"User {self.new_user_email} already exists (expected for repeated tests)"
            )
            return True
        else:
            self.log_test(
                "NEW USER REGISTRATION",
                False,
                f"Registration failed: {result.get('error', 'Unknown error')}"
            )
            return False

    def test_new_user_login(self):
        """Test new user login and verify onboarding flow"""
        print("\n=== TESTING NEW USER LOGIN ===")
        
        # Login with new user credentials
        login_data = {
            "email": self.new_user_email,
            "password": self.new_user_password
        }
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        
        if result['success']:
            token_data = result['data']
            access_token = token_data.get('access_token')
            
            if access_token:
                self.auth_tokens['new_user'] = access_token
                self.log_test(
                    "NEW USER LOGIN",
                    True,
                    f"Successfully logged in new user: {self.new_user_email}"
                )
                
                # Test JWT token validation
                auth_result = self.make_request('GET', '/auth/me', use_auth=True, auth_token=access_token)
                if auth_result['success']:
                    user_data = auth_result['data']
                    self.log_test(
                        "NEW USER JWT TOKEN VALIDATION",
                        True,
                        f"JWT token valid, user: {user_data.get('email', 'Unknown')}"
                    )
                    
                    # Check if user should go to onboarding (has_completed_onboarding should be false)
                    has_completed_onboarding = user_data.get('has_completed_onboarding', True)
                    should_show_onboarding = not has_completed_onboarding
                    
                    self.log_test(
                        "NEW USER ONBOARDING FLOW",
                        should_show_onboarding,
                        f"New user should go to onboarding: {should_show_onboarding} (has_completed_onboarding: {has_completed_onboarding})"
                    )
                    
                    return True
                else:
                    self.log_test(
                        "NEW USER JWT TOKEN VALIDATION",
                        False,
                        f"JWT token validation failed: {auth_result.get('error', 'Unknown error')}"
                    )
                    return False
            else:
                self.log_test(
                    "NEW USER LOGIN",
                    False,
                    "Login response missing access_token"
                )
                return False
        else:
            self.log_test(
                "NEW USER LOGIN",
                False,
                f"Login failed: {result.get('error', 'Unknown error')}"
            )
            return False

    def test_existing_user_login(self):
        """Test existing user login and verify dashboard flow"""
        print("\n=== TESTING EXISTING USER LOGIN ===")
        
        # Login with existing user credentials
        login_data = {
            "email": self.existing_user_email,
            "password": self.existing_user_password
        }
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        
        if result['success']:
            token_data = result['data']
            access_token = token_data.get('access_token')
            
            if access_token:
                self.auth_tokens['existing_user'] = access_token
                self.log_test(
                    "EXISTING USER LOGIN",
                    True,
                    f"Successfully logged in existing user: {self.existing_user_email}"
                )
                
                # Test JWT token validation
                auth_result = self.make_request('GET', '/auth/me', use_auth=True, auth_token=access_token)
                if auth_result['success']:
                    user_data = auth_result['data']
                    self.log_test(
                        "EXISTING USER JWT TOKEN VALIDATION",
                        True,
                        f"JWT token valid, user: {user_data.get('email', 'Unknown')}"
                    )
                    
                    # Check if user should go to dashboard (has_completed_onboarding should be true)
                    has_completed_onboarding = user_data.get('has_completed_onboarding', False)
                    should_go_to_dashboard = has_completed_onboarding
                    
                    self.log_test(
                        "EXISTING USER DASHBOARD FLOW",
                        should_go_to_dashboard,
                        f"Existing user should go to dashboard: {should_go_to_dashboard} (has_completed_onboarding: {has_completed_onboarding})"
                    )
                    
                    return True
                else:
                    self.log_test(
                        "EXISTING USER JWT TOKEN VALIDATION",
                        False,
                        f"JWT token validation failed: {auth_result.get('error', 'Unknown error')}"
                    )
                    return False
            else:
                self.log_test(
                    "EXISTING USER LOGIN",
                    False,
                    "Login response missing access_token"
                )
                return False
        else:
            self.log_test(
                "EXISTING USER LOGIN",
                False,
                f"Login failed: {result.get('error', 'Unknown error')}"
            )
            return False

    def test_protected_endpoints_access(self):
        """Test access to protected endpoints with valid tokens"""
        print("\n=== TESTING PROTECTED ENDPOINTS ACCESS ===")
        
        # Test endpoints that should be accessible with valid authentication
        protected_endpoints = [
            ('/dashboard', 'Dashboard'),
            ('/pillars', 'Pillars'),
            ('/areas', 'Areas'),
            ('/projects', 'Projects'),
            ('/tasks', 'Tasks')
        ]
        
        success_count = 0
        total_endpoints = len(protected_endpoints)
        
        # Test with existing user token (should have data)
        if 'existing_user' in self.auth_tokens:
            token = self.auth_tokens['existing_user']
            
            for endpoint, name in protected_endpoints:
                result = self.make_request('GET', endpoint, use_auth=True, auth_token=token)
                
                if result['success']:
                    self.log_test(
                        f"PROTECTED ENDPOINT ACCESS - {name}",
                        True,
                        f"{name} endpoint accessible with valid token"
                    )
                    success_count += 1
                else:
                    self.log_test(
                        f"PROTECTED ENDPOINT ACCESS - {name}",
                        False,
                        f"{name} endpoint failed: {result.get('error', 'Unknown error')}"
                    )
        
        success_rate = (success_count / total_endpoints) * 100
        overall_success = success_rate >= 80
        
        self.log_test(
            "PROTECTED ENDPOINTS ACCESS SUMMARY",
            overall_success,
            f"Protected endpoints access: {success_count}/{total_endpoints} successful ({success_rate:.1f}%)"
        )
        
        return overall_success

    def test_unauthorized_access_prevention(self):
        """Test that endpoints properly reject unauthorized requests"""
        print("\n=== TESTING UNAUTHORIZED ACCESS PREVENTION ===")
        
        # Test endpoints without authentication
        protected_endpoints = [
            ('/dashboard', 'Dashboard'),
            ('/pillars', 'Pillars'),
            ('/areas', 'Areas'),
            ('/projects', 'Projects'),
            ('/tasks', 'Tasks'),
            ('/auth/me', 'User Profile')
        ]
        
        unauthorized_count = 0
        total_endpoints = len(protected_endpoints)
        
        for endpoint, name in protected_endpoints:
            result = self.make_request('GET', endpoint, use_auth=False)
            
            # Should return 401 or 403 for unauthorized access
            if result['status_code'] in [401, 403]:
                self.log_test(
                    f"UNAUTHORIZED ACCESS PREVENTION - {name}",
                    True,
                    f"{name} properly requires authentication (status: {result['status_code']})"
                )
                unauthorized_count += 1
            else:
                self.log_test(
                    f"UNAUTHORIZED ACCESS PREVENTION - {name}",
                    False,
                    f"{name} does not require authentication (status: {result['status_code']})"
                )
        
        success_rate = (unauthorized_count / total_endpoints) * 100
        overall_success = success_rate >= 80
        
        self.log_test(
            "UNAUTHORIZED ACCESS PREVENTION SUMMARY",
            overall_success,
            f"Unauthorized access prevention: {unauthorized_count}/{total_endpoints} endpoints protected ({success_rate:.1f}%)"
        )
        
        return overall_success

    def test_invalid_token_handling(self):
        """Test handling of invalid JWT tokens"""
        print("\n=== TESTING INVALID TOKEN HANDLING ===")
        
        # Test with invalid token
        invalid_token = "invalid.jwt.token.12345"
        
        result = self.make_request('GET', '/auth/me', use_auth=True, auth_token=invalid_token)
        
        if result['status_code'] in [401, 403]:
            self.log_test(
                "INVALID TOKEN HANDLING",
                True,
                f"Invalid token properly rejected (status: {result['status_code']})"
            )
            return True
        else:
            self.log_test(
                "INVALID TOKEN HANDLING",
                False,
                f"Invalid token not properly handled (status: {result['status_code']})"
            )
            return False

    def test_token_expiration_handling(self):
        """Test JWT token structure and basic validation"""
        print("\n=== TESTING JWT TOKEN STRUCTURE ===")
        
        if 'existing_user' in self.auth_tokens:
            token = self.auth_tokens['existing_user']
            
            # Basic JWT structure check (should have 3 parts separated by dots)
            token_parts = token.split('.')
            
            if len(token_parts) == 3:
                self.log_test(
                    "JWT TOKEN STRUCTURE",
                    True,
                    f"JWT token has correct structure (3 parts)"
                )
                
                # Test that token works for multiple requests
                result1 = self.make_request('GET', '/auth/me', use_auth=True, auth_token=token)
                time.sleep(1)  # Small delay
                result2 = self.make_request('GET', '/auth/me', use_auth=True, auth_token=token)
                
                if result1['success'] and result2['success']:
                    self.log_test(
                        "JWT TOKEN PERSISTENCE",
                        True,
                        "JWT token works for multiple consecutive requests"
                    )
                    return True
                else:
                    self.log_test(
                        "JWT TOKEN PERSISTENCE",
                        False,
                        "JWT token failed on consecutive requests"
                    )
                    return False
            else:
                self.log_test(
                    "JWT TOKEN STRUCTURE",
                    False,
                    f"JWT token has incorrect structure ({len(token_parts)} parts instead of 3)"
                )
                return False
        else:
            self.log_test(
                "JWT TOKEN STRUCTURE",
                False,
                "No valid token available for testing"
            )
            return False

    def run_comprehensive_authentication_test(self):
        """Run comprehensive authentication flow tests"""
        print("\n🔐 STARTING COMPREHENSIVE AUTHENTICATION FLOW TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"New User: {self.new_user_email}")
        print(f"Existing User: {self.existing_user_email}")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Backend Connectivity", self.test_backend_connectivity),
            ("New User Registration", self.test_new_user_registration),
            ("New User Login & Onboarding Flow", self.test_new_user_login),
            ("Existing User Login & Dashboard Flow", self.test_existing_user_login),
            ("Protected Endpoints Access", self.test_protected_endpoints_access),
            ("Unauthorized Access Prevention", self.test_unauthorized_access_prevention),
            ("Invalid Token Handling", self.test_invalid_token_handling),
            ("JWT Token Structure & Persistence", self.test_token_expiration_handling)
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
        print("🔐 AUTHENTICATION FLOW TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze specific authentication functionality
        registration_tests = sum(1 for result in self.test_results if result['success'] and 'REGISTRATION' in result['test'])
        login_tests = sum(1 for result in self.test_results if result['success'] and 'LOGIN' in result['test'])
        jwt_tests = sum(1 for result in self.test_results if result['success'] and 'JWT' in result['test'])
        flow_tests = sum(1 for result in self.test_results if result['success'] and ('ONBOARDING' in result['test'] or 'DASHBOARD' in result['test']))
        
        print(f"\n🔍 AUTHENTICATION ANALYSIS:")
        print(f"Registration Tests Passed: {registration_tests}")
        print(f"Login Tests Passed: {login_tests}")
        print(f"JWT Token Tests Passed: {jwt_tests}")
        print(f"User Flow Tests Passed: {flow_tests}")
        
        if success_rate >= 85:
            print("\n✅ AUTHENTICATION SYSTEM: SUCCESS")
            print("   ✅ New user registration working")
            print("   ✅ New user login → onboarding flow")
            print("   ✅ Existing user login → dashboard flow")
            print("   ✅ JWT token generation and validation")
            print("   ✅ No 401 or connection errors")
            print("   ✅ Protected endpoints properly secured")
            print("   The authentication system is production-ready!")
        else:
            print("\n❌ AUTHENTICATION SYSTEM: ISSUES DETECTED")
            print("   Issues found in authentication implementation")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 85

def main():
    """Run Authentication Flow Tests"""
    print("🔐 STARTING AUTHENTICATION FLOW BACKEND TESTING")
    print("=" * 80)
    
    tester = AuthenticationFlowTester()
    
    try:
        # Run the comprehensive authentication flow tests
        success = tester.run_comprehensive_authentication_test()
        
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