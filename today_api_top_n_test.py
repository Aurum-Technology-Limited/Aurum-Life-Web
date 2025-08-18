#!/usr/bin/env python3
"""
TODAY API TOP_N ENFORCEMENT TESTING
Re-test Today API top_n enforcement as requested:
1) Auth as before
2) GET /api/today?top_n=3 -> expect exactly 3 tasks returned, sorted by score desc
3) GET /api/today?top_n=1 -> expect exactly 1 task
4) GET /api/today (default 3) -> expect 3 tasks
Return concise pass/fail with counts and any mismatches.
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://taskpilot-2.preview.emergentagent.com/api"

class TodayAPITopNTester:
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

    def test_today_api_top_n_3(self):
        """Test GET /api/today?top_n=3 -> expect exactly 3 tasks returned, sorted by score desc"""
        print("\n=== TESTING TODAY API WITH top_n=3 ===")
        
        if not self.auth_token:
            self.log_test("TODAY API top_n=3 - Authentication Required", False, "No authentication token available")
            return False
        
        # Test GET /api/today?top_n=3
        result = self.make_request('GET', '/today', params={'top_n': 3}, use_auth=True)
        
        if not result['success']:
            self.log_test(
                "TODAY API top_n=3",
                False,
                f"API call failed: {result.get('error', 'Unknown error')}"
            )
            return False
        
        response_data = result['data']
        
        # Check if response has tasks
        if 'tasks' not in response_data:
            self.log_test(
                "TODAY API top_n=3 - Response Structure",
                False,
                f"Response missing 'tasks' field: {list(response_data.keys())}"
            )
            return False
        
        tasks = response_data['tasks']
        task_count = len(tasks)
        
        # Check if exactly 3 tasks returned
        if task_count != 3:
            self.log_test(
                "TODAY API top_n=3 - Task Count",
                False,
                f"Expected exactly 3 tasks, got {task_count} tasks"
            )
            return False
        
        # Check if tasks are sorted by score desc
        scores = []
        for task in tasks:
            if 'score' in task:
                scores.append(task['score'])
            else:
                self.log_test(
                    "TODAY API top_n=3 - Score Field",
                    False,
                    f"Task missing 'score' field: {task.get('name', 'Unknown task')}"
                )
                return False
        
        # Verify scores are in descending order
        is_sorted_desc = all(scores[i] >= scores[i+1] for i in range(len(scores)-1))
        
        if not is_sorted_desc:
            self.log_test(
                "TODAY API top_n=3 - Score Sorting",
                False,
                f"Tasks not sorted by score desc. Scores: {scores}"
            )
            return False
        
        self.log_test(
            "TODAY API top_n=3",
            True,
            f"Returned exactly 3 tasks, sorted by score desc. Scores: {scores}"
        )
        return True

    def test_today_api_top_n_1(self):
        """Test GET /api/today?top_n=1 -> expect exactly 1 task"""
        print("\n=== TESTING TODAY API WITH top_n=1 ===")
        
        if not self.auth_token:
            self.log_test("TODAY API top_n=1 - Authentication Required", False, "No authentication token available")
            return False
        
        # Test GET /api/today?top_n=1
        result = self.make_request('GET', '/today', params={'top_n': 1}, use_auth=True)
        
        if not result['success']:
            self.log_test(
                "TODAY API top_n=1",
                False,
                f"API call failed: {result.get('error', 'Unknown error')}"
            )
            return False
        
        response_data = result['data']
        
        # Check if response has tasks
        if 'tasks' not in response_data:
            self.log_test(
                "TODAY API top_n=1 - Response Structure",
                False,
                f"Response missing 'tasks' field: {list(response_data.keys())}"
            )
            return False
        
        tasks = response_data['tasks']
        task_count = len(tasks)
        
        # Check if exactly 1 task returned
        if task_count != 1:
            self.log_test(
                "TODAY API top_n=1 - Task Count",
                False,
                f"Expected exactly 1 task, got {task_count} tasks"
            )
            return False
        
        # Check if task has score
        task = tasks[0]
        if 'score' not in task:
            self.log_test(
                "TODAY API top_n=1 - Score Field",
                False,
                f"Task missing 'score' field: {task.get('name', 'Unknown task')}"
            )
            return False
        
        self.log_test(
            "TODAY API top_n=1",
            True,
            f"Returned exactly 1 task with score: {task['score']}"
        )
        return True

    def test_today_api_default(self):
        """Test GET /api/today (default 3) -> expect 3 tasks"""
        print("\n=== TESTING TODAY API WITH DEFAULT top_n ===")
        
        if not self.auth_token:
            self.log_test("TODAY API default - Authentication Required", False, "No authentication token available")
            return False
        
        # Test GET /api/today (no top_n parameter)
        result = self.make_request('GET', '/today', use_auth=True)
        
        if not result['success']:
            self.log_test(
                "TODAY API default",
                False,
                f"API call failed: {result.get('error', 'Unknown error')}"
            )
            return False
        
        response_data = result['data']
        
        # Check if response has tasks
        if 'tasks' not in response_data:
            self.log_test(
                "TODAY API default - Response Structure",
                False,
                f"Response missing 'tasks' field: {list(response_data.keys())}"
            )
            return False
        
        tasks = response_data['tasks']
        task_count = len(tasks)
        
        # Check if exactly 3 tasks returned (default)
        if task_count != 3:
            self.log_test(
                "TODAY API default - Task Count",
                False,
                f"Expected exactly 3 tasks (default), got {task_count} tasks"
            )
            return False
        
        # Check if tasks are sorted by score desc
        scores = []
        for task in tasks:
            if 'score' in task:
                scores.append(task['score'])
            else:
                self.log_test(
                    "TODAY API default - Score Field",
                    False,
                    f"Task missing 'score' field: {task.get('name', 'Unknown task')}"
                )
                return False
        
        # Verify scores are in descending order
        is_sorted_desc = all(scores[i] >= scores[i+1] for i in range(len(scores)-1))
        
        if not is_sorted_desc:
            self.log_test(
                "TODAY API default - Score Sorting",
                False,
                f"Tasks not sorted by score desc. Scores: {scores}"
            )
            return False
        
        self.log_test(
            "TODAY API default",
            True,
            f"Returned exactly 3 tasks (default), sorted by score desc. Scores: {scores}"
        )
        return True

    def run_today_api_top_n_tests(self):
        """Run comprehensive Today API top_n enforcement tests"""
        print("\n📅 STARTING TODAY API TOP_N ENFORCEMENT TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("User Authentication", self.test_user_authentication),
            ("Today API top_n=3", self.test_today_api_top_n_3),
            ("Today API top_n=1", self.test_today_api_top_n_1),
            ("Today API default", self.test_today_api_default)
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
        print("📅 TODAY API TOP_N ENFORCEMENT TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze results for Today API functionality
        auth_tests_passed = sum(1 for result in self.test_results if result['success'] and 'AUTHENTICATION' in result['test'])
        today_api_tests_passed = sum(1 for result in self.test_results if result['success'] and 'TODAY API' in result['test'])
        
        print(f"\n🔍 SYSTEM ANALYSIS:")
        print(f"Authentication Tests Passed: {auth_tests_passed}")
        print(f"Today API Tests Passed: {today_api_tests_passed}")
        
        if success_rate >= 85:
            print("\n✅ TODAY API TOP_N ENFORCEMENT: SUCCESS")
            print("   ✅ GET /api/today?top_n=3 returns exactly 3 tasks")
            print("   ✅ GET /api/today?top_n=1 returns exactly 1 task")
            print("   ✅ GET /api/today (default) returns exactly 3 tasks")
            print("   ✅ All tasks properly sorted by score descending")
            print("   The Today API top_n enforcement is working correctly!")
        else:
            print("\n❌ TODAY API TOP_N ENFORCEMENT: ISSUES DETECTED")
            print("   Issues found in Today API top_n parameter enforcement")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 85

def main():
    """Run Today API Top_N Enforcement Tests"""
    print("📅 STARTING TODAY API TOP_N ENFORCEMENT BACKEND TESTING")
    print("=" * 80)
    
    tester = TodayAPITopNTester()
    
    try:
        # Run the comprehensive Today API top_n tests
        success = tester.run_today_api_top_n_tests()
        
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
        
        return success_rate >= 85
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)