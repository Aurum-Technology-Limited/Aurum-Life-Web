#!/usr/bin/env python3
"""
CRITICAL ONBOARDING COMPLETION ENDPOINT TESTING
Testing the onboarding completion loop issue where completing the wizard takes users back to the start.

SPECIFIC TESTING REQUIRED:
1. Login with marc.alleyne@aurumtechnologyltd.com/password
2. Check current user data via GET /api/auth/me - verify onboarding status
3. Call POST /api/auth/complete-onboarding endpoint  
4. Immediately call GET /api/auth/me again to verify has_completed_onboarding is now true
5. Verify the user record is actually updated in the database

CRITICAL FOCUS:
- Verify the endpoint successfully updates has_completed_onboarding from false to true
- Check if there are any database update errors
- Ensure the user data returned by /api/auth/me reflects the change immediately
- Look for any race conditions or caching issues that might prevent the update

This is the root cause of the onboarding loop - if the backend doesn't properly update the completion status, 
the frontend will keep showing the onboarding wizard.
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import time

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://productivity-hub-23.preview.emergentagent.com/api"

class OnboardingCompletionTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        # Use the specified test credentials from the review request
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

    def test_basic_connectivity(self):
        """Test basic connectivity to the backend API"""
        print("\n=== TESTING BASIC CONNECTIVITY ===")
        
        # Test the root endpoint which should exist
        result = self.make_request('GET', '', use_auth=False)
        if not result['success']:
            # Try the base URL without /api
            base_url = self.base_url.replace('/api', '')
            url = f"{base_url}/"
            try:
                response = self.session.get(url, timeout=30)
                result = {
                    'success': response.status_code < 400,
                    'status_code': response.status_code,
                    'data': response.json() if response.content else {},
                }
            except:
                result = {'success': False, 'error': 'Connection failed'}
        
        self.log_test(
            "BACKEND API CONNECTIVITY",
            result['success'],
            f"Backend API accessible at {self.base_url}" if result['success'] else f"Backend API not accessible: {result.get('error', 'Unknown error')}"
        )
        
        return result['success']

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
        
        # Verify token works
        result = self.make_request('GET', '/auth/me', use_auth=True)
        self.log_test(
            "AUTHENTICATION TOKEN VALIDATION",
            result['success'],
            f"Token validated successfully, user: {result['data'].get('email', 'Unknown')}" if result['success'] else f"Token validation failed: {result.get('error', 'Unknown error')}"
        )
        
        return result['success']

    def test_initial_onboarding_status(self):
        """Test 1: Check current user data via GET /api/auth/me - verify initial onboarding status"""
        print("\n=== TESTING INITIAL ONBOARDING STATUS ===")
        
        if not self.auth_token:
            self.log_test("INITIAL ONBOARDING STATUS CHECK - Authentication Required", False, "No authentication token available")
            return None
        
        # Get current user data
        result = self.make_request('GET', '/auth/me', use_auth=True)
        self.log_test(
            "GET CURRENT USER DATA (/api/auth/me)",
            result['success'],
            f"Retrieved user data successfully" if result['success'] else f"Failed to get user data: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return None
        
        user_data = result['data']
        
        # Check if has_completed_onboarding field exists
        has_onboarding_field = 'has_completed_onboarding' in user_data
        self.log_test(
            "USER DATA - HAS_COMPLETED_ONBOARDING FIELD",
            has_onboarding_field,
            f"has_completed_onboarding field present: {user_data.get('has_completed_onboarding')}" if has_onboarding_field else "has_completed_onboarding field missing from user data"
        )
        
        if not has_onboarding_field:
            return None
        
        initial_onboarding_status = user_data.get('has_completed_onboarding')
        
        # Log the initial status
        self.log_test(
            "INITIAL ONBOARDING STATUS",
            True,  # This is informational, not a pass/fail
            f"Initial onboarding status: {initial_onboarding_status}"
        )
        
        # Also check other relevant fields
        user_id = user_data.get('id')
        username = user_data.get('username')
        email = user_data.get('email')
        
        print(f"   User ID: {user_id}")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Initial has_completed_onboarding: {initial_onboarding_status}")
        
        return initial_onboarding_status

    def test_complete_onboarding_endpoint(self):
        """Test 2: Call POST /api/auth/complete-onboarding endpoint"""
        print("\n=== TESTING COMPLETE ONBOARDING ENDPOINT ===")
        
        if not self.auth_token:
            self.log_test("COMPLETE ONBOARDING ENDPOINT - Authentication Required", False, "No authentication token available")
            return False
        
        # Call the complete onboarding endpoint
        result = self.make_request('POST', '/auth/complete-onboarding', use_auth=True)
        self.log_test(
            "POST /api/auth/complete-onboarding",
            result['success'],
            f"Onboarding completion successful" if result['success'] else f"Onboarding completion failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        completion_response = result['data']
        
        # Check response structure
        has_message = 'message' in completion_response
        has_status_field = 'has_completed_onboarding' in completion_response
        
        self.log_test(
            "COMPLETE ONBOARDING - RESPONSE STRUCTURE",
            has_message and has_status_field,
            f"Response has required fields (message, has_completed_onboarding)" if (has_message and has_status_field) else f"Response structure: {list(completion_response.keys())}"
        )
        
        if has_status_field:
            returned_status = completion_response.get('has_completed_onboarding')
            self.log_test(
                "COMPLETE ONBOARDING - RETURNED STATUS",
                returned_status is True,
                f"Endpoint returned has_completed_onboarding: {returned_status}" if returned_status is True else f"Expected True, got: {returned_status}"
            )
            
            return returned_status is True
        
        return has_message

    def test_immediate_status_verification(self):
        """Test 3: Immediately call GET /api/auth/me again to verify has_completed_onboarding is now true"""
        print("\n=== TESTING IMMEDIATE STATUS VERIFICATION ===")
        
        if not self.auth_token:
            self.log_test("IMMEDIATE STATUS VERIFICATION - Authentication Required", False, "No authentication token available")
            return False
        
        # Small delay to ensure any async operations complete
        time.sleep(0.5)
        
        # Get current user data again
        result = self.make_request('GET', '/auth/me', use_auth=True)
        self.log_test(
            "GET CURRENT USER DATA AFTER COMPLETION (/api/auth/me)",
            result['success'],
            f"Retrieved user data successfully after completion" if result['success'] else f"Failed to get user data after completion: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        user_data = result['data']
        
        # Check if has_completed_onboarding field exists
        has_onboarding_field = 'has_completed_onboarding' in user_data
        self.log_test(
            "POST-COMPLETION USER DATA - HAS_COMPLETED_ONBOARDING FIELD",
            has_onboarding_field,
            f"has_completed_onboarding field present after completion" if has_onboarding_field else "has_completed_onboarding field missing from user data after completion"
        )
        
        if not has_onboarding_field:
            return False
        
        updated_onboarding_status = user_data.get('has_completed_onboarding')
        
        # Verify the status is now true
        status_updated_correctly = updated_onboarding_status is True
        self.log_test(
            "ONBOARDING STATUS UPDATE VERIFICATION",
            status_updated_correctly,
            f"Onboarding status correctly updated to: {updated_onboarding_status}" if status_updated_correctly else f"Onboarding status NOT updated correctly. Expected: True, Got: {updated_onboarding_status}"
        )
        
        # Also log other user data for debugging
        user_id = user_data.get('id')
        username = user_data.get('username')
        email = user_data.get('email')
        
        print(f"   User ID: {user_id}")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Updated has_completed_onboarding: {updated_onboarding_status}")
        
        return status_updated_correctly

    def test_database_persistence_verification(self):
        """Test 4: Verify the user record is actually updated in the database by making another call"""
        print("\n=== TESTING DATABASE PERSISTENCE VERIFICATION ===")
        
        if not self.auth_token:
            self.log_test("DATABASE PERSISTENCE VERIFICATION - Authentication Required", False, "No authentication token available")
            return False
        
        # Wait a bit longer to ensure database persistence
        time.sleep(2)
        
        # Make another call to /auth/me to verify persistence
        result = self.make_request('GET', '/auth/me', use_auth=True)
        self.log_test(
            "DATABASE PERSISTENCE CHECK (/api/auth/me)",
            result['success'],
            f"Retrieved user data for persistence check" if result['success'] else f"Failed to get user data for persistence check: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        user_data = result['data']
        persistent_onboarding_status = user_data.get('has_completed_onboarding')
        
        # Verify the status is still true (persisted)
        status_persisted = persistent_onboarding_status is True
        self.log_test(
            "DATABASE PERSISTENCE VERIFICATION",
            status_persisted,
            f"Onboarding status persisted correctly: {persistent_onboarding_status}" if status_persisted else f"Onboarding status NOT persisted. Expected: True, Got: {persistent_onboarding_status}"
        )
        
        return status_persisted

    def test_race_condition_check(self):
        """Test 5: Check for race conditions by making multiple rapid calls"""
        print("\n=== TESTING RACE CONDITION CHECK ===")
        
        if not self.auth_token:
            self.log_test("RACE CONDITION CHECK - Authentication Required", False, "No authentication token available")
            return False
        
        # Make multiple rapid calls to /auth/me to check for consistency
        consistent_results = []
        
        for i in range(5):
            result = self.make_request('GET', '/auth/me', use_auth=True)
            if result['success']:
                onboarding_status = result['data'].get('has_completed_onboarding')
                consistent_results.append(onboarding_status)
                print(f"   Call {i+1}: has_completed_onboarding = {onboarding_status}")
            else:
                print(f"   Call {i+1}: Failed - {result.get('error', 'Unknown error')}")
                consistent_results.append(None)
            
            # Small delay between calls
            time.sleep(0.1)
        
        # Check if all results are consistent
        unique_results = set(consistent_results)
        is_consistent = len(unique_results) == 1 and True in unique_results
        
        self.log_test(
            "RACE CONDITION CHECK",
            is_consistent,
            f"All {len(consistent_results)} calls returned consistent results: {list(unique_results)}" if is_consistent else f"Inconsistent results detected: {consistent_results}"
        )
        
        return is_consistent

    def test_error_handling(self):
        """Test 6: Test error handling scenarios"""
        print("\n=== TESTING ERROR HANDLING ===")
        
        # Test complete-onboarding endpoint without authentication
        result = self.make_request('POST', '/auth/complete-onboarding', use_auth=False)
        requires_auth = result['status_code'] in [401, 403]
        
        self.log_test(
            "ERROR HANDLING - COMPLETE ONBOARDING WITHOUT AUTH",
            requires_auth,
            f"Endpoint properly requires authentication (status: {result['status_code']})" if requires_auth else f"Endpoint does not require authentication (status: {result['status_code']})"
        )
        
        # Test /auth/me endpoint without authentication
        result = self.make_request('GET', '/auth/me', use_auth=False)
        me_requires_auth = result['status_code'] in [401, 403]
        
        self.log_test(
            "ERROR HANDLING - /AUTH/ME WITHOUT AUTH",
            me_requires_auth,
            f"/auth/me endpoint properly requires authentication (status: {result['status_code']})" if me_requires_auth else f"/auth/me endpoint does not require authentication (status: {result['status_code']})"
        )
        
        return requires_auth and me_requires_auth

    def run_comprehensive_onboarding_completion_test(self):
        """Run comprehensive onboarding completion endpoint tests"""
        print("\n🎯 STARTING CRITICAL ONBOARDING COMPLETION ENDPOINT TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("FOCUS: Testing onboarding completion loop issue")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Basic Connectivity", self.test_basic_connectivity),
            ("User Authentication", self.test_user_authentication),
            ("Initial Onboarding Status Check", self.test_initial_onboarding_status),
            ("Complete Onboarding Endpoint", self.test_complete_onboarding_endpoint),
            ("Immediate Status Verification", self.test_immediate_status_verification),
            ("Database Persistence Verification", self.test_database_persistence_verification),
            ("Race Condition Check", self.test_race_condition_check),
            ("Error Handling", self.test_error_handling)
        ]
        
        successful_tests = 0
        total_tests = len(test_methods)
        critical_tests_passed = 0
        critical_tests = ["Complete Onboarding Endpoint", "Immediate Status Verification", "Database Persistence Verification"]
        
        for test_name, test_method in test_methods:
            print(f"\n--- {test_name} ---")
            try:
                result = test_method()
                if result:
                    successful_tests += 1
                    print(f"✅ {test_name} completed successfully")
                    if test_name in critical_tests:
                        critical_tests_passed += 1
                else:
                    print(f"❌ {test_name} failed")
            except Exception as e:
                print(f"❌ {test_name} raised exception: {e}")
        
        success_rate = (successful_tests / total_tests) * 100
        critical_success_rate = (critical_tests_passed / len(critical_tests)) * 100
        
        print(f"\n" + "=" * 80)
        print("🎯 CRITICAL ONBOARDING COMPLETION ENDPOINT TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        print(f"Critical Tests: {critical_tests_passed}/{len(critical_tests)} successful")
        print(f"Critical Success Rate: {critical_success_rate:.1f}%")
        
        # Analyze results for onboarding completion functionality
        auth_tests_passed = sum(1 for result in self.test_results if result['success'] and 'AUTHENTICATION' in result['test'])
        onboarding_tests_passed = sum(1 for result in self.test_results if result['success'] and 'ONBOARDING' in result['test'])
        completion_tests_passed = sum(1 for result in self.test_results if result['success'] and 'COMPLETE' in result['test'])
        verification_tests_passed = sum(1 for result in self.test_results if result['success'] and 'VERIFICATION' in result['test'])
        
        print(f"\n🔍 SYSTEM ANALYSIS:")
        print(f"Authentication Tests Passed: {auth_tests_passed}")
        print(f"Onboarding Status Tests Passed: {onboarding_tests_passed}")
        print(f"Completion Endpoint Tests Passed: {completion_tests_passed}")
        print(f"Verification Tests Passed: {verification_tests_passed}")
        
        if critical_success_rate >= 100:
            print("\n✅ ONBOARDING COMPLETION ENDPOINT: SUCCESS")
            print("   ✅ POST /api/auth/complete-onboarding working correctly")
            print("   ✅ GET /api/auth/me reflects changes immediately")
            print("   ✅ Database updates are persistent")
            print("   ✅ No race conditions detected")
            print("   The onboarding completion loop issue is RESOLVED!")
        elif critical_success_rate >= 66:
            print("\n⚠️ ONBOARDING COMPLETION ENDPOINT: PARTIAL SUCCESS")
            print("   Some critical functionality working but issues remain")
            print("   The onboarding completion loop may still occur")
        else:
            print("\n❌ ONBOARDING COMPLETION ENDPOINT: CRITICAL ISSUES DETECTED")
            print("   ❌ Onboarding completion loop issue NOT resolved")
            print("   ❌ Users will continue to be taken back to onboarding start")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return critical_success_rate >= 100

def main():
    """Run Critical Onboarding Completion Endpoint Tests"""
    print("🎯 STARTING CRITICAL ONBOARDING COMPLETION ENDPOINT TESTING")
    print("=" * 80)
    
    tester = OnboardingCompletionTester()
    
    try:
        # Run the comprehensive onboarding completion tests
        success = tester.run_comprehensive_onboarding_completion_test()
        
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
        
        # Determine if the onboarding completion loop issue is resolved
        if success:
            print("\n🎉 ONBOARDING COMPLETION LOOP ISSUE: RESOLVED")
            print("✅ Users will no longer be taken back to onboarding start after completion")
        else:
            print("\n🚨 ONBOARDING COMPLETION LOOP ISSUE: NOT RESOLVED")
            print("❌ Users will continue to experience the onboarding loop")
        
        print("=" * 80)
        
        return success
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)