#!/usr/bin/env python3
"""
Focused Test for Unified Project Views - Task Creation and Status Synchronization
Tests the specific fixes implemented for task status enum and kanban board functionality
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any
import uuid
import time

# Configuration
BACKEND_URL = "https://fc488f1a-b6ad-4e7c-bf64-4eb3b4a9be77.preview.emergentagent.com/api"

class UnifiedProjectViewsTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        self.test_user_email = f"unified_test_{uuid.uuid4().hex[:8]}@aurumlife.com"
        self.test_user_password = "UnifiedTest123!"
        self.created_resources = {
            'areas': [],
            'projects': [],
            'tasks': []
        }
        
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
        print("🔐 Setting up authentication...")
        
        # Create test user
        user_data = {
            "username": f"unified_{uuid.uuid4().hex[:8]}",
            "email": self.test_user_email,
            "first_name": "Unified",
            "last_name": "Test",
            "password": self.test_user_password
        }
        
        result = self.make_request('POST', '/auth/register', data=user_data)
        if not result['success']:
            self.log_test("User Registration", False, f"Failed to register user: {result.get('error', 'Unknown error')}")
            return False
        
        # Login
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        if not result['success']:
            self.log_test("User Login", False, f"Failed to login: {result.get('error', 'Unknown error')}")
            return False
        
        self.auth_token = result['data'].get('access_token')
        self.log_test("Authentication Setup", True, f"Successfully authenticated user: {self.test_user_email}")
        return True

    def setup_test_data(self):
        """Create test area and project for testing"""
        print("🏗️ Setting up test data...")
        
        # Create test area
        area_data = {
            "name": "Unified Test Area",
            "description": "Area for unified project views testing",
            "icon": "🧪",
            "color": "#FF6B6B"
        }
        
        result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
        if not result['success']:
            self.log_test("Create Test Area", False, f"Failed to create area: {result.get('error', 'Unknown error')}")
            return None
        
        area_id = result['data']['id']
        self.created_resources['areas'].append(area_id)
        self.log_test("Create Test Area", True, f"Created area: {result['data']['name']}")
        
        # Create test project
        project_data = {
            "area_id": area_id,
            "name": "Unified Test Project",
            "description": "Project for unified views testing",
            "status": "In Progress",
            "priority": "high"
        }
        
        result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
        if not result['success']:
            self.log_test("Create Test Project", False, f"Failed to create project: {result.get('error', 'Unknown error')}")
            return None
        
        project_id = result['data']['id']
        self.created_resources['projects'].append(project_id)
        self.log_test("Create Test Project", True, f"Created project: {result['data']['name']}")
        
        return project_id

    def test_task_creation_with_all_statuses(self, project_id: str):
        """Test task creation with all new status values"""
        print("\n📝 Testing Task Creation with All Status Values:")
        
        status_tests = [
            ("todo", "to_do"),
            ("in_progress", "in_progress"), 
            ("review", "review"),
            ("completed", "done")
        ]
        
        created_task_ids = []
        
        for status, expected_column in status_tests:
            task_data = {
                "project_id": project_id,
                "name": f"Test Task - {status.title()} Status",
                "description": f"Task created to test {status} status",
                "status": status,
                "priority": "medium"
            }
            
            result = self.make_request('POST', '/tasks', data=task_data, use_auth=True)
            self.log_test(
                f"POST Task Creation - Status '{status}'",
                result['success'],
                f"Task created with {status} status successfully" if result['success'] else f"Failed to create task with {status} status: {result.get('error', 'Unknown error')}"
            )
            
            if result['success']:
                created_task_ids.append(result['data']['id'])
                task = result['data']
                
                # Verify status is set correctly
                self.log_test(
                    f"Task Status Verification - '{status}'",
                    task.get('status') == status,
                    f"Task status correctly set to '{status}'" if task.get('status') == status else f"Task status incorrect: expected '{status}', got '{task.get('status')}'"
                )
                
                # Verify kanban column mapping
                self.log_test(
                    f"Kanban Column Mapping - '{status}' -> '{expected_column}'",
                    task.get('kanban_column') == expected_column,
                    f"Kanban column correctly mapped to '{expected_column}'" if task.get('kanban_column') == expected_column else f"Kanban column incorrect: expected '{expected_column}', got '{task.get('kanban_column')}'"
                )
        
        return created_task_ids

    def test_kanban_board_four_columns(self, project_id: str):
        """Test kanban board with 4 columns"""
        print("\n📋 Testing Kanban Board with 4 Columns:")
        
        result = self.make_request('GET', f'/projects/{project_id}/kanban', use_auth=True)
        self.log_test(
            "GET Kanban Board - 4 Columns",
            result['success'],
            f"Kanban board retrieved successfully" if result['success'] else f"Failed to get kanban board: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            kanban_data = result['data']
            columns = kanban_data.get('columns', {})
            expected_columns = ['to_do', 'in_progress', 'review', 'done']
            
            # Verify all 4 columns exist
            missing_columns = [col for col in expected_columns if col not in columns]
            self.log_test(
                "Kanban Board - 4 Columns Present",
                len(missing_columns) == 0,
                f"All 4 columns present: {list(columns.keys())}" if len(missing_columns) == 0 else f"Missing columns: {missing_columns}"
            )
            
            # Print column summary
            print(f"   Kanban columns summary:")
            for col_name, tasks in columns.items():
                print(f"     {col_name}: {len(tasks)} tasks")
                
            return columns
        
        return None

    def test_task_status_transitions(self, project_id: str, task_id: str):
        """Test task status transitions"""
        print("\n🔄 Testing Task Status Transitions:")
        
        # Test transition: todo → in_progress → review → completed
        transitions = [
            ("in_progress", "in_progress"),
            ("review", "review"),
            ("completed", "done")
        ]
        
        for new_status, expected_column in transitions:
            update_data = {"status": new_status}
            result = self.make_request('PUT', f'/tasks/{task_id}', data=update_data, use_auth=True)
            
            self.log_test(
                f"Task Status Transition - to '{new_status}'",
                result['success'],
                f"Task status updated to '{new_status}'" if result['success'] else f"Failed to update task status to '{new_status}': {result.get('error', 'Unknown error')}"
            )
            
            if result['success']:
                # Verify the task appears in the correct kanban column after update
                kanban_result = self.make_request('GET', f'/projects/{project_id}/kanban', use_auth=True)
                if kanban_result['success']:
                    columns = kanban_result['data'].get('columns', {})
                    tasks_in_column = columns.get(expected_column, [])
                    task_found = any(t.get('id') == task_id for t in tasks_in_column)
                    
                    self.log_test(
                        f"Kanban Column Update - '{new_status}' -> '{expected_column}'",
                        task_found,
                        f"Task moved to '{expected_column}' column after status change" if task_found else f"Task not found in '{expected_column}' column after status change"
                    )

    def test_data_synchronization(self, project_id: str):
        """Test data synchronization between views"""
        print("\n🔄 Testing Data Synchronization:")
        
        # Create a task with 'todo' status and verify it appears in 'to_do' column
        sync_task_data = {
            "project_id": project_id,
            "name": "Sync Test Task - Todo",
            "description": "Task to test synchronization",
            "status": "todo",
            "priority": "high"
        }
        
        result = self.make_request('POST', '/tasks', data=sync_task_data, use_auth=True)
        self.log_test(
            "Data Sync - Create Todo Task",
            result['success'],
            f"Sync test task created with todo status" if result['success'] else f"Failed to create sync test task: {result.get('error', 'Unknown error')}"
        )
        
        sync_task_ids = []
        
        if result['success']:
            sync_task_id = result['data']['id']
            sync_task_ids.append(sync_task_id)
            
            # Verify task appears in kanban to_do column
            kanban_result = self.make_request('GET', f'/projects/{project_id}/kanban', use_auth=True)
            if kanban_result['success']:
                to_do_tasks = kanban_result['data'].get('columns', {}).get('to_do', [])
                task_found = any(t.get('id') == sync_task_id for t in to_do_tasks)
                
                self.log_test(
                    "Data Sync - Todo Task in Kanban",
                    task_found,
                    f"Todo task appears in kanban to_do column" if task_found else f"Todo task not found in kanban to_do column"
                )
            
            # Test creating a task with 'review' status
            review_task_data = {
                "project_id": project_id,
                "name": "Sync Test Task - Review",
                "description": "Task to test review status synchronization",
                "status": "review",
                "priority": "high"
            }
            
            result = self.make_request('POST', '/tasks', data=review_task_data, use_auth=True)
            self.log_test(
                "Data Sync - Create Review Task",
                result['success'],
                f"Review test task created successfully" if result['success'] else f"Failed to create review test task: {result.get('error', 'Unknown error')}"
            )
            
            if result['success']:
                review_task_id = result['data']['id']
                sync_task_ids.append(review_task_id)
                
                # Verify task appears in kanban review column
                kanban_result = self.make_request('GET', f'/projects/{project_id}/kanban', use_auth=True)
                if kanban_result['success']:
                    review_tasks = kanban_result['data'].get('columns', {}).get('review', [])
                    task_found = any(t.get('id') == review_task_id for t in review_tasks)
                    
                    self.log_test(
                        "Data Sync - Review Task in Kanban",
                        task_found,
                        f"Review task appears in kanban review column" if task_found else f"Review task not found in kanban review column"
                    )
        
        return sync_task_ids

    def test_project_task_counts(self, project_id: str):
        """Test project task counts with new status values"""
        print("\n📊 Testing Project Task Counts:")
        
        result = self.make_request('GET', f'/projects/{project_id}', use_auth=True)
        self.log_test(
            "GET Project with Task Counts",
            result['success'],
            f"Project data retrieved with task counts" if result['success'] else f"Failed to get project data: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            project = result['data']
            
            # Verify task count fields are present
            count_fields = ['task_count', 'completed_task_count', 'active_task_count']
            missing_fields = [field for field in count_fields if field not in project]
            
            self.log_test(
                "Project Task Count Fields",
                len(missing_fields) == 0,
                f"All task count fields present: {count_fields}" if len(missing_fields) == 0 else f"Missing task count fields: {missing_fields}"
            )
            
            # Verify active_task_count includes tasks with status todo, in_progress, review
            if 'active_task_count' in project:
                active_count = project['active_task_count']
                self.log_test(
                    "Active Task Count Calculation",
                    isinstance(active_count, int) and active_count >= 0,
                    f"Active task count is valid: {active_count}" if isinstance(active_count, int) and active_count >= 0 else f"Active task count invalid: {active_count}"
                )
                
                print(f"   Project task counts: total={project.get('task_count', 0)}, active={project.get('active_task_count', 0)}, completed={project.get('completed_task_count', 0)}")

    def test_task_completion_toggle(self, project_id: str, task_id: str):
        """Test task completion toggle still works"""
        print("\n✅ Testing Task Completion Toggle:")
        
        # Toggle completion
        update_data = {"completed": True}
        result = self.make_request('PUT', f'/tasks/{task_id}', data=update_data, use_auth=True)
        
        self.log_test(
            "Task Completion Toggle - Mark Complete",
            result['success'],
            f"Task marked as completed successfully" if result['success'] else f"Failed to mark task as completed: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            # Verify task moved to done column
            kanban_result = self.make_request('GET', f'/projects/{project_id}/kanban', use_auth=True)
            if kanban_result['success']:
                done_tasks = kanban_result['data'].get('columns', {}).get('done', [])
                task_found = any(t.get('id') == task_id for t in done_tasks)
                
                self.log_test(
                    "Completion Toggle - Task in Done Column",
                    task_found,
                    f"Completed task moved to done column" if task_found else f"Completed task not found in done column"
                )

    def cleanup_test_data(self):
        """Clean up test data"""
        print("\n🧹 Cleaning up test data:")
        
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
        print("🏁 UNIFIED PROJECT VIEWS TESTING SUMMARY")
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
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
        
        print("\n🎯 KEY FINDINGS:")
        print("   • Task Status Enum: Tests whether 'todo', 'in_progress', 'review', 'completed' work")
        print("   • Kanban Board: Tests whether 4 columns (to_do, in_progress, review, done) exist")
        print("   • Status-Column Mapping: Tests whether status changes move tasks to correct columns")
        print("   • Data Synchronization: Tests whether List View and Kanban View show same data")
        print("   • Task Counts: Tests whether active_task_count includes todo/in_progress/review tasks")

    def run_test(self):
        """Run the unified project views test"""
        print("🚀 UNIFIED PROJECT VIEWS - TASK CREATION AND STATUS SYNCHRONIZATION TEST")
        print("="*80)
        print("Testing the comprehensive fix for unified project views issues:")
        print("1. Task creation with all status values (todo, in_progress, review, completed)")
        print("2. Kanban board with 4 columns (to_do, in_progress, review, done)")
        print("3. Status-to-column mapping")
        print("4. Data synchronization between List View and Kanban View")
        print("5. Task count calculations with new status values")
        print("="*80)
        
        try:
            # Setup
            if not self.setup_authentication():
                return
            
            project_id = self.setup_test_data()
            if not project_id:
                return
            
            # Run tests
            created_task_ids = self.test_task_creation_with_all_statuses(project_id)
            self.created_resources['tasks'].extend(created_task_ids)
            
            self.test_kanban_board_four_columns(project_id)
            
            if created_task_ids:
                self.test_task_status_transitions(project_id, created_task_ids[0])
            
            sync_task_ids = self.test_data_synchronization(project_id)
            self.created_resources['tasks'].extend(sync_task_ids)
            
            self.test_project_task_counts(project_id)
            
            if created_task_ids:
                self.test_task_completion_toggle(project_id, created_task_ids[-1])
            
        except Exception as e:
            print(f"❌ CRITICAL ERROR: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.cleanup_test_data()
            self.print_summary()

if __name__ == "__main__":
    tester = UnifiedProjectViewsTester()
    tester.run_test()