#!/usr/bin/env python3
"""
ONBOARDING AND AUTHENTICATION FLOW TESTING
Testing critical onboarding and authentication flow to ensure fixes work correctly.

FOCUS AREAS:
1. Test /api/auth/me endpoint to ensure user data is returned correctly
2. Test /api/auth/complete-onboarding endpoint to verify it updates user status properly
3. Verify that after calling complete-onboarding, subsequent calls to /api/auth/me return updated has_completed_onboarding status
4. Quick test of core API endpoints (pillars, areas, projects, tasks) to ensure they still work

KEY TEST: Ensuring that after calling /api/auth/complete-onboarding, the user's has_completed_onboarding field is properly updated and returned by /api/auth/me.

CREDENTIALS: marc.alleyne@aurumtechnologyltd.com / password
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import time

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://2add7c3c-bc98-404b-af7c-7c73ee7f9c41.preview.emergentagent.com/api"

class OnboardingAuthTester:
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
        
        if not self.auth_token:
            self.log_test(
                "TOKEN EXTRACTION",
                False,
                f"No access_token in response: {list(token_data.keys())}"
            )
            return False
        
        return True

    def test_auth_me_endpoint_initial(self):
        """Test /api/auth/me endpoint to get initial user data"""
        print("\n=== TESTING /api/auth/me ENDPOINT (INITIAL) ===")
        
        if not self.auth_token:
            self.log_test("AUTH/ME INITIAL - Authentication Required", False, "No authentication token available")
            return False, None
        
        result = self.make_request('GET', '/auth/me', use_auth=True)
        self.log_test(
            "GET /api/auth/me (INITIAL)",
            result['success'],
            f"Retrieved user data successfully" if result['success'] else f"Failed to get user data: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False, None
        
        user_data = result['data']
        
        # Check if response has expected user fields
        expected_fields = ['id', 'email']
        missing_fields = [field for field in expected_fields if field not in user_data]
        
        if missing_fields:
            self.log_test(
                "AUTH/ME INITIAL - REQUIRED FIELDS",
                False,
                f"Missing required fields: {missing_fields}"
            )
            return False, None
        
        # Check has_completed_onboarding field
        has_onboarding_field = 'has_completed_onboarding' in user_data
        onboarding_status = user_data.get('has_completed_onboarding')
        
        self.log_test(
            "AUTH/ME INITIAL - ONBOARDING FIELD",
            has_onboarding_field,
            f"has_completed_onboarding field present: {onboarding_status}" if has_onboarding_field else "has_completed_onboarding field missing"
        )
        
        print(f"   Initial onboarding status: {onboarding_status}")
        return True, onboarding_status

    def test_complete_onboarding_endpoint(self):
        """Test /api/auth/complete-onboarding endpoint"""
        print("\n=== TESTING /api/auth/complete-onboarding ENDPOINT ===")
        
        if not self.auth_token:
            self.log_test("COMPLETE ONBOARDING - Authentication Required", False, "No authentication token available")
            return False
        
        result = self.make_request('POST', '/auth/complete-onboarding', use_auth=True)
        self.log_test(
            "POST /api/auth/complete-onboarding",
            result['success'],
            f"Onboarding completion successful" if result['success'] else f"Failed to complete onboarding: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        response_data = result['data']
        
        # Check response structure
        has_message = 'message' in response_data
        has_onboarding_status = 'has_completed_onboarding' in response_data
        
        self.log_test(
            "COMPLETE ONBOARDING - RESPONSE STRUCTURE",
            has_message and has_onboarding_status,
            f"Response has required fields" if (has_message and has_onboarding_status) else f"Response structure: {list(response_data.keys())}"
        )
        
        # Verify onboarding status is set to True
        onboarding_status = response_data.get('has_completed_onboarding')
        status_correct = onboarding_status is True
        
        self.log_test(
            "COMPLETE ONBOARDING - STATUS UPDATE",
            status_correct,
            f"Onboarding status set to True" if status_correct else f"Onboarding status incorrect: {onboarding_status}"
        )
        
        return status_correct

    def test_auth_me_endpoint_after_onboarding(self):
        """Test /api/auth/me endpoint after completing onboarding to verify status update"""
        print("\n=== TESTING /api/auth/me ENDPOINT (AFTER ONBOARDING) ===")
        
        if not self.auth_token:
            self.log_test("AUTH/ME AFTER - Authentication Required", False, "No authentication token available")
            return False
        
        # Wait a moment for the update to propagate
        time.sleep(1)
        
        result = self.make_request('GET', '/auth/me', use_auth=True)
        self.log_test(
            "GET /api/auth/me (AFTER ONBOARDING)",
            result['success'],
            f"Retrieved user data successfully" if result['success'] else f"Failed to get user data: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        user_data = result['data']
        
        # Check has_completed_onboarding field
        has_onboarding_field = 'has_completed_onboarding' in user_data
        onboarding_status = user_data.get('has_completed_onboarding')
        
        self.log_test(
            "AUTH/ME AFTER - ONBOARDING FIELD PRESENT",
            has_onboarding_field,
            f"has_completed_onboarding field present" if has_onboarding_field else "has_completed_onboarding field missing"
        )
        
        # CRITICAL TEST: Verify onboarding status is now True
        status_updated = onboarding_status is True
        self.log_test(
            "AUTH/ME AFTER - ONBOARDING STATUS UPDATED",
            status_updated,
            f"✅ CRITICAL SUCCESS: has_completed_onboarding is now True" if status_updated else f"❌ CRITICAL FAILURE: has_completed_onboarding is {onboarding_status}, expected True"
        )
        
        print(f"   Updated onboarding status: {onboarding_status}")
        return status_updated

    def test_core_api_endpoints(self):
        """Quick test of core API endpoints to ensure they still work"""
        print("\n=== TESTING CORE API ENDPOINTS ===")
        
        if not self.auth_token:
            self.log_test("CORE ENDPOINTS - Authentication Required", False, "No authentication token available")
            return False
        
        # Test core endpoints
        endpoints = [
            ('/pillars', 'Pillars'),
            ('/areas', 'Areas'),
            ('/projects', 'Projects'),
            ('/tasks', 'Tasks')
        ]
        
        successful_endpoints = 0
        total_endpoints = len(endpoints)
        
        for endpoint, name in endpoints:
            result = self.make_request('GET', endpoint, use_auth=True)
            success = result['success']
            
            self.log_test(
                f"CORE API - {name}",
                success,
                f"{name} endpoint working correctly" if success else f"{name} endpoint failed: {result.get('error', 'Unknown error')}"
            )
            
            if success:
                successful_endpoints += 1
                # Log data count if available
                data = result['data']
                if isinstance(data, list):
                    print(f"   Retrieved {len(data)} {name.lower()}")
        
        success_rate = (successful_endpoints / total_endpoints) * 100
        overall_success = success_rate >= 75  # 75% success rate threshold
        
        self.log_test(
            "CORE API ENDPOINTS - OVERALL",
            overall_success,
            f"Core API endpoints: {successful_endpoints}/{total_endpoints} working ({success_rate:.1f}%)"
        )
        
        return overall_success

    def run_onboarding_auth_test(self):
        """Run comprehensive onboarding and authentication flow test"""
        print("\n🔐 STARTING ONBOARDING AND AUTHENTICATION FLOW TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 80)
        
        # Track the critical onboarding flow
        initial_onboarding_status = None
        
        # Run all tests in sequence
        test_methods = [
            ("User Authentication", self.test_user_authentication),
            ("Initial /api/auth/me", lambda: self.test_auth_me_endpoint_initial()),
            ("Complete Onboarding", self.test_complete_onboarding_endpoint),
            ("Updated /api/auth/me", self.test_auth_me_endpoint_after_onboarding),
            ("Core API Endpoints", self.test_core_api_endpoints)
        ]
        
        successful_tests = 0
        total_tests = len(test_methods)
        critical_onboarding_flow_success = False
        
        for test_name, test_method in test_methods:
            print(f"\n--- {test_name} ---")
            try:
                if test_name == "Initial /api/auth/me":
                    # Special handling for initial auth/me test to capture onboarding status
                    success, initial_status = test_method()
                    initial_onboarding_status = initial_status
                    if success:
                        successful_tests += 1
                        print(f"✅ {test_name} completed successfully")
                    else:
                        print(f"❌ {test_name} failed")
                else:
                    if test_method():
                        successful_tests += 1
                        print(f"✅ {test_name} completed successfully")
                        
                        # Check if this is the critical onboarding flow completion
                        if test_name == "Updated /api/auth/me":
                            critical_onboarding_flow_success = True
                    else:
                        print(f"❌ {test_name} failed")
            except Exception as e:
                print(f"❌ {test_name} raised exception: {e}")
        
        success_rate = (successful_tests / total_tests) * 100
        
        print(f"\n" + "=" * 80)
        print("🔐 ONBOARDING AND AUTHENTICATION FLOW TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Critical onboarding flow analysis
        print(f"\n🎯 CRITICAL ONBOARDING FLOW ANALYSIS:")
        print(f"Initial onboarding status: {initial_onboarding_status}")
        
        if critical_onboarding_flow_success:
            print("✅ CRITICAL SUCCESS: Onboarding flow working correctly!")
            print("   ✅ /api/auth/me returns user data correctly")
            print("   ✅ /api/auth/complete-onboarding updates status properly")
            print("   ✅ Subsequent /api/auth/me calls return updated has_completed_onboarding status")
        else:
            print("❌ CRITICAL FAILURE: Onboarding flow has issues!")
            print("   Issues detected in the onboarding status update process")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 80 and critical_onboarding_flow_success

def main():
    """Run Onboarding and Authentication Flow Tests"""
    print("🔐 STARTING ONBOARDING AND AUTHENTICATION FLOW BACKEND TESTING")
    print("=" * 80)
    
    tester = OnboardingAuthTester()
    
    try:
        # Run the comprehensive onboarding and authentication flow tests
        success = tester.run_onboarding_auth_test()
        
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
        
        return success_rate >= 80
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)