#!/usr/bin/env python3
"""
Backend Authentication Registration Test
Tests the specific requirements from the review request:
1) POST /api/auth/register with specific user data
2) POST /api/auth/login with the same credentials
3) Capture tokens for subsequent UI tests
"""

import requests
import json
import time
from typing import Dict, Any, Optional

# Configuration - Use the correct backend URL from frontend/.env
BACKEND_URL = "https://prodforge-1.preview.emergentagent.com/api"

# Test user data as specified in the review request
TEST_USER_DATA = {
    "email": "marc.alleyne@gmail.com",
    "password": "Test$1920",
    "first_name": "Marc",
    "last_name": "Alleyne",
    "username": "MarcymooUnique"  # Using a unique username to avoid conflicts
}

class AuthRegistrationTest:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None
        self.test_results = []
        
    def log_result(self, step: str, success: bool, status_code: int = None, details: str = "", response_time: float = 0):
        """Log test result"""
        result = {
            "step": step,
            "success": success,
            "status_code": status_code,
            "details": details,
            "response_time_ms": round(response_time * 1000, 1)
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        time_str = f"({result['response_time_ms']}ms)" if response_time > 0 else ""
        print(f"{status} {step} - Status: {status_code} {time_str}")
        if details:
            print(f"    Details: {details}")
        print()

    def make_request(self, method: str, endpoint: str, **kwargs) -> tuple:
        """Make HTTP request with timing"""
        url = f"{BACKEND_URL}{endpoint}"
        
        # Add authorization header if we have a token
        if self.access_token and 'headers' not in kwargs:
            kwargs['headers'] = {}
        if self.access_token:
            kwargs['headers']['Authorization'] = f"Bearer {self.access_token}"
            
        start_time = time.time()
        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
            end_time = time.time()
            return response, end_time - start_time
        except Exception as e:
            end_time = time.time()
            print(f"Request failed: {e}")
            # Create a mock response for error handling
            class MockResponse:
                def __init__(self, error_msg):
                    self.status_code = 0
                    self.text = str(error_msg)
                    self.error_msg = error_msg
                def json(self):
                    return {"error": str(self.error_msg)}
            return MockResponse(e), end_time - start_time

    def test_step_1_register(self):
        """Step 1: POST /api/auth/register with specified user data"""
        print("📝 Step 1: Testing POST /api/auth/register")
        print(f"    Registering user: {TEST_USER_DATA['email']}")
        
        response, response_time = self.make_request("POST", "/auth/register", json=TEST_USER_DATA)
        
        success = response.status_code in [200, 409]  # 200 for new user, 409 if already exists
        details = ""
        
        if response.status_code == 200:
            try:
                data = response.json()
                user_id = data.get("id", "unknown")
                email = data.get("email", "unknown")
                username = data.get("username", "unknown")
                details = f"User created successfully: {email} (ID: {user_id}, Username: {username})"
            except Exception as e:
                details = f"Registration successful but JSON parse failed: {e}"
        elif response.status_code == 409:
            details = "User already exists (409) - this is expected if running multiple times"
            success = True  # This is acceptable for our test
        else:
            details = f"Registration failed: {response.text[:200]}"
            
        self.log_result("POST /api/auth/register", success, response.status_code, details, response_time)
        return success

    def test_step_2_login(self):
        """Step 2: POST /api/auth/login with the same credentials"""
        print("🔐 Step 2: Testing POST /api/auth/login")
        print(f"    Logging in user: {TEST_USER_DATA['email']}")
        
        login_payload = {
            "email": TEST_USER_DATA["email"],
            "password": TEST_USER_DATA["password"]
        }
        
        response, response_time = self.make_request("POST", "/auth/login", json=login_payload)
        
        success = response.status_code == 200
        details = ""
        
        if success:
            try:
                data = response.json()
                if "access_token" in data:
                    self.access_token = data["access_token"]
                    self.refresh_token = data.get("refresh_token")
                    token_type = data.get("token_type", "bearer")
                    expires_in = data.get("expires_in", "unknown")
                    
                    details = f"Login successful - Access token: {len(self.access_token)} chars, "
                    details += f"Refresh token: {'Yes' if self.refresh_token else 'No'}, "
                    details += f"Type: {token_type}, Expires: {expires_in}s"
                else:
                    success = False
                    details = "No access_token in response"
            except Exception as e:
                success = False
                details = f"Failed to parse JSON: {e}"
        else:
            details = f"Login failed: {response.text[:200]}"
            
        self.log_result("POST /api/auth/login", success, response.status_code, details, response_time)
        return success

    def test_step_3_verify_auth(self):
        """Step 3: GET /api/auth/me to verify authentication works"""
        print("👤 Step 3: Testing GET /api/auth/me (verify authentication)")
        
        if not self.access_token:
            self.log_result("GET /api/auth/me", False, None, "No access token available")
            return False
            
        response, response_time = self.make_request("GET", "/auth/me")
        
        success = response.status_code == 200
        details = ""
        
        if success:
            try:
                data = response.json()
                user_id = data.get("id", "unknown")
                email = data.get("email", "unknown")
                username = data.get("username", "unknown")
                first_name = data.get("first_name", "")
                last_name = data.get("last_name", "")
                details = f"Auth verified: {email} (ID: {user_id}, Username: {username}, Name: {first_name} {last_name})"
            except Exception as e:
                details = f"Response received but JSON parse failed: {e}"
        else:
            details = f"Auth verification failed: {response.text[:200]}"
            
        self.log_result("GET /api/auth/me", success, response.status_code, details, response_time)
        return success

    def capture_tokens_for_ui_tests(self):
        """Capture and display tokens for subsequent UI tests"""
        print("🎯 Token Capture for UI Tests")
        print("=" * 50)
        
        if self.access_token:
            print(f"✅ Access Token: {self.access_token}")
            print(f"   Length: {len(self.access_token)} characters")
            
            if self.refresh_token:
                print(f"✅ Refresh Token: {self.refresh_token}")
                print(f"   Length: {len(self.refresh_token)} characters")
            else:
                print("⚠️ No refresh token received")
                
            print("\n📋 For UI Tests, use these tokens:")
            print(f"Authorization: Bearer {self.access_token}")
            
        else:
            print("❌ No tokens available - authentication failed")
            
        print("=" * 50)

    def run_all_tests(self):
        """Run all authentication tests in sequence"""
        print("🚀 Starting Backend Authentication Registration Test")
        print("=" * 70)
        print(f"Target User: {TEST_USER_DATA['email']}")
        print(f"Backend URL: {BACKEND_URL}")
        print()
        
        test_methods = [
            self.test_step_1_register,
            self.test_step_2_login,
            self.test_step_3_verify_auth
        ]
        
        passed = 0
        total = len(test_methods)
        
        for test_method in test_methods:
            try:
                if test_method():
                    passed += 1
            except Exception as e:
                print(f"❌ Test method {test_method.__name__} crashed: {e}")
                self.log_result(test_method.__name__, False, None, f"Test crashed: {e}")
        
        print("=" * 70)
        print("📊 AUTHENTICATION TEST SUMMARY")
        print("=" * 70)
        
        success_rate = (passed / total) * 100
        print(f"Overall Success Rate: {passed}/{total} ({success_rate:.1f}%)")
        print()
        
        # Detailed results
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['step']} - {result['status_code']} ({result['response_time_ms']}ms)")
            if result["details"]:
                print(f"    {result['details']}")
        
        print()
        
        # Capture tokens for UI tests
        self.capture_tokens_for_ui_tests()
        
        print("=" * 70)
        
        if success_rate >= 80:
            print("🎉 AUTHENTICATION TEST PASSED - Ready for UI tests!")
        elif success_rate >= 60:
            print("⚠️ AUTHENTICATION TEST PARTIAL - Some issues need attention")
        else:
            print("🚨 AUTHENTICATION TEST FAILED - Critical issues require immediate fix")
            
        return success_rate

if __name__ == "__main__":
    tester = AuthRegistrationTest()
    success_rate = tester.run_all_tests()
    exit(0 if success_rate >= 80 else 1)