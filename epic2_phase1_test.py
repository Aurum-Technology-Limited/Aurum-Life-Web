#!/usr/bin/env python3
"""
Epic 2 Phase 1 Testing: Sub-task System and Due Time Enhancement
Tests the new Epic 2 Phase 1 implementations specifically
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any
import uuid

# Configuration
BACKEND_URL = "https://bc5c41e8-49fa-4e1c-8536-e71401e166ef.preview.emergentagent.com/api"

class Epic2Phase1Tester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.created_resources = {
            'areas': [],
            'projects': [],
            'tasks': [],
            'users': []
        }
        self.auth_token = None
        # Use a unique email for testing to avoid conflicts
        unique_id = uuid.uuid4().hex[:8]
        self.test_user_email = f"epic2test_{unique_id}@example.com"
        self.test_user_password = "Epic2TestPassword123!"
        
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
        headers = {}
        
        # Add authentication header if token is available and requested
        if use_auth and self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, headers=headers)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, params=params, headers=headers)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, params=params, headers=headers)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, params=params, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            return {
                'success': response.status_code < 400,
                'status_code': response.status_code,
                'data': response.json() if response.content else {},
                'response': response
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': getattr(e.response, 'status_code', None),
                'data': {},
                'response': getattr(e, 'response', None)
            }

    def setup_authentication(self):
        """Setup authentication for testing"""
        print("\n=== AUTHENTICATION SETUP ===")
        
        # Try to login with existing user
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        if result['success']:
            self.auth_token = result['data'].get('access_token')
            self.log_test(
                "Authentication Setup",
                True,
                f"Successfully authenticated with existing user: {self.test_user_email}"
            )
            return True
        else:
            # Try to create the user first
            print("   Login failed, attempting to create user...")
            user_data = {
                "username": "navtest",
                "email": self.test_user_email,
                "first_name": "Navigation",
                "last_name": "Test",
                "password": self.test_user_password
            }
            
            register_result = self.make_request('POST', '/auth/register', data=user_data)
            if register_result['success']:
                print(f"   Created user: {self.test_user_email}")
                
                # Now try to login
                result = self.make_request('POST', '/auth/login', data=login_data)
                if result['success']:
                    self.auth_token = result['data'].get('access_token')
                    self.log_test(
                        "Authentication Setup",
                        True,
                        f"Successfully created and authenticated user: {self.test_user_email}"
                    )
                    return True
                else:
                    self.log_test(
                        "Authentication Setup",
                        False,
                        f"Failed to login after user creation: {result.get('error', 'Unknown error')} - Status: {result.get('status_code')}"
                    )
                    return False
            else:
                self.log_test(
                    "Authentication Setup",
                    False,
                    f"Failed to create user: {register_result.get('error', 'Unknown error')} - Status: {register_result.get('status_code')} - Data: {register_result.get('data')}"
                )
                return False

    def setup_test_data(self):
        """Setup test data (area and project) for Epic 2 Phase 1 testing"""
        print("\n=== TEST DATA SETUP ===")
        
        # Create test area
        area_data = {
            "name": "Epic 2 Phase 1 Test Area",
            "description": "Test area for Epic 2 Phase 1 testing",
            "icon": "🧪",
            "color": "#FF6B6B"
        }
        
        result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
        if not result['success']:
            self.log_test("Test Data Setup - Area", False, f"Failed to create test area: {result.get('error', 'Unknown error')}")
            return False
        
        area_id = result['data']['id']
        self.created_resources['areas'].append(area_id)
        self.log_test("Test Data Setup - Area", True, f"Created test area: {result['data'].get('name')}")
        
        # Create test project
        project_data = {
            "area_id": area_id,
            "name": "Epic 2 Phase 1 Test Project",
            "description": "Test project for Epic 2 Phase 1 testing",
            "status": "In Progress",
            "priority": "high"
        }
        
        result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
        if not result['success']:
            self.log_test("Test Data Setup - Project", False, f"Failed to create test project: {result.get('error', 'Unknown error')}")
            return False
        
        project_id = result['data']['id']
        self.created_resources['projects'].append(project_id)
        self.log_test("Test Data Setup - Project", True, f"Created test project: {result['data'].get('name')}")
        
        self.test_project_id = project_id
        return True

    def test_enhanced_task_creation_with_new_fields(self):
        """Test Enhanced Task Creation with New Fields: due_time and sub_task_completion_required"""
        print("\n=== ENHANCED TASK CREATION WITH NEW FIELDS ===")
        
        # Test 1: Create task with due_time field (HH:MM format)
        task_with_due_time = {
            "project_id": self.test_project_id,
            "name": "Task with Due Time",
            "description": "Testing due_time field in HH:MM format",
            "priority": "high",
            "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "due_time": "14:30",  # 2:30 PM
            "category": "testing"
        }
        
        result = self.make_request('POST', '/tasks', data=task_with_due_time, use_auth=True)
        self.log_test(
            "POST Task with Due Time Field",
            result['success'],
            f"Created task with due_time '14:30': {result['data'].get('name', 'Unknown')}" if result['success'] else f"Failed: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            task_id = result['data']['id']
            self.created_resources['tasks'].append(task_id)
            
            # Verify due_time field accepts HH:MM format
            self.log_test(
                "Due Time HH:MM Format Acceptance",
                result['data'].get('due_time') == "14:30",
                f"Due time stored correctly: {result['data'].get('due_time')}"
            )
        
        # Test 2: Create task with sub_task_completion_required field
        task_with_subtask_completion = {
            "project_id": self.test_project_id,
            "name": "Parent Task with Sub-task Completion Required",
            "description": "Testing sub_task_completion_required boolean field",
            "priority": "medium",
            "sub_task_completion_required": True,
            "category": "testing"
        }
        
        result = self.make_request('POST', '/tasks', data=task_with_subtask_completion, use_auth=True)
        self.log_test(
            "POST Task with Sub-task Completion Required",
            result['success'],
            f"Created task with sub_task_completion_required=True: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Failed: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            self.parent_task_id = result['data']['id']
            self.created_resources['tasks'].append(self.parent_task_id)
            
            # Verify sub_task_completion_required boolean field works correctly
            self.log_test(
                "Sub-task Completion Required Boolean Field",
                result['data'].get('sub_task_completion_required') == True,
                f"Boolean field stored correctly: {result['data'].get('sub_task_completion_required')}"
            )

    def test_subtask_management_api(self):
        """Test Sub-task Management API Testing"""
        print("\n=== SUB-TASK MANAGEMENT API TESTING ===")
        
        if not hasattr(self, 'parent_task_id'):
            self.log_test("Sub-task Management Setup", False, "No parent task available for testing")
            return
        
        # Test 1: POST /api/tasks/{parent_task_id}/subtasks - Create subtask
        subtask_1_data = {
            "project_id": self.test_project_id,  # Required by TaskCreate model, will be overridden
            "name": "Sub-task 1",
            "description": "First sub-task for testing",
            "priority": "medium",
            "category": "testing"
        }
        
        result = self.make_request('POST', f'/tasks/{self.parent_task_id}/subtasks', data=subtask_1_data, use_auth=True)
        self.log_test(
            "POST Create Sub-task",
            result['success'],
            f"Created sub-task: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Failed: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            self.subtask_1_id = result['data']['id']
            self.created_resources['tasks'].append(self.subtask_1_id)
            
            # Test subtask creation inherits project_id from parent
            self.log_test(
                "Sub-task Inherits Project ID",
                result['data'].get('project_id') == self.test_project_id,
                f"Sub-task inherited project_id: {result['data'].get('project_id')}"
            )
            
            # Verify subtasks have proper parent_task_id reference
            self.log_test(
                "Sub-task Parent Reference",
                result['data'].get('parent_task_id') == self.parent_task_id,
                f"Sub-task has correct parent_task_id: {result['data'].get('parent_task_id')}"
            )
        
        # Create second subtask
        subtask_2_data = {
            "project_id": self.test_project_id,  # Required by TaskCreate model, will be overridden
            "name": "Sub-task 2",
            "description": "Second sub-task for testing",
            "priority": "low",
            "category": "testing"
        }
        
        result = self.make_request('POST', f'/tasks/{self.parent_task_id}/subtasks', data=subtask_2_data, use_auth=True)
        if result['success']:
            self.subtask_2_id = result['data']['id']
            self.created_resources['tasks'].append(self.subtask_2_id)
        
        # Test 2: GET /api/tasks/{task_id}/with-subtasks - Get task with all subtasks
        result = self.make_request('GET', f'/tasks/{self.parent_task_id}/with-subtasks', use_auth=True)
        self.log_test(
            "GET Task with Sub-tasks",
            result['success'],
            f"Retrieved task with {len(result['data'].get('sub_tasks', [])) if result['success'] else 0} sub-tasks" if result['success'] else f"Failed: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            subtasks = result['data'].get('sub_tasks', [])
            self.log_test(
                "Get Task with Sub-tasks Response Structure",
                len(subtasks) == 2,
                f"Task includes {len(subtasks)} sub-tasks (expected 2)"
            )
        
        # Test 3: GET /api/tasks/{task_id}/subtasks - Get subtasks list
        result = self.make_request('GET', f'/tasks/{self.parent_task_id}/subtasks', use_auth=True)
        self.log_test(
            "GET Sub-tasks List",
            result['success'],
            f"Retrieved sub-tasks list: {len(result['data']) if result['success'] else 0} sub-tasks" if result['success'] else f"Failed: {result.get('error', 'Unknown error')}"
        )

    def test_subtask_completion_logic(self):
        """Test Sub-task Completion Logic Testing"""
        print("\n=== SUB-TASK COMPLETION LOGIC TESTING ===")
        
        if not hasattr(self, 'parent_task_id') or not hasattr(self, 'subtask_1_id') or not hasattr(self, 'subtask_2_id'):
            self.log_test("Sub-task Completion Logic Setup", False, "Required tasks not available for testing")
            return
        
        # Test 1: Parent task cannot be completed until all subtasks complete
        parent_completion_data = {"completed": True}
        
        result = self.make_request('PUT', f'/tasks/{self.parent_task_id}', data=parent_completion_data, use_auth=True)
        
        # Check parent task status
        parent_check = self.make_request('GET', f'/tasks/{self.parent_task_id}/with-subtasks', use_auth=True)
        if parent_check['success']:
            parent_completed = parent_check['data'].get('completed', False)
            self.log_test(
                "Parent Task Completion Prevention",
                not parent_completed,
                f"Parent task completion prevented while sub-tasks incomplete: completed={parent_completed}"
            )
        
        # Test 2: Complete subtasks one by one
        # Complete first subtask
        result = self.make_request('PUT', f'/tasks/{self.subtask_1_id}', data={"completed": True}, use_auth=True)
        if result['success']:
            self.log_test("Complete Sub-task 1", True, "Sub-task 1 completed successfully")
            
            # Check parent status (should still be incomplete)
            parent_check = self.make_request('GET', f'/tasks/{self.parent_task_id}/with-subtasks', use_auth=True)
            if parent_check['success']:
                parent_completed = parent_check['data'].get('completed', False)
                self.log_test(
                    "Parent Status After First Sub-task",
                    not parent_completed,
                    f"Parent task still incomplete after 1 sub-task completed: completed={parent_completed}"
                )
        
        # Complete second subtask
        result = self.make_request('PUT', f'/tasks/{self.subtask_2_id}', data={"completed": True}, use_auth=True)
        if result['success']:
            self.log_test("Complete Sub-task 2", True, "Sub-task 2 completed successfully")
            
            # Test 3: Parent task auto-completes when all subtasks are done
            parent_check = self.make_request('GET', f'/tasks/{self.parent_task_id}/with-subtasks', use_auth=True)
            if parent_check['success']:
                parent_completed = parent_check['data'].get('completed', False)
                self.log_test(
                    "Parent Task Auto-completion",
                    parent_completed,
                    f"Parent task auto-completed when all sub-tasks done: completed={parent_completed}"
                )
        
        # Test 4: Parent task reverts to incomplete when subtask becomes incomplete
        result = self.make_request('PUT', f'/tasks/{self.subtask_1_id}', data={"completed": False}, use_auth=True)
        if result['success']:
            self.log_test("Sub-task Revert to Incomplete", True, "Sub-task successfully reverted to incomplete")
            
            # Check if parent reverted
            parent_check = self.make_request('GET', f'/tasks/{self.parent_task_id}/with-subtasks', use_auth=True)
            if parent_check['success']:
                parent_completed = parent_check['data'].get('completed', False)
                self.log_test(
                    "Parent Task Revert on Sub-task Incomplete",
                    not parent_completed,
                    f"Parent task reverted to incomplete when sub-task became incomplete: completed={parent_completed}"
                )

    def test_enhanced_taskservice_methods(self):
        """Test Enhanced TaskService Methods"""
        print("\n=== ENHANCED TASKSERVICE METHODS TESTING ===")
        
        if not hasattr(self, 'parent_task_id'):
            self.log_test("Enhanced TaskService Methods Setup", False, "No parent task available for testing")
            return
        
        # Test create_subtask() method with validation
        subtask_validation_data = {
            "project_id": self.test_project_id,  # Required by TaskCreate model, will be overridden
            "name": "Validation Sub-task",
            "description": "Sub-task for testing create_subtask validation",
            "priority": "low",
            "category": "testing"
        }
        
        result = self.make_request('POST', f'/tasks/{self.parent_task_id}/subtasks', data=subtask_validation_data, use_auth=True)
        self.log_test(
            "create_subtask() Method with Validation",
            result['success'],
            f"create_subtask() method working: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Failed: {result.get('error', 'Unknown error')}"
        )
        
        # Test get_task_with_subtasks() response structure
        result = self.make_request('GET', f'/tasks/{self.parent_task_id}/with-subtasks', use_auth=True)
        self.log_test(
            "get_task_with_subtasks() Response Structure",
            result['success'],
            f"get_task_with_subtasks() method working: retrieved task with {len(result['data'].get('sub_tasks', [])) if result['success'] else 0} sub-tasks" if result['success'] else f"Failed: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            task_data = result['data']
            expected_fields = ['id', 'name', 'description', 'sub_tasks', 'sub_task_completion_required']
            missing_fields = [field for field in expected_fields if field not in task_data]
            
            self.log_test(
                "Response Structure Validation",
                len(missing_fields) == 0,
                f"All expected fields present" if len(missing_fields) == 0 else f"Missing fields: {missing_fields}"
            )

    def cleanup_test_data(self):
        """Clean up test data"""
        print("\n=== CLEANUP ===")
        
        # Delete tasks
        for task_id in self.created_resources['tasks']:
            result = self.make_request('DELETE', f'/tasks/{task_id}', use_auth=True)
            if result['success']:
                print(f"   Cleaned up task: {task_id}")
        
        # Delete projects
        for project_id in self.created_resources['projects']:
            result = self.make_request('DELETE', f'/projects/{project_id}', use_auth=True)
            if result['success']:
                print(f"   Cleaned up project: {project_id}")
        
        # Delete areas
        for area_id in self.created_resources['areas']:
            result = self.make_request('DELETE', f'/areas/{area_id}', use_auth=True)
            if result['success']:
                print(f"   Cleaned up area: {area_id}")

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("🏁 EPIC 2 PHASE 1 TESTING SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for test in self.test_results:
                if not test['success']:
                    print(f"   • {test['test']}: {test['message']}")
        
        print("\n✅ EPIC 2 PHASE 1 FEATURE STATUS:")
        
        # Check Epic 2 Phase 1 specific functionality
        epic2_tests = {
            'Enhanced Task Creation (due_time)': any('Due Time' in t['test'] and t['success'] for t in self.test_results),
            'Enhanced Task Creation (sub_task_completion_required)': any('Sub-task Completion Required' in t['test'] and t['success'] for t in self.test_results),
            'Sub-task Creation API': any('POST Create Sub-task' in t['test'] and t['success'] for t in self.test_results),
            'Get Task with Sub-tasks API': any('GET Task with Sub-tasks' in t['test'] and t['success'] for t in self.test_results),
            'Get Sub-tasks List API': any('GET Sub-tasks List' in t['test'] and t['success'] for t in self.test_results),
            'Sub-task Completion Logic': any('Parent Task Auto-completion' in t['test'] and t['success'] for t in self.test_results),
            'Parent Task Completion Prevention': any('Parent Task Completion Prevention' in t['test'] and t['success'] for t in self.test_results),
            'Parent Task Revert Logic': any('Parent Task Revert' in t['test'] and t['success'] for t in self.test_results),
            'Enhanced TaskService Methods': any('create_subtask()' in t['test'] and t['success'] for t in self.test_results)
        }
        
        for feature, status in epic2_tests.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {feature}")
        
        return failed_tests == 0

    def run_all_tests(self):
        """Run all Epic 2 Phase 1 tests"""
        print("🚀 STARTING EPIC 2 PHASE 1 TESTING")
        print("=" * 80)
        print("Testing: Sub-task System and Due Time Enhancement")
        print(f"Backend URL: {self.base_url}")
        print(f"Authentication: {self.test_user_email}")
        
        try:
            # Setup
            if not self.setup_authentication():
                print("❌ Authentication failed, cannot proceed with testing")
                return False
            
            if not self.setup_test_data():
                print("❌ Test data setup failed, cannot proceed with testing")
                return False
            
            # Epic 2 Phase 1 Tests
            self.test_enhanced_task_creation_with_new_fields()
            self.test_subtask_management_api()
            self.test_subtask_completion_logic()
            self.test_enhanced_taskservice_methods()
            
        except Exception as e:
            print(f"❌ CRITICAL ERROR: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.cleanup_test_data()
        
        # Print summary
        return self.print_summary()

if __name__ == "__main__":
    tester = Epic2Phase1Tester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)