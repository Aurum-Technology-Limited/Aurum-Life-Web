#!/usr/bin/env python3
"""
Password Reset Redirect URL Fix Test
Focused test to verify the redirect URL fix prevents localhost/127.0.0.1 origins 
from being replaced with the correct preview domain URL.
"""

import requests
import json
import time
import re
from typing import Dict, Any, Optional

# Configuration - Use the correct backend URL
BACKEND_URL = "https://emotional-os-1.preview.emergentagent.com/api"
TEST_EMAIL = "marc.alleyne@aurumtechnologyltd.com"
ORIGIN_HEADER = "https://emotional-os-1.preview.emergentagent.com"

class RedirectUrlFixTest:
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
        """Test GET /api/health to confirm backend is running"""
        print("🏥 Testing GET /api/health")
        
        response, response_time = self.make_request("GET", "/health")
        
        success = response.status_code == 200
        details = ""
        
        if success:
            try:
                data = response.json()
                status = data.get("status", "unknown")
                details = f"Backend is {status}"
            except Exception as e:
                details = f"Response received but JSON parse failed: {e}"
        else:
            details = f"Health check failed: {response.text[:200]}"
            
        self.log_result("Health Check", success, response.status_code, details, response_time)
        return success

    def test_password_reset_with_proper_origin(self):
        """Test password reset with proper Origin header and check redirect URL"""
        print("🔐 Testing POST /api/auth/forgot-password with proper Origin header")
        
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
        redirect_url_correct = False
        
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
                        
                        # Check if redirect_to parameter contains the correct preview domain
                        if "redirect_to=" in recovery_url:
                            # Extract redirect_to parameter
                            redirect_match = re.search(r'redirect_to=([^&]+)', recovery_url)
                            if redirect_match:
                                redirect_to = requests.utils.unquote(redirect_match.group(1))
                                print(f"🎯 Extracted redirect_to: {redirect_to}")
                                
                                # Check if it's the correct preview domain (not localhost)
                                if "prodflow-auth.preview.emergentagent.com" in redirect_to:
                                    redirect_url_correct = True
                                    details += f", ✅ Redirect URL correct: {redirect_to}"
                                elif "localhost" in redirect_to or "127.0.0.1" in redirect_to:
                                    details += f", ❌ Redirect URL still contains localhost: {redirect_to}"
                                else:
                                    details += f", ⚠️ Redirect URL unexpected: {redirect_to}"
                            else:
                                details += ", ❌ Could not extract redirect_to parameter"
                        else:
                            details += ", ❌ No redirect_to parameter found in recovery URL"
                    else:
                        details += ", No recovery_url in response"
                else:
                    success = False
                    details = f"Success field not true: {data.get('success')}"
            except Exception as e:
                success = False
                details = f"Failed to parse JSON: {e}"
        else:
            details = f"Password reset failed: {response.text[:200]}"
            
        # Overall success requires both 200 response AND correct redirect URL
        overall_success = success and redirect_url_correct
        
        self.log_result("Password Reset with Redirect Fix", overall_success, response.status_code, details, response_time)
        return overall_success, recovery_url

    def test_localhost_origin_replacement(self):
        """Test that localhost origins are properly replaced with preview domain"""
        print("🔄 Testing localhost origin replacement")
        
        payload = {
            "email": TEST_EMAIL
        }
        
        # Use localhost origin to test the replacement logic
        headers = {
            "Origin": "http://localhost:3000",
            "Content-Type": "application/json"
        }
        
        response, response_time = self.make_request("POST", "/auth/forgot-password", json=payload, headers=headers)
        
        success = response.status_code == 200
        details = ""
        localhost_replaced = False
        
        if success:
            try:
                data = response.json()
                recovery_url = data.get("recovery_url")
                
                if recovery_url:
                    print(f"🔗 Recovery URL with localhost origin: {recovery_url}")
                    
                    # Check if redirect_to parameter contains the correct preview domain (not localhost)
                    if "redirect_to=" in recovery_url:
                        redirect_match = re.search(r'redirect_to=([^&]+)', recovery_url)
                        if redirect_match:
                            redirect_to = requests.utils.unquote(redirect_match.group(1))
                            print(f"🎯 Extracted redirect_to: {redirect_to}")
                            
                            # Check if localhost was properly replaced
                            if "prodflow-auth.preview.emergentagent.com" in redirect_to:
                                localhost_replaced = True
                                details = f"✅ Localhost properly replaced with preview domain: {redirect_to}"
                            elif "localhost" in redirect_to:
                                details = f"❌ Localhost NOT replaced: {redirect_to}"
                            else:
                                details = f"⚠️ Unexpected redirect URL: {redirect_to}"
                        else:
                            details = "❌ Could not extract redirect_to parameter"
                    else:
                        details = "❌ No redirect_to parameter found"
                else:
                    details = "❌ No recovery_url in response"
            except Exception as e:
                details = f"Failed to parse JSON: {e}"
        else:
            details = f"Request failed: {response.text[:200]}"
            
        overall_success = success and localhost_replaced
        
        self.log_result("Localhost Origin Replacement", overall_success, response.status_code, details, response_time)
        return overall_success

    def run_all_tests(self):
        """Run all redirect URL fix tests"""
        print("🚀 Starting Password Reset Redirect URL Fix Test")
        print("=" * 80)
        print(f"Target Email: {TEST_EMAIL}")
        print(f"Origin Header: {ORIGIN_HEADER}")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 80)
        print()
        
        # Test 1: Health check
        health_success = self.test_health_check()
        
        # Test 2: Password reset with proper origin
        reset_success, recovery_url = self.test_password_reset_with_proper_origin()
        
        # Test 3: Localhost origin replacement
        localhost_success = self.test_localhost_origin_replacement()
        
        print("=" * 80)
        print("📊 REDIRECT URL FIX TEST SUMMARY")
        print("=" * 80)
        
        tests_run = 3
        tests_passed = sum([health_success, reset_success, localhost_success])
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
        print("=" * 80)
        
        if success_rate == 100:
            print("🎉 REDIRECT URL FIX TEST PASSED! All localhost origins properly replaced.")
        elif success_rate >= 66:
            print("⚠️ REDIRECT URL FIX TEST PARTIAL - Some issues need attention")
        else:
            print("🚨 REDIRECT URL FIX TEST FAILED - Localhost origins not being replaced correctly")
            
        return success_rate

if __name__ == "__main__":
    tester = RedirectUrlFixTest()
    success_rate = tester.run_all_tests()
    exit(0 if success_rate >= 80 else 1)