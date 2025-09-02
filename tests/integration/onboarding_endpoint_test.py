#!/usr/bin/env python3
"""
ONBOARDING ENDPOINT FIX TESTING
===============================

This test suite validates the complete onboarding endpoint fix to ensure it returns 
200 with {"success": true} instead of 500 error as specified in the review request.

Test Coverage:
1. Login with marc.alleyne@aurumtechnologyltd.com/password123 to get access token
2. Call POST /api/auth/complete-onboarding with Bearer token
3. Verify it returns 200 with {"success": true} instead of 500 error
4. Check that the onboarding process is now working without internal server errors

Focus Areas:
- Authentication flow is working
- complete-onboarding endpoint returns success (not 500)
- No database connection errors
- User profile level gets updated correctly
"""

import asyncio
import json
import time
import requests
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configuration
BACKEND_URL = "https://aurum-life-os.preview.emergentagent.com/api"
TEST_EMAIL = "marc.alleyne@aurumtechnologyltd.com"
TEST_PASSWORD = "password123"

class OnboardingEndpointTester:
    """Focused onboarding endpoint testing suite"""
    
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_results = []
        self.access_token = None
        self.user_id = None
        
    def log_result(self, test_name: str, success: bool, details: str, response_time: float = 0):
        """Log test result with performance metrics"""
        result = {
            "test_name": test_name,
            "success": success,
            "details": details,
            "response_time_ms": round(response_time * 1000, 1),
            "timestamp": datetime.utcnow().isoformat()
        }
        self.test_results.append(result)
        print(f"{'✅' if success else '❌'} {test_name}: {details} ({response_time*1000:.1f}ms)")
        
    def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> tuple:
        """Make HTTP request with timing and error handling"""
        url = f"{self.base_url}{endpoint}"
        
        # Default headers
        default_headers = {"Content-Type": "application/json"}
        if headers:
            default_headers.update(headers)
            
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=default_headers, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=default_headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            response_time = time.time() - start_time
            
            # Parse JSON response if possible
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}
                
            return response.status_code, response_data, response_time
            
        except requests.exceptions.Timeout:
            response_time = time.time() - start_time
            return 408, {"error": "Request timeout"}, response_time
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            return 500, {"error": str(e)}, response_time

    def test_authentication_flow(self):
        """Test authentication with specified credentials"""
        print("\n🔐 TESTING AUTHENTICATION FLOW")
        print("-" * 40)
        
        # First try with specified credentials
        login_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        status, data, response_time = self.make_request("POST", "/auth/login", login_data)
        
        success = status == 200 and "access_token" in data
        if success:
            self.access_token = data.get("access_token")
            details = f"Login successful with specified credentials - Token received, expires_in: {data.get('expires_in', 'N/A')}"
            self.log_result("Authentication Flow", success, details, response_time)
            return success
        else:
            details = f"Login failed with specified credentials - Status: {status}, Response: {data}"
            self.log_result("Authentication Flow (Specified Credentials)", False, details, response_time)
        
        # If specified credentials fail, try to create a new test account
        print("  🔄 Specified credentials failed, attempting to create test account...")
        
        import time
        test_user_data = {
            "username": f"onboarding_test_{int(time.time())}",
            "email": f"onboarding_test_{int(time.time())}@aurumtechnologyltd.com",
            "first_name": "Onboarding",
            "last_name": "Test",
            "password": "OnboardingTest123!"
        }
        
        # Try to create new user
        status, data, response_time = self.make_request("POST", "/auth/register", test_user_data)
        
        if status == 200:
            print(f"  ✅ Test account created: {test_user_data['email']}")
            
            # Now try to login with new account
            login_data = {
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
            
            status, data, response_time = self.make_request("POST", "/auth/login", login_data)
            
            success = status == 200 and "access_token" in data
            if success:
                self.access_token = data.get("access_token")
                details = f"Login successful with new test account - Token received, expires_in: {data.get('expires_in', 'N/A')}"
            else:
                details = f"Login failed with new test account - Status: {status}, Response: {data}"
                
            self.log_result("Authentication Flow (New Account)", success, details, response_time)
            return success
        else:
            details = f"Failed to create test account - Status: {status}, Response: {data}"
            self.log_result("Authentication Flow (Account Creation)", False, details, response_time)
            return False

    def test_get_user_profile(self):
        """Test getting current user profile to verify authentication"""
        if not self.access_token:
            self.log_result("Get User Profile", False, "No access token available", 0)
            return False
            
        headers = {"Authorization": f"Bearer {self.access_token}"}
        status, data, response_time = self.make_request("GET", "/auth/me", headers=headers)
        
        success = status == 200 and "id" in data
        if success:
            self.user_id = data.get("id")
            current_level = data.get("level", "unknown")
            onboarding_status = data.get("has_completed_onboarding", "unknown")
            details = f"User profile retrieved - ID: {self.user_id[:8] if self.user_id else 'N/A'}..., Level: {current_level}, Onboarding: {onboarding_status}"
        else:
            details = f"Failed to get user profile - Status: {status}, Response: {data}"
            
        self.log_result("Get User Profile", success, details, response_time)
        return success

    def test_complete_onboarding_endpoint(self):
        """Test the complete onboarding endpoint - MAIN TEST"""
        print("\n🎯 TESTING COMPLETE ONBOARDING ENDPOINT")
        print("-" * 45)
        
        if not self.access_token:
            self.log_result("Complete Onboarding Endpoint", False, "No access token available", 0)
            return False
            
        headers = {"Authorization": f"Bearer {self.access_token}"}
        status, data, response_time = self.make_request("POST", "/auth/complete-onboarding", headers=headers)
        
        # CRITICAL TEST: Should return 200 with {"success": true} instead of 500
        success = status == 200 and data.get("success") is True
        
        if status == 200:
            if data.get("success") is True:
                details = f"✅ ENDPOINT FIX SUCCESSFUL - Status: {status}, Response: {data}"
            else:
                details = f"⚠️ Status 200 but success not true - Status: {status}, Response: {data}"
        elif status == 500:
            details = f"❌ STILL RETURNING 500 ERROR - Status: {status}, Response: {data}"
        else:
            details = f"Unexpected status - Status: {status}, Response: {data}"
            
        self.log_result("Complete Onboarding Endpoint", success, details, response_time)
        return success

    def test_user_profile_level_update(self):
        """Verify that user profile level gets updated correctly after onboarding"""
        if not self.access_token:
            self.log_result("Profile Level Update", False, "No access token available", 0)
            return False
            
        headers = {"Authorization": f"Bearer {self.access_token}"}
        status, data, response_time = self.make_request("GET", "/auth/me", headers=headers)
        
        success = status == 200
        if success:
            current_level = data.get("level", "unknown")
            onboarding_status = data.get("has_completed_onboarding", "unknown")
            
            # Check if level is 2 or higher (indicating completed onboarding)
            level_updated = current_level >= 2 if isinstance(current_level, int) else False
            onboarding_complete = onboarding_status is True
            
            if level_updated and onboarding_complete:
                details = f"✅ Profile updated correctly - Level: {current_level}, Onboarding: {onboarding_status}"
            elif level_updated:
                details = f"⚠️ Level updated but onboarding flag issue - Level: {current_level}, Onboarding: {onboarding_status}"
            else:
                details = f"❌ Profile not updated - Level: {current_level}, Onboarding: {onboarding_status}"
                success = False
        else:
            details = f"Failed to get updated profile - Status: {status}, Response: {data}"
            
        self.log_result("Profile Level Update", success, details, response_time)
        return success

    def test_database_connection(self):
        """Test that database operations are working without errors"""
        print("\n🗄️ TESTING DATABASE CONNECTION")
        print("-" * 35)
        
        # Test health endpoint to verify backend is running
        status, data, response_time = self.make_request("GET", "/health")
        
        success = status == 200 and data.get("status") == "healthy"
        details = f"Backend health - Status: {status}, Health: {data.get('status', 'unknown')}"
        
        self.log_result("Database Connection", success, details, response_time)
        return success

    def run_onboarding_endpoint_test(self):
        """Run the focused onboarding endpoint test suite"""
        
        print("🚀 ONBOARDING ENDPOINT FIX TESTING")
        print("=" * 50)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Email: {TEST_EMAIL}")
        print(f"Started at: {datetime.utcnow().isoformat()}")
        print()
        
        # Test execution sequence
        test_sequence = [
            ("Database Connection Check", self.test_database_connection),
            ("Authentication Flow", self.test_authentication_flow),
            ("Get User Profile (Pre-Onboarding)", self.test_get_user_profile),
            ("Complete Onboarding Endpoint", self.test_complete_onboarding_endpoint),
            ("Profile Level Update Verification", self.test_user_profile_level_update)
        ]
        
        total_tests = len(test_sequence)
        passed_tests = 0
        critical_failure = False
        
        for test_name, test_func in test_sequence:
            print(f"\n🧪 {test_name}")
            print("-" * (len(test_name) + 4))
            
            try:
                result = test_func()
                if result:
                    passed_tests += 1
                elif test_name == "Complete Onboarding Endpoint":
                    critical_failure = True
            except Exception as e:
                self.log_result(test_name, False, f"Exception: {str(e)}", 0)
                if test_name == "Complete Onboarding Endpoint":
                    critical_failure = True
                    
        # Generate focused report
        self.generate_onboarding_test_report(total_tests, passed_tests, critical_failure)
        
        return passed_tests, total_tests, critical_failure

    def generate_onboarding_test_report(self, total_tests: int, passed_tests: int, critical_failure: bool):
        """Generate focused onboarding test report"""
        
        print("\n" + "=" * 60)
        print("📊 ONBOARDING ENDPOINT FIX TEST REPORT")
        print("=" * 60)
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Critical endpoint status
        onboarding_test = next((r for r in self.test_results if "Complete Onboarding Endpoint" in r["test_name"]), None)
        if onboarding_test:
            print(f"\n🎯 CRITICAL ENDPOINT STATUS:")
            if onboarding_test["success"]:
                print(f"  ✅ POST /api/auth/complete-onboarding: WORKING (200 with success: true)")
            else:
                print(f"  ❌ POST /api/auth/complete-onboarding: FAILING")
                print(f"     └─ {onboarding_test['details']}")
        
        # Detailed results
        print(f"\n📋 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"  {status} | {result['test_name']} | {result['response_time_ms']}ms")
            if not result["success"]:
                print(f"    └─ {result['details']}")
        
        # Critical issues summary
        failed_tests = [r for r in self.test_results if not r["success"]]
        if failed_tests:
            print(f"\n🚨 ISSUES IDENTIFIED:")
            for test in failed_tests:
                print(f"  • {test['test_name']}: {test['details']}")
        
        # Final assessment
        print(f"\n🎯 ONBOARDING ENDPOINT FIX ASSESSMENT:")
        if critical_failure:
            print("  ❌ CRITICAL: Complete onboarding endpoint still returning errors")
            print("  🔧 ACTION REQUIRED: Fix the 500 Internal Server Error in complete-onboarding")
        elif success_rate >= 80:
            print("  ✅ SUCCESS: Onboarding endpoint fix is working correctly")
            print("  🎉 RESULT: Returns 200 with {\"success\": true} as expected")
        else:
            print("  ⚠️ PARTIAL: Some issues detected but endpoint may be working")
            
        print(f"\nTest completed at: {datetime.utcnow().isoformat()}")


def main():
    """Main test execution function"""
    tester = OnboardingEndpointTester()
    passed, total, critical_failure = tester.run_onboarding_endpoint_test()
    
    # Exit with appropriate code
    if critical_failure:
        exit(2)  # Critical failure
    elif passed == total:
        exit(0)  # All tests passed
    else:
        exit(1)  # Some tests failed


if __name__ == "__main__":
    main()