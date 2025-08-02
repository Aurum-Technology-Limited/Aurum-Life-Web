#!/usr/bin/env python3
"""
USER MENU BACKEND TESTING
Quick test of core authentication and user-related functionality to verify 
the backend is ready for the User Menu feature.

TEST REQUIREMENTS:
1. User Authentication: Test login endpoint and JWT validation
2. Profile Endpoints: Test user profile retrieval 
3. Feedback Endpoint: Quick verification that /api/feedback still works
4. Session Management: Verify that user data is properly returned

CONTEXT:
Testing backend support for User & Account Menu component that allows users to:
- Access Profile & Settings (navigates to profile page)
- Send Feedback (navigates to feedback page) 
- Logout (clears session)
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any
import uuid

# Configuration - Using the production backend URL from frontend/.env
BACKEND_URL = "https://b2358db8-5047-4c29-b8c1-f51d8a27f653.preview.emergentagent.com/api"

class UserMenuBackendTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        self.user_id = None
        
        # Use realistic test data for user menu testing
        self.test_user_email = f"usermenu.tester_{uuid.uuid4().hex[:8]}@aurumlife.com"
        self.test_user_password = "UserMenuTest2025!"
        self.test_user_data = {
            "username": f"usermenu_tester_{uuid.uuid4().hex[:8]}",
            "email": self.test_user_email,
            "first_name": "UserMenu",
            "last_name": "Tester",
            "password": self.test_user_password
        }
        
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
        
        result = self.make_request('GET', '/health')
        self.log_test(
            "BACKEND API CONNECTIVITY",
            result['success'],
            f"Backend API accessible at {self.base_url}" if result['success'] else f"Backend API not accessible: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            health_data = result['data']
            self.log_test(
                "HEALTH CHECK RESPONSE",
                'status' in health_data,
                f"Health check returned: {health_data.get('status', 'Unknown status')}"
            )
        
        return result['success']

    def test_user_authentication(self):
        """Test user registration, login endpoint and JWT validation"""
        print("\n=== TESTING USER AUTHENTICATION ===")
        
        # 1. Test user registration
        result = self.make_request('POST', '/auth/register', data=self.test_user_data)
        self.log_test(
            "USER REGISTRATION",
            result['success'],
            f"User registered successfully: {result['data'].get('email', 'Unknown')}" if result['success'] else f"Registration failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        self.user_id = result['data'].get('id')
        
        # 2. Test login endpoint
        login_data = {
            "email": self.test_user_data['email'],
            "password": self.test_user_data['password']
        }
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        self.log_test(
            "LOGIN ENDPOINT",
            result['success'],
            f"Login successful, JWT token received" if result['success'] else f"Login failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        token_data = result['data']
        self.auth_token = token_data.get('access_token')
        
        # Verify token structure
        token_valid = self.auth_token and len(self.auth_token) > 50  # JWT tokens are typically long
        self.log_test(
            "JWT TOKEN STRUCTURE",
            token_valid,
            f"JWT token received with proper structure (length: {len(self.auth_token) if self.auth_token else 0})" if token_valid else "Invalid or missing JWT token"
        )
        
        # 3. Test JWT validation with protected endpoint
        result = self.make_request('GET', '/auth/me', use_auth=True)
        self.log_test(
            "JWT TOKEN VALIDATION",
            result['success'],
            f"Token validated successfully, user: {result['data'].get('email', 'Unknown')}" if result['success'] else f"Token validation failed: {result.get('error', 'Unknown error')}"
        )
        
        # 4. Test authentication without token (should fail)
        result = self.make_request('GET', '/auth/me', use_auth=False)
        auth_required = not result['success'] and result['status_code'] in [401, 403]
        self.log_test(
            "AUTHENTICATION REQUIRED",
            auth_required,
            f"Protected endpoint properly requires authentication (status: {result['status_code']})" if auth_required else f"Authentication not properly enforced"
        )
        
        return token_valid and result['success'] and auth_required

    def test_profile_endpoints(self):
        """Test user profile retrieval endpoints"""
        print("\n=== TESTING PROFILE ENDPOINTS ===")
        
        if not self.auth_token:
            self.log_test("PROFILE ENDPOINTS - Authentication Required", False, "No authentication token available")
            return False
        
        # 1. Test GET /auth/me (current user info)
        result = self.make_request('GET', '/auth/me', use_auth=True)
        self.log_test(
            "GET CURRENT USER INFO (/auth/me)",
            result['success'],
            f"Current user info retrieved successfully" if result['success'] else f"Failed to get current user: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        # Verify user data structure
        user_data = result['data']
        required_fields = ['id', 'email', 'first_name', 'last_name', 'is_active']
        missing_fields = [field for field in required_fields if field not in user_data]
        
        self.log_test(
            "USER DATA STRUCTURE",
            len(missing_fields) == 0,
            f"All required user fields present: {required_fields}" if len(missing_fields) == 0 else f"Missing fields: {missing_fields}"
        )
        
        # Verify user data matches registration
        email_matches = user_data.get('email') == self.test_user_email
        name_matches = user_data.get('first_name') == 'UserMenu' and user_data.get('last_name') == 'Tester'
        
        self.log_test(
            "USER DATA ACCURACY",
            email_matches and name_matches,
            f"User data matches registration (email: {email_matches}, name: {name_matches})" if email_matches and name_matches else f"User data mismatch"
        )
        
        # 2. Test profile update endpoint
        update_data = {
            "first_name": "UpdatedUserMenu",
            "last_name": "UpdatedTester"
        }
        
        result = self.make_request('PUT', '/users/me', data=update_data, use_auth=True)
        self.log_test(
            "PROFILE UPDATE (/users/me)",
            result['success'],
            f"Profile updated successfully" if result['success'] else f"Profile update failed: {result.get('error', 'Unknown error')}"
        )
        
        # 3. Verify profile update by getting user info again
        if result['success']:
            result = self.make_request('GET', '/auth/me', use_auth=True)
            if result['success']:
                updated_user_data = result['data']
                update_persisted = (updated_user_data.get('first_name') == 'UpdatedUserMenu' and 
                                  updated_user_data.get('last_name') == 'UpdatedTester')
                
                self.log_test(
                    "PROFILE UPDATE PERSISTENCE",
                    update_persisted,
                    f"Profile updates persisted correctly" if update_persisted else f"Profile updates not persisted"
                )
                
                return update_persisted
        
        return False

    def test_feedback_endpoint(self):
        """Quick verification that /api/feedback endpoint works"""
        print("\n=== TESTING FEEDBACK ENDPOINT ===")
        
        if not self.auth_token:
            self.log_test("FEEDBACK ENDPOINT - Authentication Required", False, "No authentication token available")
            return False
        
        # Test feedback submission
        feedback_data = {
            "category": "suggestion",
            "subject": "User Menu Testing Feedback",
            "message": "This is a test feedback submission from the User Menu backend testing suite.",
            "priority": "medium"
        }
        
        result = self.make_request('POST', '/feedback', data=feedback_data, use_auth=True)
        self.log_test(
            "FEEDBACK SUBMISSION",
            result['success'],
            f"Feedback submitted successfully" if result['success'] else f"Feedback submission failed: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            # Verify feedback response structure
            feedback_response = result['data']
            expected_fields = ['success', 'message']
            has_required_fields = all(field in feedback_response for field in expected_fields)
            
            self.log_test(
                "FEEDBACK RESPONSE STRUCTURE",
                has_required_fields,
                f"Feedback response has required fields: {expected_fields}" if has_required_fields else f"Missing fields in feedback response"
            )
            
            return has_required_fields
        
        return False

    def test_session_management(self):
        """Verify that user data is properly returned and session management works"""
        print("\n=== TESTING SESSION MANAGEMENT ===")
        
        if not self.auth_token:
            self.log_test("SESSION MANAGEMENT - Authentication Required", False, "No authentication token available")
            return False
        
        # 1. Test that user data is consistently returned
        result1 = self.make_request('GET', '/auth/me', use_auth=True)
        result2 = self.make_request('GET', '/auth/me', use_auth=True)
        
        both_successful = result1['success'] and result2['success']
        self.log_test(
            "CONSISTENT USER DATA RETRIEVAL",
            both_successful,
            f"User data retrieved consistently across multiple requests" if both_successful else f"Inconsistent user data retrieval"
        )
        
        if not both_successful:
            return False
        
        # 2. Verify user data consistency
        user_data1 = result1['data']
        user_data2 = result2['data']
        
        data_consistent = (user_data1.get('id') == user_data2.get('id') and 
                          user_data1.get('email') == user_data2.get('email'))
        
        self.log_test(
            "USER DATA CONSISTENCY",
            data_consistent,
            f"User data consistent across requests" if data_consistent else f"User data inconsistent between requests"
        )
        
        # 3. Test that session persists across different endpoints
        endpoints_to_test = [
            ('/auth/me', 'Current user info'),
            ('/dashboard', 'Dashboard data'),
            ('/stats', 'User statistics')
        ]
        
        session_persistent = True
        for endpoint, description in endpoints_to_test:
            result = self.make_request('GET', endpoint, use_auth=True)
            endpoint_success = result['success']
            
            self.log_test(
                f"SESSION PERSISTENCE - {description}",
                endpoint_success,
                f"Session valid for {description}" if endpoint_success else f"Session invalid for {description}: {result.get('error', 'Unknown error')}"
            )
            
            if not endpoint_success:
                session_persistent = False
        
        # 4. Test invalid token handling
        original_token = self.auth_token
        self.auth_token = "invalid_token_12345"
        
        result = self.make_request('GET', '/auth/me', use_auth=True)
        invalid_token_rejected = not result['success'] and result['status_code'] in [401, 403]
        
        self.log_test(
            "INVALID TOKEN REJECTION",
            invalid_token_rejected,
            f"Invalid token properly rejected (status: {result['status_code']})" if invalid_token_rejected else f"Invalid token not properly rejected"
        )
        
        # Restore valid token
        self.auth_token = original_token
        
        return data_consistent and session_persistent and invalid_token_rejected

    def run_user_menu_tests(self):
        """Run all User Menu backend tests"""
        print("\n🔐 STARTING USER MENU BACKEND TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Basic Connectivity", self.test_basic_connectivity),
            ("User Authentication", self.test_user_authentication),
            ("Profile Endpoints", self.test_profile_endpoints),
            ("Feedback Endpoint", self.test_feedback_endpoint),
            ("Session Management", self.test_session_management)
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
        print("🔐 USER MENU BACKEND TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze results for User Menu functionality
        auth_tests_passed = sum(1 for result in self.test_results if result['success'] and ('AUTHENTICATION' in result['test'] or 'LOGIN' in result['test'] or 'JWT' in result['test']))
        profile_tests_passed = sum(1 for result in self.test_results if result['success'] and 'PROFILE' in result['test'])
        feedback_tests_passed = sum(1 for result in self.test_results if result['success'] and 'FEEDBACK' in result['test'])
        session_tests_passed = sum(1 for result in self.test_results if result['success'] and 'SESSION' in result['test'])
        
        print(f"\n🔍 SYSTEM ANALYSIS:")
        print(f"Authentication Tests Passed: {auth_tests_passed}")
        print(f"Profile Tests Passed: {profile_tests_passed}")
        print(f"Feedback Tests Passed: {feedback_tests_passed}")
        print(f"Session Management Tests Passed: {session_tests_passed}")
        
        if success_rate >= 80:
            print("\n✅ USER MENU BACKEND: READY")
            print("   ✅ User authentication working (login endpoint & JWT validation)")
            print("   ✅ Profile endpoints functional (user data retrieval)")
            print("   ✅ Feedback endpoint operational")
            print("   ✅ Session management working properly")
            print("   The backend is ready to support the User Menu feature!")
        else:
            print("\n❌ USER MENU BACKEND: ISSUES DETECTED")
            print("   Issues found that may affect User Menu functionality")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 80

def main():
    """Run User Menu Backend Tests"""
    print("🔐 STARTING USER MENU BACKEND TESTING")
    print("=" * 80)
    
    tester = UserMenuBackendTester()
    
    try:
        # Run the User Menu backend tests
        success = tester.run_user_menu_tests()
        
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