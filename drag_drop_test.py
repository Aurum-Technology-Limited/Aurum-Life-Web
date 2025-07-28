#!/usr/bin/env python3
"""
Enhanced Drag & Drop Backend Integration Testing - Phase 2
Tests drag & drop functionality, status updates, dependency validation, and kanban synchronization
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any
import uuid
import time

# Configuration
BACKEND_URL = "https://19eedb9d-8356-46da-a868-07e1ec72a1d8.preview.emergentagent.com/api"

class DragDropTester:
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
        self.test_user_email = f"dragdroptest_{uuid.uuid4().hex[:8]}@aurumlife.com"
        self.test_user_password = "DragDropTest123!"
        
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
        print("=== AUTHENTICATION SETUP ===")
        
        # Create test user
        test_user_data = {
            "username": f"dragdroptest_{uuid.uuid4().hex[:8]}",
            "email": self.test_user_email,
            "first_name": "DragDrop",
            "last_name": "Test",
            "password": self.test_user_password
        }
        
        result = self.make_request('POST', '/auth/register', data=test_user_data)
        if result['success']:
            self.created_resources['users'].append(result['data']['id'])
            
            # Login with the test user
            login_data = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            login_result = self.make_request('POST', '/auth/login', data=login_data)
            if login_result['success']:
                self.auth_token = login_result['data'].get('access_token')
                self.log_test(
                    "Authentication Setup",
                    True,
                    f"Successfully authenticated test user: {self.test_user_email}"
                )
                return True
            else:
                self.log_test(
                    "Authentication Setup - Login",
                    False,
                    f"Failed to login: {login_result.get('error', 'Unknown error')}"
                )
        else:
            self.log_test(
                "Authentication Setup - Registration",
                False,
                f"Failed to register user: {result.get('error', 'Unknown error')}"
            )
        
        return False

    def test_enhanced_drag_drop_backend_integration(self):
        """Test Enhanced Drag & Drop Backend Integration - Phase 2"""
        print("\n=== ENHANCED DRAG & DROP BACKEND INTEGRATION - PHASE 2 TESTING ===")
        
        if not self.auth_token:
            self.log_test("Drag & Drop Testing Setup", False, "No auth token available for testing")
            return
        
        # Setup: Create test area and project
        area_data = {
            "name": "Drag & Drop Test Area",
            "description": "Area for testing drag & drop functionality",
            "icon": "🎯",
            "color": "#4CAF50"
        }
        
        area_result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
        if not area_result['success']:
            self.log_test("Drag & Drop Setup - Create Area", False, f"Failed to create test area: {area_result.get('error', 'Unknown error')}")
            return
        
        test_area_id = area_result['data']['id']
        self.created_resources['areas'].append(test_area_id)
        
        project_data = {
            "area_id": test_area_id,
            "name": "Drag & Drop Test Project",
            "description": "Project for testing drag & drop functionality",
            "status": "In Progress",
            "priority": "high"
        }
        
        project_result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
        if not project_result['success']:
            self.log_test("Drag & Drop Setup - Create Project", False, f"Failed to create test project: {project_result.get('error', 'Unknown error')}")
            return
        
        test_project_id = project_result['data']['id']
        self.created_resources['projects'].append(test_project_id)
        
        self.log_test(
            "Drag & Drop Setup",
            True,
            f"Created test area and project successfully"
        )
        
        # Create test tasks for drag & drop testing
        tasks_data = [
            {
                "project_id": test_project_id,
                "name": "Task 1 - Todo Status",
                "description": "Task for testing drag from todo",
                "status": "todo",
                "priority": "high"
            },
            {
                "project_id": test_project_id,
                "name": "Task 2 - In Progress Status",
                "description": "Task for testing drag from in_progress",
                "status": "in_progress",
                "priority": "medium"
            },
            {
                "project_id": test_project_id,
                "name": "Task 3 - Review Status",
                "description": "Task for testing drag from review",
                "status": "review",
                "priority": "low"
            },
            {
                "project_id": test_project_id,
                "name": "Task 4 - Completed Status",
                "description": "Task for testing drag from completed",
                "status": "completed",
                "priority": "medium"
            }
        ]
        
        created_task_ids = []
        for i, task_data in enumerate(tasks_data):
            result = self.make_request('POST', '/tasks', data=task_data, use_auth=True)
            if result['success']:
                task_id = result['data']['id']
                created_task_ids.append(task_id)
                self.created_resources['tasks'].append(task_id)
                self.log_test(
                    f"Create Test Task {i+1}",
                    True,
                    f"Created task: {task_data['name']} with status: {task_data['status']}"
                )
            else:
                self.log_test(f"Create Test Task {i+1}", False, f"Failed to create task: {result.get('error', 'Unknown error')}")
                return
        
        # TEST 1: TASK STATUS UPDATES VIA DRAG & DROP
        print("\n   --- TASK STATUS UPDATES VIA DRAG & DROP TESTING ---")
        
        # Test status transitions: todo → in_progress → review → completed
        if len(created_task_ids) >= 1:
            task_id = created_task_ids[0]  # Task 1 - Todo Status
            
            # Test todo → in_progress
            update_data = {"status": "in_progress"}
            result = self.make_request('PUT', f'/tasks/{task_id}', data=update_data, use_auth=True)
            self.log_test(
                "Drag & Drop - Todo to In Progress",
                result['success'],
                f"Task status updated from todo to in_progress" if result['success'] else f"Failed to update status: {result.get('error', 'Unknown error')}"
            )
            
            # Test in_progress → review
            update_data = {"status": "review"}
            result = self.make_request('PUT', f'/tasks/{task_id}', data=update_data, use_auth=True)
            self.log_test(
                "Drag & Drop - In Progress to Review",
                result['success'],
                f"Task status updated from in_progress to review" if result['success'] else f"Failed to update status: {result.get('error', 'Unknown error')}"
            )
            
            # Test review → completed
            update_data = {"status": "completed"}
            result = self.make_request('PUT', f'/tasks/{task_id}', data=update_data, use_auth=True)
            self.log_test(
                "Drag & Drop - Review to Completed",
                result['success'],
                f"Task status updated from review to completed" if result['success'] else f"Failed to update status: {result.get('error', 'Unknown error')}"
            )
            
            # Test reverse transitions: completed → review → in_progress → todo
            update_data = {"status": "review"}
            result = self.make_request('PUT', f'/tasks/{task_id}', data=update_data, use_auth=True)
            self.log_test(
                "Drag & Drop - Completed to Review (Reverse)",
                result['success'],
                f"Task status updated from completed to review" if result['success'] else f"Failed to update status: {result.get('error', 'Unknown error')}"
            )
            
            update_data = {"status": "in_progress"}
            result = self.make_request('PUT', f'/tasks/{task_id}', data=update_data, use_auth=True)
            self.log_test(
                "Drag & Drop - Review to In Progress (Reverse)",
                result['success'],
                f"Task status updated from review to in_progress" if result['success'] else f"Failed to update status: {result.get('error', 'Unknown error')}"
            )
            
            update_data = {"status": "todo"}
            result = self.make_request('PUT', f'/tasks/{task_id}', data=update_data, use_auth=True)
            self.log_test(
                "Drag & Drop - In Progress to Todo (Reverse)",
                result['success'],
                f"Task status updated from in_progress to todo" if result['success'] else f"Failed to update status: {result.get('error', 'Unknown error')}"
            )
        
        # TEST 2: KANBAN COLUMN SYNCHRONIZATION
        print("\n   --- KANBAN COLUMN SYNCHRONIZATION TESTING ---")
        
        # Get kanban board to verify column mapping
        kanban_result = self.make_request('GET', f'/projects/{test_project_id}/kanban', use_auth=True)
        self.log_test(
            "Get Kanban Board for Sync Test",
            kanban_result['success'],
            f"Retrieved kanban board successfully" if kanban_result['success'] else f"Failed to get kanban board: {kanban_result.get('error', 'Unknown error')}"
        )
        
        if kanban_result['success']:
            kanban_data = kanban_result['data']
            columns = kanban_data.get('columns', {})
            
            # Verify all 4 columns exist
            expected_columns = ['to_do', 'in_progress', 'review', 'done']
            missing_columns = [col for col in expected_columns if col not in columns]
            
            self.log_test(
                "Kanban Column Structure",
                len(missing_columns) == 0,
                f"All 4 columns present: {list(columns.keys())}" if len(missing_columns) == 0 else f"Missing columns: {missing_columns}"
            )
            
            # Test status-to-column mapping
            status_to_column_mapping = {
                'todo': 'to_do',
                'in_progress': 'in_progress', 
                'review': 'review',
                'completed': 'done'
            }
            
            for status, expected_column in status_to_column_mapping.items():
                # Create a task with specific status
                test_task_data = {
                    "project_id": test_project_id,
                    "name": f"Mapping Test Task - {status}",
                    "description": f"Task for testing {status} to {expected_column} mapping",
                    "status": status,
                    "priority": "medium"
                }
                
                create_result = self.make_request('POST', '/tasks', data=test_task_data, use_auth=True)
                if create_result['success']:
                    mapping_task_id = create_result['data']['id']
                    self.created_resources['tasks'].append(mapping_task_id)
                    
                    # Get updated kanban board
                    updated_kanban = self.make_request('GET', f'/projects/{test_project_id}/kanban', use_auth=True)
                    if updated_kanban['success']:
                        updated_columns = updated_kanban['data'].get('columns', {})
                        column_tasks = updated_columns.get(expected_column, [])
                        
                        # Check if task appears in correct column
                        task_in_column = any(task.get('id') == mapping_task_id for task in column_tasks)
                        
                        self.log_test(
                            f"Status-to-Column Mapping - {status} → {expected_column}",
                            task_in_column,
                            f"Task correctly appears in {expected_column} column" if task_in_column else f"Task not found in {expected_column} column"
                        )
        
        # TEST 3: DRAG & DROP ERROR SCENARIOS (BLOCKED TASKS WITH DEPENDENCIES)
        print("\n   --- DRAG & DROP ERROR SCENARIOS TESTING ---")
        
        # Create tasks with dependencies for error testing
        prerequisite_task_data = {
            "project_id": test_project_id,
            "name": "Prerequisite Task for Drag Test",
            "description": "Task that must be completed first",
            "status": "todo",
            "priority": "high"
        }
        
        prereq_result = self.make_request('POST', '/tasks', data=prerequisite_task_data, use_auth=True)
        if prereq_result['success']:
            prereq_task_id = prereq_result['data']['id']
            self.created_resources['tasks'].append(prereq_task_id)
            
            # Create dependent task
            dependent_task_data = {
                "project_id": test_project_id,
                "name": "Dependent Task for Drag Test",
                "description": "Task that depends on prerequisite",
                "status": "todo",
                "priority": "medium",
                "dependency_task_ids": [prereq_task_id]
            }
            
            dependent_result = self.make_request('POST', '/tasks', data=dependent_task_data, use_auth=True)
            if dependent_result['success']:
                dependent_task_id = dependent_result['data']['id']
                self.created_resources['tasks'].append(dependent_task_id)
                
                # Test dragging blocked task to restricted statuses
                restricted_statuses = ['in_progress', 'review', 'completed']
                
                for status in restricted_statuses:
                    update_data = {"status": status}
                    result = self.make_request('PUT', f'/tasks/{dependent_task_id}', data=update_data, use_auth=True)
                    
                    self.log_test(
                        f"Drag Blocked Task - Prevent {status} Status",
                        not result['success'] and result['status_code'] == 400,
                        f"Blocked task correctly prevented from moving to {status}" if not result['success'] else f"Blocked task incorrectly allowed to move to {status}"
                    )
                    
                    # Verify error message mentions prerequisites
                    if not result['success'] and 'data' in result and 'detail' in result['data']:
                        error_message = result['data']['detail']
                        contains_prereq_info = "Prerequisite Task for Drag Test" in error_message
                        self.log_test(
                            f"Drag Error Message - {status} Status",
                            contains_prereq_info,
                            f"Error message correctly mentions prerequisite task" if contains_prereq_info else f"Error message incomplete: {error_message}"
                        )
                
                # Test that task can be dragged after prerequisite is completed
                # Complete the prerequisite task
                complete_prereq_data = {"status": "completed"}
                prereq_complete_result = self.make_request('PUT', f'/tasks/{prereq_task_id}', data=complete_prereq_data, use_auth=True)
                
                if prereq_complete_result['success']:
                    # Now try to drag the dependent task
                    update_data = {"status": "in_progress"}
                    result = self.make_request('PUT', f'/tasks/{dependent_task_id}', data=update_data, use_auth=True)
                    
                    self.log_test(
                        "Drag Unblocked Task - Allow Status Change",
                        result['success'],
                        f"Task correctly allowed to move to in_progress after prerequisite completed" if result['success'] else f"Task incorrectly blocked after prerequisite completed"
                    )
        
        # TEST 4: PERFORMANCE AND RELIABILITY
        print("\n   --- PERFORMANCE AND RELIABILITY TESTING ---")
        
        if len(created_task_ids) >= 2:
            # Test multiple rapid drag operations
            start_time = time.time()
            rapid_operations = []
            
            for i in range(3):  # Perform 3 rapid status changes
                task_id = created_task_ids[i % len(created_task_ids)]
                statuses = ['todo', 'in_progress', 'review', 'completed']
                new_status = statuses[i % len(statuses)]
                
                update_data = {"status": new_status}
                result = self.make_request('PUT', f'/tasks/{task_id}', data=update_data, use_auth=True)
                rapid_operations.append(result['success'])
            
            end_time = time.time()
            operation_time = end_time - start_time
            
            self.log_test(
                "Rapid Drag Operations - Performance",
                all(rapid_operations) and operation_time < 5.0,
                f"Completed {len(rapid_operations)} rapid operations in {operation_time:.2f}s (all successful: {all(rapid_operations)})"
            )
            
            # Test database consistency after rapid operations
            consistency_check = self.make_request('GET', f'/projects/{test_project_id}/kanban', use_auth=True)
            self.log_test(
                "Database Consistency - After Rapid Operations",
                consistency_check['success'],
                f"Kanban board data consistent after rapid operations" if consistency_check['success'] else "Database consistency issues detected"
            )
        
        # TEST 5: ERROR RECOVERY TESTING
        print("\n   --- ERROR RECOVERY TESTING ---")
        
        # Test invalid status values
        if len(created_task_ids) >= 1:
            task_id = created_task_ids[0]
            
            invalid_statuses = ['invalid_status', 'not_started', 'pending', '']
            
            for invalid_status in invalid_statuses:
                update_data = {"status": invalid_status}
                result = self.make_request('PUT', f'/tasks/{task_id}', data=update_data, use_auth=True)
                
                self.log_test(
                    f"Error Recovery - Invalid Status '{invalid_status}'",
                    not result['success'],
                    f"Invalid status '{invalid_status}' correctly rejected" if not result['success'] else f"Invalid status '{invalid_status}' incorrectly accepted"
                )
            
            # Test task still functional after error attempts
            valid_update_data = {"status": "in_progress"}
            recovery_result = self.make_request('PUT', f'/tasks/{task_id}', data=valid_update_data, use_auth=True)
            
            self.log_test(
                "Error Recovery - Task Still Functional",
                recovery_result['success'],
                f"Task still functional after error attempts" if recovery_result['success'] else "Task corrupted after error attempts"
            )

    def cleanup_test_data(self):
        """Clean up test data"""
        print("\n=== CLEANUP ===")
        
        # Clean up in reverse order: tasks, projects, areas
        for task_id in self.created_resources['tasks']:
            self.make_request('DELETE', f'/tasks/{task_id}', use_auth=True)
        
        for project_id in self.created_resources['projects']:
            self.make_request('DELETE', f'/projects/{project_id}', use_auth=True)
        
        for area_id in self.created_resources['areas']:
            self.make_request('DELETE', f'/areas/{area_id}', use_auth=True)
        
        print(f"   Cleaned up {len(self.created_resources['tasks'])} tasks")
        print(f"   Cleaned up {len(self.created_resources['projects'])} projects")
        print(f"   Cleaned up {len(self.created_resources['areas'])} areas")

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("🏁 ENHANCED DRAG & DROP BACKEND INTEGRATION TESTING SUMMARY")
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
        
        print("\n✅ DRAG & DROP FUNCTIONALITY STATUS:")
        
        # Check drag & drop specific functionality
        drag_drop_tests = {
            'Task Status Updates': any('Drag & Drop -' in t['test'] and t['success'] for t in self.test_results),
            'Kanban Column Sync': any('Status-to-Column Mapping' in t['test'] and t['success'] for t in self.test_results),
            'Dependency Validation': any('Drag Blocked Task' in t['test'] and t['success'] for t in self.test_results),
            'Error Handling': any('Error Recovery' in t['test'] and t['success'] for t in self.test_results),
            'Performance': any('Rapid Drag Operations' in t['test'] and t['success'] for t in self.test_results)
        }
        
        for feature, status in drag_drop_tests.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {feature}")
        
        return failed_tests == 0

    def run_all_tests(self):
        """Run all drag & drop tests"""
        print("🚀 STARTING ENHANCED DRAG & DROP BACKEND INTEGRATION TESTING - PHASE 2")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        
        try:
            # Setup authentication
            if not self.setup_authentication():
                print("❌ CRITICAL ERROR: Authentication setup failed")
                return False
            
            # Run drag & drop tests
            self.test_enhanced_drag_drop_backend_integration()
            
        except Exception as e:
            print(f"\n❌ CRITICAL ERROR during testing: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Cleanup
            self.cleanup_test_data()
            
            # Print summary
            success = self.print_summary()
            return success

if __name__ == "__main__":
    tester = DragDropTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)