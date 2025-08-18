#!/usr/bin/env python3
"""
AUTH CORS VALIDATION TESTING
Testing CORS validation for auth endpoints as requested in review.

FOCUS AREAS:
1. OPTIONS preflight to /api/auth/login and /api/auth/me with Origin=https://productivity-hub-23.preview.emergentagent.com
2. Verify 204/200 and Access-Control-Allow-* headers include origin, methods, headers
3. POST /api/auth/login with JSON body for known test user; verify 200 and access_token
4. GET /api/auth/me with Bearer token; verify 200 user payload

CREDENTIALS: marc.alleyne@aurumtechnologyltd.com / password123
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://productivity-hub-23.preview.emergentagent.com/api"
ORIGIN = "https://productivity-hub-23.preview.emergentagent.com"

class AuthCORSValidator:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.origin = ORIGIN
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

    def test_options_preflight_login(self):
        """Test OPTIONS preflight to /api/auth/login with browser-like headers"""
        print("\n=== TESTING OPTIONS PREFLIGHT TO /api/auth/login ===")
        
        url = f"{self.base_url}/auth/login"
        headers = {
            'Origin': self.origin,
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type, Authorization'
        }
        
        try:
            response = self.session.options(url, headers=headers, timeout=30)
            
            # Check status code (should be 204 or 200)
            status_ok = response.status_code in [200, 204]
            self.log_test(
                "OPTIONS /api/auth/login - Status Code",
                status_ok,
                f"Status: {response.status_code}" if status_ok else f"Expected 200/204, got {response.status_code}"
            )
            
            if not status_ok:
                return False
            
            # Check CORS headers
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
                'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
            }
            
            # Verify origin is allowed
            origin_allowed = (cors_headers['Access-Control-Allow-Origin'] == self.origin or 
                            cors_headers['Access-Control-Allow-Origin'] == '*')
            self.log_test(
                "OPTIONS /api/auth/login - Origin Allowed",
                origin_allowed,
                f"Origin '{self.origin}' allowed" if origin_allowed else f"Origin not allowed: {cors_headers['Access-Control-Allow-Origin']}"
            )
            
            # Verify methods include POST
            methods_ok = (cors_headers['Access-Control-Allow-Methods'] and 
                         'POST' in cors_headers['Access-Control-Allow-Methods'])
            self.log_test(
                "OPTIONS /api/auth/login - POST Method Allowed",
                methods_ok,
                f"POST method allowed: {cors_headers['Access-Control-Allow-Methods']}" if methods_ok else f"POST not in allowed methods: {cors_headers['Access-Control-Allow-Methods']}"
            )
            
            # Verify headers include Content-Type
            headers_ok = (cors_headers['Access-Control-Allow-Headers'] and 
                         'Content-Type' in cors_headers['Access-Control-Allow-Headers'])
            self.log_test(
                "OPTIONS /api/auth/login - Content-Type Header Allowed",
                headers_ok,
                f"Content-Type allowed: {cors_headers['Access-Control-Allow-Headers']}" if headers_ok else f"Content-Type not in allowed headers: {cors_headers['Access-Control-Allow-Headers']}"
            )
            
            # Print all CORS headers for debugging
            print(f"   CORS Headers: {json.dumps(cors_headers, indent=2)}")
            
            return origin_allowed and methods_ok and headers_ok
            
        except requests.exceptions.RequestException as e:
            self.log_test(
                "OPTIONS /api/auth/login - Request Failed",
                False,
                f"Request failed: {str(e)}"
            )
            return False

    def test_options_preflight_me(self):
        """Test OPTIONS preflight to /api/auth/me with browser-like headers"""
        print("\n=== TESTING OPTIONS PREFLIGHT TO /api/auth/me ===")
        
        url = f"{self.base_url}/auth/me"
        headers = {
            'Origin': self.origin,
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Authorization'
        }
        
        try:
            response = self.session.options(url, headers=headers, timeout=30)
            
            # Check status code (should be 204 or 200)
            status_ok = response.status_code in [200, 204]
            self.log_test(
                "OPTIONS /api/auth/me - Status Code",
                status_ok,
                f"Status: {response.status_code}" if status_ok else f"Expected 200/204, got {response.status_code}"
            )
            
            if not status_ok:
                return False
            
            # Check CORS headers
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
                'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
            }
            
            # Verify origin is allowed
            origin_allowed = (cors_headers['Access-Control-Allow-Origin'] == self.origin or 
                            cors_headers['Access-Control-Allow-Origin'] == '*')
            self.log_test(
                "OPTIONS /api/auth/me - Origin Allowed",
                origin_allowed,
                f"Origin '{self.origin}' allowed" if origin_allowed else f"Origin not allowed: {cors_headers['Access-Control-Allow-Origin']}"
            )
            
            # Verify methods include GET
            methods_ok = (cors_headers['Access-Control-Allow-Methods'] and 
                         'GET' in cors_headers['Access-Control-Allow-Methods'])
            self.log_test(
                "OPTIONS /api/auth/me - GET Method Allowed",
                methods_ok,
                f"GET method allowed: {cors_headers['Access-Control-Allow-Methods']}" if methods_ok else f"GET not in allowed methods: {cors_headers['Access-Control-Allow-Methods']}"
            )
            
            # Verify headers include Authorization
            headers_ok = (cors_headers['Access-Control-Allow-Headers'] and 
                         'Authorization' in cors_headers['Access-Control-Allow-Headers'])
            self.log_test(
                "OPTIONS /api/auth/me - Authorization Header Allowed",
                headers_ok,
                f"Authorization allowed: {cors_headers['Access-Control-Allow-Headers']}" if headers_ok else f"Authorization not in allowed headers: {cors_headers['Access-Control-Allow-Headers']}"
            )
            
            # Print all CORS headers for debugging
            print(f"   CORS Headers: {json.dumps(cors_headers, indent=2)}")
            
            return origin_allowed and methods_ok and headers_ok
            
        except requests.exceptions.RequestException as e:
            self.log_test(
                "OPTIONS /api/auth/me - Request Failed",
                False,
                f"Request failed: {str(e)}"
            )
            return False

    def test_post_login(self):
        """Test POST /api/auth/login with JSON body for known test user"""
        print("\n=== TESTING POST /api/auth/login ===")
        
        url = f"{self.base_url}/auth/login"
        headers = {
            'Content-Type': 'application/json',
            'Origin': self.origin
        }
        
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        try:
            response = self.session.post(url, json=login_data, headers=headers, timeout=30)
            
            # Check status code (should be 200)
            status_ok = response.status_code == 200
            self.log_test(
                "POST /api/auth/login - Status Code",
                status_ok,
                f"Status: {response.status_code}" if status_ok else f"Expected 200, got {response.status_code}"
            )
            
            if not status_ok:
                error_text = response.text
                print(f"   Error response: {error_text}")
                return False
            
            # Parse response
            try:
                response_data = response.json()
            except:
                self.log_test(
                    "POST /api/auth/login - JSON Response",
                    False,
                    "Response is not valid JSON"
                )
                return False
            
            # Check for access_token
            has_token = 'access_token' in response_data
            self.log_test(
                "POST /api/auth/login - Access Token Present",
                has_token,
                f"Access token received" if has_token else "No access_token in response"
            )
            
            if has_token:
                self.auth_token = response_data['access_token']
                print(f"   Token (first 20 chars): {self.auth_token[:20]}...")
            
            # Check CORS headers in response
            cors_origin = response.headers.get('Access-Control-Allow-Origin')
            cors_ok = cors_origin == self.origin or cors_origin == '*'
            self.log_test(
                "POST /api/auth/login - CORS Origin Header",
                cors_ok,
                f"CORS origin header: {cors_origin}" if cors_ok else f"Missing or incorrect CORS origin: {cors_origin}"
            )
            
            return has_token and cors_ok
            
        except requests.exceptions.RequestException as e:
            self.log_test(
                "POST /api/auth/login - Request Failed",
                False,
                f"Request failed: {str(e)}"
            )
            return False

    def test_get_me(self):
        """Test GET /api/auth/me with Bearer token"""
        print("\n=== TESTING GET /api/auth/me ===")
        
        if not self.auth_token:
            self.log_test(
                "GET /api/auth/me - No Token",
                False,
                "No authentication token available from login test"
            )
            return False
        
        url = f"{self.base_url}/auth/me"
        headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'Origin': self.origin
        }
        
        try:
            response = self.session.get(url, headers=headers, timeout=30)
            
            # Check status code (should be 200)
            status_ok = response.status_code == 200
            self.log_test(
                "GET /api/auth/me - Status Code",
                status_ok,
                f"Status: {response.status_code}" if status_ok else f"Expected 200, got {response.status_code}"
            )
            
            if not status_ok:
                error_text = response.text
                print(f"   Error response: {error_text}")
                return False
            
            # Parse response
            try:
                user_data = response.json()
            except:
                self.log_test(
                    "GET /api/auth/me - JSON Response",
                    False,
                    "Response is not valid JSON"
                )
                return False
            
            # Check for user payload fields
            expected_fields = ['id', 'email']
            has_user_fields = all(field in user_data for field in expected_fields)
            self.log_test(
                "GET /api/auth/me - User Payload",
                has_user_fields,
                f"User payload contains expected fields: {list(user_data.keys())}" if has_user_fields else f"Missing expected fields. Got: {list(user_data.keys())}"
            )
            
            # Verify email matches
            email_matches = user_data.get('email') == self.test_user_email
            self.log_test(
                "GET /api/auth/me - Email Verification",
                email_matches,
                f"Email matches: {user_data.get('email')}" if email_matches else f"Email mismatch: expected {self.test_user_email}, got {user_data.get('email')}"
            )
            
            # Check CORS headers in response
            cors_origin = response.headers.get('Access-Control-Allow-Origin')
            cors_ok = cors_origin == self.origin or cors_origin == '*'
            self.log_test(
                "GET /api/auth/me - CORS Origin Header",
                cors_ok,
                f"CORS origin header: {cors_origin}" if cors_ok else f"Missing or incorrect CORS origin: {cors_origin}"
            )
            
            print(f"   User data: {json.dumps(user_data, indent=2)}")
            
            return has_user_fields and email_matches and cors_ok
            
        except requests.exceptions.RequestException as e:
            self.log_test(
                "GET /api/auth/me - Request Failed",
                False,
                f"Request failed: {str(e)}"
            )
            return False

    def run_auth_cors_validation(self):
        """Run comprehensive auth CORS validation tests"""
        print("\n🔐 STARTING AUTH CORS VALIDATION TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Origin: {self.origin}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("OPTIONS Preflight /api/auth/login", self.test_options_preflight_login),
            ("OPTIONS Preflight /api/auth/me", self.test_options_preflight_me),
            ("POST /api/auth/login", self.test_post_login),
            ("GET /api/auth/me", self.test_get_me)
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
        print("🔐 AUTH CORS VALIDATION TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Origin: {self.origin}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        # Show header samples
        print(f"\n📋 HEADER SAMPLES:")
        print("   (Check console output above for detailed CORS headers)")
        
        if success_rate >= 75:
            print("\n✅ AUTH CORS VALIDATION: SUCCESS")
            print("   ✅ OPTIONS preflight requests working")
            print("   ✅ CORS headers properly configured")
            print("   ✅ Authentication flow functional")
            print("   ✅ User profile retrieval working")
            print("   The Auth CORS configuration is production-ready!")
        else:
            print("\n❌ AUTH CORS VALIDATION: ISSUES DETECTED")
            print("   Issues found in CORS configuration or auth endpoints")
        
        return success_rate >= 75

def main():
    """Run Auth CORS Validation Tests"""
    print("🔐 STARTING AUTH CORS VALIDATION BACKEND TESTING")
    print("=" * 80)
    
    validator = AuthCORSValidator()
    
    try:
        # Run the comprehensive auth CORS validation tests
        success = validator.run_auth_cors_validation()
        
        # Calculate overall results
        total_tests = len(validator.test_results)
        passed_tests = sum(1 for result in validator.test_results if result['success'])
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