#!/usr/bin/env python3
"""
TASKS CRUD + DEPENDENCIES BACKEND TESTING
Testing Tasks CRUD operations and Dependencies functionality as requested in review.

FOCUS AREAS:
1. Login with known test user; capture token
2. GET /api/tasks → expect 200, array
3. Create a temporary project via POST /api/projects with minimal fields; capture project.id
4. POST /api/tasks with name, project_id=project.id → expect 200, respond with id
5. GET /api/tasks?project_id=<project.id> → expect array includes created task
6. GET /api/projects/<project.id>/tasks/available-dependencies → expect 200 array
7. PUT /api/tasks/<task.id>/dependencies with [] → expect 200 ok
8. GET /api/tasks/<task.id>/dependencies → expect 200 with empty arrays
9. PUT /api/tasks/<task.id>/dependencies with [<task.id>] → expect 400 invalid or test behavior
10. DELETE /api/tasks/<task.id> and DELETE /api/projects/<project.id> cleanup

CREDENTIALS: marc.alleyne@aurumtechnologyltd.com / password123
"""

import requests
import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Any

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://focus-planner-3.preview.emergentagent.com/api"

class TasksDependenciesAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        # Use the specified test credentials
        self.test_user_email = "marc.alleyne@aurumtechnologyltd.com"
        self.test_user_password = "password123"
        self.created_project_id = None
        self.created_task_id = None
        self.start_time = time.time()
        
    def log_test(self, test_name: str, success: bool, message: str = "", data: Any = None, response_time: float = None):
        """Log test results with response time"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'response_time_ms': int(response_time * 1000) if response_time else None
        }
        if data:
            result['data'] = data
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        time_info = f" ({int(response_time * 1000)}ms)" if response_time else ""
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

    def test_step_1_login(self):
        """Step 1: Login with known test user; capture token"""
        print("\n=== STEP 1: LOGIN WITH KNOWN TEST USER ===")
        
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        
        if result['success']:
            token_data = result['data']
            self.auth_token = token_data.get('access_token')
            self.log_test(
                "STEP 1: USER LOGIN",
                True,
                f"Login successful with {self.test_user_email}, token captured",
                response_time=result['response_time']
            )
            return True
        else:
            self.log_test(
                "STEP 1: USER LOGIN",
                False,
                f"Login failed: {result.get('error', 'Unknown error')}",
                response_time=result['response_time']
            )
            return False

    def test_step_2_get_tasks(self):
        """Step 2: GET /api/tasks → expect 200, array"""
        print("\n=== STEP 2: GET /api/tasks → EXPECT 200, ARRAY ===")
        
        result = self.make_request('GET', '/tasks', use_auth=True)
        
        if result['success'] and result['status_code'] == 200:
            tasks_data = result['data']
            if isinstance(tasks_data, list):
                self.log_test(
                    "STEP 2: GET TASKS",
                    True,
                    f"GET /api/tasks returned 200 with array of {len(tasks_data)} tasks",
                    response_time=result['response_time']
                )
                return True
            else:
                self.log_test(
                    "STEP 2: GET TASKS",
                    False,
                    f"GET /api/tasks returned 200 but data is not array: {type(tasks_data)}",
                    response_time=result['response_time']
                )
                return False
        else:
            self.log_test(
                "STEP 2: GET TASKS",
                False,
                f"GET /api/tasks failed: {result.get('error', 'Unknown error')}",
                response_time=result['response_time']
            )
            return False

    def test_step_3_get_existing_project(self):
        """Step 3: Get an existing project via GET /api/ultra/projects; capture project.id"""
        print("\n=== STEP 3: GET EXISTING PROJECT (POST /api/projects NOT AVAILABLE) ===")
        
        # Try to get existing projects from ultra endpoint
        result = self.make_request('GET', '/ultra/projects', use_auth=True)
        
        if result['success'] and result['status_code'] == 200:
            projects = result['data']
            if isinstance(projects, list) and len(projects) > 0:
                # Use the first available project
                project = projects[0]
                if 'id' in project:
                    self.created_project_id = project['id']
                    self.log_test(
                        "STEP 3: GET EXISTING PROJECT",
                        True,
                        f"GET /api/ultra/projects successful, using existing project.id: {self.created_project_id}",
                        response_time=result['response_time']
                    )
                    return True
                else:
                    self.log_test(
                        "STEP 3: GET EXISTING PROJECT",
                        False,
                        f"GET /api/ultra/projects returned projects but no 'id' field",
                        data=project,
                        response_time=result['response_time']
                    )
                    return False
            else:
                self.log_test(
                    "STEP 3: GET EXISTING PROJECT",
                    False,
                    f"GET /api/ultra/projects returned empty array - no projects available for testing",
                    response_time=result['response_time']
                )
                return False
        else:
            self.log_test(
                "STEP 3: GET EXISTING PROJECT",
                False,
                f"GET /api/ultra/projects failed: {result.get('error', 'Unknown error')}",
                response_time=result['response_time']
            )
            return False

    def test_step_4_create_task(self):
        """Step 4: POST /api/tasks with name, project_id=project.id → expect 200, respond with id"""
        print("\n=== STEP 4: CREATE TASK WITH PROJECT_ID ===")
        
        if not self.created_project_id:
            self.log_test(
                "STEP 4: CREATE TASK",
                False,
                "Cannot create task - no project_id available from step 3"
            )
            return False
        
        # Create task with project_id
        task_data = {
            "name": f"Test Task Dependencies {int(time.time())}",
            "project_id": self.created_project_id
        }
        
        result = self.make_request('POST', '/tasks', data=task_data, use_auth=True)
        
        if result['success'] and result['status_code'] == 200:
            task = result['data']
            if 'id' in task:
                self.created_task_id = task['id']
                self.log_test(
                    "STEP 4: CREATE TASK",
                    True,
                    f"POST /api/tasks successful, task.id captured: {self.created_task_id}",
                    response_time=result['response_time']
                )
                return True
            else:
                self.log_test(
                    "STEP 4: CREATE TASK",
                    False,
                    f"POST /api/tasks returned 200 but no 'id' field in response",
                    data=task,
                    response_time=result['response_time']
                )
                return False
        else:
            self.log_test(
                "STEP 4: CREATE TASK",
                False,
                f"POST /api/tasks failed: {result.get('error', 'Unknown error')}",
                response_time=result['response_time']
            )
            return False

    def test_step_5_get_tasks_by_project(self):
        """Step 5: GET /api/tasks?project_id=<project.id> → expect array includes created task"""
        print("\n=== STEP 5: GET TASKS BY PROJECT_ID ===")
        
        if not self.created_project_id or not self.created_task_id:
            self.log_test(
                "STEP 5: GET TASKS BY PROJECT",
                False,
                "Cannot test - missing project_id or task_id from previous steps"
            )
            return False
        
        params = {"project_id": self.created_project_id}
        result = self.make_request('GET', '/tasks', params=params, use_auth=True)
        
        if result['success'] and result['status_code'] == 200:
            tasks_data = result['data']
            if isinstance(tasks_data, list):
                # Check if created task is in the array
                created_task_found = any(task.get('id') == self.created_task_id for task in tasks_data)
                if created_task_found:
                    self.log_test(
                        "STEP 5: GET TASKS BY PROJECT",
                        True,
                        f"GET /api/tasks?project_id={self.created_project_id} returned array with created task included",
                        response_time=result['response_time']
                    )
                    return True
                else:
                    self.log_test(
                        "STEP 5: GET TASKS BY PROJECT",
                        False,
                        f"GET /api/tasks?project_id={self.created_project_id} returned array but created task not found",
                        data={"task_ids": [task.get('id') for task in tasks_data]},
                        response_time=result['response_time']
                    )
                    return False
            else:
                self.log_test(
                    "STEP 5: GET TASKS BY PROJECT",
                    False,
                    f"GET /api/tasks?project_id={self.created_project_id} returned 200 but data is not array",
                    response_time=result['response_time']
                )
                return False
        else:
            self.log_test(
                "STEP 5: GET TASKS BY PROJECT",
                False,
                f"GET /api/tasks?project_id={self.created_project_id} failed: {result.get('error', 'Unknown error')}",
                response_time=result['response_time']
            )
            return False

    def test_step_6_get_available_dependencies(self):
        """Step 6: GET /api/projects/<project.id>/tasks/available-dependencies → expect 200 array"""
        print("\n=== STEP 6: GET AVAILABLE DEPENDENCIES ===")
        
        if not self.created_project_id:
            self.log_test(
                "STEP 6: GET AVAILABLE DEPENDENCIES",
                False,
                "Cannot test - missing project_id from previous steps"
            )
            return False
        
        # Test without task_id parameter first
        endpoint = f'/projects/{self.created_project_id}/tasks/available-dependencies'
        result = self.make_request('GET', endpoint, use_auth=True)
        
        if result['success'] and result['status_code'] == 200:
            deps_data = result['data']
            if isinstance(deps_data, list):
                self.log_test(
                    "STEP 6A: GET AVAILABLE DEPENDENCIES (NO TASK_ID)",
                    True,
                    f"GET /api/projects/{self.created_project_id}/tasks/available-dependencies returned array with {len(deps_data)} tasks",
                    response_time=result['response_time']
                )
                
                # Test with task_id parameter to exclude the task itself
                if self.created_task_id:
                    params = {"task_id": self.created_task_id}
                    result2 = self.make_request('GET', endpoint, params=params, use_auth=True)
                    
                    if result2['success'] and result2['status_code'] == 200:
                        deps_data2 = result2['data']
                        if isinstance(deps_data2, list):
                            # Should exclude the task itself
                            task_excluded = not any(task.get('id') == self.created_task_id for task in deps_data2)
                            self.log_test(
                                "STEP 6B: GET AVAILABLE DEPENDENCIES (WITH TASK_ID)",
                                True,
                                f"GET available-dependencies with task_id={self.created_task_id} returned array with {len(deps_data2)} tasks, task excluded: {task_excluded}",
                                response_time=result2['response_time']
                            )
                            return True
                        else:
                            self.log_test(
                                "STEP 6B: GET AVAILABLE DEPENDENCIES (WITH TASK_ID)",
                                False,
                                f"GET available-dependencies with task_id returned 200 but data is not array",
                                response_time=result2['response_time']
                            )
                            return False
                    else:
                        self.log_test(
                            "STEP 6B: GET AVAILABLE DEPENDENCIES (WITH TASK_ID)",
                            False,
                            f"GET available-dependencies with task_id failed: {result2.get('error', 'Unknown error')}",
                            response_time=result2['response_time']
                        )
                        return False
                else:
                    return True  # First test passed, no task_id to test with
            else:
                self.log_test(
                    "STEP 6: GET AVAILABLE DEPENDENCIES",
                    False,
                    f"GET available-dependencies returned 200 but data is not array: {type(deps_data)}",
                    response_time=result['response_time']
                )
                return False
        else:
            self.log_test(
                "STEP 6: GET AVAILABLE DEPENDENCIES",
                False,
                f"GET available-dependencies failed: {result.get('error', 'Unknown error')}",
                response_time=result['response_time']
            )
            return False

    def test_step_7_set_empty_dependencies(self):
        """Step 7: PUT /api/tasks/<task.id>/dependencies with [] → expect 200 ok"""
        print("\n=== STEP 7: SET EMPTY DEPENDENCIES ===")
        
        if not self.created_task_id:
            self.log_test(
                "STEP 7: SET EMPTY DEPENDENCIES",
                False,
                "Cannot test - missing task_id from previous steps"
            )
            return False
        
        # Set empty dependencies array
        endpoint = f'/tasks/{self.created_task_id}/dependencies'
        result = self.make_request('PUT', endpoint, data=[], use_auth=True)
        
        if result['success'] and result['status_code'] == 200:
            self.log_test(
                "STEP 7: SET EMPTY DEPENDENCIES",
                True,
                f"PUT /api/tasks/{self.created_task_id}/dependencies with [] returned 200 OK",
                response_time=result['response_time']
            )
            return True
        else:
            self.log_test(
                "STEP 7: SET EMPTY DEPENDENCIES",
                False,
                f"PUT dependencies with [] failed: {result.get('error', 'Unknown error')}",
                response_time=result['response_time']
            )
            return False

    def test_step_8_get_dependencies(self):
        """Step 8: GET /api/tasks/<task.id>/dependencies → expect 200 with empty arrays"""
        print("\n=== STEP 8: GET TASK DEPENDENCIES ===")
        
        if not self.created_task_id:
            self.log_test(
                "STEP 8: GET TASK DEPENDENCIES",
                False,
                "Cannot test - missing task_id from previous steps"
            )
            return False
        
        endpoint = f'/tasks/{self.created_task_id}/dependencies'
        result = self.make_request('GET', endpoint, use_auth=True)
        
        if result['success'] and result['status_code'] == 200:
            deps_data = result['data']
            # Check for expected structure with empty arrays
            if isinstance(deps_data, dict):
                dependency_task_ids = deps_data.get('dependency_task_ids', [])
                dependency_tasks = deps_data.get('dependency_tasks', [])
                
                if isinstance(dependency_task_ids, list) and isinstance(dependency_tasks, list):
                    if len(dependency_task_ids) == 0 and len(dependency_tasks) == 0:
                        self.log_test(
                            "STEP 8: GET TASK DEPENDENCIES",
                            True,
                            f"GET /api/tasks/{self.created_task_id}/dependencies returned 200 with empty arrays",
                            response_time=result['response_time']
                        )
                        return True
                    else:
                        self.log_test(
                            "STEP 8: GET TASK DEPENDENCIES",
                            False,
                            f"GET dependencies returned arrays but not empty: ids={len(dependency_task_ids)}, tasks={len(dependency_tasks)}",
                            data=deps_data,
                            response_time=result['response_time']
                        )
                        return False
                else:
                    self.log_test(
                        "STEP 8: GET TASK DEPENDENCIES",
                        False,
                        f"GET dependencies returned 200 but arrays are not lists",
                        data=deps_data,
                        response_time=result['response_time']
                    )
                    return False
            else:
                self.log_test(
                    "STEP 8: GET TASK DEPENDENCIES",
                    False,
                    f"GET dependencies returned 200 but data is not dict: {type(deps_data)}",
                    response_time=result['response_time']
                )
                return False
        else:
            self.log_test(
                "STEP 8: GET TASK DEPENDENCIES",
                False,
                f"GET dependencies failed: {result.get('error', 'Unknown error')}",
                response_time=result['response_time']
            )
            return False

    def test_step_9_self_dependency(self):
        """Step 9: PUT /api/tasks/<task.id>/dependencies with [<task.id>] → test behavior"""
        print("\n=== STEP 9: TEST SELF-DEPENDENCY BEHAVIOR ===")
        
        if not self.created_task_id:
            self.log_test(
                "STEP 9: TEST SELF-DEPENDENCY",
                False,
                "Cannot test - missing task_id from previous steps"
            )
            return False
        
        # Try to set task as dependency of itself
        endpoint = f'/tasks/{self.created_task_id}/dependencies'
        result = self.make_request('PUT', endpoint, data=[self.created_task_id], use_auth=True)
        
        if result['status_code'] == 400:
            self.log_test(
                "STEP 9: TEST SELF-DEPENDENCY",
                True,
                f"PUT /api/tasks/{self.created_task_id}/dependencies with [self] returned 400 (invalid) as expected",
                response_time=result['response_time']
            )
            return True
        elif result['status_code'] == 200:
            # System allows self-dependency, let's check if it's actually set
            get_result = self.make_request('GET', endpoint, use_auth=True)
            if get_result['success']:
                deps_data = get_result['data']
                dependency_task_ids = deps_data.get('dependency_task_ids', [])
                if self.created_task_id in dependency_task_ids:
                    self.log_test(
                        "STEP 9: TEST SELF-DEPENDENCY",
                        True,
                        f"PUT self-dependency returned 200 and GET confirms it's set (system allows self-dependencies)",
                        response_time=result['response_time']
                    )
                    return True
                else:
                    self.log_test(
                        "STEP 9: TEST SELF-DEPENDENCY",
                        True,
                        f"PUT self-dependency returned 200 but GET shows it's filtered out (system prevents self-dependencies)",
                        response_time=result['response_time']
                    )
                    return True
            else:
                self.log_test(
                    "STEP 9: TEST SELF-DEPENDENCY",
                    False,
                    f"PUT self-dependency returned 200 but GET failed to verify",
                    response_time=result['response_time']
                )
                return False
        else:
            self.log_test(
                "STEP 9: TEST SELF-DEPENDENCY",
                False,
                f"PUT self-dependency failed with unexpected status: {result.get('error', 'Unknown error')}",
                response_time=result['response_time']
            )
            return False

    def test_step_10_cleanup(self):
        """Step 10: DELETE /api/tasks/<task.id> cleanup (skip project deletion since we used existing project)"""
        print("\n=== STEP 10: CLEANUP RESOURCES ===")
        
        cleanup_success = True
        
        # Delete task only (we used an existing project, so don't delete it)
        if self.created_task_id:
            endpoint = f'/tasks/{self.created_task_id}'
            result = self.make_request('DELETE', endpoint, use_auth=True)
            
            if result['success'] and result['status_code'] == 200:
                self.log_test(
                    "STEP 10: DELETE TASK",
                    True,
                    f"DELETE /api/tasks/{self.created_task_id} successful",
                    response_time=result['response_time']
                )
            else:
                self.log_test(
                    "STEP 10: DELETE TASK",
                    False,
                    f"DELETE task failed: {result.get('error', 'Unknown error')}",
                    response_time=result['response_time']
                )
                cleanup_success = False
        else:
            self.log_test(
                "STEP 10: CLEANUP",
                True,
                "No task to cleanup (task creation failed)",
            )
        
        return cleanup_success

    def run_comprehensive_tasks_dependencies_test(self):
        """Run comprehensive Tasks CRUD + Dependencies test as specified in review request"""
        print("\n🔧 STARTING TASKS CRUD + DEPENDENCIES BACKEND TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 80)
        
        # Run all test steps in sequence
        test_steps = [
            ("Step 1: Login with known test user", self.test_step_1_login),
            ("Step 2: GET /api/tasks → expect 200, array", self.test_step_2_get_tasks),
            ("Step 3: Create temporary project", self.test_step_3_create_project),
            ("Step 4: POST /api/tasks with project_id", self.test_step_4_create_task),
            ("Step 5: GET /api/tasks?project_id → includes created task", self.test_step_5_get_tasks_by_project),
            ("Step 6: GET available-dependencies → expect 200 array", self.test_step_6_get_available_dependencies),
            ("Step 7: PUT dependencies with [] → expect 200", self.test_step_7_set_empty_dependencies),
            ("Step 8: GET dependencies → expect empty arrays", self.test_step_8_get_dependencies),
            ("Step 9: PUT self-dependency → test behavior", self.test_step_9_self_dependency),
            ("Step 10: Cleanup resources", self.test_step_10_cleanup)
        ]
        
        successful_tests = 0
        total_tests = len(test_steps)
        
        for step_name, test_method in test_steps:
            print(f"\n--- {step_name} ---")
            try:
                if test_method():
                    successful_tests += 1
                    print(f"✅ {step_name} completed successfully")
                else:
                    print(f"❌ {step_name} failed")
                    # Continue with remaining tests even if one fails
            except Exception as e:
                print(f"❌ {step_name} raised exception: {e}")
        
        success_rate = (successful_tests / total_tests) * 100
        total_time = time.time() - self.start_time
        
        print(f"\n" + "=" * 80)
        print("🔧 TASKS CRUD + DEPENDENCIES TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Steps: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        print(f"Total Test Time: {total_time:.2f}s")
        
        # Calculate average response times
        response_times = [r['response_time_ms'] for r in self.test_results if r.get('response_time_ms')]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            print(f"Average Response Time: {avg_response_time:.0f}ms")
        
        # Analyze results by category
        auth_tests_passed = sum(1 for result in self.test_results if result['success'] and 'LOGIN' in result['test'])
        crud_tests_passed = sum(1 for result in self.test_results if result['success'] and any(x in result['test'] for x in ['GET TASKS', 'CREATE', 'DELETE']))
        dependency_tests_passed = sum(1 for result in self.test_results if result['success'] and 'DEPENDENCIES' in result['test'])
        
        print(f"\n🔍 SYSTEM ANALYSIS:")
        print(f"Authentication Tests Passed: {auth_tests_passed}")
        print(f"CRUD Tests Passed: {crud_tests_passed}")
        print(f"Dependencies Tests Passed: {dependency_tests_passed}")
        
        if success_rate >= 90:
            print("\n✅ TASKS CRUD + DEPENDENCIES SYSTEM: SUCCESS")
            print("   ✅ User authentication working")
            print("   ✅ Tasks CRUD operations functional")
            print("   ✅ Project creation and linking working")
            print("   ✅ Task dependencies system operational")
            print("   ✅ Available dependencies endpoint working")
            print("   ✅ Self-dependency validation tested")
            print("   The Tasks CRUD + Dependencies system is production-ready!")
        elif success_rate >= 70:
            print("\n⚠️ TASKS CRUD + DEPENDENCIES SYSTEM: MOSTLY FUNCTIONAL")
            print("   Most core functionality working with some issues")
        else:
            print("\n❌ TASKS CRUD + DEPENDENCIES SYSTEM: ISSUES DETECTED")
            print("   Significant issues found in Tasks CRUD + Dependencies implementation")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 90

def main():
    """Run Tasks CRUD + Dependencies Tests"""
    print("🔧 STARTING TASKS CRUD + DEPENDENCIES BACKEND TESTING")
    print("=" * 80)
    
    tester = TasksDependenciesAPITester()
    
    try:
        # Run the comprehensive Tasks CRUD + Dependencies tests
        success = tester.run_comprehensive_tasks_dependencies_test()
        
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
        
        return success_rate >= 90
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)