#!/usr/bin/env python3
"""
LOGIN COMPATIBILITY BACKEND TEST
Testing login compatibility via /api/auth/login and /api/auth/me endpoints.

SPECIFIC REQUIREMENTS FROM REVIEW REQUEST:
1. Attempt login via /api/auth/login using a recently created user
2. Verify that the endpoint returns an access_token (either Supabase session token or legacy JWT)
3. Call /api/auth/me using that token and confirm 200
4. Use base https://productivity-hub-23.preview.emergentagent.com
5. If login fails, capture status code and response detail

CREDENTIALS TO TEST:
- marc.alleyne@aurumtechnologyltd.com / password123 (existing user)
- nav.test@aurumlife.com / testpassword123 (existing user)
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any
import time

# Configuration - Using the specified base URL from review request
BASE_URL = "https://productivity-hub-23.preview.emergentagent.com"
API_BASE = f"{BASE_URL}/api"

class LoginCompatibilityTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        
        # Test users to try (recently created/existing users)
        self.test_users = [
            {"email": "marc.alleyne@aurumtechnologyltd.com", "password": "password123"},
            {"email": "nav.test@aurumlife.com", "password": "testpassword123"}
        ]
        
    def log_test(self, test_name: str, success: bool, message: str = "", data: Any = None, status_code: int = None):
        """Log test results with detailed information"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'status_code': status_code
        }
        if data:
            result['data'] = data
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        status_info = f" (HTTP {status_code})" if status_code else ""
        print(f"{status} {test_name}{status_info}: {message}")
        if data and not success:
            print(f"   Response Data: {json.dumps(data, indent=2, default=str)}")

    def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None, timeout: int = 30) -> Dict:
        """Make HTTP request with comprehensive error handling"""
        url = f"{API_BASE}{endpoint}"
        request_headers = {"Content-Type": "application/json"}
        if headers:
            request_headers.update(headers)
        
        try:
            start_time = time.time()
            
            if method.upper() == 'GET':
                response = self.session.get(url, headers=request_headers, timeout=timeout)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, headers=request_headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response_time = round((time.time() - start_time) * 1000, 0)  # ms
            
            # Try to parse JSON response
            try:
                response_data = response.json() if response.content else {}
            except:
                response_data = {"raw_content": response.text[:500] if response.text else "No content"}
                
            return {
                'success': response.status_code < 400,
                'status_code': response.status_code,
                'data': response_data,
                'response_time': response_time,
                'error': None if response.status_code < 400 else f"HTTP {response.status_code}: {response_data}"
            }
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            status_code = None
            
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
                try:
                    error_data = e.response.json()
                    error_msg += f" - Response: {error_data}"
                except:
                    error_msg += f" - Response: {e.response.text[:200]}"
            
            return {
                'success': False,
                'error': error_msg,
                'status_code': status_code,
                'data': {},
                'response_time': 0
            }

    def test_backend_connectivity(self):
        """Test basic connectivity to the backend"""
        print("\n=== TESTING BACKEND CONNECTIVITY ===")
        
        # Test the root endpoint
        try:
            response = self.session.get(BASE_URL, timeout=30)
            if response.status_code < 400:
                self.log_test(
                    "BACKEND CONNECTIVITY",
                    True,
                    f"Backend accessible at {BASE_URL}",
                    status_code=response.status_code
                )
                return True
            else:
                self.log_test(
                    "BACKEND CONNECTIVITY",
                    False,
                    f"Backend returned error status",
                    status_code=response.status_code
                )
                return False
        except Exception as e:
            self.log_test(
                "BACKEND CONNECTIVITY",
                False,
                f"Backend not accessible: {str(e)}"
            )
            return False

    def test_login_compatibility(self):
        """Test login compatibility with multiple user accounts"""
        print("\n=== TESTING LOGIN COMPATIBILITY ===")
        
        successful_logins = 0
        
        for i, user_creds in enumerate(self.test_users, 1):
            email = user_creds["email"]
            password = user_creds["password"]
            
            print(f"\n--- Testing User {i}: {email} ---")
            
            # Attempt login
            login_data = {
                "email": email,
                "password": password
            }
            
            result = self.make_request('POST', '/auth/login', data=login_data)
            
            if result['success']:
                token_data = result['data']
                access_token = token_data.get('access_token')
                token_type = token_data.get('token_type', 'bearer')
                
                if access_token:
                    self.log_test(
                        f"LOGIN - {email}",
                        True,
                        f"Login successful, received access_token (type: {token_type})",
                        status_code=result['status_code']
                    )
                    
                    # Store token for /api/auth/me test
                    self.auth_token = access_token
                    successful_logins += 1
                    
                    # Test /api/auth/me with this token
                    if self.test_auth_me_endpoint(email):
                        # If we got a successful login and /me call, we can stop here
                        return True
                else:
                    self.log_test(
                        f"LOGIN - {email}",
                        False,
                        "Login response missing access_token",
                        data=token_data,
                        status_code=result['status_code']
                    )
            else:
                self.log_test(
                    f"LOGIN - {email}",
                    False,
                    f"Login failed: {result.get('error', 'Unknown error')}",
                    data=result['data'],
                    status_code=result['status_code']
                )
        
        return successful_logins > 0

    def test_auth_me_endpoint(self, user_email: str):
        """Test /api/auth/me endpoint with the obtained token"""
        print(f"\n=== TESTING /api/auth/me WITH TOKEN FOR {user_email} ===")
        
        if not self.auth_token:
            self.log_test(
                "AUTH/ME ENDPOINT",
                False,
                "No authentication token available"
            )
            return False
        
        # Test /api/auth/me with Bearer token
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        result = self.make_request('GET', '/auth/me', headers=headers)
        
        if result['success'] and result['status_code'] == 200:
            user_data = result['data']
            user_id = user_data.get('id')
            returned_email = user_data.get('email')
            
            self.log_test(
                "AUTH/ME ENDPOINT",
                True,
                f"Successfully retrieved user profile (ID: {user_id}, Email: {returned_email})",
                status_code=result['status_code']
            )
            
            # Verify the email matches
            if returned_email == user_email:
                self.log_test(
                    "AUTH/ME EMAIL VERIFICATION",
                    True,
                    f"Email matches login credentials: {returned_email}"
                )
            else:
                self.log_test(
                    "AUTH/ME EMAIL VERIFICATION",
                    False,
                    f"Email mismatch - Expected: {user_email}, Got: {returned_email}"
                )
            
            return True
        else:
            self.log_test(
                "AUTH/ME ENDPOINT",
                False,
                f"Failed to retrieve user profile: {result.get('error', 'Unknown error')}",
                data=result['data'],
                status_code=result['status_code']
            )
            return False

    def test_token_format_analysis(self):
        """Analyze the token format to determine if it's Supabase or legacy JWT"""
        print("\n=== ANALYZING TOKEN FORMAT ===")
        
        if not self.auth_token:
            self.log_test(
                "TOKEN FORMAT ANALYSIS",
                False,
                "No token available for analysis"
            )
            return
        
        token_parts = self.auth_token.split('.')
        
        if len(token_parts) == 3:
            # Looks like JWT format
            try:
                import base64
                # Decode header (first part)
                header_padded = token_parts[0] + '=' * (4 - len(token_parts[0]) % 4)
                header_decoded = base64.urlsafe_b64decode(header_padded)
                header_json = json.loads(header_decoded)
                
                self.log_test(
                    "TOKEN FORMAT ANALYSIS",
                    True,
                    f"Token appears to be JWT format with algorithm: {header_json.get('alg', 'unknown')}",
                    data={"header": header_json, "token_length": len(self.auth_token)}
                )
            except Exception as e:
                self.log_test(
                    "TOKEN FORMAT ANALYSIS",
                    True,
                    f"Token appears to be JWT format (3 parts) but header decode failed: {str(e)}",
                    data={"token_length": len(self.auth_token)}
                )
        else:
            # Could be Supabase session token or other format
            self.log_test(
                "TOKEN FORMAT ANALYSIS",
                True,
                f"Token format: {len(token_parts)} parts, length: {len(self.auth_token)} chars (possibly Supabase session token)",
                data={"token_parts": len(token_parts), "token_length": len(self.auth_token)}
            )

    def run_comprehensive_login_test(self):
        """Run comprehensive login compatibility test"""
        print("\n🔐 STARTING LOGIN COMPATIBILITY BACKEND TEST")
        print("=" * 80)
        print(f"Base URL: {BASE_URL}")
        print(f"API Base: {API_BASE}")
        print(f"Test Users: {len(self.test_users)}")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Backend Connectivity", self.test_backend_connectivity),
            ("Login Compatibility", self.test_login_compatibility),
            ("Token Format Analysis", self.test_token_format_analysis)
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
        print("🔐 LOGIN COMPATIBILITY TEST SUMMARY")
        print("=" * 80)
        print(f"Base URL: {BASE_URL}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze specific login results
        login_tests = [r for r in self.test_results if 'LOGIN -' in r['test']]
        auth_me_tests = [r for r in self.test_results if 'AUTH/ME' in r['test']]
        
        successful_logins = sum(1 for r in login_tests if r['success'])
        successful_auth_me = sum(1 for r in auth_me_tests if r['success'])
        
        print(f"\n🔍 DETAILED ANALYSIS:")
        print(f"Login Attempts: {len(login_tests)}")
        print(f"Successful Logins: {successful_logins}")
        print(f"Auth/Me Tests: {len(auth_me_tests)}")
        print(f"Successful Auth/Me: {successful_auth_me}")
        
        # Determine overall system status
        if successful_logins > 0 and successful_auth_me > 0:
            print("\n✅ LOGIN COMPATIBILITY: SUCCESS")
            print("   ✅ /api/auth/login endpoint working")
            print("   ✅ Access token generation functional")
            print("   ✅ /api/auth/me endpoint accessible with token")
            print("   ✅ Token authentication flow operational")
            print("   The login compatibility system is working correctly!")
        elif successful_logins > 0:
            print("\n⚠️ LOGIN COMPATIBILITY: PARTIAL SUCCESS")
            print("   ✅ /api/auth/login endpoint working")
            print("   ✅ Access token generation functional")
            print("   ❌ /api/auth/me endpoint issues detected")
            print("   Login works but token validation may have issues")
        else:
            print("\n❌ LOGIN COMPATIBILITY: FAILURE")
            print("   ❌ /api/auth/login endpoint not working")
            print("   Issues detected in login system")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                status_info = f" (HTTP {test['status_code']})" if test.get('status_code') else ""
                print(f"   ❌ {test['test']}{status_info}: {test['message']}")
        
        return successful_logins > 0 and successful_auth_me > 0

def main():
    """Run Login Compatibility Test"""
    print("🔐 STARTING LOGIN COMPATIBILITY BACKEND TESTING")
    print("=" * 80)
    
    tester = LoginCompatibilityTester()
    
    try:
        # Run the comprehensive login compatibility test
        success = tester.run_comprehensive_login_test()
        
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
        
        return success
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)