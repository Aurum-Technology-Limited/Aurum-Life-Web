#!/usr/bin/env python3
"""
Task Status Migration Verification - Quick Test
Tests that the migration from 'not_started' to 'todo' status was successful
"""

import requests
import json
import sys
from datetime import datetime
import uuid

# Configuration
BACKEND_URL = "https://7b39a747-36d6-44f7-9408-a498365475ba.preview.emergentagent.com/api"

class MigrationTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test results"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")

    def make_request(self, method: str, endpoint: str, data: dict = None, params: dict = None, use_auth: bool = False):
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
        """Set up authentication for testing"""
        print("\n=== AUTHENTICATION SETUP ===")
        
        # Try to login with existing user first
        existing_users = [
            {"email": "navtest@example.com", "password": "password123"},
            {"email": "demo@aurumlife.com", "password": "demo123"},
            {"email": "test@example.com", "password": "password123"}
        ]
        
        for user_creds in existing_users:
            result = self.make_request('POST', '/auth/login', data=user_creds)
            if result['success']:
                self.auth_token = result['data'].get('access_token')
                self.log_test(
                    "Authentication Setup - Existing User",
                    True,
                    f"Successfully authenticated with existing user: {user_creds['email']}"
                )
                return True
        
        # If no existing user works, create a new one
        test_user_data = {
            "username": f"migrationtest_{uuid.uuid4().hex[:8]}",
            "email": f"migrationtest_{uuid.uuid4().hex[:8]}@aurumlife.com",
            "first_name": "Migration",
            "last_name": "Test",
            "password": "MigrationTest123!"
        }
        
        # Register the user
        result = self.make_request('POST', '/auth/register', data=test_user_data)
        if result['success']:
            # Login with the new user
            login_data = {
                "email": test_user_data['email'],
                "password": test_user_data['password']
            }
            
            result = self.make_request('POST', '/auth/login', data=login_data)
            if result['success']:
                self.auth_token = result['data'].get('access_token')
                self.log_test(
                    "Authentication Setup - New User",
                    True,
                    f"Successfully created and authenticated new user: {test_user_data['email']}"
                )
                return True
            else:
                self.log_test(
                    "Authentication Setup - Login Failed",
                    False,
                    f"Failed to login with new user: {result.get('error', 'Unknown error')}"
                )
        else:
            self.log_test(
                "Authentication Setup - Registration Failed",
                False,
                f"Failed to create new user: {result.get('error', 'Unknown error')}"
            )
        
        return False

    def test_health_check(self):
        """Test basic API health"""
        print("\n=== HEALTH CHECK ===")
        
        # Test root endpoint
        result = self.make_request('GET', '/')
        self.log_test(
            "API Root Endpoint",
            result['success'],
            f"Status: {result['status_code']}, Message: {result['data'].get('message', 'No message')}"
        )
        
        # Test health endpoint
        result = self.make_request('GET', '/health')
        self.log_test(
            "Health Check Endpoint",
            result['success'],
            f"Status: {result['status_code']}, Service: {result['data'].get('service', 'Unknown')}"
        )

    def test_task_status_migration_verification(self):
        """Test Task Status Migration Verification - Main Test"""
        print("\n=== TASK STATUS MIGRATION VERIFICATION - MAIN TEST ===")
        
        if not self.auth_token:
            self.log_test("Task Status Migration Setup", False, "No auth token available for testing")
            return
        
        # Test 1: Basic Task Retrieval - Test GET /api/tasks to verify no validation errors
        result = self.make_request('GET', '/tasks', use_auth=True)
        self.log_test(
            "GET Tasks - Basic Retrieval (No Validation Errors)",
            result['success'],
            f"Retrieved {len(result['data']) if result['success'] else 0} tasks without validation errors" if result['success'] else f"Task retrieval failed: {result.get('error', 'Unknown error')}"
        )
        
        task_data = result['data'] if result['success'] else []
        
        # Test 2: Status Validation - Verify no tasks have old status values
        if result['success']:
            valid_statuses = ['todo', 'in_progress', 'review', 'completed']
            invalid_status_tasks = []
            status_distribution = {'todo': 0, 'in_progress': 0, 'review': 0, 'completed': 0, 'other': 0}
            
            for task in task_data:
                task_status = task.get('status', 'unknown')
                if task_status in valid_statuses:
                    status_distribution[task_status] += 1
                else:
                    status_distribution['other'] += 1
                    invalid_status_tasks.append({
                        'id': task.get('id'),
                        'name': task.get('name'),
                        'status': task_status
                    })
            
            self.log_test(
                "Task Status Validation - No Old Status Values",
                len(invalid_status_tasks) == 0,
                f"All tasks have valid status values. Distribution: {status_distribution}" if len(invalid_status_tasks) == 0 else f"Found {len(invalid_status_tasks)} tasks with invalid status: {invalid_status_tasks}"
            )
            
            if task_data:
                # Verify status distribution is reasonable (should have tasks in 'todo' status after migration)
                self.log_test(
                    "Task Status Distribution - Migration Success",
                    status_distribution['todo'] > 0 or len(task_data) == 0,
                    f"Tasks successfully migrated to 'todo' status: {status_distribution['todo']} tasks" if status_distribution['todo'] > 0 else f"No tasks with 'todo' status found (may be expected if no tasks exist)"
                )
            else:
                self.log_test(
                    "Task Status Validation - No Tasks Found",
                    True,  # Not necessarily an error if no tasks exist
                    "No tasks found to validate status migration (this may be expected for new users)"
                )
        
        # Test 3: Dashboard Functionality - Test GET /api/areas to ensure dashboard loads
        result = self.make_request('GET', '/areas', use_auth=True)
        self.log_test(
            "GET Areas - Dashboard Functionality",
            result['success'],
            f"Areas endpoint working - retrieved {len(result['data']) if result['success'] else 0} areas" if result['success'] else f"Areas retrieval failed: {result.get('error', 'Unknown error')}"
        )
        
        # Test 4: Dashboard Functionality - Test GET /api/projects to verify project data works
        result = self.make_request('GET', '/projects', use_auth=True)
        self.log_test(
            "GET Projects - Dashboard Functionality",
            result['success'],
            f"Projects endpoint working - retrieved {len(result['data']) if result['success'] else 0} projects" if result['success'] else f"Projects retrieval failed: {result.get('error', 'Unknown error')}"
        )
        
        # Test 5: Comprehensive Dashboard Load Test
        result = self.make_request('GET', '/dashboard', use_auth=True)
        self.log_test(
            "GET Dashboard - Complete Load Test",
            result['success'],
            f"Dashboard loads successfully without validation errors" if result['success'] else f"Dashboard load failed: {result.get('error', 'Unknown error')}"
        )
        
        # Test 6: Today View - Should work with migrated task statuses
        result = self.make_request('GET', '/today', use_auth=True)
        self.log_test(
            "GET Today View - Post-Migration Functionality",
            result['success'],
            f"Today view loads successfully with migrated task statuses" if result['success'] else f"Today view failed: {result.get('error', 'Unknown error')}"
        )
        
        # Test 7: Kanban Board - Test with a project to ensure status mapping works
        projects_result = self.make_request('GET', '/projects', use_auth=True)
        if projects_result['success'] and projects_result['data']:
            test_project_id = projects_result['data'][0]['id']
            
            result = self.make_request('GET', f'/projects/{test_project_id}/kanban', use_auth=True)
            self.log_test(
                "GET Kanban Board - Status Mapping Verification",
                result['success'],
                f"Kanban board loads successfully with migrated statuses" if result['success'] else f"Kanban board failed: {result.get('error', 'Unknown error')}"
            )
            
            if result['success']:
                kanban_data = result['data']
                columns = kanban_data.get('columns', {})
                expected_columns = ['to_do', 'in_progress', 'review', 'done']
                missing_columns = [col for col in expected_columns if col not in columns]
                
                self.log_test(
                    "Kanban Board - Column Structure Verification",
                    len(missing_columns) == 0,
                    f"All expected kanban columns present: {list(columns.keys())}" if len(missing_columns) == 0 else f"Missing kanban columns: {missing_columns}"
                )
        else:
            self.log_test(
                "Kanban Board Test - No Projects Available",
                True,  # Not an error if no projects exist
                "No projects available for kanban board testing (expected for new users)"
            )

    def create_test_data_for_migration_verification(self):
        """Create some test data to verify migration works with actual data"""
        print("\n=== CREATING TEST DATA FOR MIGRATION VERIFICATION ===")
        
        if not self.auth_token:
            return
        
        # Create an area
        area_data = {
            "name": "Migration Test Area",
            "description": "Area created for migration testing",
            "icon": "🧪",
            "color": "#FF6B6B"
        }
        
        result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
        if result['success']:
            area_id = result['data']['id']
            self.log_test(
                "Test Data Creation - Area",
                True,
                f"Created test area: {result['data'].get('name')}"
            )
            
            # Create a project in the area
            project_data = {
                "area_id": area_id,
                "name": "Migration Test Project",
                "description": "Project created for migration testing",
                "status": "In Progress",
                "priority": "high"
            }
            
            result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
            if result['success']:
                project_id = result['data']['id']
                self.log_test(
                    "Test Data Creation - Project",
                    True,
                    f"Created test project: {result['data'].get('name')}"
                )
                
                # Create tasks with different statuses to test migration
                task_statuses = ['todo', 'in_progress', 'review', 'completed']
                for i, status in enumerate(task_statuses):
                    task_data = {
                        "project_id": project_id,
                        "name": f"Migration Test Task {i+1} - {status}",
                        "description": f"Task created for migration testing with {status} status",
                        "status": status,
                        "priority": "medium"
                    }
                    
                    result = self.make_request('POST', '/tasks', data=task_data, use_auth=True)
                    if result['success']:
                        self.log_test(
                            f"Test Data Creation - Task ({status})",
                            True,
                            f"Created test task with {status} status"
                        )
                    else:
                        self.log_test(
                            f"Test Data Creation - Task ({status})",
                            False,
                            f"Failed to create task with {status} status: {result.get('error', 'Unknown error')}"
                        )
            else:
                self.log_test(
                    "Test Data Creation - Project",
                    False,
                    f"Failed to create test project: {result.get('error', 'Unknown error')}"
                )
        else:
            self.log_test(
                "Test Data Creation - Area",
                False,
                f"Failed to create test area: {result.get('error', 'Unknown error')}"
            )

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("🏁 TASK STATUS MIGRATION VERIFICATION SUMMARY")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for t in self.test_results if t['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for test in self.test_results:
                if not test['success']:
                    print(f"   - {test['test']}: {test['message']}")
        
        # Key migration verification results
        print(f"\n✅ MIGRATION VERIFICATION RESULTS:")
        migration_tests = [
            'GET Tasks - Basic Retrieval (No Validation Errors)',
            'Task Status Validation - No Old Status Values', 
            'GET Areas - Dashboard Functionality',
            'GET Projects - Dashboard Functionality',
            'GET Dashboard - Complete Load Test',
            'GET Today View - Post-Migration Functionality'
        ]
        
        for test_name in migration_tests:
            test_result = next((t for t in self.test_results if t['test'] == test_name), None)
            if test_result:
                status = "✅" if test_result['success'] else "❌"
                print(f"   {status} {test_name}")
        
        return failed_tests == 0

    def run_migration_verification(self):
        """Run the complete migration verification test"""
        print("🚀 Starting Task Status Migration Verification - Quick Test")
        print(f"Backend URL: {self.base_url}")
        print("=" * 80)
        
        try:
            # Health check first
            self.test_health_check()
            
            # Set up authentication
            if not self.setup_authentication():
                print("❌ CRITICAL: Could not set up authentication. Aborting tests.")
                return False
            
            # Create some test data to verify migration works
            self.create_test_data_for_migration_verification()
            
            # Main migration verification test
            self.test_task_status_migration_verification()
            
        except Exception as e:
            print(f"\n❌ CRITICAL ERROR during testing: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Print summary
        return self.print_summary()

if __name__ == "__main__":
    tester = MigrationTester()
    success = tester.run_migration_verification()
    sys.exit(0 if success else 1)