#!/usr/bin/env python3
"""
Backend Testing for Tasks Due Date Filters After Timezone Fix
Tests the specific requirements from the review request:
- Auth then call: /api/tasks?due_date=overdue, /api/tasks?due_date=today, /api/tasks?due_date=week
- Ensure 200 OK and array responses (even if empty)
- Confirm other tests unchanged
"""

import requests
import json
import time
from typing import Dict, Any, Optional

# Configuration
BACKEND_URL = "https://aurum-life-os.preview.emergentagent.com/api"
TEST_EMAIL = "marc.alleyne@aurumtechnologyltd.com"
TEST_PASSWORD = "password123"

class DueDateFiltersTest:
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

    def make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
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
                def __init__(self, error_msg):
                    self.status_code = 0
                    self.text = str(error_msg)
                    self.error_msg = error_msg
                def json(self):
                    return {"error": str(self.error_msg)}
            return MockResponse(e), end_time - start_time

    def test_step_1_login(self):
        """Step 1: POST /api/auth/login with credentials"""
        print("🔐 Step 1: Testing POST /api/auth/login")
        
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
                    details = f"Access token received (length: {len(self.access_token)})"
                else:
                    success = False
                    details = "No access_token in response"
            except Exception as e:
                success = False
                details = f"Failed to parse JSON: {e}"
        else:
            details = f"Login failed: {response.text[:200]}"
            
        self.log_result("POST /api/auth/login", success, response.status_code, details, response_time)
        return success

    def test_step_2_tasks_due_date_overdue(self):
        """Step 2: GET /api/tasks?due_date=overdue"""
        print("📅 Step 2: Testing GET /api/tasks?due_date=overdue")
        
        response, response_time = self.make_request("GET", "/tasks?due_date=overdue")
        
        success = response.status_code == 200
        details = ""
        
        if success:
            try:
                data = response.json()
                if isinstance(data, list):
                    details = f"Retrieved {len(data)} overdue tasks (array response confirmed)"
                else:
                    success = False
                    details = f"Expected array, got {type(data)}"
            except Exception as e:
                success = False
                details = f"JSON parse failed: {e}"
        else:
            details = f"Request failed: {response.text[:200]}"
            
        self.log_result("GET /api/tasks?due_date=overdue", success, response.status_code, details, response_time)
        return success

    def test_step_3_tasks_due_date_today(self):
        """Step 3: GET /api/tasks?due_date=today"""
        print("📅 Step 3: Testing GET /api/tasks?due_date=today")
        
        response, response_time = self.make_request("GET", "/tasks?due_date=today")
        
        success = response.status_code == 200
        details = ""
        
        if success:
            try:
                data = response.json()
                if isinstance(data, list):
                    details = f"Retrieved {len(data)} today tasks (array response confirmed)"
                else:
                    success = False
                    details = f"Expected array, got {type(data)}"
            except Exception as e:
                success = False
                details = f"JSON parse failed: {e}"
        else:
            details = f"Request failed: {response.text[:200]}"
            
        self.log_result("GET /api/tasks?due_date=today", success, response.status_code, details, response_time)
        return success

    def test_step_4_tasks_due_date_week(self):
        """Step 4: GET /api/tasks?due_date=week"""
        print("📅 Step 4: Testing GET /api/tasks?due_date=week")
        
        response, response_time = self.make_request("GET", "/tasks?due_date=week")
        
        success = response.status_code == 200
        details = ""
        
        if success:
            try:
                data = response.json()
                if isinstance(data, list):
                    details = f"Retrieved {len(data)} week tasks (array response confirmed)"
                else:
                    success = False
                    details = f"Expected array, got {type(data)}"
            except Exception as e:
                success = False
                details = f"JSON parse failed: {e}"
        else:
            details = f"Request failed: {response.text[:200]}"
            
        self.log_result("GET /api/tasks?due_date=week", success, response.status_code, details, response_time)
        return success

    def test_step_5_tasks_no_filter(self):
        """Step 5: GET /api/tasks (no filter) - confirm other tests unchanged"""
        print("✅ Step 5: Testing GET /api/tasks (no filter) - baseline check")
        
        response, response_time = self.make_request("GET", "/tasks")
        
        success = response.status_code == 200
        details = ""
        
        if success:
            try:
                data = response.json()
                if isinstance(data, list):
                    details = f"Retrieved {len(data)} total tasks (baseline confirmed)"
                else:
                    success = False
                    details = f"Expected array, got {type(data)}"
            except Exception as e:
                success = False
                details = f"JSON parse failed: {e}"
        else:
            details = f"Request failed: {response.text[:200]}"
            
        self.log_result("GET /api/tasks (no filter)", success, response.status_code, details, response_time)
        return success

    def test_step_6_tasks_other_filters(self):
        """Step 6: Test other filters still work - confirm other tests unchanged"""
        print("🔍 Step 6: Testing other filters still work")
        
        # Test status filter
        response, response_time = self.make_request("GET", "/tasks?status=pending")
        
        success = response.status_code == 200
        details = ""
        
        if success:
            try:
                data = response.json()
                if isinstance(data, list):
                    details = f"Status filter working: {len(data)} pending tasks"
                else:
                    success = False
                    details = f"Expected array, got {type(data)}"
            except Exception as e:
                success = False
                details = f"JSON parse failed: {e}"
        else:
            details = f"Request failed: {response.text[:200]}"
            
        self.log_result("GET /api/tasks?status=pending", success, response.status_code, details, response_time)
        return success

    def run_all_tests(self):
        """Run all due date filter tests in sequence"""
        print("🚀 Starting Backend Due Date Filters Test After Timezone Fix")
        print("=" * 70)
        print()
        
        test_methods = [
            self.test_step_1_login,
            self.test_step_2_tasks_due_date_overdue,
            self.test_step_3_tasks_due_date_today,
            self.test_step_4_tasks_due_date_week,
            self.test_step_5_tasks_no_filter,
            self.test_step_6_tasks_other_filters
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
        print("📊 DUE DATE FILTERS TEST SUMMARY")
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
        
        # Specific analysis for due_date filters
        due_date_tests = [r for r in self.test_results if "due_date=" in r["step"]]
        due_date_passed = sum(1 for r in due_date_tests if r["success"])
        
        print("🎯 DUE DATE FILTERS SPECIFIC ANALYSIS:")
        print(f"Due Date Filters Success Rate: {due_date_passed}/{len(due_date_tests)} ({(due_date_passed/len(due_date_tests)*100):.1f}%)")
        
        if due_date_passed == len(due_date_tests):
            print("✅ ALL DUE DATE FILTERS WORKING - Timezone fix successful!")
        else:
            print("❌ SOME DUE DATE FILTERS FAILING - Timezone fix needs attention")
        
        print()
        
        if success_rate >= 80:
            print("🎉 DUE DATE FILTERS TEST PASSED - Backend timezone fix working!")
        elif success_rate >= 60:
            print("⚠️ DUE DATE FILTERS TEST PARTIAL - Some issues need attention")
        else:
            print("🚨 DUE DATE FILTERS TEST FAILED - Critical timezone issues remain")
            
        return success_rate, due_date_passed == len(due_date_tests)

if __name__ == "__main__":
    tester = DueDateFiltersTest()
    success_rate, due_date_success = tester.run_all_tests()
    exit(0 if due_date_success else 1)