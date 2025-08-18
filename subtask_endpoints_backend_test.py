#!/usr/bin/env python3
"""
SUBTASK ENDPOINTS BACKEND TESTING
Testing newly added subtask endpoints used by Tasks modal as requested in review.

TEST STEPS:
1) Login and capture token
2) Pick an existing task from GET /api/tasks (ensure it has project_id), or create one if needed
3) GET /api/tasks/{task_id}/subtasks → expect 200 array
4) POST /api/tasks/{task_id}/subtasks with name/description/priority → expect 200 and object with id
5) GET again → array length increased
6) Cleanup: none required, report created subtask id

CREDENTIALS: marc.alleyne@aurumtechnologyltd.com / password123
"""

import requests
import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://taskpilot-2.preview.emergentagent.com/api"

class SubtaskEndpointsAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        # Use the specified test credentials
        self.test_user_email = "marc.alleyne@aurumtechnologyltd.com"
        self.test_user_password = "password123"
        self.created_subtask_id = None
        
    def log_test(self, test_name: str, success: bool, message: str = "", data: Any = None, response_time: float = None):
        """Log test results with response time"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        if data:
            result['data'] = data
        if response_time:
            result['response_time_ms'] = round(response_time * 1000, 2)
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        time_info = f" ({response_time*1000:.0f}ms)" if response_time else ""
        print(f"{status} {test_name}{time_info}: {message}")
        if data and not success:
            print(f"   Data: {json.dumps(data, indent=2, default=str)}")

    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None, use_auth: bool = False) -> Dict:
        """Make HTTP request with error handling and timing"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        # Add authentication header if token is available and requested
        if use_auth and self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        start_time = time.time()
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
            
            response_time = time.time() - start_time
            
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
                'response_time': response_time,
                'error': f"HTTP {response.status_code}: {response_data}" if response.status_code >= 400 else None
            }
            
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
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
                'response': getattr(e, 'response', None),
                'response_time': response_time
            }

    def test_step_1_login_and_capture_token(self):
        """Step 1: Login and capture token"""
        print("\n=== STEP 1: LOGIN AND CAPTURE TOKEN ===")
        
        # Login user with specified credentials
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        self.log_test(
            "LOGIN AND TOKEN CAPTURE",
            result['success'],
            f"Login successful with {self.test_user_email}" if result['success'] else f"Login failed: {result.get('error', 'Unknown error')}",
            response_time=result.get('response_time')
        )
        
        if not result['success']:
            return False
        
        token_data = result['data']
        self.auth_token = token_data.get('access_token')
        
        # Verify token works
        result = self.make_request('GET', '/auth/me', use_auth=True)
        self.log_test(
            "TOKEN VALIDATION",
            result['success'],
            f"Token validated successfully, user: {result['data'].get('email', 'Unknown')}" if result['success'] else f"Token validation failed: {result.get('error', 'Unknown error')}",
            response_time=result.get('response_time')
        )
        
        return result['success']

    def test_step_2_get_or_create_task_with_project_id(self):
        """Step 2: Pick an existing task from GET /api/tasks (ensure it has project_id), or create one if needed"""
        print("\n=== STEP 2: GET OR CREATE TASK WITH PROJECT_ID ===")
        
        if not self.auth_token:
            self.log_test("GET TASKS - Authentication Required", False, "No authentication token available")
            return None
        
        # First, try to get existing tasks
        result = self.make_request('GET', '/tasks', use_auth=True)
        self.log_test(
            "GET EXISTING TASKS",
            result['success'],
            f"Retrieved tasks successfully" if result['success'] else f"Failed to get tasks: {result.get('error', 'Unknown error')}",
            response_time=result.get('response_time')
        )
        
        if result['success']:
            tasks = result['data']
            # Look for a task with project_id
            task_with_project = None
            for task in tasks:
                if task.get('project_id'):
                    task_with_project = task
                    break
            
            if task_with_project:
                self.log_test(
                    "FOUND EXISTING TASK WITH PROJECT_ID",
                    True,
                    f"Found task '{task_with_project.get('name', 'Unknown')}' with project_id: {task_with_project.get('project_id')}"
                )
                return task_with_project['id']
        
        # If no existing task with project_id, we need to create one
        # First, get or create a project
        project_id = self.get_or_create_project()
        if not project_id:
            return None
        
        # Create a task with the project_id
        task_data = {
            "project_id": project_id,
            "name": "Test Task for Subtasks",
            "description": "Task created for testing subtask endpoints",
            "priority": "medium",
            "status": "todo"
        }
        
        result = self.make_request('POST', '/tasks', data=task_data, use_auth=True)
        self.log_test(
            "CREATE TASK WITH PROJECT_ID",
            result['success'],
            f"Created task successfully" if result['success'] else f"Failed to create task: {result.get('error', 'Unknown error')}",
            response_time=result.get('response_time')
        )
        
        if result['success']:
            task = result['data']
            return task['id']
        
        return None

    def get_or_create_project(self):
        """Helper: Get or create a project for task creation"""
        # First, try to get existing projects
        result = self.make_request('GET', '/projects', use_auth=True)
        if result['success']:
            projects = result['data']
            if projects:
                return projects[0]['id']
        
        # If no projects, get or create an area first
        area_id = self.get_or_create_area()
        if not area_id:
            return None
        
        # Create a project
        project_data = {
            "area_id": area_id,
            "name": "Test Project for Subtasks",
            "description": "Project created for testing subtask endpoints",
            "status": "Not Started",
            "priority": "medium"
        }
        
        result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
        if result['success']:
            project = result['data']
            return project['id']
        
        return None

    def get_or_create_area(self):
        """Helper: Get or create an area for project creation"""
        # First, try to get existing areas
        result = self.make_request('GET', '/areas', use_auth=True)
        if result['success']:
            areas = result['data']
            if areas:
                return areas[0]['id']
        
        # If no areas, get or create a pillar first
        pillar_id = self.get_or_create_pillar()
        if not pillar_id:
            return None
        
        # Create an area
        area_data = {
            "pillar_id": pillar_id,
            "name": "Test Area for Subtasks",
            "description": "Area created for testing subtask endpoints",
            "icon": "🧪",
            "color": "#3B82F6",
            "importance": 3
        }
        
        result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
        if result['success']:
            area = result['data']
            return area['id']
        
        return None

    def get_or_create_pillar(self):
        """Helper: Get or create a pillar for area creation"""
        # First, try to get existing pillars
        result = self.make_request('GET', '/pillars', use_auth=True)
        if result['success']:
            pillars = result['data']
            if pillars:
                return pillars[0]['id']
        
        # Create a pillar
        pillar_data = {
            "name": "Test Pillar for Subtasks",
            "description": "Pillar created for testing subtask endpoints",
            "icon": "🧪",
            "color": "#10B981",
            "time_allocation_percentage": 25.0
        }
        
        result = self.make_request('POST', '/pillars', data=pillar_data, use_auth=True)
        if result['success']:
            pillar = result['data']
            return pillar['id']
        
        return None

    def test_step_3_get_subtasks_empty_array(self, task_id: str):
        """Step 3: GET /api/tasks/{task_id}/subtasks → expect 200 array"""
        print("\n=== STEP 3: GET SUBTASKS (EXPECT EMPTY ARRAY) ===")
        
        if not self.auth_token:
            self.log_test("GET SUBTASKS - Authentication Required", False, "No authentication token available")
            return False, 0
        
        result = self.make_request('GET', f'/tasks/{task_id}/subtasks', use_auth=True)
        self.log_test(
            "GET SUBTASKS (INITIAL)",
            result['success'],
            f"Retrieved subtasks successfully, count: {len(result['data']) if result['success'] and isinstance(result['data'], list) else 'N/A'}" if result['success'] else f"Failed to get subtasks: {result.get('error', 'Unknown error')}",
            response_time=result.get('response_time')
        )
        
        if result['success']:
            subtasks = result['data']
            if isinstance(subtasks, list):
                return True, len(subtasks)
            else:
                self.log_test("SUBTASKS RESPONSE FORMAT", False, f"Expected array, got: {type(subtasks)}")
                return False, 0
        
        return False, 0

    def test_step_4_create_subtask(self, task_id: str):
        """Step 4: POST /api/tasks/{task_id}/subtasks with name/description/priority → expect 200 and object with id"""
        print("\n=== STEP 4: CREATE SUBTASK ===")
        
        if not self.auth_token:
            self.log_test("CREATE SUBTASK - Authentication Required", False, "No authentication token available")
            return None
        
        subtask_data = {
            "name": "Test Subtask",
            "description": "Subtask created for testing subtask endpoints",
            "priority": "high",
            "category": "testing"
        }
        
        result = self.make_request('POST', f'/tasks/{task_id}/subtasks', data=subtask_data, use_auth=True)
        self.log_test(
            "CREATE SUBTASK",
            result['success'],
            f"Created subtask successfully" if result['success'] else f"Failed to create subtask: {result.get('error', 'Unknown error')}",
            response_time=result.get('response_time')
        )
        
        if result['success']:
            subtask = result['data']
            if isinstance(subtask, dict) and 'id' in subtask:
                self.created_subtask_id = subtask['id']
                self.log_test(
                    "SUBTASK RESPONSE VALIDATION",
                    True,
                    f"Subtask created with ID: {subtask['id']}, name: '{subtask.get('name', 'Unknown')}'"
                )
                return subtask['id']
            else:
                self.log_test("SUBTASK RESPONSE FORMAT", False, f"Expected object with id, got: {subtask}")
                return None
        
        return None

    def test_step_5_verify_subtask_count_increased(self, task_id: str, initial_count: int):
        """Step 5: GET again → array length increased"""
        print("\n=== STEP 5: VERIFY SUBTASK COUNT INCREASED ===")
        
        if not self.auth_token:
            self.log_test("VERIFY SUBTASK COUNT - Authentication Required", False, "No authentication token available")
            return False
        
        result = self.make_request('GET', f'/tasks/{task_id}/subtasks', use_auth=True)
        self.log_test(
            "GET SUBTASKS (AFTER CREATE)",
            result['success'],
            f"Retrieved subtasks successfully, count: {len(result['data']) if result['success'] and isinstance(result['data'], list) else 'N/A'}" if result['success'] else f"Failed to get subtasks: {result.get('error', 'Unknown error')}",
            response_time=result.get('response_time')
        )
        
        if result['success']:
            subtasks = result['data']
            if isinstance(subtasks, list):
                new_count = len(subtasks)
                count_increased = new_count > initial_count
                self.log_test(
                    "SUBTASK COUNT VERIFICATION",
                    count_increased,
                    f"Count increased from {initial_count} to {new_count}" if count_increased else f"Count did not increase: {initial_count} → {new_count}"
                )
                
                # Verify our created subtask is in the list
                if self.created_subtask_id:
                    subtask_found = any(s.get('id') == self.created_subtask_id for s in subtasks)
                    self.log_test(
                        "CREATED SUBTASK IN LIST",
                        subtask_found,
                        f"Created subtask {self.created_subtask_id} found in list" if subtask_found else f"Created subtask {self.created_subtask_id} not found in list"
                    )
                    return count_increased and subtask_found
                
                return count_increased
            else:
                self.log_test("SUBTASKS RESPONSE FORMAT", False, f"Expected array, got: {type(subtasks)}")
                return False
        
        return False

    def run_comprehensive_subtask_endpoints_test(self):
        """Run comprehensive subtask endpoints API tests"""
        print("\n🔧 STARTING SUBTASK ENDPOINTS API COMPREHENSIVE TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 80)
        
        # Step 1: Login and capture token
        if not self.test_step_1_login_and_capture_token():
            print("❌ Authentication failed, cannot proceed with testing")
            return False
        
        # Step 2: Get or create task with project_id
        task_id = self.test_step_2_get_or_create_task_with_project_id()
        if not task_id:
            print("❌ Could not get or create task with project_id, cannot proceed")
            return False
        
        print(f"\n📋 Using task ID: {task_id}")
        
        # Step 3: Get initial subtasks (expect empty array)
        success, initial_count = self.test_step_3_get_subtasks_empty_array(task_id)
        if not success:
            print("❌ Failed to get initial subtasks, cannot proceed")
            return False
        
        # Step 4: Create subtask
        created_subtask_id = self.test_step_4_create_subtask(task_id)
        if not created_subtask_id:
            print("❌ Failed to create subtask, cannot proceed")
            return False
        
        # Step 5: Verify subtask count increased
        if not self.test_step_5_verify_subtask_count_increased(task_id, initial_count):
            print("❌ Subtask count verification failed")
            return False
        
        # Calculate success metrics
        successful_tests = sum(1 for result in self.test_results if result['success'])
        total_tests = len(self.test_results)
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Calculate average response time
        response_times = [r.get('response_time_ms', 0) for r in self.test_results if r.get('response_time_ms')]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        print(f"\n" + "=" * 80)
        print("🔧 SUBTASK ENDPOINTS API TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        print(f"Average Response Time: {avg_response_time:.0f}ms")
        
        if self.created_subtask_id:
            print(f"Created Subtask ID: {self.created_subtask_id}")
        
        if success_rate >= 85:
            print("\n✅ SUBTASK ENDPOINTS API SYSTEM: SUCCESS")
            print("   ✅ GET /api/tasks/{task_id}/subtasks working")
            print("   ✅ POST /api/tasks/{task_id}/subtasks functional")
            print("   ✅ Subtask creation and retrieval verified")
            print("   ✅ Authentication and authorization working")
            print("   The Subtask Endpoints API is production-ready!")
        else:
            print("\n❌ SUBTASK ENDPOINTS API SYSTEM: ISSUES DETECTED")
            print("   Issues found in subtask endpoints API implementation")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 85

def main():
    """Run Subtask Endpoints API Tests"""
    print("🔧 STARTING SUBTASK ENDPOINTS API BACKEND TESTING")
    print("=" * 80)
    
    tester = SubtaskEndpointsAPITester()
    
    try:
        # Run the comprehensive subtask endpoints API tests
        success = tester.run_comprehensive_subtask_endpoints_test()
        
        # Calculate overall results
        total_tests = len(tester.test_results)
        passed_tests = sum(1 for result in tester.test_results if result['success'])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Calculate response time summary
        response_times = [r.get('response_time_ms', 0) for r in tester.test_results if r.get('response_time_ms')]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        
        print("\n" + "=" * 80)
        print("📊 FINAL RESULTS")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Response Times: avg={avg_response_time:.0f}ms, min={min_response_time:.0f}ms, max={max_response_time:.0f}ms")
        if tester.created_subtask_id:
            print(f"Created Subtask ID: {tester.created_subtask_id}")
        print("=" * 80)
        
        return success_rate >= 85
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)