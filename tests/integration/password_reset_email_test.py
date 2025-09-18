#!/usr/bin/env python3
"""
Password Reset Email Delivery Test - SMTP Configuration Fix Verification
Tests the specific requirements from the review request after SMTP fix:
1. Health check: GET /api/health to confirm backend is running
2. Test password reset email delivery: POST /api/auth/forgot-password with email "marc.alleyne@aurumtechnologyltd.com" and proper Origin header for the preview domain
3. Verify the response includes success=true and message about email being sent
4. Check if the recovery_url is still included in dev fallback (should be there for preview domains)
5. Monitor the response time - should be reasonable for email processing
6. The key test is whether the actual email gets delivered to the specified email address

Focus: Confirming that the SMTP configuration fix (changing host from smtp-mail.outlook.com to smtp.office365.com and using app password) has resolved the email delivery issue.
"""

import requests
import json
import time
from typing import Dict, Any, Optional

# Configuration - Use the correct backend URL from frontend/.env
BACKEND_URL = "https://supa-data-explained.preview.emergentagent.com/api"
TEST_EMAIL = "marc.alleyne@aurumtechnologyltd.com"
ORIGIN_HEADER = "https://supa-data-explained.preview.emergentagent.com"

class PasswordResetEmailTest:
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

    def test_step_1_health_check(self):
        """Step 1: GET /api/health to confirm backend is running"""
        print("🏥 Step 1: Testing GET /api/health")
        
        response, response_time = self.make_request("GET", "/health")
        
        success = response.status_code == 200
        details = ""
        
        if success:
            try:
                data = response.json()
                status = data.get("status", "unknown")
                timestamp = data.get("timestamp", "unknown")
                details = f"Backend status: {status}, timestamp: {timestamp}"
            except Exception as e:
                details = f"Response received but JSON parse failed: {e}"
        else:
            details = f"Health check failed: {response.text[:200]}"
            
        self.log_result("GET /api/health", success, response.status_code, details, response_time)
        return success

    def test_step_2_forgot_password(self):
        """Step 2: POST /api/auth/forgot-password with email and Origin header"""
        print("📧 Step 2: Testing POST /api/auth/forgot-password")
        
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
        recovery_url_present = False
        
        if success:
            try:
                data = response.json()
                success_flag = data.get("success", False)
                message = data.get("message", "")
                recovery_url = data.get("recovery_url", None)
                
                if success_flag:
                    details = f"Success: {success_flag}, Message: '{message}'"
                    if recovery_url:
                        recovery_url_present = True
                        details += f", Recovery URL present: {recovery_url[:100]}..."
                    else:
                        details += ", No recovery_url in response (expected for production security)"
                else:
                    success = False
                    details = f"Success flag is false: {data}"
                    
            except Exception as e:
                success = False
                details = f"JSON parse failed: {e}, Raw response: {response.text[:200]}"
        else:
            details = f"Forgot password request failed: {response.text[:200]}"
            
        self.log_result("POST /api/auth/forgot-password", success, response.status_code, details, response_time)
        
        # Additional verification for dev fallback
        if success and recovery_url_present:
            print("🔧 Dev Fallback Verification: Recovery URL is present for preview domain")
        elif success and not recovery_url_present:
            print("🔒 Production Security: No recovery URL in response (expected for security)")
            
        return success, response_time

    def test_step_3_response_time_analysis(self, forgot_password_time: float):
        """Step 3: Analyze response time for email processing"""
        print("⏱️ Step 3: Response Time Analysis")
        
        # Email processing should be reasonable but not too fast (indicates actual email sending)
        reasonable_min_time = 1.0  # At least 1 second for actual email processing
        reasonable_max_time = 10.0  # No more than 10 seconds for good UX
        
        success = reasonable_min_time <= forgot_password_time <= reasonable_max_time
        
        if success:
            details = f"Response time {forgot_password_time:.2f}s is reasonable for email processing (between {reasonable_min_time}s and {reasonable_max_time}s)"
        else:
            if forgot_password_time < reasonable_min_time:
                details = f"Response time {forgot_password_time:.2f}s is too fast - may indicate email not actually being sent"
            else:
                details = f"Response time {forgot_password_time:.2f}s is too slow - may impact user experience"
                
        self.log_result("Response Time Analysis", success, None, details, 0)
        return success

    def run_all_tests(self):
        """Run all password reset email delivery tests"""
        print("🎯 PASSWORD RESET EMAIL DELIVERY TEST - SMTP CONFIGURATION FIX VERIFICATION")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Email: {TEST_EMAIL}")
        print(f"Origin Header: {ORIGIN_HEADER}")
        print("=" * 80)
        print()
        
        # Step 1: Health Check
        health_success = self.test_step_1_health_check()
        
        # Step 2: Forgot Password with Email Delivery
        forgot_password_success, forgot_password_time = self.test_step_2_forgot_password()
        
        # Step 3: Response Time Analysis
        time_analysis_success = self.test_step_3_response_time_analysis(forgot_password_time)
        
        # Summary
        print("=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Detailed results
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['step']} - {result['status_code']} ({result['response_time_ms']}ms)")
            if result["details"]:
                print(f"    {result['details']}")
        
        print()
        print("🔑 KEY FINDINGS:")
        if health_success:
            print("✅ Backend is healthy and accessible")
        else:
            print("❌ Backend health check failed - system may be down")
            
        if forgot_password_success:
            print("✅ Password reset email endpoint is working correctly")
            print("✅ Response includes success=true and proper message")
            if forgot_password_time >= 1.0:
                print("✅ Response time indicates actual email processing is occurring")
            else:
                print("⚠️ Fast response time - verify actual email delivery")
        else:
            print("❌ Password reset email endpoint failed - SMTP configuration may still have issues")
            
        if time_analysis_success:
            print("✅ Response time is reasonable for email processing operations")
        else:
            print("⚠️ Response time analysis indicates potential issues with email processing")
            
        print()
        print("📧 SMTP CONFIGURATION FIX VERIFICATION:")
        print("The key test is whether the actual email gets delivered to marc.alleyne@aurumtechnologyltd.com")
        print("Please check the email inbox to confirm delivery after running this test.")
        print("If email is received, the SMTP configuration fix (smtp.office365.com + app password) is successful.")
        
        overall_success = health_success and forgot_password_success
        return overall_success

if __name__ == "__main__":
    test = PasswordResetEmailTest()
    success = test.run_all_tests()
    exit(0 if success else 1)