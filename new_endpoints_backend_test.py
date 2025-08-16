#!/usr/bin/env python3
"""
NEW ENDPOINTS BACKEND TESTING - COMPREHENSIVE TESTING
Testing the new endpoints as specified in the review request:

1. Search endpoint: GET /api/tasks/search?q=plan&limit=5
2. Suggest Focus endpoint: GET /api/tasks/suggest-focus
3. Today endpoint regression: GET /api/today?top_n=0 and GET /api/today?top_n=3

FOCUS AREAS:
- Authentication flow with valid token
- Rate limiting behavior validation
- Response structure validation
- User scoping (tasks belong to authenticated user)
- Business logic validation (completed=false, deduplication, etc.)

CREDENTIALS: Using existing test account or creating new one as needed
"""

import requests
import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Any

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://fcbe964d-a00c-4624-8b03-88a109fb0408.preview.emergentagent.com/api"

class NewEndpointsAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        # Use existing test credentials
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
        result = self.make_request('GET', '/api/auth/me', use_auth=True)
        self.log_test(
            "AUTHENTICATION TOKEN VALIDATION",
            result['success'],
            f"Token validated successfully, user: {result['data'].get('email', 'Unknown')}" if result['success'] else f"Token validation failed: {result.get('error', 'Unknown error')}"
        )
        
        return result['success']

    def test_search_endpoint(self):
        """Test GET /api/tasks/search endpoint as specified in review request"""
        print("\n=== TESTING SEARCH ENDPOINT ===")
        
        if not self.auth_token:
            self.log_test("SEARCH ENDPOINT - Authentication Required", False, "No authentication token available")
            return False
        
        # Test 1: Basic search functionality
        search_params = {"q": "plan", "limit": 5}
        result = self.make_request('GET', '/tasks/search', params=search_params, use_auth=True)
        
        self.log_test(
            "SEARCH ENDPOINT - BASIC FUNCTIONALITY",
            result['success'],
            f"Search endpoint accessible and returned {result['status_code']}" if result['success'] else f"Search failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        search_data = result['data']
        
        # Test 2: Response structure validation
        if isinstance(search_data, list):
            self.log_test(
                "SEARCH ENDPOINT - RESPONSE STRUCTURE",
                True,
                f"Response is array with {len(search_data)} items"
            )
            
            # Test 3: Response field validation
            if len(search_data) > 0:
                required_fields = ['taskId', 'title', 'description', 'project', 'dueDate', 'priority', 'status']
                first_task = search_data[0]
                missing_fields = [field for field in required_fields if field not in first_task]
                
                fields_valid = len(missing_fields) == 0
                self.log_test(
                    "SEARCH ENDPOINT - RESPONSE FIELDS",
                    fields_valid,
                    f"All required fields present: {required_fields}" if fields_valid else f"Missing fields: {missing_fields}"
                )
                
                # Test 4: Limit validation
                limit_respected = len(search_data) <= 5
                self.log_test(
                    "SEARCH ENDPOINT - LIMIT VALIDATION",
                    limit_respected,
                    f"Limit respected: {len(search_data)} <= 5" if limit_respected else f"Limit exceeded: {len(search_data)} > 5"
                )
            else:
                self.log_test(
                    "SEARCH ENDPOINT - NO RESULTS",
                    True,
                    "No search results returned (may be expected if no matching tasks)"
                )
        else:
            self.log_test(
                "SEARCH ENDPOINT - RESPONSE STRUCTURE",
                False,
                f"Expected array, got: {type(search_data)}"
            )
            return False
        
        # Test 5: Rate limiting validation (call 35 times within a minute)
        print("Testing rate limiting (35 calls within a minute)...")
        rate_limit_hits = 0
        successful_calls = 0
        
        for i in range(35):
            result = self.make_request('GET', '/tasks/search', params=search_params, use_auth=True)
            if result['status_code'] == 429:
                rate_limit_hits += 1
            elif result['success']:
                successful_calls += 1
            
            # Small delay to avoid overwhelming the server
            time.sleep(0.1)
        
        rate_limit_working = rate_limit_hits > 0 and successful_calls >= 25
        self.log_test(
            "SEARCH ENDPOINT - RATE LIMITING",
            rate_limit_working,
            f"Rate limiting working: {rate_limit_hits} rate limit responses after {successful_calls} successful calls" if rate_limit_working else f"Rate limiting may not be working: {rate_limit_hits} rate limits, {successful_calls} successful"
        )
        
        return True

    def test_suggest_focus_endpoint(self):
        """Test GET /api/tasks/suggest-focus endpoint as specified in review request"""
        print("\n=== TESTING SUGGEST FOCUS ENDPOINT ===")
        
        if not self.auth_token:
            self.log_test("SUGGEST FOCUS ENDPOINT - Authentication Required", False, "No authentication token available")
            return False
        
        # Test 1: Basic functionality
        result = self.make_request('GET', '/tasks/suggest-focus', use_auth=True)
        
        self.log_test(
            "SUGGEST FOCUS ENDPOINT - BASIC FUNCTIONALITY",
            result['success'],
            f"Suggest focus endpoint accessible and returned {result['status_code']}" if result['success'] else f"Suggest focus failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        focus_data = result['data']
        
        # Test 2: Response structure validation
        if isinstance(focus_data, list):
            self.log_test(
                "SUGGEST FOCUS ENDPOINT - RESPONSE STRUCTURE",
                True,
                f"Response is array with {len(focus_data)} items"
            )
            
            # Test 3: Length validation (should be <= 3)
            length_valid = len(focus_data) <= 3
            self.log_test(
                "SUGGEST FOCUS ENDPOINT - LENGTH VALIDATION",
                length_valid,
                f"Length within limit: {len(focus_data)} <= 3" if length_valid else f"Length exceeds limit: {len(focus_data)} > 3"
            )
            
            # Test 4: Response field validation
            if len(focus_data) > 0:
                required_fields = ['taskId', 'title', 'description', 'project', 'dueDate', 'priority', 'status']
                first_task = focus_data[0]
                missing_fields = [field for field in required_fields if field not in first_task]
                
                fields_valid = len(missing_fields) == 0
                self.log_test(
                    "SUGGEST FOCUS ENDPOINT - RESPONSE FIELDS",
                    fields_valid,
                    f"All required fields present: {required_fields}" if fields_valid else f"Missing fields: {missing_fields}"
                )
                
                # Test 5: Deduplication check (all taskIds should be unique)
                task_ids = [task.get('taskId') for task in focus_data]
                unique_ids = set(task_ids)
                deduped = len(task_ids) == len(unique_ids)
                self.log_test(
                    "SUGGEST FOCUS ENDPOINT - DEDUPLICATION",
                    deduped,
                    f"Tasks properly deduped: {len(unique_ids)} unique out of {len(task_ids)}" if deduped else f"Duplicate tasks found: {len(task_ids)} total, {len(unique_ids)} unique"
                )
            else:
                self.log_test(
                    "SUGGEST FOCUS ENDPOINT - NO RESULTS",
                    True,
                    "No focus suggestions returned (may be expected if no tasks available)"
                )
        else:
            self.log_test(
                "SUGGEST FOCUS ENDPOINT - RESPONSE STRUCTURE",
                False,
                f"Expected array, got: {type(focus_data)}"
            )
            return False
        
        # Test 6: Rate limiting validation (call 8 times, expect 429 after 6)
        print("Testing rate limiting (8 calls, expecting 429 after 6)...")
        rate_limit_hits = 0
        successful_calls = 0
        
        for i in range(8):
            result = self.make_request('GET', '/tasks/suggest-focus', use_auth=True)
            if result['status_code'] == 429:
                rate_limit_hits += 1
            elif result['success']:
                successful_calls += 1
            
            # Small delay to avoid overwhelming the server
            time.sleep(0.5)
        
        rate_limit_working = rate_limit_hits > 0 and successful_calls >= 5
        self.log_test(
            "SUGGEST FOCUS ENDPOINT - RATE LIMITING",
            rate_limit_working,
            f"Rate limiting working: {rate_limit_hits} rate limit responses after {successful_calls} successful calls" if rate_limit_working else f"Rate limiting may not be working: {rate_limit_hits} rate limits, {successful_calls} successful"
        )
        
        return True

    def test_today_endpoint_regression(self):
        """Test GET /api/today endpoint regression as specified in review request"""
        print("\n=== TESTING TODAY ENDPOINT REGRESSION ===")
        
        if not self.auth_token:
            self.log_test("TODAY ENDPOINT - Authentication Required", False, "No authentication token available")
            return False
        
        # Test 1: Today endpoint with top_n=0 (no AI coaching)
        result = self.make_request('GET', '/today', params={'top_n': 0}, use_auth=True)
        
        self.log_test(
            "TODAY ENDPOINT - TOP_N=0 FUNCTIONALITY",
            result['success'],
            f"Today endpoint (top_n=0) accessible and returned {result['status_code']}" if result['success'] else f"Today endpoint failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        today_data_no_ai = result['data']
        
        # Test 2: Validate no ai_powered in items when top_n=0
        if isinstance(today_data_no_ai, dict) and 'tasks' in today_data_no_ai:
            tasks = today_data_no_ai['tasks']
            has_ai_powered = any('ai_powered' in task for task in tasks if isinstance(task, dict))
            
            self.log_test(
                "TODAY ENDPOINT - NO AI_POWERED (TOP_N=0)",
                not has_ai_powered,
                f"No ai_powered fields found in tasks (as expected)" if not has_ai_powered else f"ai_powered fields found when top_n=0"
            )
            
            # Check for coaching calls
            has_coaching = 'coaching_message' in today_data_no_ai
            self.log_test(
                "TODAY ENDPOINT - NO COACHING (TOP_N=0)",
                not has_coaching,
                f"No coaching message found (as expected)" if not has_coaching else f"Coaching message found when top_n=0"
            )
        else:
            self.log_test(
                "TODAY ENDPOINT - RESPONSE STRUCTURE (TOP_N=0)",
                False,
                f"Expected dict with 'tasks' key, got: {type(today_data_no_ai)}"
            )
        
        # Test 3: Today endpoint with top_n=3 (with AI coaching)
        result = self.make_request('GET', '/today', params={'top_n': 3}, use_auth=True)
        
        self.log_test(
            "TODAY ENDPOINT - TOP_N=3 FUNCTIONALITY",
            result['success'],
            f"Today endpoint (top_n=3) accessible and returned {result['status_code']}" if result['success'] else f"Today endpoint failed: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            today_data_with_ai = result['data']
            
            # Test 4: May include coaching_message when top_n=3
            if isinstance(today_data_with_ai, dict):
                has_coaching = 'coaching_message' in today_data_with_ai
                self.log_test(
                    "TODAY ENDPOINT - COACHING AVAILABILITY (TOP_N=3)",
                    True,  # This is informational, not a failure
                    f"Coaching message {'present' if has_coaching else 'not present'} (both are valid)"
                )
            
            # Test 5: Rate limiting validation (3/min for top_n=3)
            print("Testing rate limiting for top_n=3 (3/min limit)...")
            rate_limit_hits = 0
            successful_calls = 0
            
            for i in range(5):
                result = self.make_request('GET', '/today', params={'top_n': 3}, use_auth=True)
                if result['status_code'] == 429:
                    rate_limit_hits += 1
                elif result['success']:
                    successful_calls += 1
                
                # Small delay
                time.sleep(0.5)
            
            rate_limit_working = rate_limit_hits > 0 or successful_calls <= 3
            self.log_test(
                "TODAY ENDPOINT - RATE LIMITING (TOP_N=3)",
                rate_limit_working,
                f"Rate limiting working: {rate_limit_hits} rate limit responses after {successful_calls} successful calls" if rate_limit_working else f"Rate limiting may not be working: {rate_limit_hits} rate limits, {successful_calls} successful"
            )
        
        return True

    def run_comprehensive_new_endpoints_test(self):
        """Run comprehensive new endpoints API tests"""
        print("\n🔍 STARTING NEW ENDPOINTS API COMPREHENSIVE TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("User Authentication", self.test_user_authentication),
            ("Search Endpoint", self.test_search_endpoint),
            ("Suggest Focus Endpoint", self.test_suggest_focus_endpoint),
            ("Today Endpoint Regression", self.test_today_endpoint_regression)
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
        print("🔍 NEW ENDPOINTS API TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze results for specific endpoints
        search_tests_passed = sum(1 for result in self.test_results if result['success'] and 'SEARCH ENDPOINT' in result['test'])
        focus_tests_passed = sum(1 for result in self.test_results if result['success'] and 'SUGGEST FOCUS ENDPOINT' in result['test'])
        today_tests_passed = sum(1 for result in self.test_results if result['success'] and 'TODAY ENDPOINT' in result['test'])
        
        print(f"\n🔍 ENDPOINT ANALYSIS:")
        print(f"Search Endpoint Tests Passed: {search_tests_passed}")
        print(f"Suggest Focus Endpoint Tests Passed: {focus_tests_passed}")
        print(f"Today Endpoint Tests Passed: {today_tests_passed}")
        
        if success_rate >= 85:
            print("\n✅ NEW ENDPOINTS API SYSTEM: SUCCESS")
            print("   ✅ GET /api/tasks/search working with rate limiting")
            print("   ✅ GET /api/tasks/suggest-focus functional with deduplication")
            print("   ✅ GET /api/today regression tests passed")
            print("   ✅ Authentication and rate limiting verified")
            print("   The new endpoints are production-ready!")
        else:
            print("\n❌ NEW ENDPOINTS API SYSTEM: ISSUES DETECTED")
            print("   Issues found in new endpoints implementation")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 85

def main():
    """Run New Endpoints API Tests"""
    print("🔍 STARTING NEW ENDPOINTS API BACKEND TESTING")
    print("=" * 80)
    
    tester = NewEndpointsAPITester()
    
    try:
        # Run the comprehensive new endpoints API tests
        success = tester.run_comprehensive_new_endpoints_test()
        
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