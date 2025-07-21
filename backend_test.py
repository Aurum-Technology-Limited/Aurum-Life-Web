#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Aurum Life Authentication and User Profile Management System
Tests Authentication, User Registration, Login, JWT tokens, Protected Routes, and User Profile Management
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any
import uuid
import time

# Configuration
BACKEND_URL = "https://575a5fc8-3b5a-4d3d-9314-0d71af76d86c.preview.emergentagent.com/api"
DEFAULT_USER_ID = "demo-user-123"

class BackendTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.user_id = DEFAULT_USER_ID
        self.session = requests.Session()
        self.test_results = []
        self.created_resources = {
            'areas': [],
            'projects': [],
            'tasks': [],
            'users': []
        }
        self.auth_token = None
        self.test_user_email = f"testuser_{uuid.uuid4().hex[:8]}@aurumlife.com"
        self.test_user_password = "SecurePassword123!"
        self.test_user_data = {
            "username": f"testuser_{uuid.uuid4().hex[:8]}",
            "email": self.test_user_email,
            "first_name": "John",
            "last_name": "Doe",
            "password": self.test_user_password
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

    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, params=params)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, params=params)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, params=params)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            response.raise_for_status()
            return {
                'success': True,
                'status_code': response.status_code,
                'data': response.json() if response.content else {}
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': getattr(e.response, 'status_code', None),
                'data': {}
            }

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

    def test_areas_api(self):
        """Test Areas CRUD operations"""
        print("\n=== AREAS API TESTING ===")
        
        # Test GET areas (should return seeded data)
        result = self.make_request('GET', '/areas', params={'user_id': self.user_id})
        self.log_test(
            "GET Areas - Initial Data",
            result['success'],
            f"Retrieved {len(result['data']) if result['success'] else 0} areas"
        )
        
        if result['success'] and result['data']:
            print(f"   Found areas: {[area['name'] for area in result['data']]}")
        
        # Test GET areas with projects included
        result = self.make_request('GET', '/areas', params={'user_id': self.user_id, 'include_projects': True})
        self.log_test(
            "GET Areas with Projects",
            result['success'],
            f"Retrieved areas with project data included"
        )
        
        # Test CREATE area
        new_area_data = {
            "name": "Test Area - Backend Testing",
            "description": "Area created during backend testing",
            "icon": "🧪",
            "color": "#FF6B6B"
        }
        
        result = self.make_request('POST', '/areas', data=new_area_data, params={'user_id': self.user_id})
        self.log_test(
            "POST Create Area",
            result['success'],
            f"Created area: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Failed to create area: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            created_area_id = result['data']['id']
            self.created_resources['areas'].append(created_area_id)
            
            # Test GET specific area
            result = self.make_request('GET', f'/areas/{created_area_id}', params={'user_id': self.user_id})
            self.log_test(
                "GET Specific Area",
                result['success'],
                f"Retrieved area: {result['data'].get('name', 'Unknown')}" if result['success'] else "Failed to retrieve area"
            )
            
            # Test UPDATE area
            update_data = {
                "name": "Updated Test Area",
                "description": "Updated during testing"
            }
            
            result = self.make_request('PUT', f'/areas/{created_area_id}', data=update_data, params={'user_id': self.user_id})
            self.log_test(
                "PUT Update Area",
                result['success'],
                "Area updated successfully" if result['success'] else f"Failed to update area: {result.get('error', 'Unknown error')}"
            )

    def test_projects_api(self):
        """Test Projects CRUD operations"""
        print("\n=== PROJECTS API TESTING ===")
        
        # First, get an area to create projects in
        areas_result = self.make_request('GET', '/areas', params={'user_id': self.user_id})
        if not areas_result['success'] or not areas_result['data']:
            self.log_test("Projects API Setup", False, "No areas found to create projects in")
            return
            
        test_area_id = areas_result['data'][0]['id']
        
        # Test GET projects
        result = self.make_request('GET', '/projects', params={'user_id': self.user_id})
        self.log_test(
            "GET Projects - All",
            result['success'],
            f"Retrieved {len(result['data']) if result['success'] else 0} projects"
        )
        
        # Test GET projects filtered by area
        result = self.make_request('GET', '/projects', params={'user_id': self.user_id, 'area_id': test_area_id})
        self.log_test(
            "GET Projects - Filtered by Area",
            result['success'],
            f"Retrieved {len(result['data']) if result['success'] else 0} projects for area"
        )
        
        # Test CREATE project
        new_project_data = {
            "area_id": test_area_id,
            "name": "Test Project - Backend Testing",
            "description": "Project created during backend testing",
            "status": "In Progress",
            "priority": "high",
            "deadline": (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        result = self.make_request('POST', '/projects', data=new_project_data, params={'user_id': self.user_id})
        self.log_test(
            "POST Create Project",
            result['success'],
            f"Created project: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Failed to create project: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            created_project_id = result['data']['id']
            self.created_resources['projects'].append(created_project_id)
            
            # Test GET specific project
            result = self.make_request('GET', f'/projects/{created_project_id}', params={'user_id': self.user_id})
            self.log_test(
                "GET Specific Project",
                result['success'],
                f"Retrieved project: {result['data'].get('name', 'Unknown')}" if result['success'] else "Failed to retrieve project"
            )
            
            # Test GET project with tasks
            result = self.make_request('GET', f'/projects/{created_project_id}', params={'user_id': self.user_id, 'include_tasks': True})
            self.log_test(
                "GET Project with Tasks",
                result['success'],
                f"Retrieved project with tasks included" if result['success'] else "Failed to retrieve project with tasks"
            )
            
            # Test UPDATE project
            update_data = {
                "name": "Updated Test Project",
                "status": "Completed"
            }
            
            result = self.make_request('PUT', f'/projects/{created_project_id}', data=update_data, params={'user_id': self.user_id})
            self.log_test(
                "PUT Update Project",
                result['success'],
                "Project updated successfully" if result['success'] else f"Failed to update project: {result.get('error', 'Unknown error')}"
            )

    def test_tasks_api(self):
        """Test Enhanced Tasks CRUD operations"""
        print("\n=== TASKS API TESTING ===")
        
        # Get a project to create tasks in
        projects_result = self.make_request('GET', '/projects', params={'user_id': self.user_id})
        if not projects_result['success'] or not projects_result['data']:
            self.log_test("Tasks API Setup", False, "No projects found to create tasks in")
            return
            
        test_project_id = projects_result['data'][0]['id']
        
        # Test GET tasks
        result = self.make_request('GET', '/tasks', params={'user_id': self.user_id})
        self.log_test(
            "GET Tasks - All",
            result['success'],
            f"Retrieved {len(result['data']) if result['success'] else 0} tasks"
        )
        
        # Test GET tasks filtered by project
        result = self.make_request('GET', '/tasks', params={'user_id': self.user_id, 'project_id': test_project_id})
        self.log_test(
            "GET Tasks - Filtered by Project",
            result['success'],
            f"Retrieved {len(result['data']) if result['success'] else 0} tasks for project"
        )
        
        # Test CREATE task
        new_task_data = {
            "project_id": test_project_id,
            "name": "Test Task - Backend Testing",
            "description": "Task created during backend testing",
            "status": "not_started",
            "priority": "high",
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "category": "testing",
            "estimated_duration": 120
        }
        
        result = self.make_request('POST', '/tasks', data=new_task_data, params={'user_id': self.user_id})
        self.log_test(
            "POST Create Task",
            result['success'],
            f"Created task: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Failed to create task: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            created_task_id = result['data']['id']
            self.created_resources['tasks'].append(created_task_id)
            
            # Test UPDATE task
            update_data = {
                "name": "Updated Test Task",
                "status": "in_progress",
                "completed": False
            }
            
            result = self.make_request('PUT', f'/tasks/{created_task_id}', data=update_data, params={'user_id': self.user_id})
            self.log_test(
                "PUT Update Task",
                result['success'],
                "Task updated successfully" if result['success'] else f"Failed to update task: {result.get('error', 'Unknown error')}"
            )
            
            # Test move task between kanban columns
            result = self.make_request('PUT', f'/tasks/{created_task_id}/column', params={'user_id': self.user_id, 'new_column': 'in_progress'})
            self.log_test(
                "PUT Move Task Column",
                result['success'],
                "Task moved to in_progress column" if result['success'] else f"Failed to move task: {result.get('error', 'Unknown error')}"
            )
            
            # Test move to done column
            result = self.make_request('PUT', f'/tasks/{created_task_id}/column', params={'user_id': self.user_id, 'new_column': 'done'})
            self.log_test(
                "PUT Move Task to Done",
                result['success'],
                "Task moved to done column" if result['success'] else f"Failed to move task to done: {result.get('error', 'Unknown error')}"
            )

    def test_project_tasks_api(self):
        """Test project-specific task endpoints"""
        print("\n=== PROJECT TASKS API TESTING ===")
        
        # Get a project with tasks
        projects_result = self.make_request('GET', '/projects', params={'user_id': self.user_id})
        if not projects_result['success'] or not projects_result['data']:
            self.log_test("Project Tasks API Setup", False, "No projects found")
            return
            
        test_project_id = projects_result['data'][0]['id']
        
        # Test GET project tasks
        result = self.make_request('GET', f'/projects/{test_project_id}/tasks', params={'user_id': self.user_id})
        self.log_test(
            "GET Project Tasks",
            result['success'],
            f"Retrieved {len(result['data']) if result['success'] else 0} tasks for project"
        )

    def test_kanban_board_api(self):
        """Test Kanban Board functionality"""
        print("\n=== KANBAN BOARD API TESTING ===")
        
        # Get a project for kanban testing
        projects_result = self.make_request('GET', '/projects', params={'user_id': self.user_id})
        if not projects_result['success'] or not projects_result['data']:
            self.log_test("Kanban API Setup", False, "No projects found for kanban testing")
            return
            
        test_project_id = projects_result['data'][0]['id']
        
        # Test GET kanban board
        result = self.make_request('GET', f'/projects/{test_project_id}/kanban', params={'user_id': self.user_id})
        self.log_test(
            "GET Kanban Board",
            result['success'],
            f"Retrieved kanban board for project: {result['data'].get('project_name', 'Unknown')}" if result['success'] else f"Failed to get kanban board: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            kanban_data = result['data']
            columns = kanban_data.get('columns', {})
            print(f"   Kanban columns: to_do({len(columns.get('to_do', []))}), in_progress({len(columns.get('in_progress', []))}), done({len(columns.get('done', []))})")

    def test_today_view_api(self):
        """Test Today View unified API"""
        print("\n=== TODAY VIEW API TESTING ===")
        
        # Test GET today view
        result = self.make_request('GET', '/today', params={'user_id': self.user_id})
        self.log_test(
            "GET Today View",
            result['success'],
            f"Retrieved today view with {len(result['data'].get('tasks', [])) if result['success'] else 0} tasks and {len(result['data'].get('habits', [])) if result['success'] else 0} habits"
        )
        
        if result['success']:
            today_data = result['data']
            print(f"   Today's stats: {today_data.get('completed_tasks', 0)}/{today_data.get('total_tasks', 0)} tasks completed")
            print(f"   Estimated duration: {today_data.get('estimated_duration', 0)} minutes")

    def test_statistics_api(self):
        """Test Statistics and Analytics"""
        print("\n=== STATISTICS API TESTING ===")
        
        # Test GET user stats
        result = self.make_request('GET', '/stats', params={'user_id': self.user_id})
        self.log_test(
            "GET User Statistics",
            result['success'],
            "Retrieved user statistics" if result['success'] else f"Failed to get stats: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            stats = result['data']
            print(f"   Areas: {stats.get('total_areas', 0)}, Projects: {stats.get('total_projects', 0)}, Tasks: {stats.get('total_tasks', 0)}")
            print(f"   Completed: Projects({stats.get('completed_projects', 0)}), Tasks({stats.get('tasks_completed', 0)})")
        
        # Test POST update stats
        result = self.make_request('POST', '/stats/update', params={'user_id': self.user_id})
        self.log_test(
            "POST Update Statistics",
            result['success'],
            "Statistics updated successfully" if result['success'] else f"Failed to update stats: {result.get('error', 'Unknown error')}"
        )

    def test_dashboard_api(self):
        """Test Dashboard API with hierarchical data"""
        print("\n=== DASHBOARD API TESTING ===")
        
        # Test GET dashboard
        result = self.make_request('GET', '/dashboard', params={'user_id': self.user_id})
        self.log_test(
            "GET Dashboard Data",
            result['success'],
            "Retrieved dashboard data with hierarchical structure" if result['success'] else f"Failed to get dashboard: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            dashboard = result['data']
            print(f"   User: {dashboard.get('user', {}).get('username', 'Unknown')}")
            print(f"   Areas: {len(dashboard.get('areas', []))}")
            print(f"   Today's tasks: {len(dashboard.get('today_tasks', []))}")
            print(f"   Recent habits: {len(dashboard.get('recent_habits', []))}")

    def test_data_persistence(self):
        """Test that hierarchical relationships persist correctly"""
        print("\n=== DATA PERSISTENCE TESTING ===")
        
        # Test cascade delete - create area with project and task, then delete area
        if self.created_resources['areas']:
            area_id = self.created_resources['areas'][0]
            
            # Get projects in this area before deletion
            projects_before = self.make_request('GET', '/projects', params={'user_id': self.user_id, 'area_id': area_id})
            project_count_before = len(projects_before['data']) if projects_before['success'] else 0
            
            # Delete the area (should cascade delete projects and tasks)
            result = self.make_request('DELETE', f'/areas/{area_id}', params={'user_id': self.user_id})
            self.log_test(
                "DELETE Area (Cascade Test)",
                result['success'],
                f"Area deleted successfully, should cascade delete {project_count_before} projects" if result['success'] else f"Failed to delete area: {result.get('error', 'Unknown error')}"
            )
            
            if result['success']:
                # Verify projects were deleted
                projects_after = self.make_request('GET', '/projects', params={'user_id': self.user_id, 'area_id': area_id})
                project_count_after = len(projects_after['data']) if projects_after['success'] else 0
                
                self.log_test(
                    "Cascade Delete Verification",
                    project_count_after == 0,
                    f"Projects in deleted area: {project_count_after} (should be 0)"
                )

    def cleanup_test_data(self):
        """Clean up any remaining test data"""
        print("\n=== CLEANUP ===")
        
        # Delete remaining test tasks
        for task_id in self.created_resources['tasks']:
            result = self.make_request('DELETE', f'/tasks/{task_id}', params={'user_id': self.user_id})
            if result['success']:
                print(f"   Cleaned up task: {task_id}")
        
        # Delete remaining test projects
        for project_id in self.created_resources['projects']:
            result = self.make_request('DELETE', f'/projects/{project_id}', params={'user_id': self.user_id})
            if result['success']:
                print(f"   Cleaned up project: {project_id}")
        
        # Delete remaining test areas (already done in cascade test, but just in case)
        for area_id in self.created_resources['areas']:
            result = self.make_request('DELETE', f'/areas/{area_id}', params={'user_id': self.user_id})
            if result['success']:
                print(f"   Cleaned up area: {area_id}")

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Comprehensive Backend API Testing for Aurum Life Hierarchical System")
        print(f"Backend URL: {self.base_url}")
        print(f"User ID: {self.user_id}")
        
        try:
            # Core API tests
            self.test_health_check()
            self.test_areas_api()
            self.test_projects_api()
            self.test_tasks_api()
            self.test_project_tasks_api()
            self.test_kanban_board_api()
            self.test_today_view_api()
            self.test_statistics_api()
            self.test_dashboard_api()
            self.test_data_persistence()
            
        except Exception as e:
            print(f"❌ CRITICAL ERROR during testing: {e}")
            self.log_test("Critical Error", False, str(e))
        
        finally:
            self.cleanup_test_data()
            self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("🏁 BACKEND TESTING SUMMARY")
        print("="*60)
        
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
        
        print("\n✅ KEY FUNCTIONALITY STATUS:")
        
        # Check critical functionality
        critical_tests = {
            'Areas API': any('GET Areas' in t['test'] and t['success'] for t in self.test_results),
            'Projects API': any('GET Projects' in t['test'] and t['success'] for t in self.test_results),
            'Tasks API': any('GET Tasks' in t['test'] and t['success'] for t in self.test_results),
            'Today View': any('GET Today View' in t['test'] and t['success'] for t in self.test_results),
            'Kanban Board': any('GET Kanban Board' in t['test'] and t['success'] for t in self.test_results),
            'Dashboard': any('GET Dashboard Data' in t['test'] and t['success'] for t in self.test_results),
            'Statistics': any('GET User Statistics' in t['test'] and t['success'] for t in self.test_results)
        }
        
        for feature, status in critical_tests.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {feature}")
        
        return failed_tests == 0

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)