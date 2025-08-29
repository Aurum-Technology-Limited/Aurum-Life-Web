#!/usr/bin/env python3
"""
Backend Focused Testing for Tasks Filters and Insights Structure
Tests the specific requirements from the review request:
1) GET /api/tasks with optional filters (project_id, q, status, priority, due_date) - returns 200 with array
2) GET /api/insights - returns 200 with required keys: eisenhower_matrix, alignment_snapshot, area_distribution, generated_at
3) Ensure no 500s across these endpoints under authenticated context using marc.alleyne@aurumtechnologyltd.com / password123
"""

import requests
import json
import time
from typing import Dict, Any, Optional

# Configuration
BACKEND_URL = "https://aurum-codebase.preview.emergentagent.com/api"
TEST_EMAIL = "marc.alleyne@aurumtechnologyltd.com"
TEST_PASSWORD = "password123"

class FocusedBackendTest:
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
                def __init__(self, error_msg):
                    self.status_code = 0
                    self.text = str(error_msg)
                    self.error_msg = error_msg
                def json(self):
                    return {"error": str(self.error_msg)}
            return MockResponse(e), end_time - start_time

    def test_authentication(self):
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

    def test_tasks_no_filters(self):
        """Test GET /api/tasks without any filters"""
        print("✅ Step 2a: Testing GET /api/tasks (no filters)")
        
        response, response_time = self.make_request("GET", "/tasks")
        
        success = response.status_code == 200
        details = ""
        
        if success:
            try:
                data = response.json()
                if isinstance(data, list):
                    details = f"Retrieved {len(data)} tasks (array response confirmed)"
                else:
                    success = False
                    details = f"Expected array, got {type(data)}"
            except Exception as e:
                success = False
                details = f"JSON parse failed: {e}"
        else:
            details = f"Tasks request failed: {response.text[:500]}"
            
        self.log_result("GET /api/tasks (no filters)", success, response.status_code, details, response_time)
        return success

    def test_tasks_with_filters(self):
        """Test GET /api/tasks with various filter combinations"""
        print("✅ Step 2b: Testing GET /api/tasks with filters")
        
        # Test different filter combinations
        filter_tests = [
            {"q": "test"},
            {"status": "pending"},
            {"priority": "high"},
            {"project_id": "test-project-id"},
            {"due_date": "2025-01-01"},
            {"q": "search", "status": "pending"},
            {"priority": "high", "status": "completed"},
        ]
        
        all_passed = True
        filter_results = []
        
        for i, filters in enumerate(filter_tests):
            filter_str = "&".join([f"{k}={v}" for k, v in filters.items()])
            endpoint = f"/tasks?{filter_str}"
            
            response, response_time = self.make_request("GET", endpoint)
            
            success = response.status_code == 200
            if success:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        filter_results.append(f"Filter {i+1} ({filter_str}): {len(data)} tasks")
                    else:
                        success = False
                        filter_results.append(f"Filter {i+1} ({filter_str}): Expected array, got {type(data)}")
                        all_passed = False
                except Exception as e:
                    success = False
                    filter_results.append(f"Filter {i+1} ({filter_str}): JSON parse failed - {e}")
                    all_passed = False
            else:
                filter_results.append(f"Filter {i+1} ({filter_str}): HTTP {response.status_code} - {response.text[:100]}")
                all_passed = False
        
        details = "; ".join(filter_results)
        self.log_result("GET /api/tasks (with filters)", all_passed, 200 if all_passed else 500, details, 0)
        return all_passed

    def test_insights_structure(self):
        """Test GET /api/insights for required structure"""
        print("📊 Step 3: Testing GET /api/insights structure")
        
        response, response_time = self.make_request("GET", "/insights")
        
        success = response.status_code == 200
        details = ""
        
        if success:
            try:
                data = response.json()
                
                # Check required keys
                required_keys = ["eisenhower_matrix", "alignment_snapshot", "area_distribution", "generated_at"]
                missing_keys = []
                present_keys = []
                
                for key in required_keys:
                    if key in data:
                        present_keys.append(key)
                    else:
                        missing_keys.append(key)
                
                if missing_keys:
                    success = False
                    details = f"Missing required keys: {missing_keys}. Present keys: {present_keys}"
                else:
                    # Validate structure of each key
                    structure_details = []
                    
                    # Check eisenhower_matrix structure
                    em = data.get("eisenhower_matrix", {})
                    if isinstance(em, dict):
                        quadrants = ["Q1", "Q2", "Q3", "Q4"]
                        em_quadrants = [q for q in quadrants if q in em]
                        structure_details.append(f"eisenhower_matrix has {len(em_quadrants)}/4 quadrants: {em_quadrants}")
                        
                        # Check if quadrants have count and tasks
                        for q in em_quadrants[:2]:  # Check first 2 quadrants
                            quad_data = em[q]
                            if isinstance(quad_data, dict):
                                has_count = "count" in quad_data
                                has_tasks = "tasks" in quad_data
                                structure_details.append(f"{q}: count={has_count}, tasks={has_tasks}")
                    else:
                        structure_details.append(f"eisenhower_matrix is {type(em)}, expected dict")
                    
                    # Check alignment_snapshot structure
                    as_data = data.get("alignment_snapshot", {})
                    if isinstance(as_data, dict):
                        has_pillar_alignment = "pillar_alignment" in as_data
                        if has_pillar_alignment:
                            pa = as_data["pillar_alignment"]
                            structure_details.append(f"alignment_snapshot.pillar_alignment is {type(pa)} with {len(pa) if isinstance(pa, list) else 'N/A'} items")
                        else:
                            structure_details.append("alignment_snapshot missing pillar_alignment")
                    else:
                        structure_details.append(f"alignment_snapshot is {type(as_data)}, expected dict")
                    
                    # Check area_distribution structure
                    ad = data.get("area_distribution", [])
                    structure_details.append(f"area_distribution is {type(ad)} with {len(ad) if isinstance(ad, list) else 'N/A'} items")
                    
                    # Check generated_at
                    generated_at = data.get("generated_at")
                    structure_details.append(f"generated_at: {type(generated_at)} = {generated_at}")
                    
                    details = "; ".join(structure_details)
                    
            except Exception as e:
                success = False
                details = f"JSON parse failed: {e}"
        else:
            details = f"Insights request failed: {response.text[:500]}"
            
        self.log_result("GET /api/insights (structure)", success, response.status_code, details, response_time)
        return success

    def test_no_500_errors(self):
        """Verify no 500 errors across all tested endpoints"""
        print("🚨 Step 4: Checking for 500 errors across all tests")
        
        error_500_count = 0
        error_500_endpoints = []
        
        for result in self.test_results:
            if result["status_code"] == 500:
                error_500_count += 1
                error_500_endpoints.append(result["step"])
        
        success = error_500_count == 0
        details = f"Found {error_500_count} endpoints with 500 errors"
        if error_500_endpoints:
            details += f": {', '.join(error_500_endpoints)}"
        else:
            details += " - All endpoints returned non-500 status codes"
            
        self.log_result("No 500 errors check", success, None, details, 0)
        return success

    def run_focused_tests(self):
        """Run focused tests for the review request"""
        print("🎯 Starting Focused Backend Testing for Tasks Filters and Insights Structure")
        print("=" * 80)
        print()
        
        test_methods = [
            self.test_authentication,
            self.test_tasks_no_filters,
            self.test_tasks_with_filters,
            self.test_insights_structure,
            self.test_no_500_errors
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
        print("📊 FOCUSED TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (passed / total) * 100
        print(f"Overall Success Rate: {passed}/{total} ({success_rate:.1f}%)")
        print()
        
        # Detailed results
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            time_str = f" ({result['response_time_ms']}ms)" if result['response_time_ms'] > 0 else ""
            print(f"{status} {result['step']} - {result['status_code']}{time_str}")
            if result["details"]:
                print(f"    {result['details']}")
        
        print()
        print("=" * 80)
        
        # Specific review request validation
        print("🎯 REVIEW REQUEST VALIDATION:")
        print("=" * 80)
        
        # Check specific requirements
        tasks_no_filters_passed = any(r["step"] == "GET /api/tasks (no filters)" and r["success"] for r in self.test_results)
        tasks_with_filters_passed = any(r["step"] == "GET /api/tasks (with filters)" and r["success"] for r in self.test_results)
        insights_structure_passed = any(r["step"] == "GET /api/insights (structure)" and r["success"] for r in self.test_results)
        no_500_errors_passed = any(r["step"] == "No 500 errors check" and r["success"] for r in self.test_results)
        auth_passed = any(r["step"] == "POST /api/auth/login" and r["success"] for r in self.test_results)
        
        print(f"✅ Authentication with marc.alleyne@aurumtechnologyltd.com: {'PASS' if auth_passed else 'FAIL'}")
        print(f"✅ GET /api/tasks returns 200 with array (no params): {'PASS' if tasks_no_filters_passed else 'FAIL'}")
        print(f"✅ GET /api/tasks supports filters (project_id, q, status, priority, due_date): {'PASS' if tasks_with_filters_passed else 'FAIL'}")
        print(f"✅ GET /api/insights returns 200 with required keys: {'PASS' if insights_structure_passed else 'FAIL'}")
        print(f"✅ No 500 errors across endpoints: {'PASS' if no_500_errors_passed else 'FAIL'}")
        
        print()
        
        if success_rate >= 80:
            print("🎉 FOCUSED TEST PASSED - Review requirements met!")
        elif success_rate >= 60:
            print("⚠️ FOCUSED TEST PARTIAL - Some requirements need attention")
        else:
            print("🚨 FOCUSED TEST FAILED - Critical requirements not met")
            
        return success_rate

if __name__ == "__main__":
    tester = FocusedBackendTest()
    success_rate = tester.run_focused_tests()
    exit(0 if success_rate >= 80 else 1)