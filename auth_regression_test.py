#!/usr/bin/env python3
"""
AUTH REGRESSION TESTING - SPA CATCH-ALL ORDER FIX
Testing auth endpoints after SPA catch-all route order fix.

FOCUS AREAS:
1. OPTIONS /api/auth/login and /api/auth/me with Origin to confirm CORS headers present
2. POST /api/auth/login with known test account; expect 200 and access_token
3. GET /api/auth/me with Bearer token; expect 200 user profile

EXPECTED BEHAVIOR:
- CORS headers should be present for OPTIONS requests
- Login should work with existing test credentials
- Profile endpoint should return user data with valid token

CREDENTIALS: marc.alleyne@aurumtechnologyltd.com / password123
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://fcbe964d-a00c-4624-8b03-88a109fb0408.preview.emergentagent.com/api"

class AuthRegressionTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        # Use the specified test credentials
        self.test_user_email = "marc.alleyne@aurumtechnologyltd.com"
        self.test_user_password = "password123"
        
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

    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None, 
                    use_auth: bool = False, origin: str = None) -> Dict:
        """Make HTTP request with error handling and optional authentication"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        # Add Origin header for CORS testing
        if origin:
            headers["Origin"] = origin
        
        # Add authentication header if token is available and requested
        if use_auth and self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, headers=headers, timeout=30)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, params=params, headers=headers, timeout=30)
            elif method.upper() == 'OPTIONS':
                response = self.session.options(url, headers=headers, timeout=30)
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
                'headers': dict(response.headers),
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
                'headers': {},
                'response': getattr(e, 'response', None)
            }

    def test_cors_headers_login(self):
        """Test 1: OPTIONS /api/auth/login with Origin to confirm CORS headers present"""
        print("\n=== TESTING CORS HEADERS FOR LOGIN ENDPOINT ===")
        
        # Test OPTIONS request with Origin header
        origin = "https://datahierarchy-app.preview.emergentagent.com"
        result = self.make_request('OPTIONS', '/auth/login', origin=origin)
        
        cors_headers_present = False
        cors_details = []
        
        if result['success'] or result['status_code'] in [200, 204]:
            headers = result['headers']
            
            # Check for CORS headers
            cors_headers = {
                'Access-Control-Allow-Origin': headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': headers.get('Access-Control-Allow-Headers'),
                'Access-Control-Allow-Credentials': headers.get('Access-Control-Allow-Credentials')
            }
            
            # Check if essential CORS headers are present
            has_origin = cors_headers['Access-Control-Allow-Origin'] is not None
            has_methods = cors_headers['Access-Control-Allow-Methods'] is not None
            has_headers = cors_headers['Access-Control-Allow-Headers'] is not None
            
            cors_headers_present = has_origin or has_methods or has_headers
            
            for header, value in cors_headers.items():
                if value:
                    cors_details.append(f"{header}: {value}")
        
        self.log_test(
            "OPTIONS /api/auth/login CORS Headers",
            cors_headers_present,
            f"CORS headers present: {', '.join(cors_details)}" if cors_headers_present else f"No CORS headers found. Status: {result.get('status_code', 'Unknown')}"
        )
        
        return cors_headers_present

    def test_cors_headers_me(self):
        """Test 2: OPTIONS /api/auth/me with Origin to confirm CORS headers present"""
        print("\n=== TESTING CORS HEADERS FOR ME ENDPOINT ===")
        
        # Test OPTIONS request with Origin header
        origin = "https://datahierarchy-app.preview.emergentagent.com"
        result = self.make_request('OPTIONS', '/auth/me', origin=origin)
        
        cors_headers_present = False
        cors_details = []
        
        if result['success'] or result['status_code'] in [200, 204]:
            headers = result['headers']
            
            # Check for CORS headers
            cors_headers = {
                'Access-Control-Allow-Origin': headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': headers.get('Access-Control-Allow-Headers'),
                'Access-Control-Allow-Credentials': headers.get('Access-Control-Allow-Credentials')
            }
            
            # Check if essential CORS headers are present
            has_origin = cors_headers['Access-Control-Allow-Origin'] is not None
            has_methods = cors_headers['Access-Control-Allow-Methods'] is not None
            has_headers = cors_headers['Access-Control-Allow-Headers'] is not None
            
            cors_headers_present = has_origin or has_methods or has_headers
            
            for header, value in cors_headers.items():
                if value:
                    cors_details.append(f"{header}: {value}")
        
        self.log_test(
            "OPTIONS /api/auth/me CORS Headers",
            cors_headers_present,
            f"CORS headers present: {', '.join(cors_details)}" if cors_headers_present else f"No CORS headers found. Status: {result.get('status_code', 'Unknown')}"
        )
        
        return cors_headers_present

    def test_login_with_known_account(self):
        """Test 3: POST /api/auth/login with known test account; expect 200 and access_token"""
        print("\n=== TESTING LOGIN WITH KNOWN TEST ACCOUNT ===")
        
        # Login with specified credentials
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        
        login_success = False
        access_token_present = False
        
        if result['success'] and result['status_code'] == 200:
            token_data = result['data']
            access_token = token_data.get('access_token')
            token_type = token_data.get('token_type')
            
            if access_token:
                self.auth_token = access_token
                access_token_present = True
                login_success = True
                
                self.log_test(
                    "POST /api/auth/login Success",
                    True,
                    f"Login successful with {self.test_user_email}. Token type: {token_type}, Token length: {len(access_token) if access_token else 0}"
                )
            else:
                self.log_test(
                    "POST /api/auth/login Token",
                    False,
                    f"Login returned 200 but no access_token found. Response keys: {list(token_data.keys())}"
                )
        else:
            self.log_test(
                "POST /api/auth/login Failed",
                False,
                f"Login failed with status {result.get('status_code', 'Unknown')}: {result.get('error', 'Unknown error')}"
            )
        
        return login_success and access_token_present

    def test_profile_with_bearer_token(self):
        """Test 4: GET /api/auth/me with Bearer token; expect 200 user profile"""
        print("\n=== TESTING PROFILE ENDPOINT WITH BEARER TOKEN ===")
        
        if not self.auth_token:
            self.log_test(
                "GET /api/auth/me - No Token",
                False,
                "No authentication token available from login test"
            )
            return False
        
        # Test GET /api/auth/me with Bearer token
        result = self.make_request('GET', '/auth/me', use_auth=True)
        
        profile_success = False
        user_data_present = False
        
        if result['success'] and result['status_code'] == 200:
            user_data = result['data']
            
            # Check for expected user profile fields
            expected_fields = ['id', 'email']
            present_fields = [field for field in expected_fields if field in user_data]
            
            if len(present_fields) >= 1:  # At least one expected field present
                user_data_present = True
                profile_success = True
                
                user_email = user_data.get('email', 'Unknown')
                user_id = user_data.get('id', 'Unknown')
                
                self.log_test(
                    "GET /api/auth/me Success",
                    True,
                    f"Profile retrieved successfully. Email: {user_email}, ID: {user_id}, Fields: {list(user_data.keys())}"
                )
            else:
                self.log_test(
                    "GET /api/auth/me Data",
                    False,
                    f"Profile returned 200 but missing expected fields. Available fields: {list(user_data.keys())}"
                )
        else:
            self.log_test(
                "GET /api/auth/me Failed",
                False,
                f"Profile request failed with status {result.get('status_code', 'Unknown')}: {result.get('error', 'Unknown error')}"
            )
        
        return profile_success and user_data_present

    def test_404_detection(self):
        """Test 5: Check for any 404 errors encountered during testing"""
        print("\n=== CHECKING FOR 404 ERRORS ===")
        
        # Check if any of our tests encountered 404 errors
        found_404s = []
        
        for result in self.test_results:
            if '404' in str(result.get('message', '')) or '404' in str(result.get('data', '')):
                found_404s.append(result['test'])
        
        # Also test a known endpoint to see if we get unexpected 404s
        test_endpoints = [
            '/auth/login',
            '/auth/me'
        ]
        
        for endpoint in test_endpoints:
            # Test with GET (should not be 404, might be 405 Method Not Allowed or 401 Unauthorized)
            result = self.make_request('GET', endpoint)
            if result['status_code'] == 404:
                found_404s.append(f"GET {endpoint}")
        
        no_404s = len(found_404s) == 0
        
        self.log_test(
            "404 Error Detection",
            no_404s,
            f"No 404 errors detected" if no_404s else f"404 errors found on: {', '.join(found_404s)}"
        )
        
        return no_404s, found_404s

    def run_auth_regression_test(self):
        """Run comprehensive auth regression tests"""
        print("\n🔐 STARTING AUTH REGRESSION TESTING - SPA CATCH-ALL ORDER FIX")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 80)
        
        # Run all tests in sequence as specified in review request
        test_methods = [
            ("CORS Headers - Login", self.test_cors_headers_login),
            ("CORS Headers - Me", self.test_cors_headers_me),
            ("Login with Known Account", self.test_login_with_known_account),
            ("Profile with Bearer Token", self.test_profile_with_bearer_token),
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
        
        # Check for 404 errors
        print(f"\n--- 404 Error Detection ---")
        try:
            no_404s, found_404s = self.test_404_detection()
            if no_404s:
                print(f"✅ 404 Error Detection completed successfully")
            else:
                print(f"❌ 404 Error Detection found issues")
        except Exception as e:
            print(f"❌ 404 Error Detection raised exception: {e}")
            found_404s = []
        
        success_rate = (successful_tests / total_tests) * 100
        
        print(f"\n" + "=" * 80)
        print("🔐 AUTH REGRESSION TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Concise pass/fail summary as requested
        print(f"\n📋 CONCISE RESULTS:")
        cors_login_passed = any(r['success'] and 'OPTIONS /api/auth/login' in r['test'] for r in self.test_results)
        cors_me_passed = any(r['success'] and 'OPTIONS /api/auth/me' in r['test'] for r in self.test_results)
        login_passed = any(r['success'] and 'POST /api/auth/login' in r['test'] for r in self.test_results)
        profile_passed = any(r['success'] and 'GET /api/auth/me' in r['test'] for r in self.test_results)
        
        print(f"1) OPTIONS /api/auth/login CORS: {'PASS' if cors_login_passed else 'FAIL'}")
        print(f"2) OPTIONS /api/auth/me CORS: {'PASS' if cors_me_passed else 'FAIL'}")
        print(f"3) POST /api/auth/login: {'PASS' if login_passed else 'FAIL'}")
        print(f"4) GET /api/auth/me: {'PASS' if profile_passed else 'FAIL'}")
        
        if found_404s:
            print(f"5) 404 Errors Found: {', '.join(found_404s)}")
        else:
            print(f"5) 404 Errors: NONE")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 75  # 3 out of 4 main tests should pass

def main():
    """Run Auth Regression Tests"""
    print("🔐 STARTING AUTH REGRESSION BACKEND TESTING")
    print("=" * 80)
    
    tester = AuthRegressionTester()
    
    try:
        # Run the comprehensive auth regression tests
        success = tester.run_auth_regression_test()
        
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
        
        return success_rate >= 75
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)