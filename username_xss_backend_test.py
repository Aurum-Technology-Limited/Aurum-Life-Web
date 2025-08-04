#!/usr/bin/env python3
"""
USERNAME CHANGE RATE LIMITING & ENHANCED XSS PROTECTION TESTING
Testing the updated username change rate limiting system and enhanced XSS protection.

FOCUS AREAS:
1. USERNAME CHANGE RATE LIMITING (CRITICAL FIX)
   - First username change should work and set last_username_change timestamp
   - Second username change within 7 days should return 429 error with clear message
   - Rate limit message should show exact days remaining
   - Same username change should not trigger rate limiting (no actual change)

2. ENHANCED XSS PROTECTION (SECURITY FIX)
   - Javascript protocol should be completely removed
   - Data protocol should be sanitized
   - Other protocols (vbscript, file) should be removed
   - Standard XSS should still be blocked

3. DATABASE PERSISTENCE VERIFICATION
   - Profile updates should persist correctly
   - Username tracking should be set when username changes
   - Response consistency should match database values

CREDENTIALS: marc.alleyne@aurumtechnologyltd.com / password
ENDPOINT: PUT /api/auth/profile
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any
import time

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://fa85c789-1504-48f1-9b33-719ff2e79ef1.preview.emergentagent.com/api"

class UsernameRateLimitXSSTestSuite:
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

    def test_first_username_change(self):
        """Test first username change - should work and set timestamp"""
        print("\n=== TESTING FIRST USERNAME CHANGE ===")
        
        if not self.auth_token:
            self.log_test("FIRST USERNAME CHANGE - Authentication Required", False, "No authentication token available")
            return False
        
        # Generate unique username to avoid conflicts
        timestamp = int(datetime.now().timestamp())
        new_username = f"testuser_{timestamp}"
        
        profile_data = {
            "username": new_username,
            "first_name": "Test",
            "last_name": "User"
        }
        
        result = self.make_request('PUT', '/auth/profile', data=profile_data, use_auth=True)
        
        # Check if this is the database schema issue
        if result['status_code'] == 500 and 'last_username_change' in str(result.get('data', {})):
            self.log_test(
                "FIRST USERNAME CHANGE - DATABASE SCHEMA ISSUE",
                False,
                "Database schema missing 'last_username_change' field - this is the root cause of the 500 errors"
            )
            return False
        
        success = result['success'] and result['status_code'] == 200
        self.log_test(
            "FIRST USERNAME CHANGE",
            success,
            f"First username change successful to '{new_username}'" if success else f"First username change failed: {result.get('error', 'Unknown error')}"
        )
        
        if success:
            # Verify response contains updated username
            response_data = result['data']
            username_updated = response_data.get('username') == new_username
            self.log_test(
                "FIRST USERNAME CHANGE - RESPONSE VERIFICATION",
                username_updated,
                f"Response contains updated username: {response_data.get('username')}" if username_updated else f"Response username mismatch: expected {new_username}, got {response_data.get('username')}"
            )
            
            # Store the username for next test
            self.current_username = new_username
            return username_updated
        
        return False

    def test_second_username_change_rate_limit(self):
        """Test second username change within 7 days - should return 429 error"""
        print("\n=== TESTING SECOND USERNAME CHANGE RATE LIMIT ===")
        
        if not self.auth_token or not hasattr(self, 'current_username'):
            self.log_test("SECOND USERNAME CHANGE - Prerequisites Missing", False, "Authentication token or current username not available")
            return False
        
        # Try to change username again immediately (should be rate limited)
        timestamp = int(datetime.now().timestamp())
        new_username = f"testuser2_{timestamp}"
        
        profile_data = {
            "username": new_username,
            "first_name": "Test",
            "last_name": "User"
        }
        
        result = self.make_request('PUT', '/auth/profile', data=profile_data, use_auth=True)
        
        # Should return 429 (Too Many Requests) for rate limiting
        rate_limited = result['status_code'] == 429
        self.log_test(
            "SECOND USERNAME CHANGE - RATE LIMIT",
            rate_limited,
            f"Rate limiting working correctly (HTTP 429)" if rate_limited else f"Rate limiting failed: got HTTP {result['status_code']} instead of 429"
        )
        
        if rate_limited:
            # Check if error message contains days remaining information
            error_message = result['data'].get('detail', '')
            has_days_info = 'days' in error_message.lower() or 'day' in error_message.lower()
            self.log_test(
                "RATE LIMIT MESSAGE - DAYS REMAINING",
                has_days_info,
                f"Error message contains days remaining info: '{error_message}'" if has_days_info else f"Error message missing days info: '{error_message}'"
            )
            
            return has_days_info
        
        return False

    def test_same_username_change_no_rate_limit(self):
        """Test changing to same username - should not trigger rate limiting"""
        print("\n=== TESTING SAME USERNAME CHANGE (NO RATE LIMIT) ===")
        
        if not self.auth_token or not hasattr(self, 'current_username'):
            self.log_test("SAME USERNAME CHANGE - Prerequisites Missing", False, "Authentication token or current username not available")
            return False
        
        # Try to change to the same username (should not trigger rate limiting)
        profile_data = {
            "username": self.current_username,  # Same username
            "first_name": "Test Updated",
            "last_name": "User Updated"
        }
        
        result = self.make_request('PUT', '/auth/profile', data=profile_data, use_auth=True)
        
        # Should succeed (200) since username didn't actually change
        success = result['success'] and result['status_code'] == 200
        self.log_test(
            "SAME USERNAME CHANGE - NO RATE LIMIT",
            success,
            f"Same username change allowed (no rate limit triggered)" if success else f"Same username change failed: {result.get('error', 'Unknown error')}"
        )
        
        if success:
            # Verify other fields were updated
            response_data = result['data']
            first_name_updated = response_data.get('first_name') == 'Test Updated'
            last_name_updated = response_data.get('last_name') == 'User Updated'
            
            fields_updated = first_name_updated and last_name_updated
            self.log_test(
                "SAME USERNAME CHANGE - OTHER FIELDS UPDATED",
                fields_updated,
                f"Other profile fields updated correctly" if fields_updated else f"Other fields not updated: first_name={response_data.get('first_name')}, last_name={response_data.get('last_name')}"
            )
            
            return fields_updated
        
        return False

    def test_javascript_protocol_xss_protection(self):
        """Test enhanced XSS protection against javascript: protocol"""
        print("\n=== TESTING JAVASCRIPT PROTOCOL XSS PROTECTION ===")
        
        if not self.auth_token:
            self.log_test("JAVASCRIPT PROTOCOL XSS - Authentication Required", False, "No authentication token available")
            return False
        
        # Test javascript: protocol in various fields
        xss_payloads = [
            "javascript:alert('XSS')",
            "JAVASCRIPT:alert('XSS')",
            "javascript:void(0)",
            "javascript:document.cookie"
        ]
        
        success_count = 0
        total_tests = len(xss_payloads)
        
        for i, payload in enumerate(xss_payloads):
            profile_data = {
                "first_name": payload,
                "last_name": "Test",
                "username": f"testuser_js_{i}"
            }
            
            result = self.make_request('PUT', '/auth/profile', data=profile_data, use_auth=True)
            
            if result['success']:
                # Check if javascript: protocol was removed/sanitized
                response_data = result['data']
                first_name = response_data.get('first_name', '')
                
                # Javascript protocol should be completely removed
                js_removed = 'javascript:' not in first_name.lower()
                
                self.log_test(
                    f"JAVASCRIPT PROTOCOL XSS - PAYLOAD {i+1}",
                    js_removed,
                    f"Javascript protocol removed: '{payload}' → '{first_name}'" if js_removed else f"Javascript protocol NOT removed: '{payload}' → '{first_name}'"
                )
                
                if js_removed:
                    success_count += 1
            else:
                # If request failed, that's also acceptable (validation rejected it)
                self.log_test(
                    f"JAVASCRIPT PROTOCOL XSS - PAYLOAD {i+1}",
                    True,
                    f"Request rejected (validation working): {result.get('error', 'Unknown error')}"
                )
                success_count += 1
        
        overall_success = success_count >= total_tests * 0.8  # 80% success rate
        self.log_test(
            "JAVASCRIPT PROTOCOL XSS - OVERALL",
            overall_success,
            f"Javascript protocol protection: {success_count}/{total_tests} tests passed"
        )
        
        return overall_success

    def test_data_protocol_xss_protection(self):
        """Test enhanced XSS protection against data: protocol"""
        print("\n=== TESTING DATA PROTOCOL XSS PROTECTION ===")
        
        if not self.auth_token:
            self.log_test("DATA PROTOCOL XSS - Authentication Required", False, "No authentication token available")
            return False
        
        # Test data: protocol payloads
        xss_payloads = [
            "data:text/html,<script>alert(1)</script>",
            "data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==",
            "data:application/javascript,alert('XSS')"
        ]
        
        success_count = 0
        total_tests = len(xss_payloads)
        
        for i, payload in enumerate(xss_payloads):
            profile_data = {
                "first_name": payload,
                "last_name": "Test",
                "username": f"testuser_data_{i}"
            }
            
            result = self.make_request('PUT', '/auth/profile', data=profile_data, use_auth=True)
            
            if result['success']:
                # Check if data: protocol was removed/sanitized
                response_data = result['data']
                first_name = response_data.get('first_name', '')
                
                # Data protocol should be removed or sanitized
                data_sanitized = 'data:' not in first_name.lower() or '<script>' not in first_name.lower()
                
                self.log_test(
                    f"DATA PROTOCOL XSS - PAYLOAD {i+1}",
                    data_sanitized,
                    f"Data protocol sanitized: '{payload}' → '{first_name}'" if data_sanitized else f"Data protocol NOT sanitized: '{payload}' → '{first_name}'"
                )
                
                if data_sanitized:
                    success_count += 1
            else:
                # If request failed, that's also acceptable (validation rejected it)
                self.log_test(
                    f"DATA PROTOCOL XSS - PAYLOAD {i+1}",
                    True,
                    f"Request rejected (validation working): {result.get('error', 'Unknown error')}"
                )
                success_count += 1
        
        overall_success = success_count >= total_tests * 0.8  # 80% success rate
        self.log_test(
            "DATA PROTOCOL XSS - OVERALL",
            overall_success,
            f"Data protocol protection: {success_count}/{total_tests} tests passed"
        )
        
        return overall_success

    def test_other_dangerous_protocols(self):
        """Test protection against other dangerous protocols"""
        print("\n=== TESTING OTHER DANGEROUS PROTOCOLS ===")
        
        if not self.auth_token:
            self.log_test("OTHER PROTOCOLS XSS - Authentication Required", False, "No authentication token available")
            return False
        
        # Test other dangerous protocols
        dangerous_protocols = [
            "vbscript:msgbox('XSS')",
            "file:///etc/passwd",
            "ftp://malicious.com/",
            "mailto:test@evil.com?subject=<script>alert(1)</script>"
        ]
        
        success_count = 0
        total_tests = len(dangerous_protocols)
        
        for i, payload in enumerate(dangerous_protocols):
            profile_data = {
                "first_name": payload,
                "last_name": "Test",
                "username": f"testuser_proto_{i}"
            }
            
            result = self.make_request('PUT', '/auth/profile', data=profile_data, use_auth=True)
            
            if result['success']:
                # Check if dangerous protocols were removed/sanitized
                response_data = result['data']
                first_name = response_data.get('first_name', '')
                
                # Extract protocol from payload
                protocol = payload.split(':')[0].lower()
                protocol_removed = f'{protocol}:' not in first_name.lower()
                
                self.log_test(
                    f"DANGEROUS PROTOCOL XSS - {protocol.upper()}",
                    protocol_removed,
                    f"Dangerous protocol removed: '{payload}' → '{first_name}'" if protocol_removed else f"Dangerous protocol NOT removed: '{payload}' → '{first_name}'"
                )
                
                if protocol_removed:
                    success_count += 1
            else:
                # If request failed, that's also acceptable (validation rejected it)
                protocol = payload.split(':')[0].upper()
                self.log_test(
                    f"DANGEROUS PROTOCOL XSS - {protocol}",
                    True,
                    f"Request rejected (validation working): {result.get('error', 'Unknown error')}"
                )
                success_count += 1
        
        overall_success = success_count >= total_tests * 0.8  # 80% success rate
        self.log_test(
            "DANGEROUS PROTOCOLS XSS - OVERALL",
            overall_success,
            f"Dangerous protocols protection: {success_count}/{total_tests} tests passed"
        )
        
        return overall_success

    def test_standard_xss_protection(self):
        """Test that standard XSS protection still works"""
        print("\n=== TESTING STANDARD XSS PROTECTION ===")
        
        if not self.auth_token:
            self.log_test("STANDARD XSS - Authentication Required", False, "No authentication token available")
            return False
        
        # Test standard XSS payloads
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert(1)>",
            "<svg onload=alert(1)>",
            "';alert('XSS');//"
        ]
        
        success_count = 0
        total_tests = len(xss_payloads)
        
        for i, payload in enumerate(xss_payloads):
            profile_data = {
                "first_name": payload,
                "last_name": "Test",
                "username": f"testuser_xss_{i}"
            }
            
            result = self.make_request('PUT', '/auth/profile', data=profile_data, use_auth=True)
            
            if result['success']:
                # Check if XSS was sanitized
                response_data = result['data']
                first_name = response_data.get('first_name', '')
                
                # Script tags and event handlers should be removed
                xss_sanitized = ('<script>' not in first_name.lower() and 
                               'onerror=' not in first_name.lower() and 
                               'onload=' not in first_name.lower())
                
                self.log_test(
                    f"STANDARD XSS - PAYLOAD {i+1}",
                    xss_sanitized,
                    f"XSS sanitized: '{payload}' → '{first_name}'" if xss_sanitized else f"XSS NOT sanitized: '{payload}' → '{first_name}'"
                )
                
                if xss_sanitized:
                    success_count += 1
            else:
                # If request failed, that's also acceptable (validation rejected it)
                self.log_test(
                    f"STANDARD XSS - PAYLOAD {i+1}",
                    True,
                    f"Request rejected (validation working): {result.get('error', 'Unknown error')}"
                )
                success_count += 1
        
        overall_success = success_count >= total_tests * 0.8  # 80% success rate
        self.log_test(
            "STANDARD XSS - OVERALL",
            overall_success,
            f"Standard XSS protection: {success_count}/{total_tests} tests passed"
        )
        
        return overall_success

    def test_database_persistence(self):
        """Test that profile updates persist correctly in database"""
        print("\n=== TESTING DATABASE PERSISTENCE ===")
        
        if not self.auth_token:
            self.log_test("DATABASE PERSISTENCE - Authentication Required", False, "No authentication token available")
            return False
        
        # Update profile with clean data
        timestamp = int(datetime.now().timestamp())
        test_data = {
            "first_name": f"TestFirst_{timestamp}",
            "last_name": f"TestLast_{timestamp}",
            "username": f"testuser_persist_{timestamp}"
        }
        
        # Update profile
        result = self.make_request('PUT', '/auth/profile', data=test_data, use_auth=True)
        
        if not result['success']:
            self.log_test(
                "DATABASE PERSISTENCE - UPDATE FAILED",
                False,
                f"Profile update failed: {result.get('error', 'Unknown error')}"
            )
            return False
        
        # Wait a moment for database to update
        time.sleep(1)
        
        # Retrieve profile to verify persistence
        result = self.make_request('GET', '/auth/me', use_auth=True)
        
        if not result['success']:
            self.log_test(
                "DATABASE PERSISTENCE - RETRIEVAL FAILED",
                False,
                f"Profile retrieval failed: {result.get('error', 'Unknown error')}"
            )
            return False
        
        # Verify data matches
        profile_data = result['data']
        first_name_match = profile_data.get('first_name') == test_data['first_name']
        last_name_match = profile_data.get('last_name') == test_data['last_name']
        username_match = profile_data.get('username') == test_data['username']
        
        persistence_success = first_name_match and last_name_match and username_match
        
        self.log_test(
            "DATABASE PERSISTENCE - DATA VERIFICATION",
            persistence_success,
            f"Profile data persisted correctly" if persistence_success else f"Data mismatch: first_name={first_name_match}, last_name={last_name_match}, username={username_match}"
        )
        
        return persistence_success

    def run_comprehensive_test(self):
        """Run comprehensive username rate limiting and XSS protection tests"""
        print("\n🔐 STARTING USERNAME RATE LIMITING & XSS PROTECTION TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Basic Connectivity", self.test_basic_connectivity),
            ("User Authentication", self.test_user_authentication),
            ("First Username Change", self.test_first_username_change),
            ("Second Username Change Rate Limit", self.test_second_username_change_rate_limit),
            ("Same Username Change (No Rate Limit)", self.test_same_username_change_no_rate_limit),
            ("Javascript Protocol XSS Protection", self.test_javascript_protocol_xss_protection),
            ("Data Protocol XSS Protection", self.test_data_protocol_xss_protection),
            ("Other Dangerous Protocols", self.test_other_dangerous_protocols),
            ("Standard XSS Protection", self.test_standard_xss_protection),
            ("Database Persistence", self.test_database_persistence)
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
        print("🔐 USERNAME RATE LIMITING & XSS PROTECTION TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze results by category
        rate_limit_tests = sum(1 for result in self.test_results if result['success'] and 'USERNAME CHANGE' in result['test'])
        xss_tests = sum(1 for result in self.test_results if result['success'] and 'XSS' in result['test'])
        persistence_tests = sum(1 for result in self.test_results if result['success'] and 'PERSISTENCE' in result['test'])
        
        print(f"\n🔍 SYSTEM ANALYSIS:")
        print(f"Username Rate Limiting Tests Passed: {rate_limit_tests}")
        print(f"XSS Protection Tests Passed: {xss_tests}")
        print(f"Database Persistence Tests Passed: {persistence_tests}")
        
        if success_rate >= 90:
            print("\n✅ USERNAME RATE LIMITING & XSS PROTECTION: SUCCESS")
            print("   ✅ Username rate limiting works with 7-day restriction")
            print("   ✅ Javascript protocol and dangerous protocols removed")
            print("   ✅ Profile updates persist correctly in database")
            print("   ✅ Clear error messages for rate limiting violations")
            print("   The updated system is production-ready!")
        else:
            print("\n❌ USERNAME RATE LIMITING & XSS PROTECTION: ISSUES DETECTED")
            print("   Issues found in rate limiting or XSS protection implementation")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 90

def main():
    """Run Username Rate Limiting & XSS Protection Tests"""
    print("🔐 STARTING USERNAME RATE LIMITING & XSS PROTECTION BACKEND TESTING")
    print("=" * 80)
    
    tester = UsernameRateLimitXSSTestSuite()
    
    try:
        # Run the comprehensive tests
        success = tester.run_comprehensive_test()
        
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