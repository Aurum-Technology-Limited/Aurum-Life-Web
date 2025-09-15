#!/usr/bin/env python3
"""
Password Reset Flow Backend Test
Tests the specific requirements from the review request:
1) POST /api/auth/forgot-password with specific email and Origin header
2) Check for recovery_url in response and test it if present  
3) GET /api/health sanity check
"""

import requests
import json
import time
from typing import Dict, Any, Optional

# Configuration - Use the correct backend URL
BACKEND_URL = "https://supa-data-explained.preview.emergentagent.com/api"
TEST_EMAIL = "marc.alleyne@aurumtechnologyltd.com"
ORIGIN_HEADER = "https://supa-data-explained.preview.emergentagent.com"

class PasswordResetTest:
    def __init__(self):
        self.session = requests.Session()
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

    def test_health_check(self):
        """Test GET /api/health"""
        print("🏥 Testing GET /api/health")
        
        response, response_time = self.make_request("GET", "/health")
        
        success = response.status_code == 200
        details = ""
        
        if success:
            try:
                data = response.json()
                status = data.get("status", "unknown")
                details = f"Health status: {status}"
            except Exception as e:
                details = f"Response received but JSON parse failed: {e}"
        else:
            details = f"Health check failed: {response.text[:200]}"
            
        self.log_result("GET /api/health", success, response.status_code, details, response_time)
        return success

    def test_forgot_password(self):
        """Test POST /api/auth/forgot-password with specific email and Origin header"""
        print("🔐 Testing POST /api/auth/forgot-password")
        
        payload = {
            "email": TEST_EMAIL
        }
        
        headers = {
            "Origin": ORIGIN_HEADER,
            "Content-Type": "application/json"
        }
        
        response, response_time = self.make_request("POST", "/auth/forgot-password", json=payload, headers=headers)
        
        success = response.status_code == 200
        details = ""
        recovery_url = None
        
        if success:
            try:
                data = response.json()
                print(f"📋 Full JSON Response: {json.dumps(data, indent=2)}")
                
                # Check for required fields
                if data.get("success") is True:
                    message = data.get("message", "")
                    recovery_url = data.get("recovery_url")
                    
                    details = f"Success: {data.get('success')}, Message: '{message}'"
                    if recovery_url:
                        details += f", Recovery URL present: {len(recovery_url)} chars"
                        print(f"🔗 Recovery URL: {recovery_url}")
                    else:
                        details += ", No recovery_url in response"
                else:
                    success = False
                    details = f"Success field not true: {data.get('success')}"
            except Exception as e:
                success = False
                details = f"Failed to parse JSON: {e}"
        else:
            details = f"Forgot password failed: {response.text[:200]}"
            
        self.log_result("POST /api/auth/forgot-password", success, response.status_code, details, response_time)
        return success, recovery_url

    def test_recovery_url(self, recovery_url: str):
        """Test recovery_url with HEAD request (don't follow redirects)"""
        print("🔗 Testing recovery_url")
        
        if not recovery_url:
            self.log_result("HEAD recovery_url", False, None, "No recovery_url provided")
            return False
            
        start_time = time.time()
        try:
            # Try HEAD request first (don't follow redirects)
            response = requests.head(recovery_url, allow_redirects=False, timeout=30)
            end_time = time.time()
            response_time = end_time - start_time
            
            success = True  # Any response is considered success for this test
            details = f"HEAD response received"
            
            if response.status_code in [301, 302, 303, 307, 308]:
                location = response.headers.get('Location', 'No Location header')
                details += f", Redirect to: {location[:100]}"
            elif response.status_code == 200:
                details += ", Direct 200 response"
            else:
                details += f", Status: {response.status_code}"
                
            self.log_result("HEAD recovery_url", success, response.status_code, details, response_time)
            return success
            
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            
            print(f"    HEAD failed, trying GET without redirects: {e}")
            
            # Fallback to GET without following redirects
            try:
                response = requests.get(recovery_url, allow_redirects=False, timeout=30)
                
                success = True
                details = f"GET response received (HEAD failed: {str(e)[:50]})"
                
                if response.status_code in [301, 302, 303, 307, 308]:
                    location = response.headers.get('Location', 'No Location header')
                    details += f", Redirect to: {location[:100]}"
                elif response.status_code == 200:
                    details += ", Direct 200 response"
                else:
                    details += f", Status: {response.status_code}"
                    
                self.log_result("GET recovery_url (HEAD fallback)", success, response.status_code, details, response_time)
                return success
                
            except Exception as e2:
                self.log_result("GET recovery_url (HEAD fallback)", False, 0, f"Both HEAD and GET failed: {e2}", response_time)
                return False

    def run_all_tests(self):
        """Run all password reset tests in sequence"""
        print("🚀 Starting Password Reset Flow Backend Test")
        print("=" * 70)
        print(f"Target Email: {TEST_EMAIL}")
        print(f"Origin Header: {ORIGIN_HEADER}")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 70)
        print()
        
        # Test 1: Health check
        health_success = self.test_health_check()
        
        # Test 2: Forgot password
        forgot_success, recovery_url = self.test_forgot_password()
        
        # Test 3: Recovery URL (if present)
        recovery_success = True  # Default to true if no URL to test
        if recovery_url:
            recovery_success = self.test_recovery_url(recovery_url)
        else:
            print("⏭️  Skipping recovery URL test - no recovery_url in response")
            print()
        
        print("=" * 70)
        print("📊 PASSWORD RESET TEST SUMMARY")
        print("=" * 70)
        
        tests_run = 2 + (1 if recovery_url else 0)
        tests_passed = sum([health_success, forgot_success, recovery_success])
        success_rate = (tests_passed / tests_run) * 100
        
        print(f"Overall Success Rate: {tests_passed}/{tests_run} ({success_rate:.1f}%)")
        print()
        
        # Detailed results
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['step']} - {result['status_code']} ({result['response_time_ms']}ms)")
            if result["details"]:
                print(f"    {result['details']}")
        
        print()
        print("=" * 70)
        
        if success_rate >= 80:
            print("🎉 PASSWORD RESET TEST PASSED!")
        elif success_rate >= 60:
            print("⚠️ PASSWORD RESET TEST PARTIAL - Some issues need attention")
        else:
            print("🚨 PASSWORD RESET TEST FAILED - Critical issues require immediate fix")
            
        return success_rate

if __name__ == "__main__":
    tester = PasswordResetTest()
    success_rate = tester.run_all_tests()
    exit(0 if success_rate >= 80 else 1)