#!/usr/bin/env python3
"""
USERNAME CHANGE RATE LIMITING & XSS PROTECTION TESTING - DATABASE FIX VERIFICATION
Testing the updated username change rate limiting system that now uses profile_data JSON field.

FOCUS AREAS:
1. USERNAME CHANGE RATE LIMITING (DATABASE FIX) - Uses profile_data JSON field
2. COMPLETE PROFILE UPDATE TESTING - All profile update functionality
3. XSS PROTECTION VERIFICATION - Enhanced XSS protection still working
4. END-TO-END FUNCTIONALITY - Authentication, profile updates, security

TESTING CRITERIA:
- First Username Change: Should work and store timestamp in profile_data
- Second Username Change: Within 7 days should return 429 error with clear message
- Rate Limit Message: Should show exact days remaining
- Database Compatibility: Uses existing profile_data field, no schema changes needed
- XSS Protection: javascript: protocol and other dangerous content blocked
- Profile Updates: Basic profile updates (first_name, last_name) should work

CREDENTIALS: marc.alleyne@aurumtechnologyltd.com / password
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any
import time

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://2ba83010-29ce-4f25-8827-92c31097d7b1.preview.emergentagent.com/api"

class UsernameRateLimitingTester:
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
        
        # Verify token works
        result = self.make_request('GET', '/auth/me', use_auth=True)
        self.log_test(
            "AUTHENTICATION TOKEN VALIDATION",
            result['success'],
            f"Token validated successfully, user: {result['data'].get('email', 'Unknown')}" if result['success'] else f"Token validation failed: {result.get('error', 'Unknown error')}"
        )
        
        return result['success']

    def test_basic_profile_updates(self):
        """Test basic profile updates (first_name, last_name) to ensure core functionality works"""
        print("\n=== TESTING BASIC PROFILE UPDATES ===")
        
        if not self.auth_token:
            self.log_test("BASIC PROFILE UPDATES - Authentication Required", False, "No authentication token available")
            return False
        
        # Test basic profile update (first_name, last_name)
        basic_update_data = {
            "first_name": "Marc",
            "last_name": "Alleyne"
        }
        
        result = self.make_request('PUT', '/auth/profile', data=basic_update_data, use_auth=True)
        self.log_test(
            "BASIC PROFILE UPDATE (first_name, last_name)",
            result['success'],
            f"Basic profile update successful" if result['success'] else f"Basic profile update failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        # Verify the update was applied
        profile_result = self.make_request('GET', '/auth/me', use_auth=True)
        if profile_result['success']:
            profile_data = profile_result['data']
            first_name_correct = profile_data.get('first_name') == 'Marc'
            last_name_correct = profile_data.get('last_name') == 'Alleyne'
            
            self.log_test(
                "BASIC PROFILE UPDATE VERIFICATION",
                first_name_correct and last_name_correct,
                f"Profile updates verified: first_name={profile_data.get('first_name')}, last_name={profile_data.get('last_name')}" if (first_name_correct and last_name_correct) else f"Profile update verification failed: first_name={profile_data.get('first_name')}, last_name={profile_data.get('last_name')}"
            )
            
            return first_name_correct and last_name_correct
        
        return False

    def test_first_username_change(self):
        """Test first username change - should work and store timestamp in profile_data"""
        print("\n=== TESTING FIRST USERNAME CHANGE ===")
        
        if not self.auth_token:
            self.log_test("FIRST USERNAME CHANGE - Authentication Required", False, "No authentication token available")
            return False
        
        # Generate unique username for testing
        timestamp = int(time.time())
        new_username = f"testuser_{timestamp}"
        
        # Test first username change
        username_update_data = {
            "username": new_username
        }
        
        result = self.make_request('PUT', '/auth/profile', data=username_update_data, use_auth=True)
        self.log_test(
            "FIRST USERNAME CHANGE",
            result['success'],
            f"First username change successful to '{new_username}'" if result['success'] else f"First username change failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        # Verify the username was updated
        profile_result = self.make_request('GET', '/auth/me', use_auth=True)
        if profile_result['success']:
            profile_data = profile_result['data']
            username_updated = profile_data.get('username') == new_username
            
            self.log_test(
                "FIRST USERNAME CHANGE VERIFICATION",
                username_updated,
                f"Username successfully updated to '{new_username}'" if username_updated else f"Username update verification failed: expected '{new_username}', got '{profile_data.get('username')}'"
            )
            
            return username_updated
        
        return False

    def test_second_username_change_rate_limiting(self):
        """Test second username change within 7 days - should return 429 error with clear message"""
        print("\n=== TESTING USERNAME CHANGE RATE LIMITING ===")
        
        if not self.auth_token:
            self.log_test("USERNAME CHANGE RATE LIMITING - Authentication Required", False, "No authentication token available")
            return False
        
        # Generate another unique username for testing
        timestamp = int(time.time())
        new_username = f"testuser2_{timestamp}"
        
        # Test second username change (should be rate limited)
        username_update_data = {
            "username": new_username
        }
        
        result = self.make_request('PUT', '/auth/profile', data=username_update_data, use_auth=True)
        
        # Should return 429 (Too Many Requests) for rate limiting
        rate_limited = result['status_code'] == 429
        self.log_test(
            "USERNAME CHANGE RATE LIMITING",
            rate_limited,
            f"Username change properly rate limited with 429 status" if rate_limited else f"Username change rate limiting failed: got status {result['status_code']} instead of 429"
        )
        
        if not rate_limited:
            return False
        
        # Check if error message contains rate limiting information
        error_message = result['data'].get('detail', '') if isinstance(result['data'], dict) else str(result['data'])
        has_rate_limit_message = 'Username can only be changed' in error_message or 'days' in error_message.lower()
        
        self.log_test(
            "RATE LIMIT ERROR MESSAGE",
            has_rate_limit_message,
            f"Rate limit message contains timing information: '{error_message}'" if has_rate_limit_message else f"Rate limit message unclear: '{error_message}'"
        )
        
        return has_rate_limit_message

    def test_xss_protection_javascript_protocol(self):
        """Test XSS protection against javascript: protocol"""
        print("\n=== TESTING XSS PROTECTION - JAVASCRIPT PROTOCOL ===")
        
        if not self.auth_token:
            self.log_test("XSS PROTECTION - Authentication Required", False, "No authentication token available")
            return False
        
        # Test javascript: protocol in various fields
        xss_payloads = [
            {"first_name": "javascript:alert('XSS')"},
            {"last_name": "javascript:alert('XSS')"},
            {"username": "javascript:alert('XSS')"}
        ]
        
        blocked_count = 0
        total_tests = len(xss_payloads)
        
        for i, payload in enumerate(xss_payloads):
            field_name = list(payload.keys())[0]
            field_value = list(payload.values())[0]
            
            result = self.make_request('PUT', '/auth/profile', data=payload, use_auth=True)
            
            # XSS should be blocked (either sanitized or rejected)
            if result['success']:
                # Check if the dangerous content was sanitized
                profile_result = self.make_request('GET', '/auth/me', use_auth=True)
                if profile_result['success']:
                    profile_data = profile_result['data']
                    field_value_in_profile = profile_data.get(field_name, '')
                    
                    # Check if javascript: protocol was removed/sanitized
                    is_sanitized = 'javascript:' not in field_value_in_profile.lower()
                    if is_sanitized:
                        blocked_count += 1
                        self.log_test(
                            f"XSS PROTECTION - {field_name.upper()} JAVASCRIPT PROTOCOL",
                            True,
                            f"Javascript protocol sanitized in {field_name}: '{field_value}' → '{field_value_in_profile}'"
                        )
                    else:
                        self.log_test(
                            f"XSS PROTECTION - {field_name.upper()} JAVASCRIPT PROTOCOL",
                            False,
                            f"Javascript protocol NOT sanitized in {field_name}: '{field_value_in_profile}'"
                        )
            else:
                # Request was rejected, which is also good XSS protection
                blocked_count += 1
                self.log_test(
                    f"XSS PROTECTION - {field_name.upper()} JAVASCRIPT PROTOCOL",
                    True,
                    f"Javascript protocol blocked in {field_name}: request rejected with status {result['status_code']}"
                )
        
        protection_rate = (blocked_count / total_tests) * 100
        overall_success = protection_rate >= 100  # All should be blocked
        
        self.log_test(
            "XSS PROTECTION - JAVASCRIPT PROTOCOL OVERALL",
            overall_success,
            f"Javascript protocol protection: {blocked_count}/{total_tests} tests blocked ({protection_rate:.1f}%)"
        )
        
        return overall_success

    def test_xss_protection_standard_payloads(self):
        """Test XSS protection against standard XSS payloads"""
        print("\n=== TESTING XSS PROTECTION - STANDARD PAYLOADS ===")
        
        if not self.auth_token:
            self.log_test("XSS PROTECTION STANDARD - Authentication Required", False, "No authentication token available")
            return False
        
        # Test standard XSS payloads
        xss_payloads = [
            {"first_name": "<script>alert('XSS')</script>"},
            {"last_name": "<img src=x onerror=alert('XSS')>"},
            {"username": "<svg onload=alert('XSS')>"}
        ]
        
        blocked_count = 0
        total_tests = len(xss_payloads)
        
        for payload in xss_payloads:
            field_name = list(payload.keys())[0]
            field_value = list(payload.values())[0]
            
            result = self.make_request('PUT', '/auth/profile', data=payload, use_auth=True)
            
            # XSS should be blocked or sanitized
            if result['success']:
                # Check if the dangerous content was sanitized
                profile_result = self.make_request('GET', '/auth/me', use_auth=True)
                if profile_result['success']:
                    profile_data = profile_result['data']
                    field_value_in_profile = profile_data.get(field_name, '')
                    
                    # Check if dangerous tags were removed/sanitized
                    dangerous_tags = ['<script', '<img', '<svg', 'onerror', 'onload', 'alert(']
                    is_sanitized = not any(tag.lower() in field_value_in_profile.lower() for tag in dangerous_tags)
                    
                    if is_sanitized:
                        blocked_count += 1
                        self.log_test(
                            f"XSS PROTECTION - {field_name.upper()} STANDARD PAYLOAD",
                            True,
                            f"XSS payload sanitized in {field_name}: dangerous content removed"
                        )
                    else:
                        self.log_test(
                            f"XSS PROTECTION - {field_name.upper()} STANDARD PAYLOAD",
                            False,
                            f"XSS payload NOT sanitized in {field_name}: '{field_value_in_profile}'"
                        )
            else:
                # Request was rejected, which is also good XSS protection
                blocked_count += 1
                self.log_test(
                    f"XSS PROTECTION - {field_name.upper()} STANDARD PAYLOAD",
                    True,
                    f"XSS payload blocked in {field_name}: request rejected with status {result['status_code']}"
                )
        
        protection_rate = (blocked_count / total_tests) * 100
        overall_success = protection_rate >= 100  # All should be blocked
        
        self.log_test(
            "XSS PROTECTION - STANDARD PAYLOADS OVERALL",
            overall_success,
            f"Standard XSS payload protection: {blocked_count}/{total_tests} tests blocked ({protection_rate:.1f}%)"
        )
        
        return overall_success

    def test_profile_data_json_field_usage(self):
        """Test that the system is using profile_data JSON field for rate limiting"""
        print("\n=== TESTING PROFILE_DATA JSON FIELD USAGE ===")
        
        if not self.auth_token:
            self.log_test("PROFILE_DATA JSON FIELD - Authentication Required", False, "No authentication token available")
            return False
        
        # Get current profile to check if profile_data field exists and contains rate limiting info
        result = self.make_request('GET', '/auth/me', use_auth=True)
        
        if not result['success']:
            self.log_test(
                "PROFILE_DATA JSON FIELD CHECK",
                False,
                f"Failed to get profile data: {result.get('error', 'Unknown error')}"
            )
            return False
        
        profile_data = result['data']
        
        # Check if profile_data field exists (this indicates the JSON field approach is being used)
        has_profile_data_field = 'profile_data' in profile_data
        
        self.log_test(
            "PROFILE_DATA JSON FIELD EXISTS",
            has_profile_data_field,
            f"profile_data JSON field present in user profile" if has_profile_data_field else "profile_data JSON field not found in user profile"
        )
        
        # If profile_data exists, check if it contains rate limiting information
        if has_profile_data_field:
            profile_data_content = profile_data.get('profile_data', {})
            if isinstance(profile_data_content, str):
                try:
                    profile_data_content = json.loads(profile_data_content)
                except:
                    profile_data_content = {}
            
            has_username_change_timestamp = 'last_username_change' in profile_data_content
            
            self.log_test(
                "PROFILE_DATA CONTAINS RATE LIMITING INFO",
                has_username_change_timestamp,
                f"profile_data contains last_username_change timestamp" if has_username_change_timestamp else "profile_data does not contain rate limiting information"
            )
            
            return has_username_change_timestamp
        
        return has_profile_data_field

    def run_comprehensive_username_rate_limiting_test(self):
        """Run comprehensive username rate limiting and XSS protection tests"""
        print("\n🔐 STARTING USERNAME CHANGE RATE LIMITING & XSS PROTECTION TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("Testing updated system that uses profile_data JSON field")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Basic Connectivity", self.test_basic_connectivity),
            ("User Authentication", self.test_user_authentication),
            ("Basic Profile Updates", self.test_basic_profile_updates),
            ("First Username Change", self.test_first_username_change),
            ("Username Change Rate Limiting", self.test_second_username_change_rate_limiting),
            ("XSS Protection - Javascript Protocol", self.test_xss_protection_javascript_protocol),
            ("XSS Protection - Standard Payloads", self.test_xss_protection_standard_payloads),
            ("Profile Data JSON Field Usage", self.test_profile_data_json_field_usage)
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
        print("🔐 USERNAME CHANGE RATE LIMITING & XSS PROTECTION TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze results for specific functionality
        auth_tests_passed = sum(1 for result in self.test_results if result['success'] and 'AUTHENTICATION' in result['test'])
        profile_tests_passed = sum(1 for result in self.test_results if result['success'] and 'PROFILE' in result['test'])
        username_tests_passed = sum(1 for result in self.test_results if result['success'] and 'USERNAME' in result['test'])
        xss_tests_passed = sum(1 for result in self.test_results if result['success'] and 'XSS' in result['test'])
        
        print(f"\n🔍 SYSTEM ANALYSIS:")
        print(f"Authentication Tests Passed: {auth_tests_passed}")
        print(f"Profile Update Tests Passed: {profile_tests_passed}")
        print(f"Username Rate Limiting Tests Passed: {username_tests_passed}")
        print(f"XSS Protection Tests Passed: {xss_tests_passed}")
        
        if success_rate >= 90:
            print("\n✅ USERNAME CHANGE RATE LIMITING & XSS PROTECTION: SUCCESS")
            print("   ✅ Profile update endpoint working without database schema errors")
            print("   ✅ Username change rate limiting enforced with 7-day restriction")
            print("   ✅ Clear error messages for rate limiting violations (429 errors)")
            print("   ✅ Enhanced XSS protection blocking dangerous protocols")
            print("   ✅ All core profile functionality preserved")
            print("   The database fix is working correctly!")
        elif success_rate >= 75:
            print("\n⚠️ USERNAME CHANGE RATE LIMITING & XSS PROTECTION: MOSTLY WORKING")
            print("   Some issues detected but core functionality operational")
        else:
            print("\n❌ USERNAME CHANGE RATE LIMITING & XSS PROTECTION: ISSUES DETECTED")
            print("   Significant issues found in implementation")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 90

def main():
    """Run Username Rate Limiting & XSS Protection Tests"""
    print("🔐 STARTING USERNAME CHANGE RATE LIMITING & XSS PROTECTION BACKEND TESTING")
    print("=" * 80)
    
    tester = UsernameRateLimitingTester()
    
    try:
        # Run the comprehensive tests
        success = tester.run_comprehensive_username_rate_limiting_test()
        
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
        
        return success_rate >= 90
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)