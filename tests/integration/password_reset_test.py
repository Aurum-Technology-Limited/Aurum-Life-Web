#!/usr/bin/env python3
"""
Password Reset Flow Backend Test with Dev Fallback
Tests the specific requirements from the review request:
1) POST /api/auth/forgot-password with dev fallback enabled
2) GET /api/health to confirm backend is healthy
"""

import requests
import json
import time
from typing import Dict, Any, Optional

# Configuration - Use the correct backend URL from frontend/.env
BACKEND_URL = "https://aurum-codebase.preview.emergentagent.com/api"
TEST_EMAIL = "marc.alleyne@aurumtechnologyltd.com"

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

    def make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
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
                def json(self):
                    return {"error": str(error_msg)}
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
                details = f"Backend status: {status}"
            except Exception as e:
                details = f"Response received but JSON parse failed: {e}"
        else:
            details = f"Health check failed: {response.text[:200]}"
            
        self.log_result("GET /api/health", success, response.status_code, details, response_time)
        return success

    def test_forgot_password(self):
        """Test POST /api/auth/forgot-password with dev fallback"""
        print("🔐 Testing POST /api/auth/forgot-password with dev fallback")
        
        payload = {
            "email": TEST_EMAIL
        }
        
        headers = {
            "Origin": "https://aurum-codebase.preview.emergentagent.com",
            "Content-Type": "application/json"
        }
        
        response, response_time = self.make_request("POST", "/auth/forgot-password", json=payload, headers=headers)
        
        success = response.status_code == 200
        details = ""
        recovery_url = None
        
        if success:
            try:
                data = response.json()
                success_flag = data.get("success", False)
                message = data.get("message", "")
                recovery_url = data.get("recovery_url")
                
                if success_flag:
                    details = f"Success: {message}"
                    if recovery_url:
                        details += f" | Recovery URL provided (dev fallback enabled)"
                        print(f"🔗 RECOVERY URL: {recovery_url}")
                    else:
                        details += " | No recovery URL (production mode)"
                else:
                    success = False
                    details = f"API returned success=false: {message}"
            except Exception as e:
                success = False
                details = f"Failed to parse JSON: {e}"
        else:
            details = f"Forgot password failed: {response.text[:200]}"
            
        self.log_result("POST /api/auth/forgot-password", success, response.status_code, details, response_time)
        
        # Print recovery URL separately for visibility
        if recovery_url:
            print("=" * 70)
            print("🔗 RECOVERY URL FOR TESTING:")
            print(recovery_url)
            print("=" * 70)
            print()
        
        return success

    def run_tests(self):
        """Run password reset tests"""
        print("🚀 Starting Password Reset Flow Backend Test")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Email: {TEST_EMAIL}")
        print(f"Origin Header: https://aurum-codebase.preview.emergentagent.com")
        print("=" * 70)
        print()
        
        test_methods = [
            self.test_health_check,
            self.test_forgot_password
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
        print("📊 PASSWORD RESET TEST SUMMARY")
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
        print("=" * 70)
        
        if success_rate >= 100:
            print("🎉 PASSWORD RESET TEST PASSED - All requirements met!")
        elif success_rate >= 50:
            print("⚠️ PASSWORD RESET TEST PARTIAL - Some issues need attention")
        else:
            print("🚨 PASSWORD RESET TEST FAILED - Critical issues require immediate fix")
            
        return success_rate

if __name__ == "__main__":
    tester = PasswordResetTest()
    success_rate = tester.run_tests()
    exit(0 if success_rate >= 100 else 1)