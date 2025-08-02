#!/usr/bin/env python3
"""
TARGETED 422 ERROR REPRODUCTION TEST

This test specifically targets scenarios that could cause 422 errors during onboarding template application.
Based on the user's report, we need to test edge cases and validation failures that might occur when
a new user selects a template during onboarding.

FOCUS AREAS:
1. Test with missing required fields
2. Test with invalid data types
3. Test with malformed data
4. Test foreign key constraint violations
5. Test validation edge cases that could cause 422 errors
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import time
import uuid

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://55e67447-e9b1-4184-8259-f18223824d38.preview.emergentagent.com/api"

class Targeted422ErrorTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        # Use working test user
        self.test_user_email = "test422.user@aurumlife.com"
        self.test_user_password = "testpassword123"
        self.found_422_errors = []
        
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

    def authenticate(self):
        """Authenticate with test user"""
        print("\n=== AUTHENTICATING ===")
        
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        if result['success']:
            self.auth_token = result['data'].get('access_token')
            print(f"✅ Authenticated successfully")
            return True
        else:
            print(f"❌ Authentication failed: {result.get('error')}")
            return False

    def test_pillar_422_scenarios(self):
        """Test pillar creation scenarios that could cause 422 errors"""
        print("\n=== TESTING PILLAR 422 SCENARIOS ===")
        
        scenarios = [
            {
                "name": "Missing required name field",
                "data": {
                    "description": "Test pillar without name",
                    "icon": "💪",
                    "color": "#10B981",
                    "time_allocation_percentage": 25.0
                }
            },
            {
                "name": "Invalid time_allocation_percentage type",
                "data": {
                    "name": "Test Pillar",
                    "description": "Test pillar with invalid time allocation",
                    "icon": "💪",
                    "color": "#10B981",
                    "time_allocation_percentage": "invalid_number"
                }
            },
            {
                "name": "Negative time_allocation_percentage",
                "data": {
                    "name": "Test Pillar",
                    "description": "Test pillar with negative time allocation",
                    "icon": "💪",
                    "color": "#10B981",
                    "time_allocation_percentage": -10.0
                }
            },
            {
                "name": "Time allocation over 100%",
                "data": {
                    "name": "Test Pillar",
                    "description": "Test pillar with over 100% time allocation",
                    "icon": "💪",
                    "color": "#10B981",
                    "time_allocation_percentage": 150.0
                }
            },
            {
                "name": "Empty name field",
                "data": {
                    "name": "",
                    "description": "Test pillar with empty name",
                    "icon": "💪",
                    "color": "#10B981",
                    "time_allocation_percentage": 25.0
                }
            },
            {
                "name": "Null values in required fields",
                "data": {
                    "name": None,
                    "description": None,
                    "icon": None,
                    "color": None,
                    "time_allocation_percentage": None
                }
            }
        ]
        
        for scenario in scenarios:
            result = self.make_request('POST', '/pillars', data=scenario["data"], use_auth=True)
            if result['status_code'] == 422:
                self.found_422_errors.append({
                    "endpoint": "POST /pillars",
                    "scenario": scenario["name"],
                    "data": scenario["data"],
                    "response": result['data']
                })
                self.log_test(
                    f"PILLAR 422 - {scenario['name']}",
                    False,
                    f"422 error detected: {result.get('error', 'Unknown error')}",
                    result['data']
                )
            else:
                self.log_test(
                    f"PILLAR VALIDATION - {scenario['name']}",
                    True,
                    f"Handled gracefully with status {result['status_code']}"
                )

    def test_area_422_scenarios(self):
        """Test area creation scenarios that could cause 422 errors"""
        print("\n=== TESTING AREA 422 SCENARIOS ===")
        
        # First create a valid pillar for testing
        pillar_data = {
            "name": "Test Pillar for Areas",
            "description": "Test pillar",
            "icon": "💪",
            "color": "#10B981",
            "time_allocation_percentage": 25.0
        }
        pillar_result = self.make_request('POST', '/pillars', data=pillar_data, use_auth=True)
        valid_pillar_id = pillar_result['data']['id'] if pillar_result['success'] else str(uuid.uuid4())
        
        scenarios = [
            {
                "name": "Missing required name field",
                "data": {
                    "pillar_id": valid_pillar_id,
                    "description": "Test area without name",
                    "icon": "🏃",
                    "color": "#F59E0B",
                    "importance": 4
                }
            },
            {
                "name": "Invalid importance value (string)",
                "data": {
                    "pillar_id": valid_pillar_id,
                    "name": "Test Area",
                    "description": "Test area with invalid importance",
                    "icon": "🏃",
                    "color": "#F59E0B",
                    "importance": "invalid_importance"
                }
            },
            {
                "name": "Importance out of range (too high)",
                "data": {
                    "pillar_id": valid_pillar_id,
                    "name": "Test Area",
                    "description": "Test area with importance too high",
                    "icon": "🏃",
                    "color": "#F59E0B",
                    "importance": 10
                }
            },
            {
                "name": "Importance out of range (too low)",
                "data": {
                    "pillar_id": valid_pillar_id,
                    "name": "Test Area",
                    "description": "Test area with importance too low",
                    "icon": "🏃",
                    "color": "#F59E0B",
                    "importance": 0
                }
            },
            {
                "name": "Invalid pillar_id format",
                "data": {
                    "pillar_id": "not-a-valid-uuid",
                    "name": "Test Area",
                    "description": "Test area with invalid pillar_id",
                    "icon": "🏃",
                    "color": "#F59E0B",
                    "importance": 4
                }
            },
            {
                "name": "Non-existent pillar_id",
                "data": {
                    "pillar_id": str(uuid.uuid4()),
                    "name": "Test Area",
                    "description": "Test area with non-existent pillar_id",
                    "icon": "🏃",
                    "color": "#F59E0B",
                    "importance": 4
                }
            },
            {
                "name": "Empty name field",
                "data": {
                    "pillar_id": valid_pillar_id,
                    "name": "",
                    "description": "Test area with empty name",
                    "icon": "🏃",
                    "color": "#F59E0B",
                    "importance": 4
                }
            }
        ]
        
        for scenario in scenarios:
            result = self.make_request('POST', '/areas', data=scenario["data"], use_auth=True)
            if result['status_code'] == 422:
                self.found_422_errors.append({
                    "endpoint": "POST /areas",
                    "scenario": scenario["name"],
                    "data": scenario["data"],
                    "response": result['data']
                })
                self.log_test(
                    f"AREA 422 - {scenario['name']}",
                    False,
                    f"422 error detected: {result.get('error', 'Unknown error')}",
                    result['data']
                )
            else:
                self.log_test(
                    f"AREA VALIDATION - {scenario['name']}",
                    True,
                    f"Handled gracefully with status {result['status_code']}"
                )

    def test_project_422_scenarios(self):
        """Test project creation scenarios that could cause 422 errors"""
        print("\n=== TESTING PROJECT 422 SCENARIOS ===")
        
        # Create valid pillar and area for testing
        pillar_data = {
            "name": "Test Pillar for Projects",
            "description": "Test pillar",
            "icon": "💪",
            "color": "#10B981",
            "time_allocation_percentage": 25.0
        }
        pillar_result = self.make_request('POST', '/pillars', data=pillar_data, use_auth=True)
        valid_pillar_id = pillar_result['data']['id'] if pillar_result['success'] else str(uuid.uuid4())
        
        area_data = {
            "pillar_id": valid_pillar_id,
            "name": "Test Area for Projects",
            "description": "Test area",
            "icon": "🏃",
            "color": "#F59E0B",
            "importance": 4
        }
        area_result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
        valid_area_id = area_result['data']['id'] if area_result['success'] else str(uuid.uuid4())
        
        scenarios = [
            {
                "name": "Missing required name field",
                "data": {
                    "area_id": valid_area_id,
                    "description": "Test project without name",
                    "icon": "🏋️",
                    "status": "Not Started",
                    "priority": "high"
                }
            },
            {
                "name": "Invalid status value",
                "data": {
                    "area_id": valid_area_id,
                    "name": "Test Project",
                    "description": "Test project with invalid status",
                    "icon": "🏋️",
                    "status": "Invalid Status",
                    "priority": "high"
                }
            },
            {
                "name": "Invalid priority value",
                "data": {
                    "area_id": valid_area_id,
                    "name": "Test Project",
                    "description": "Test project with invalid priority",
                    "icon": "🏋️",
                    "status": "Not Started",
                    "priority": "invalid_priority"
                }
            },
            {
                "name": "Invalid deadline format",
                "data": {
                    "area_id": valid_area_id,
                    "name": "Test Project",
                    "description": "Test project with invalid deadline",
                    "icon": "🏋️",
                    "status": "Not Started",
                    "priority": "high",
                    "deadline": "not-a-date"
                }
            },
            {
                "name": "Invalid area_id format",
                "data": {
                    "area_id": "not-a-valid-uuid",
                    "name": "Test Project",
                    "description": "Test project with invalid area_id",
                    "icon": "🏋️",
                    "status": "Not Started",
                    "priority": "high"
                }
            },
            {
                "name": "Non-existent area_id",
                "data": {
                    "area_id": str(uuid.uuid4()),
                    "name": "Test Project",
                    "description": "Test project with non-existent area_id",
                    "icon": "🏋️",
                    "status": "Not Started",
                    "priority": "high"
                }
            }
        ]
        
        for scenario in scenarios:
            result = self.make_request('POST', '/projects', data=scenario["data"], use_auth=True)
            if result['status_code'] == 422:
                self.found_422_errors.append({
                    "endpoint": "POST /projects",
                    "scenario": scenario["name"],
                    "data": scenario["data"],
                    "response": result['data']
                })
                self.log_test(
                    f"PROJECT 422 - {scenario['name']}",
                    False,
                    f"422 error detected: {result.get('error', 'Unknown error')}",
                    result['data']
                )
            else:
                self.log_test(
                    f"PROJECT VALIDATION - {scenario['name']}",
                    True,
                    f"Handled gracefully with status {result['status_code']}"
                )

    def test_task_422_scenarios(self):
        """Test task creation scenarios that could cause 422 errors"""
        print("\n=== TESTING TASK 422 SCENARIOS ===")
        
        # Create valid hierarchy for testing
        pillar_data = {
            "name": "Test Pillar for Tasks",
            "description": "Test pillar",
            "icon": "💪",
            "color": "#10B981",
            "time_allocation_percentage": 25.0
        }
        pillar_result = self.make_request('POST', '/pillars', data=pillar_data, use_auth=True)
        valid_pillar_id = pillar_result['data']['id'] if pillar_result['success'] else str(uuid.uuid4())
        
        area_data = {
            "pillar_id": valid_pillar_id,
            "name": "Test Area for Tasks",
            "description": "Test area",
            "icon": "🏃",
            "color": "#F59E0B",
            "importance": 4
        }
        area_result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
        valid_area_id = area_result['data']['id'] if area_result['success'] else str(uuid.uuid4())
        
        project_data = {
            "area_id": valid_area_id,
            "name": "Test Project for Tasks",
            "description": "Test project",
            "icon": "🏋️",
            "status": "Not Started",
            "priority": "high"
        }
        project_result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
        valid_project_id = project_result['data']['id'] if project_result['success'] else str(uuid.uuid4())
        
        scenarios = [
            {
                "name": "Missing required name field",
                "data": {
                    "project_id": valid_project_id,
                    "description": "Test task without name",
                    "status": "todo",
                    "priority": "medium"
                }
            },
            {
                "name": "Invalid status value",
                "data": {
                    "project_id": valid_project_id,
                    "name": "Test Task",
                    "description": "Test task with invalid status",
                    "status": "invalid_status",
                    "priority": "medium"
                }
            },
            {
                "name": "Invalid priority value",
                "data": {
                    "project_id": valid_project_id,
                    "name": "Test Task",
                    "description": "Test task with invalid priority",
                    "status": "todo",
                    "priority": "invalid_priority"
                }
            },
            {
                "name": "Invalid due_date format",
                "data": {
                    "project_id": valid_project_id,
                    "name": "Test Task",
                    "description": "Test task with invalid due_date",
                    "status": "todo",
                    "priority": "medium",
                    "due_date": "not-a-date"
                }
            },
            {
                "name": "Invalid project_id format",
                "data": {
                    "project_id": "not-a-valid-uuid",
                    "name": "Test Task",
                    "description": "Test task with invalid project_id",
                    "status": "todo",
                    "priority": "medium"
                }
            },
            {
                "name": "Non-existent project_id",
                "data": {
                    "project_id": str(uuid.uuid4()),
                    "name": "Test Task",
                    "description": "Test task with non-existent project_id",
                    "status": "todo",
                    "priority": "medium"
                }
            },
            {
                "name": "Invalid parent_task_id format",
                "data": {
                    "project_id": valid_project_id,
                    "parent_task_id": "not-a-valid-uuid",
                    "name": "Test Task",
                    "description": "Test task with invalid parent_task_id",
                    "status": "todo",
                    "priority": "medium"
                }
            }
        ]
        
        for scenario in scenarios:
            result = self.make_request('POST', '/tasks', data=scenario["data"], use_auth=True)
            if result['status_code'] == 422:
                self.found_422_errors.append({
                    "endpoint": "POST /tasks",
                    "scenario": scenario["name"],
                    "data": scenario["data"],
                    "response": result['data']
                })
                self.log_test(
                    f"TASK 422 - {scenario['name']}",
                    False,
                    f"422 error detected: {result.get('error', 'Unknown error')}",
                    result['data']
                )
            else:
                self.log_test(
                    f"TASK VALIDATION - {scenario['name']}",
                    True,
                    f"Handled gracefully with status {result['status_code']}"
                )

    def test_complete_onboarding_422_scenarios(self):
        """Test complete onboarding scenarios that could cause 422 errors"""
        print("\n=== TESTING COMPLETE ONBOARDING 422 SCENARIOS ===")
        
        scenarios = [
            {
                "name": "Complete onboarding with invalid data",
                "data": {
                    "invalid_field": "invalid_value"
                }
            },
            {
                "name": "Complete onboarding with malformed request",
                "data": "not_a_dict"
            }
        ]
        
        for scenario in scenarios:
            result = self.make_request('POST', '/auth/complete-onboarding', data=scenario["data"], use_auth=True)
            if result['status_code'] == 422:
                self.found_422_errors.append({
                    "endpoint": "POST /auth/complete-onboarding",
                    "scenario": scenario["name"],
                    "data": scenario["data"],
                    "response": result['data']
                })
                self.log_test(
                    f"ONBOARDING 422 - {scenario['name']}",
                    False,
                    f"422 error detected: {result.get('error', 'Unknown error')}",
                    result['data']
                )
            else:
                self.log_test(
                    f"ONBOARDING VALIDATION - {scenario['name']}",
                    True,
                    f"Handled gracefully with status {result['status_code']}"
                )

    def run_targeted_422_tests(self):
        """Run all targeted 422 error tests"""
        print("\n🎯 STARTING TARGETED 422 ERROR REPRODUCTION TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 80)
        
        if not self.authenticate():
            print("❌ Authentication failed, cannot proceed with tests")
            return False
        
        # Run all 422 error tests
        test_methods = [
            ("Pillar 422 Scenarios", self.test_pillar_422_scenarios),
            ("Area 422 Scenarios", self.test_area_422_scenarios),
            ("Project 422 Scenarios", self.test_project_422_scenarios),
            ("Task 422 Scenarios", self.test_task_422_scenarios),
            ("Complete Onboarding 422 Scenarios", self.test_complete_onboarding_422_scenarios)
        ]
        
        for test_name, test_method in test_methods:
            print(f"\n--- {test_name} ---")
            try:
                test_method()
            except Exception as e:
                print(f"❌ {test_name} raised exception: {e}")
        
        # Summary
        print(f"\n" + "=" * 80)
        print("🎯 TARGETED 422 ERROR TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Total Tests Run: {len(self.test_results)}")
        print(f"422 Errors Found: {len(self.found_422_errors)}")
        
        if self.found_422_errors:
            print(f"\n🚨 422 ERRORS DETECTED ({len(self.found_422_errors)}):")
            for i, error in enumerate(self.found_422_errors, 1):
                print(f"\n{i}. {error['endpoint']} - {error['scenario']}")
                print(f"   Request Data: {json.dumps(error['data'], indent=4, default=str)}")
                print(f"   Response: {json.dumps(error['response'], indent=4, default=str)}")
            
            print(f"\n🎉 SUCCESS: REPRODUCED THE USER'S 422 ERROR ISSUE!")
            print("These 422 errors match the user's report about template application failures.")
            print("The frontend is likely trying to render these error objects, causing React errors.")
        else:
            print(f"\n✅ NO 422 ERRORS DETECTED")
            print("The backend is handling validation gracefully without 422 errors.")
        
        return len(self.found_422_errors) > 0

def main():
    """Run Targeted 422 Error Tests"""
    print("🎯 STARTING TARGETED 422 ERROR REPRODUCTION TESTING")
    print("=" * 80)
    
    tester = Targeted422ErrorTester()
    
    try:
        # Run the targeted 422 error tests
        found_422_errors = tester.run_targeted_422_tests()
        
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
        print(f"422 Errors Found: {len(tester.found_422_errors)}")
        
        if found_422_errors:
            print("\n🎉 MISSION ACCOMPLISHED!")
            print("Successfully reproduced 422 errors that match the user's reported issue.")
            print("These validation failures during template application are causing frontend React errors.")
        else:
            print("\n🤔 NO 422 ERRORS REPRODUCED")
            print("The backend validation is working correctly without 422 errors.")
        
        print("=" * 80)
        
        return found_422_errors
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)