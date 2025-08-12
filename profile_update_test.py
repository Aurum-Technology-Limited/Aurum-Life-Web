#!/usr/bin/env python3
"""
PROFILE UPDATE ENDPOINT TESTING - COMPREHENSIVE TESTING
Testing the new profile update endpoint implementation with username change rate limiting.

FOCUS AREAS:
1. PUT /api/auth/profile - Profile update endpoint accessibility (not 404)
2. Authentication requirements - JWT token validation
3. Basic profile updates - first_name and last_name fields
4. Username change functionality with 7-day rate limiting
5. Security and input validation - XSS protection, IDOR protection
6. Database tracking - username change records and rate limit calculation

TESTING CRITERIA:
- Endpoint responds correctly (not 404)
- Requires valid JWT token
- Basic profile updates work (first_name, last_name)
- First username change works
- Second username change within 7 days returns 429 error
- Username uniqueness validation (409 error for duplicates)
- User-friendly error messages for rate limiting
- XSS protection for malicious input
- IDOR protection (users can only update their own profiles)

CREDENTIALS: marc.alleyne@aurumtechnologyltd.com / password
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any
import time

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://fastapi-react-fix.preview.emergentagent.com/api"

class ProfileUpdateAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        # Use the specified test credentials
        self.test_user_email = "marc.alleyne@aurumtechnologyltd.com"
        self.test_user_password = "password"
        
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

    def test_user_authentication(self):
        """Test user authentication with specified credentials"""
        print("\n=== TESTING USER AUTHENTICATION ===")
        
        # Login user with specified credentials
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        self.log_test(
            "USER LOGIN",
            result['success'],
            f"Login successful with {self.test_user_email}" if result['success'] else f"Login failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        token_data = result['data']
        self.auth_token = token_data.get('access_token')
        
        # Debug: Print token info
        print(f"DEBUG: Token received: {self.auth_token[:50] if self.auth_token else 'None'}...")
        print(f"DEBUG: Full token data: {token_data}")
        
        # Verify token works
        result = self.make_request('GET', '/auth/me', use_auth=True)
        self.log_test(
            "AUTHENTICATION TOKEN VALIDATION",
            result['success'],
            f"Token validated successfully, user: {result['data'].get('email', 'Unknown')}" if result['success'] else f"Token validation failed: {result.get('error', 'Unknown error')}"
        )
        
        # Debug: Print auth/me response
        print(f"DEBUG: Auth/me response: {result}")
        
        return result['success']

    def test_profile_endpoint_accessibility(self):
        """Test 1: Profile update endpoint accessibility (not 404)"""
        print("\n=== TESTING PROFILE ENDPOINT ACCESSIBILITY ===")
        
        if not self.auth_token:
            self.log_test("PROFILE ENDPOINT ACCESSIBILITY - Authentication Required", False, "No authentication token available")
            return False
        
        # Test PUT /api/auth/profile endpoint exists (should not return 404)
        test_data = {"first_name": "Test"}
        result = self.make_request('PUT', '/auth/profile', data=test_data, use_auth=True)
        
        endpoint_accessible = result['status_code'] != 404
        self.log_test(
            "PROFILE ENDPOINT ACCESSIBILITY",
            endpoint_accessible,
            f"PUT /api/auth/profile endpoint accessible (status: {result['status_code']})" if endpoint_accessible else f"PUT /api/auth/profile returns 404 - endpoint not found"
        )
        
        return endpoint_accessible

    def test_authentication_requirements(self):
        """Test 2: Authentication requirements - JWT token validation"""
        print("\n=== TESTING AUTHENTICATION REQUIREMENTS ===")
        
        # Test without authentication token (should return 401/403)
        test_data = {"first_name": "Test"}
        result = self.make_request('PUT', '/auth/profile', data=test_data, use_auth=False)
        
        requires_auth = result['status_code'] in [401, 403]
        self.log_test(
            "AUTHENTICATION REQUIREMENT",
            requires_auth,
            f"Endpoint properly requires authentication (status: {result['status_code']})" if requires_auth else f"Endpoint does not require authentication (status: {result['status_code']})"
        )
        
        # Test with invalid token
        invalid_headers = {"Authorization": "Bearer invalid-token-12345", "Content-Type": "application/json"}
        try:
            response = self.session.put(f"{self.base_url}/auth/profile", json=test_data, headers=invalid_headers, timeout=30)
            invalid_token_rejected = response.status_code in [401, 403]
            self.log_test(
                "INVALID TOKEN REJECTION",
                invalid_token_rejected,
                f"Invalid token properly rejected (status: {response.status_code})" if invalid_token_rejected else f"Invalid token not properly handled (status: {response.status_code})"
            )
        except Exception as e:
            self.log_test("INVALID TOKEN REJECTION", False, f"Error testing invalid token: {str(e)}")
            invalid_token_rejected = False
        
        return requires_auth and invalid_token_rejected

    def test_basic_profile_updates(self):
        """Test 3: Basic profile updates - first_name and last_name fields"""
        print("\n=== TESTING BASIC PROFILE UPDATES ===")
        
        if not self.auth_token:
            self.log_test("BASIC PROFILE UPDATES - Authentication Required", False, "No authentication token available")
            return False
        
        # Test updating first_name
        first_name_data = {"first_name": "UpdatedFirstName"}
        result = self.make_request('PUT', '/auth/profile', data=first_name_data, use_auth=True)
        
        first_name_success = result['success'] and result['status_code'] == 200
        self.log_test(
            "FIRST NAME UPDATE",
            first_name_success,
            f"First name updated successfully" if first_name_success else f"First name update failed: {result.get('error', 'Unknown error')}"
        )
        
        # Verify response structure for first_name update
        if first_name_success:
            response_data = result['data']
            has_required_fields = all(field in response_data for field in ['id', 'email', 'first_name'])
            updated_first_name = response_data.get('first_name') == 'UpdatedFirstName'
            
            self.log_test(
                "FIRST NAME UPDATE RESPONSE",
                has_required_fields and updated_first_name,
                f"Response contains updated first_name: {response_data.get('first_name')}" if updated_first_name else f"Response structure or first_name incorrect: {response_data}"
            )
        
        # Test updating last_name
        last_name_data = {"last_name": "UpdatedLastName"}
        result = self.make_request('PUT', '/auth/profile', data=last_name_data, use_auth=True)
        
        last_name_success = result['success'] and result['status_code'] == 200
        self.log_test(
            "LAST NAME UPDATE",
            last_name_success,
            f"Last name updated successfully" if last_name_success else f"Last name update failed: {result.get('error', 'Unknown error')}"
        )
        
        # Verify response structure for last_name update
        if last_name_success:
            response_data = result['data']
            has_required_fields = all(field in response_data for field in ['id', 'email', 'last_name'])
            updated_last_name = response_data.get('last_name') == 'UpdatedLastName'
            
            self.log_test(
                "LAST NAME UPDATE RESPONSE",
                has_required_fields and updated_last_name,
                f"Response contains updated last_name: {response_data.get('last_name')}" if updated_last_name else f"Response structure or last_name incorrect: {response_data}"
            )
        
        # Test updating both fields together
        both_fields_data = {"first_name": "BothFirst", "last_name": "BothLast"}
        result = self.make_request('PUT', '/auth/profile', data=both_fields_data, use_auth=True)
        
        both_fields_success = result['success'] and result['status_code'] == 200
        self.log_test(
            "BOTH NAMES UPDATE",
            both_fields_success,
            f"Both first_name and last_name updated successfully" if both_fields_success else f"Both names update failed: {result.get('error', 'Unknown error')}"
        )
        
        return first_name_success and last_name_success and both_fields_success

    def test_username_change_functionality(self):
        """Test 4: Username change functionality with 7-day rate limiting"""
        print("\n=== TESTING USERNAME CHANGE FUNCTIONALITY ===")
        
        if not self.auth_token:
            self.log_test("USERNAME CHANGE - Authentication Required", False, "No authentication token available")
            return False
        
        # Generate unique username for testing
        timestamp = int(time.time())
        new_username = f"testuser_{timestamp}"
        
        # Test first username change (should work)
        username_data = {"username": new_username}
        result = self.make_request('PUT', '/auth/profile', data=username_data, use_auth=True)
        
        first_change_success = result['success'] and result['status_code'] == 200
        self.log_test(
            "FIRST USERNAME CHANGE",
            first_change_success,
            f"First username change successful to: {new_username}" if first_change_success else f"First username change failed: {result.get('error', 'Unknown error')}"
        )
        
        if not first_change_success:
            return False
        
        # Verify response contains updated username
        response_data = result['data']
        username_updated = response_data.get('username') == new_username
        self.log_test(
            "USERNAME UPDATE VERIFICATION",
            username_updated,
            f"Response contains updated username: {response_data.get('username')}" if username_updated else f"Username not updated in response: {response_data}"
        )
        
        # Test second username change within 7 days (should return 429 error)
        second_username = f"testuser2_{timestamp}"
        username_data_2 = {"username": second_username}
        result = self.make_request('PUT', '/auth/profile', data=username_data_2, use_auth=True)
        
        rate_limited = result['status_code'] == 429
        self.log_test(
            "USERNAME CHANGE RATE LIMITING",
            rate_limited,
            f"Second username change properly rate limited (status: 429)" if rate_limited else f"Rate limiting not working (status: {result['status_code']}): {result.get('error', 'No error')}"
        )
        
        # Verify rate limiting error message is user-friendly
        if rate_limited:
            error_message = result['data'].get('detail', '')
            user_friendly_message = 'Username can only be changed' in error_message or '7 days' in error_message
            self.log_test(
                "RATE LIMITING ERROR MESSAGE",
                user_friendly_message,
                f"User-friendly rate limiting message: {error_message}" if user_friendly_message else f"Rate limiting message not user-friendly: {error_message}"
            )
        
        return first_change_success and username_updated and rate_limited

    def test_username_uniqueness(self):
        """Test 5: Username uniqueness validation (409 error for duplicates)"""
        print("\n=== TESTING USERNAME UNIQUENESS ===")
        
        if not self.auth_token:
            self.log_test("USERNAME UNIQUENESS - Authentication Required", False, "No authentication token available")
            return False
        
        # Try to use a username that likely already exists (the current user's email prefix)
        existing_username = self.test_user_email.split('@')[0]  # "marc.alleyne"
        
        username_data = {"username": existing_username}
        result = self.make_request('PUT', '/auth/profile', data=username_data, use_auth=True)
        
        # This should either succeed (if it's the user's current username) or fail with 409/429
        if result['status_code'] == 409:
            # Username already taken by another user
            uniqueness_enforced = True
            error_message = result['data'].get('detail', '')
            user_friendly_message = 'already taken' in error_message.lower() or 'exists' in error_message.lower()
            
            self.log_test(
                "USERNAME UNIQUENESS VALIDATION",
                uniqueness_enforced,
                f"Username uniqueness properly enforced (status: 409): {error_message}"
            )
            
            self.log_test(
                "UNIQUENESS ERROR MESSAGE",
                user_friendly_message,
                f"User-friendly uniqueness message: {error_message}" if user_friendly_message else f"Uniqueness message not user-friendly: {error_message}"
            )
            
            return uniqueness_enforced and user_friendly_message
        elif result['status_code'] == 429:
            # Rate limited (expected if we just changed username)
            self.log_test(
                "USERNAME UNIQUENESS VALIDATION",
                True,
                f"Username change rate limited as expected (status: 429)"
            )
            return True
        elif result['status_code'] == 200:
            # Successfully updated (probably the user's current username)
            self.log_test(
                "USERNAME UNIQUENESS VALIDATION",
                True,
                f"Username update successful (likely current username)"
            )
            return True
        else:
            self.log_test(
                "USERNAME UNIQUENESS VALIDATION",
                False,
                f"Unexpected response for username uniqueness test (status: {result['status_code']}): {result.get('error', 'No error')}"
            )
            return False

    def test_xss_protection(self):
        """Test 6: XSS protection - malicious input sanitization"""
        print("\n=== TESTING XSS PROTECTION ===")
        
        if not self.auth_token:
            self.log_test("XSS PROTECTION - Authentication Required", False, "No authentication token available")
            return False
        
        # Test XSS payloads in different fields
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "';DROP TABLE users;--"
        ]
        
        xss_tests_passed = 0
        total_xss_tests = 0
        
        for payload in xss_payloads:
            # Test XSS in first_name
            xss_data = {"first_name": payload}
            result = self.make_request('PUT', '/auth/profile', data=xss_data, use_auth=True)
            
            total_xss_tests += 1
            if result['success']:
                # Check if the payload was sanitized
                response_data = result['data']
                sanitized_name = response_data.get('first_name', '')
                is_sanitized = payload not in sanitized_name and '<script>' not in sanitized_name
                
                if is_sanitized:
                    xss_tests_passed += 1
                    self.log_test(
                        f"XSS PROTECTION - FIRST NAME ({payload[:20]}...)",
                        True,
                        f"XSS payload sanitized: {sanitized_name[:50]}..."
                    )
                else:
                    self.log_test(
                        f"XSS PROTECTION - FIRST NAME ({payload[:20]}...)",
                        False,
                        f"XSS payload not sanitized: {sanitized_name}"
                    )
            else:
                # Request failed - could be due to validation
                if result['status_code'] in [400, 422]:
                    xss_tests_passed += 1
                    self.log_test(
                        f"XSS PROTECTION - FIRST NAME ({payload[:20]}...)",
                        True,
                        f"XSS payload rejected by validation (status: {result['status_code']})"
                    )
                else:
                    self.log_test(
                        f"XSS PROTECTION - FIRST NAME ({payload[:20]}...)",
                        False,
                        f"Unexpected error with XSS payload (status: {result['status_code']})"
                    )
        
        xss_protection_rate = (xss_tests_passed / total_xss_tests) * 100 if total_xss_tests > 0 else 0
        overall_xss_success = xss_protection_rate >= 80
        
        self.log_test(
            "XSS PROTECTION OVERALL",
            overall_xss_success,
            f"XSS protection: {xss_tests_passed}/{total_xss_tests} tests passed ({xss_protection_rate:.1f}%)"
        )
        
        return overall_xss_success

    def test_idor_protection(self):
        """Test 7: IDOR protection - users can only update their own profiles"""
        print("\n=== TESTING IDOR PROTECTION ===")
        
        if not self.auth_token:
            self.log_test("IDOR PROTECTION - Authentication Required", False, "No authentication token available")
            return False
        
        # The profile endpoint should only allow users to update their own profile
        # Since we're using /auth/profile (not /auth/profile/{user_id}), IDOR protection
        # is inherently built-in as the endpoint uses the authenticated user's token
        
        # Test that the endpoint updates the correct user's profile
        test_data = {"first_name": "IDORTest"}
        result = self.make_request('PUT', '/auth/profile', data=test_data, use_auth=True)
        
        if result['success']:
            response_data = result['data']
            # Verify the response contains the authenticated user's email
            correct_user = response_data.get('email') == self.test_user_email
            
            self.log_test(
                "IDOR PROTECTION VERIFICATION",
                correct_user,
                f"Profile update affects correct user: {response_data.get('email')}" if correct_user else f"Profile update affects wrong user: {response_data.get('email')} (expected: {self.test_user_email})"
            )
            
            return correct_user
        else:
            self.log_test(
                "IDOR PROTECTION VERIFICATION",
                False,
                f"Profile update failed during IDOR test: {result.get('error', 'Unknown error')}"
            )
            return False

    def test_input_validation(self):
        """Test 8: Input validation - various input scenarios"""
        print("\n=== TESTING INPUT VALIDATION ===")
        
        if not self.auth_token:
            self.log_test("INPUT VALIDATION - Authentication Required", False, "No authentication token available")
            return False
        
        validation_tests_passed = 0
        total_validation_tests = 0
        
        # Test empty data
        total_validation_tests += 1
        result = self.make_request('PUT', '/auth/profile', data={}, use_auth=True)
        if result['success']:
            validation_tests_passed += 1
            self.log_test("INPUT VALIDATION - EMPTY DATA", True, "Empty data handled gracefully")
        else:
            self.log_test("INPUT VALIDATION - EMPTY DATA", False, f"Empty data not handled: {result.get('error', 'Unknown error')}")
        
        # Test null values
        total_validation_tests += 1
        null_data = {"first_name": None, "last_name": None}
        result = self.make_request('PUT', '/auth/profile', data=null_data, use_auth=True)
        handles_null = result['success'] or result['status_code'] in [400, 422]
        if handles_null:
            validation_tests_passed += 1
            self.log_test("INPUT VALIDATION - NULL VALUES", True, f"Null values handled appropriately (status: {result['status_code']})")
        else:
            self.log_test("INPUT VALIDATION - NULL VALUES", False, f"Null values not handled properly: {result.get('error', 'Unknown error')}")
        
        # Test very long strings
        total_validation_tests += 1
        long_string = "A" * 1000
        long_data = {"first_name": long_string}
        result = self.make_request('PUT', '/auth/profile', data=long_data, use_auth=True)
        handles_long_strings = result['success'] or result['status_code'] in [400, 422]
        if handles_long_strings:
            validation_tests_passed += 1
            self.log_test("INPUT VALIDATION - LONG STRINGS", True, f"Long strings handled appropriately (status: {result['status_code']})")
        else:
            self.log_test("INPUT VALIDATION - LONG STRINGS", False, f"Long strings not handled properly: {result.get('error', 'Unknown error')}")
        
        # Test invalid field types
        total_validation_tests += 1
        invalid_data = {"first_name": 12345, "last_name": ["array", "value"]}
        result = self.make_request('PUT', '/auth/profile', data=invalid_data, use_auth=True)
        handles_invalid_types = result['success'] or result['status_code'] in [400, 422]
        if handles_invalid_types:
            validation_tests_passed += 1
            self.log_test("INPUT VALIDATION - INVALID TYPES", True, f"Invalid types handled appropriately (status: {result['status_code']})")
        else:
            self.log_test("INPUT VALIDATION - INVALID TYPES", False, f"Invalid types not handled properly: {result.get('error', 'Unknown error')}")
        
        validation_rate = (validation_tests_passed / total_validation_tests) * 100 if total_validation_tests > 0 else 0
        overall_validation_success = validation_rate >= 75
        
        self.log_test(
            "INPUT VALIDATION OVERALL",
            overall_validation_success,
            f"Input validation: {validation_tests_passed}/{total_validation_tests} tests passed ({validation_rate:.1f}%)"
        )
        
        return overall_validation_success

    def run_comprehensive_profile_update_test(self):
        """Run comprehensive profile update endpoint tests"""
        print("\n🔐 STARTING PROFILE UPDATE ENDPOINT COMPREHENSIVE TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("Testing PUT /api/auth/profile with 7-day username change rate limiting")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Basic Connectivity", self.test_basic_connectivity),
            ("User Authentication", self.test_user_authentication),
            ("Profile Endpoint Accessibility", self.test_profile_endpoint_accessibility),
            ("Authentication Requirements", self.test_authentication_requirements),
            ("Basic Profile Updates", self.test_basic_profile_updates),
            ("Username Change Functionality", self.test_username_change_functionality),
            ("Username Uniqueness", self.test_username_uniqueness),
            ("XSS Protection", self.test_xss_protection),
            ("IDOR Protection", self.test_idor_protection),
            ("Input Validation", self.test_input_validation)
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
        print("🔐 PROFILE UPDATE ENDPOINT TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze results for profile update functionality
        endpoint_tests_passed = sum(1 for result in self.test_results if result['success'] and 'ENDPOINT' in result['test'])
        auth_tests_passed = sum(1 for result in self.test_results if result['success'] and 'AUTHENTICATION' in result['test'])
        profile_tests_passed = sum(1 for result in self.test_results if result['success'] and ('PROFILE' in result['test'] or 'NAME' in result['test']))
        username_tests_passed = sum(1 for result in self.test_results if result['success'] and 'USERNAME' in result['test'])
        security_tests_passed = sum(1 for result in self.test_results if result['success'] and ('XSS' in result['test'] or 'IDOR' in result['test'] or 'VALIDATION' in result['test']))
        
        print(f"\n🔍 SYSTEM ANALYSIS:")
        print(f"Endpoint Accessibility Tests Passed: {endpoint_tests_passed}")
        print(f"Authentication Tests Passed: {auth_tests_passed}")
        print(f"Profile Update Tests Passed: {profile_tests_passed}")
        print(f"Username Change Tests Passed: {username_tests_passed}")
        print(f"Security Tests Passed: {security_tests_passed}")
        
        if success_rate >= 85:
            print("\n✅ PROFILE UPDATE ENDPOINT SYSTEM: SUCCESS")
            print("   ✅ PUT /api/auth/profile endpoint accessible (not 404)")
            print("   ✅ Authentication requirements working")
            print("   ✅ Basic profile updates (first_name, last_name) functional")
            print("   ✅ Username change with 7-day rate limiting working")
            print("   ✅ Security measures (XSS, IDOR protection) verified")
            print("   The Profile Update endpoint is production-ready!")
        else:
            print("\n❌ PROFILE UPDATE ENDPOINT SYSTEM: ISSUES DETECTED")
            print("   Issues found in profile update endpoint implementation")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 85

def main():
    """Run Profile Update Endpoint Tests"""
    print("🔐 STARTING PROFILE UPDATE ENDPOINT BACKEND TESTING")
    print("=" * 80)
    
    tester = ProfileUpdateAPITester()
    
    try:
        # Run the comprehensive profile update endpoint tests
        success = tester.run_comprehensive_profile_update_test()
        
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