#!/usr/bin/env python3
"""
MONTHLY GOAL CRUD BACKEND TEST
Testing Monthly Goal CRUD operations as requested in review.

TEST SEQUENCE:
1) Auth as test user
2) GET /api/alignment/monthly-goal -> expect 200, {goal: number}
3) PUT /api/alignment/monthly-goal {goal: 123} -> expect 200, status ok
4) GET again -> expect goal == 123

CREDENTIALS: marc.alleyne@aurumtechnologyltd.com / password123
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://productivity-hub-23.preview.emergentagent.com/api"

class MonthlyGoalCRUDTester:
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
        
        # Verify token works
        result = self.make_request('GET', '/auth/me', use_auth=True)
        self.log_test(
            "AUTHENTICATION TOKEN VALIDATION",
            result['success'],
            f"Token validated successfully, user: {result['data'].get('email', 'Unknown')}" if result['success'] else f"Token validation failed: {result.get('error', 'Unknown error')}"
        )
        
        return result['success']

    def test_get_monthly_goal_initial(self):
        """Test GET /api/alignment/monthly-goal (initial state)"""
        print("\n=== TESTING GET MONTHLY GOAL (INITIAL) ===")
        
        if not self.auth_token:
            self.log_test("GET MONTHLY GOAL - Authentication Required", False, "No authentication token available")
            return False, None
        
        # Test GET /api/alignment/monthly-goal
        result = self.make_request('GET', '/alignment/monthly-goal', use_auth=True)
        
        if result['success']:
            response_data = result['data']
            
            # Check if response has the expected structure {goal: number}
            has_goal_field = 'goal' in response_data
            goal_value = response_data.get('goal')
            is_number = isinstance(goal_value, (int, float))
            
            self.log_test(
                "GET MONTHLY GOAL - INITIAL STATE",
                has_goal_field and is_number,
                f"Retrieved monthly goal: {goal_value}" if (has_goal_field and is_number) else f"Invalid response structure: {response_data}"
            )
            
            return has_goal_field and is_number, goal_value
        else:
            self.log_test(
                "GET MONTHLY GOAL - INITIAL STATE",
                False,
                f"Failed to get monthly goal: {result.get('error', 'Unknown error')}"
            )
            return False, None

    def test_put_monthly_goal(self):
        """Test PUT /api/alignment/monthly-goal with goal: 123"""
        print("\n=== TESTING PUT MONTHLY GOAL ===")
        
        if not self.auth_token:
            self.log_test("PUT MONTHLY GOAL - Authentication Required", False, "No authentication token available")
            return False
        
        # Test PUT /api/alignment/monthly-goal with goal: 123
        update_data = {"goal": 123}
        
        result = self.make_request('PUT', '/alignment/monthly-goal', data=update_data, use_auth=True)
        
        if result['success']:
            response_data = result['data']
            
            # Check if response has status: ok
            has_status = 'status' in response_data
            status_ok = response_data.get('status') == 'ok'
            
            self.log_test(
                "PUT MONTHLY GOAL",
                has_status and status_ok,
                f"Monthly goal updated successfully: {response_data}" if (has_status and status_ok) else f"Invalid response structure: {response_data}"
            )
            
            return has_status and status_ok
        else:
            self.log_test(
                "PUT MONTHLY GOAL",
                False,
                f"Failed to update monthly goal: {result.get('error', 'Unknown error')}"
            )
            return False

    def test_get_monthly_goal_verification(self):
        """Test GET /api/alignment/monthly-goal (verify goal == 123)"""
        print("\n=== TESTING GET MONTHLY GOAL (VERIFICATION) ===")
        
        if not self.auth_token:
            self.log_test("GET MONTHLY GOAL VERIFICATION - Authentication Required", False, "No authentication token available")
            return False
        
        # Test GET /api/alignment/monthly-goal again to verify update
        result = self.make_request('GET', '/alignment/monthly-goal', use_auth=True)
        
        if result['success']:
            response_data = result['data']
            
            # Check if goal == 123
            goal_value = response_data.get('goal')
            goal_matches = goal_value == 123
            
            self.log_test(
                "GET MONTHLY GOAL - VERIFICATION",
                goal_matches,
                f"Goal verified as 123: {goal_value}" if goal_matches else f"Goal mismatch - expected 123, got: {goal_value}"
            )
            
            return goal_matches
        else:
            self.log_test(
                "GET MONTHLY GOAL - VERIFICATION",
                False,
                f"Failed to verify monthly goal: {result.get('error', 'Unknown error')}"
            )
            return False

    def run_monthly_goal_crud_test(self):
        """Run comprehensive monthly goal CRUD test as specified in review"""
        print("\n🎯 STARTING MONTHLY GOAL CRUD BACKEND TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 80)
        
        # Test sequence as specified in review request
        test_sequence = [
            ("1. User Authentication", self.test_user_authentication),
            ("2. GET Monthly Goal (Initial)", lambda: self.test_get_monthly_goal_initial()[0]),
            ("3. PUT Monthly Goal (goal: 123)", self.test_put_monthly_goal),
            ("4. GET Monthly Goal (Verify goal == 123)", self.test_get_monthly_goal_verification)
        ]
        
        successful_tests = 0
        total_tests = len(test_sequence)
        
        for test_name, test_method in test_sequence:
            print(f"\n--- {test_name} ---")
            try:
                if test_method():
                    successful_tests += 1
                    print(f"✅ {test_name} completed successfully")
                else:
                    print(f"❌ {test_name} failed")
                    # Continue with remaining tests even if one fails
            except Exception as e:
                print(f"❌ {test_name} raised exception: {e}")
        
        success_rate = (successful_tests / total_tests) * 100
        
        print(f"\n" + "=" * 80)
        print("🎯 MONTHLY GOAL CRUD TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Sequence: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Detailed results
        print(f"\n🔍 DETAILED RESULTS:")
        for result in self.test_results:
            status_icon = "✅" if result['success'] else "❌"
            print(f"{status_icon} {result['test']}: {result['message']}")
        
        if success_rate == 100:
            print("\n✅ MONTHLY GOAL CRUD SYSTEM: COMPLETE SUCCESS")
            print("   ✅ Authentication working")
            print("   ✅ GET /api/alignment/monthly-goal returns {goal: number}")
            print("   ✅ PUT /api/alignment/monthly-goal accepts {goal: 123} and returns status ok")
            print("   ✅ GET verification confirms goal == 123")
            print("   The Monthly Goal CRUD system is fully functional!")
        elif success_rate >= 75:
            print("\n⚠️ MONTHLY GOAL CRUD SYSTEM: MOSTLY FUNCTIONAL")
            print("   Most operations working with minor issues")
        else:
            print("\n❌ MONTHLY GOAL CRUD SYSTEM: SIGNIFICANT ISSUES")
            print("   Critical failures detected in Monthly Goal CRUD operations")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 75

def main():
    """Run Monthly Goal CRUD Tests"""
    print("🎯 STARTING MONTHLY GOAL CRUD BACKEND TESTING")
    print("=" * 80)
    
    tester = MonthlyGoalCRUDTester()
    
    try:
        # Run the comprehensive monthly goal CRUD tests
        success = tester.run_monthly_goal_crud_test()
        
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