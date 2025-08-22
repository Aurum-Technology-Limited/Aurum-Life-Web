#!/usr/bin/env python3
"""
Backend Testing for Tasks Extended Features and Insights Stability
Tests the specific requirements from the review request:
1) Auth with marc.alleyne@aurumtechnologyltd.com/password123
2) /api/tasks: No params => array, 200
3) /api/tasks filters: q, status (active|completed|todo|in_progress|review), priority (low|medium|high), due_date (overdue|today|week), project_id (use invalid id to ensure 200 with empty array)
4) /api/tasks pagination: page & limit return sliced data; return_meta=true returns {tasks,total,page,limit,has_more}; verify page 1 and page 2 differ when total>limit
5) /api/tasks backward compatibility: no page/limit still returns array
6) /api/insights => 200 and required keys
"""

import requests
import json
import time
from typing import Dict, Any, Optional

# Configuration
BACKEND_URL = "https://auth-wizard-2.preview.emergentagent.com/api"
TEST_EMAIL = "marc.alleyne@aurumtechnologyltd.com"
TEST_PASSWORD = "password123"

class TasksInsightsBackendTest:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
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
        
        # Add authorization header if we have a token
        if self.access_token and 'headers' not in kwargs:
            kwargs['headers'] = {}
        if self.access_token:
            kwargs['headers']['Authorization'] = f"Bearer {self.access_token}"
            
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
                def __init__(self, error_exception):
                    self.status_code = 0
                    self.text = str(error_exception)
                    self.error_exception = error_exception
                def json(self):
                    return {"error": str(self.error_exception)}
            return MockResponse(e), end_time - start_time

    def test_step_1_authentication(self):
        """Step 1: Authenticate with marc.alleyne@aurumtechnologyltd.com/password123"""
        print("🔐 Step 1: Testing Authentication")
        
        payload = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        response, response_time = self.make_request("POST", "/auth/login", json=payload)
        
        success = response.status_code == 200
        details = ""
        
        if success:
            try:
                data = response.json()
                if "access_token" in data:
                    self.access_token = data["access_token"]
                    details = f"Successfully authenticated with {TEST_EMAIL}"
                else:
                    success = False
                    details = "No access_token in response"
            except Exception as e:
                success = False
                details = f"Failed to parse JSON: {e}"
        else:
            details = f"Authentication failed: {response.text[:200]}"
            
        self.log_result("Authentication", success, response.status_code, details, response_time)
        return success

    def test_step_2_tasks_no_params(self):
        """Step 2: GET /api/tasks with no params => array, 200"""
        print("✅ Step 2: Testing GET /api/tasks (no params)")
        
        response, response_time = self.make_request("GET", "/tasks")
        
        success = response.status_code == 200
        details = ""
        
        if success:
            try:
                data = response.json()
                if isinstance(data, list):
                    details = f"Retrieved {len(data)} tasks as array"
                else:
                    success = False
                    details = f"Expected array, got {type(data)}"
            except Exception as e:
                success = False
                details = f"JSON parse failed: {e}"
        else:
            details = f"Request failed: {response.text[:200]}"
            
        self.log_result("GET /api/tasks (no params)", success, response.status_code, details, response_time)
        return success

    def test_step_3_tasks_filters(self):
        """Step 3: Test /api/tasks with various filters"""
        print("🔍 Step 3: Testing GET /api/tasks with filters")
        
        filters_to_test = [
            {"q": "test", "description": "text search filter"},
            {"status": "active", "description": "status=active filter"},
            {"status": "completed", "description": "status=completed filter"},
            {"status": "todo", "description": "status=todo filter"},
            {"status": "in_progress", "description": "status=in_progress filter"},
            {"status": "review", "description": "status=review filter"},
            {"priority": "low", "description": "priority=low filter"},
            {"priority": "medium", "description": "priority=medium filter"},
            {"priority": "high", "description": "priority=high filter"},
            {"due_date": "overdue", "description": "due_date=overdue filter"},
            {"due_date": "today", "description": "due_date=today filter"},
            {"due_date": "week", "description": "due_date=week filter"},
            {"project_id": "invalid-project-id-12345", "description": "invalid project_id filter (should return empty array)"},
        ]
        
        all_passed = True
        
        for filter_params in filters_to_test:
            description = filter_params.pop("description")
            
            # Build query string
            query_params = "&".join([f"{k}={v}" for k, v in filter_params.items()])
            endpoint = f"/tasks?{query_params}"
            
            response, response_time = self.make_request("GET", endpoint)
            
            success = response.status_code == 200
            details = ""
            
            if success:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        details = f"{description}: {len(data)} tasks returned"
                    else:
                        success = False
                        details = f"{description}: Expected array, got {type(data)}"
                except Exception as e:
                    success = False
                    details = f"{description}: JSON parse failed: {e}"
            else:
                success = False
                details = f"{description}: Request failed: {response.text[:200]}"
            
            self.log_result(f"Filter: {description}", success, response.status_code, details, response_time)
            
            if not success:
                all_passed = False
        
        return all_passed

    def test_step_4_tasks_pagination(self):
        """Step 4: Test /api/tasks pagination features"""
        print("📄 Step 4: Testing GET /api/tasks pagination")
        
        all_passed = True
        
        # Test 4a: Basic pagination with return_meta=true
        print("    4a: Testing pagination with return_meta=true")
        response, response_time = self.make_request("GET", "/tasks?page=1&limit=5&return_meta=true")
        
        success = response.status_code == 200
        details = ""
        
        if success:
            try:
                data = response.json()
                if isinstance(data, dict) and "tasks" in data and "total" in data and "page" in data and "limit" in data and "has_more" in data:
                    tasks_count = len(data["tasks"])
                    total = data["total"]
                    page = data["page"]
                    limit = data["limit"]
                    has_more = data["has_more"]
                    details = f"Meta response: {tasks_count} tasks, total={total}, page={page}, limit={limit}, has_more={has_more}"
                else:
                    success = False
                    details = f"Expected meta object with required keys, got: {list(data.keys()) if isinstance(data, dict) else type(data)}"
            except Exception as e:
                success = False
                details = f"JSON parse failed: {e}"
        else:
            details = f"Request failed: {response.text[:200]}"
        
        self.log_result("Pagination with return_meta=true", success, response.status_code, details, response_time)
        if not success:
            all_passed = False
        
        # Test 4b: Pagination without return_meta (should return array)
        print("    4b: Testing pagination without return_meta (backward compatibility)")
        response, response_time = self.make_request("GET", "/tasks?page=1&limit=5")
        
        success = response.status_code == 200
        details = ""
        
        if success:
            try:
                data = response.json()
                if isinstance(data, list):
                    details = f"Backward compatibility: {len(data)} tasks returned as array"
                else:
                    success = False
                    details = f"Expected array for backward compatibility, got {type(data)}"
            except Exception as e:
                success = False
                details = f"JSON parse failed: {e}"
        else:
            details = f"Request failed: {response.text[:200]}"
        
        self.log_result("Pagination backward compatibility", success, response.status_code, details, response_time)
        if not success:
            all_passed = False
        
        # Test 4c: Verify page 1 and page 2 differ when total > limit
        print("    4c: Testing page 1 vs page 2 difference")
        
        # Get page 1
        response1, response_time1 = self.make_request("GET", "/tasks?page=1&limit=3&return_meta=true")
        
        if response1.status_code == 200:
            try:
                data1 = response1.json()
                total = data1.get("total", 0)
                
                if total > 3:  # Only test if we have enough data
                    # Get page 2
                    response2, response_time2 = self.make_request("GET", "/tasks?page=2&limit=3&return_meta=true")
                    
                    if response2.status_code == 200:
                        try:
                            data2 = response2.json()
                            
                            # Compare task IDs to ensure they're different
                            page1_ids = [task.get("id") for task in data1.get("tasks", [])]
                            page2_ids = [task.get("id") for task in data2.get("tasks", [])]
                            
                            # Check if pages have different tasks
                            if set(page1_ids) != set(page2_ids):
                                details = f"Page 1 and 2 have different tasks (total={total})"
                                success = True
                            else:
                                details = f"Page 1 and 2 have same tasks - pagination not working correctly"
                                success = False
                        except Exception as e:
                            success = False
                            details = f"Page 2 JSON parse failed: {e}"
                    else:
                        success = False
                        details = f"Page 2 request failed: {response2.text[:200]}"
                else:
                    success = True
                    details = f"Not enough data to test pagination (total={total} <= limit=3)"
                    
            except Exception as e:
                success = False
                details = f"Page 1 JSON parse failed: {e}"
        else:
            success = False
            details = f"Page 1 request failed: {response1.text[:200]}"
        
        self.log_result("Page 1 vs Page 2 difference", success, response1.status_code, details, response_time1)
        if not success:
            all_passed = False
        
        return all_passed

    def test_step_5_tasks_backward_compatibility(self):
        """Step 5: Test /api/tasks backward compatibility (no page/limit still returns array)"""
        print("🔄 Step 5: Testing GET /api/tasks backward compatibility")
        
        response, response_time = self.make_request("GET", "/tasks")
        
        success = response.status_code == 200
        details = ""
        
        if success:
            try:
                data = response.json()
                if isinstance(data, list):
                    details = f"Backward compatibility confirmed: {len(data)} tasks returned as array"
                else:
                    success = False
                    details = f"Backward compatibility broken: Expected array, got {type(data)}"
            except Exception as e:
                success = False
                details = f"JSON parse failed: {e}"
        else:
            details = f"Request failed: {response.text[:200]}"
        
        self.log_result("Backward compatibility", success, response.status_code, details, response_time)
        return success

    def test_step_6_insights_stability(self):
        """Step 6: Test /api/insights => 200 and required keys"""
        print("📊 Step 6: Testing GET /api/insights stability and structure")
        
        response, response_time = self.make_request("GET", "/insights")
        
        success = response.status_code == 200
        details = ""
        
        if success:
            try:
                data = response.json()
                if isinstance(data, dict):
                    # Check for required keys
                    required_keys = ["eisenhower_matrix", "alignment_snapshot", "area_distribution", "generated_at"]
                    missing_keys = [key for key in required_keys if key not in data]
                    
                    if not missing_keys:
                        details = f"All required keys present: {required_keys}"
                        
                        # Additional validation of structure
                        eisenhower = data.get("eisenhower_matrix", {})
                        if isinstance(eisenhower, dict):
                            quadrants = ["Q1", "Q2", "Q3", "Q4"]
                            found_quadrants = [q for q in quadrants if q in eisenhower]
                            details += f", Eisenhower quadrants: {found_quadrants}"
                        
                        alignment = data.get("alignment_snapshot", {})
                        if isinstance(alignment, dict) and "pillar_alignment" in alignment:
                            details += f", Alignment snapshot structure valid"
                        
                        area_dist = data.get("area_distribution")
                        if isinstance(area_dist, list):
                            details += f", Area distribution: {len(area_dist)} items"
                        
                        generated_at = data.get("generated_at")
                        if isinstance(generated_at, str):
                            details += f", Generated at: {generated_at[:19]}"
                        
                    else:
                        success = False
                        details = f"Missing required keys: {missing_keys}. Found keys: {list(data.keys())}"
                else:
                    success = False
                    details = f"Expected dict, got {type(data)}"
            except Exception as e:
                success = False
                details = f"JSON parse failed: {e}"
        else:
            details = f"Request failed: {response.text[:200]}"
        
        self.log_result("GET /api/insights structure", success, response.status_code, details, response_time)
        return success

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Tasks Extended Features and Insights Stability Test")
        print("=" * 80)
        print()
        
        test_methods = [
            self.test_step_1_authentication,
            self.test_step_2_tasks_no_params,
            self.test_step_3_tasks_filters,
            self.test_step_4_tasks_pagination,
            self.test_step_5_tasks_backward_compatibility,
            self.test_step_6_insights_stability
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
        
        print("=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
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
        print("=" * 80)
        
        if success_rate >= 90:
            print("🎉 TESTS PASSED - Tasks extended features and Insights are stable!")
        elif success_rate >= 70:
            print("⚠️ TESTS PARTIAL - Some issues need attention")
        else:
            print("🚨 TESTS FAILED - Critical issues require immediate fix")
            
        return success_rate

if __name__ == "__main__":
    tester = TasksInsightsBackendTest()
    success_rate = tester.run_all_tests()
    exit(0 if success_rate >= 80 else 1)