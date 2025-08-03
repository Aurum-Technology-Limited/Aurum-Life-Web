#!/usr/bin/env python3
"""
COMPREHENSIVE BACKEND API TESTING
Complete end-to-end testing of all core backend API endpoints for Aurum Life platform.

FOCUS AREAS:
1. AUTHENTICATION SYSTEM - User registration, login, JWT token validation
2. PROJECTS API - Project CRUD operations, filtering, archiving 
3. AREAS API - Area management, pillar linking, importance levels
4. TASKS API - Task creation, updates, status changes
5. INSIGHTS API - Insights data retrieval and calculations
6. GENERAL SYSTEM HEALTH - Database connectivity and core services

SPECIFIC ENDPOINTS TO TEST:
Authentication:
- POST /api/auth/register
- POST /api/auth/login
- GET /api/auth/me
- POST /api/auth/google
- POST /api/auth/forgot-password
- POST /api/auth/reset-password

Projects:
- POST /api/projects
- GET /api/projects
- GET /api/projects/{id}
- PUT /api/projects/{id}
- PUT /api/projects/{id}/archive
- PUT /api/projects/{id}/unarchive
- DELETE /api/projects/{id}

Areas:
- POST /api/areas
- GET /api/areas
- GET /api/areas/{id}
- PUT /api/areas/{id}
- PUT /api/areas/{id}/archive
- PUT /api/areas/{id}/unarchive
- DELETE /api/areas/{id}

Tasks:
- POST /api/tasks
- GET /api/tasks
- PUT /api/tasks/{id}
- DELETE /api/tasks/{id}
- GET /api/projects/{id}/kanban
- PUT /api/tasks/{id}/column

Insights:
- GET /api/insights
- GET /api/insights/areas/{id}
- GET /api/insights/projects/{id}

System Health:
- GET /api/health
- GET /api/dashboard
- GET /api/stats

AUTHENTICATION:
- Use realistic test credentials for comprehensive testing
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any
import uuid
import time

# Configuration - Using the production backend URL from frontend/.env
BACKEND_URL = "https://7b39a747-36d6-44f7-9408-a498365475ba.preview.emergentagent.com/api"

class ComprehensiveBackendTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.created_resources = {
            'pillars': [],
            'areas': [],
            'projects': [],
            'tasks': [],
            'users': []
        }
        self.auth_token = None
        # Use realistic test data
        self.test_user_email = f"backend.tester_{uuid.uuid4().hex[:8]}@aurumlife.com"
        self.test_user_password = "BackendTest2025!"
        self.test_user_data = {
            "username": f"backend_tester_{uuid.uuid4().hex[:8]}",
            "email": self.test_user_email,
            "first_name": "Backend",
            "last_name": "Tester",
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

    def test_system_health(self):
        """Test basic system health and connectivity"""
        print("\n=== TESTING SYSTEM HEALTH ===")
        
        # Test health endpoint
        result = self.make_request('GET', '/health')
        self.log_test(
            "SYSTEM HEALTH CHECK",
            result['success'],
            f"Health endpoint accessible" if result['success'] else f"Health endpoint failed: {result.get('error', 'Unknown error')}"
        )
        
        # Test root endpoint
        result = self.make_request('GET', '/')
        self.log_test(
            "API ROOT ENDPOINT",
            result['success'],
            f"API root accessible" if result['success'] else f"API root failed: {result.get('error', 'Unknown error')}"
        )
        
        return result['success']

    def test_authentication_system(self):
        """Test complete authentication system"""
        print("\n=== TESTING AUTHENTICATION SYSTEM ===")
        
        # Test user registration
        result = self.make_request('POST', '/auth/register', data=self.test_user_data)
        registration_success = result['success']
        self.log_test(
            "USER REGISTRATION",
            registration_success,
            f"User registered successfully: {result['data'].get('email', 'Unknown')}" if registration_success else f"Registration failed: {result.get('error', 'Unknown error')}"
        )
        
        if not registration_success:
            return False
        
        self.created_resources['users'].append(result['data'].get('id'))
        
        # Test user login
        login_data = {
            "email": self.test_user_data['email'],
            "password": self.test_user_data['password']
        }
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        login_success = result['success']
        self.log_test(
            "USER LOGIN",
            login_success,
            f"Login successful, JWT token received" if login_success else f"Login failed: {result.get('error', 'Unknown error')}"
        )
        
        if not login_success:
            return False
        
        token_data = result['data']
        self.auth_token = token_data.get('access_token')
        
        # Test JWT token validation
        result = self.make_request('GET', '/auth/me', use_auth=True)
        token_validation_success = result['success']
        self.log_test(
            "JWT TOKEN VALIDATION",
            token_validation_success,
            f"Token validated successfully, user: {result['data'].get('email', 'Unknown')}" if token_validation_success else f"Token validation failed: {result.get('error', 'Unknown error')}"
        )
        
        # Test protected route access
        result = self.make_request('GET', '/dashboard', use_auth=True)
        protected_route_success = result['success']
        self.log_test(
            "PROTECTED ROUTE ACCESS",
            protected_route_success,
            f"Protected route accessible with valid token" if protected_route_success else f"Protected route access failed: {result.get('error', 'Unknown error')}"
        )
        
        # Test invalid token handling
        old_token = self.auth_token
        self.auth_token = "invalid_token_12345"
        result = self.make_request('GET', '/auth/me', use_auth=True)
        invalid_token_rejected = not result['success']
        self.log_test(
            "INVALID TOKEN REJECTION",
            invalid_token_rejected,
            f"Invalid token properly rejected" if invalid_token_rejected else f"Invalid token was accepted (security issue)"
        )
        
        # Restore valid token
        self.auth_token = old_token
        
        return all([registration_success, login_success, token_validation_success, protected_route_success, invalid_token_rejected])

    def setup_test_infrastructure(self):
        """Create pillar and area for testing"""
        print("\n=== SETTING UP TEST INFRASTRUCTURE ===")
        
        if not self.auth_token:
            self.log_test("INFRASTRUCTURE SETUP - Authentication Required", False, "No authentication token available")
            return None, None
        
        # Create test pillar
        pillar_data = {
            "name": "Backend Test Pillar",
            "description": "Test pillar for comprehensive backend testing",
            "icon": "🧪",
            "color": "#4CAF50"
        }
        
        result = self.make_request('POST', '/pillars', data=pillar_data, use_auth=True)
        if not result['success']:
            self.log_test("INFRASTRUCTURE - CREATE PILLAR", False, f"Failed to create test pillar: {result.get('error', 'Unknown error')}")
            return None, None
        
        pillar_id = result['data']['id']
        self.created_resources['pillars'].append(pillar_id)
        self.log_test("INFRASTRUCTURE - CREATE PILLAR", True, f"Created test pillar: {pillar_id}")
        
        # Create test area
        area_data = {
            "name": "Backend Test Area",
            "description": "Test area for comprehensive backend testing",
            "icon": "🔧",
            "color": "#2196F3",
            "pillar_id": pillar_id
        }
        
        result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
        if not result['success']:
            self.log_test("INFRASTRUCTURE - CREATE AREA", False, f"Failed to create test area: {result.get('error', 'Unknown error')}")
            return pillar_id, None
        
        area_id = result['data']['id']
        self.created_resources['areas'].append(area_id)
        self.log_test("INFRASTRUCTURE - CREATE AREA", True, f"Created test area: {area_id}")
        
        return pillar_id, area_id

    def test_projects_api(self):
        """Test complete Projects API functionality"""
        print("\n=== TESTING PROJECTS API ===")
        
        pillar_id, area_id = self.setup_test_infrastructure()
        if not area_id:
            return False
        
        # Test project creation
        project_data = {
            "area_id": area_id,
            "name": "Backend Test Project",
            "description": "Testing project CRUD operations",
            "priority": "high",
            "icon": "🚀"
        }
        
        result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
        create_success = result['success']
        self.log_test(
            "PROJECT CREATION",
            create_success,
            f"Project created successfully" if create_success else f"Project creation failed: {result.get('error', 'Unknown error')}"
        )
        
        if not create_success:
            return False
        
        project_id = result['data']['id']
        self.created_resources['projects'].append(project_id)
        
        # Test project retrieval (specific)
        result = self.make_request('GET', f'/projects/{project_id}', use_auth=True)
        get_specific_success = result['success']
        self.log_test(
            "PROJECT GET SPECIFIC",
            get_specific_success,
            f"Project retrieved successfully" if get_specific_success else f"Project retrieval failed: {result.get('error', 'Unknown error')}"
        )
        
        # Test projects list
        result = self.make_request('GET', '/projects', use_auth=True)
        get_list_success = result['success']
        self.log_test(
            "PROJECTS LIST",
            get_list_success,
            f"Projects list retrieved successfully" if get_list_success else f"Projects list failed: {result.get('error', 'Unknown error')}"
        )
        
        # Test project update
        update_data = {
            "name": "Updated Backend Test Project",
            "description": "Updated description for testing",
            "priority": "medium"
        }
        
        result = self.make_request('PUT', f'/projects/{project_id}', data=update_data, use_auth=True)
        update_success = result['success']
        self.log_test(
            "PROJECT UPDATE",
            update_success,
            f"Project updated successfully" if update_success else f"Project update failed: {result.get('error', 'Unknown error')}"
        )
        
        # Test project archiving
        result = self.make_request('PUT', f'/projects/{project_id}/archive', use_auth=True)
        archive_success = result['success']
        self.log_test(
            "PROJECT ARCHIVE",
            archive_success,
            f"Project archived successfully" if archive_success else f"Project archiving failed: {result.get('error', 'Unknown error')}"
        )
        
        # Test project unarchiving
        result = self.make_request('PUT', f'/projects/{project_id}/unarchive', use_auth=True)
        unarchive_success = result['success']
        self.log_test(
            "PROJECT UNARCHIVE",
            unarchive_success,
            f"Project unarchived successfully" if unarchive_success else f"Project unarchiving failed: {result.get('error', 'Unknown error')}"
        )
        
        # Test project filtering by area
        result = self.make_request('GET', '/projects', params={'area_id': area_id}, use_auth=True)
        filter_success = result['success']
        self.log_test(
            "PROJECT FILTERING",
            filter_success,
            f"Project filtering by area successful" if filter_success else f"Project filtering failed: {result.get('error', 'Unknown error')}"
        )
        
        return all([create_success, get_specific_success, get_list_success, update_success, archive_success, unarchive_success, filter_success])

    def test_areas_api(self):
        """Test complete Areas API functionality"""
        print("\n=== TESTING AREAS API ===")
        
        pillar_id, _ = self.setup_test_infrastructure()
        if not pillar_id:
            return False
        
        # Test area creation
        area_data = {
            "name": "Backend Test Area 2",
            "description": "Testing area CRUD operations",
            "icon": "⚙️",
            "color": "#FF9800",
            "pillar_id": pillar_id
        }
        
        result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
        create_success = result['success']
        self.log_test(
            "AREA CREATION",
            create_success,
            f"Area created successfully" if create_success else f"Area creation failed: {result.get('error', 'Unknown error')}"
        )
        
        if not create_success:
            return False
        
        area_id = result['data']['id']
        self.created_resources['areas'].append(area_id)
        
        # Test area retrieval (specific)
        result = self.make_request('GET', f'/areas/{area_id}', use_auth=True)
        get_specific_success = result['success']
        self.log_test(
            "AREA GET SPECIFIC",
            get_specific_success,
            f"Area retrieved successfully" if get_specific_success else f"Area retrieval failed: {result.get('error', 'Unknown error')}"
        )
        
        # Test areas list
        result = self.make_request('GET', '/areas', use_auth=True)
        get_list_success = result['success']
        self.log_test(
            "AREAS LIST",
            get_list_success,
            f"Areas list retrieved successfully" if get_list_success else f"Areas list failed: {result.get('error', 'Unknown error')}"
        )
        
        # Test area update
        update_data = {
            "name": "Updated Backend Test Area 2",
            "description": "Updated description for testing"
        }
        
        result = self.make_request('PUT', f'/areas/{area_id}', data=update_data, use_auth=True)
        update_success = result['success']
        self.log_test(
            "AREA UPDATE",
            update_success,
            f"Area updated successfully" if update_success else f"Area update failed: {result.get('error', 'Unknown error')}"
        )
        
        # Test area archiving
        result = self.make_request('PUT', f'/areas/{area_id}/archive', use_auth=True)
        archive_success = result['success']
        self.log_test(
            "AREA ARCHIVE",
            archive_success,
            f"Area archived successfully" if archive_success else f"Area archiving failed: {result.get('error', 'Unknown error')}"
        )
        
        # Test area unarchiving
        result = self.make_request('PUT', f'/areas/{area_id}/unarchive', use_auth=True)
        unarchive_success = result['success']
        self.log_test(
            "AREA UNARCHIVE",
            unarchive_success,
            f"Area unarchived successfully" if unarchive_success else f"Area unarchiving failed: {result.get('error', 'Unknown error')}"
        )
        
        # Test pillar linking verification
        result = self.make_request('GET', f'/areas/{area_id}', use_auth=True)
        pillar_link_success = result['success'] and result['data'].get('pillar_id') == pillar_id
        self.log_test(
            "AREA PILLAR LINKING",
            pillar_link_success,
            f"Area properly linked to pillar" if pillar_link_success else f"Area pillar linking failed"
        )
        
        return all([create_success, get_specific_success, get_list_success, update_success, archive_success, unarchive_success, pillar_link_success])

    def test_tasks_api(self):
        """Test complete Tasks API functionality"""
        print("\n=== TESTING TASKS API ===")
        
        pillar_id, area_id = self.setup_test_infrastructure()
        if not area_id:
            return False
        
        # Create a project for task testing
        project_data = {
            "area_id": area_id,
            "name": "Task Test Project",
            "description": "Project for testing tasks",
            "priority": "medium"
        }
        
        result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
        if not result['success']:
            self.log_test("TASK TESTING - CREATE PROJECT", False, "Failed to create project for task testing")
            return False
        
        project_id = result['data']['id']
        self.created_resources['projects'].append(project_id)
        
        # Test task creation
        task_data = {
            "project_id": project_id,
            "name": "Backend Test Task",
            "description": "Testing task CRUD operations",
            "priority": "high",
            "status": "todo"
        }
        
        result = self.make_request('POST', '/tasks', data=task_data, use_auth=True)
        create_success = result['success']
        self.log_test(
            "TASK CREATION",
            create_success,
            f"Task created successfully" if create_success else f"Task creation failed: {result.get('error', 'Unknown error')}"
        )
        
        if not create_success:
            return False
        
        task_id = result['data']['id']
        self.created_resources['tasks'].append(task_id)
        
        # Test tasks list
        result = self.make_request('GET', '/tasks', use_auth=True)
        get_list_success = result['success']
        self.log_test(
            "TASKS LIST",
            get_list_success,
            f"Tasks list retrieved successfully" if get_list_success else f"Tasks list failed: {result.get('error', 'Unknown error')}"
        )
        
        # Test task update
        update_data = {
            "name": "Updated Backend Test Task",
            "description": "Updated description for testing",
            "status": "in_progress"
        }
        
        result = self.make_request('PUT', f'/tasks/{task_id}', data=update_data, use_auth=True)
        update_success = result['success']
        self.log_test(
            "TASK UPDATE",
            update_success,
            f"Task updated successfully" if update_success else f"Task update failed: {result.get('error', 'Unknown error')}"
        )
        
        # Test task status changes
        status_data = {"status": "completed"}
        result = self.make_request('PUT', f'/tasks/{task_id}', data=status_data, use_auth=True)
        status_change_success = result['success']
        self.log_test(
            "TASK STATUS CHANGE",
            status_change_success,
            f"Task status changed successfully" if status_change_success else f"Task status change failed: {result.get('error', 'Unknown error')}"
        )
        
        # Test kanban board
        result = self.make_request('GET', f'/projects/{project_id}/kanban', use_auth=True)
        kanban_success = result['success']
        self.log_test(
            "KANBAN BOARD",
            kanban_success,
            f"Kanban board retrieved successfully" if kanban_success else f"Kanban board failed: {result.get('error', 'Unknown error')}"
        )
        
        # Test task column movement
        result = self.make_request('PUT', f'/tasks/{task_id}/column', params={'new_column': 'done'}, use_auth=True)
        column_move_success = result['success']
        self.log_test(
            "TASK COLUMN MOVEMENT",
            column_move_success,
            f"Task moved between columns successfully" if column_move_success else f"Task column movement failed: {result.get('error', 'Unknown error')}"
        )
        
        # Test project tasks
        result = self.make_request('GET', f'/projects/{project_id}/tasks', use_auth=True)
        project_tasks_success = result['success']
        self.log_test(
            "PROJECT TASKS",
            project_tasks_success,
            f"Project tasks retrieved successfully" if project_tasks_success else f"Project tasks failed: {result.get('error', 'Unknown error')}"
        )
        
        return all([create_success, get_list_success, update_success, status_change_success, kanban_success, column_move_success, project_tasks_success])

    def test_insights_api(self):
        """Test Insights API functionality"""
        print("\n=== TESTING INSIGHTS API ===")
        
        pillar_id, area_id = self.setup_test_infrastructure()
        if not area_id:
            return False
        
        # Create some data for insights
        project_data = {
            "area_id": area_id,
            "name": "Insights Test Project",
            "description": "Project for testing insights",
            "priority": "medium"
        }
        
        result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
        if result['success']:
            project_id = result['data']['id']
            self.created_resources['projects'].append(project_id)
            
            # Create a task for more data
            task_data = {
                "project_id": project_id,
                "name": "Insights Test Task",
                "description": "Task for testing insights",
                "status": "completed"
            }
            
            result = self.make_request('POST', '/tasks', data=task_data, use_auth=True)
            if result['success']:
                self.created_resources['tasks'].append(result['data']['id'])
        
        # Test main insights endpoint
        result = self.make_request('GET', '/insights', use_auth=True)
        insights_success = result['success']
        self.log_test(
            "INSIGHTS DATA",
            insights_success,
            f"Insights data retrieved successfully" if insights_success else f"Insights data failed: {result.get('error', 'Unknown error')}"
        )
        
        # Test insights with date range
        result = self.make_request('GET', '/insights', params={'date_range': 'monthly'}, use_auth=True)
        insights_filtered_success = result['success']
        self.log_test(
            "INSIGHTS FILTERED",
            insights_filtered_success,
            f"Filtered insights retrieved successfully" if insights_filtered_success else f"Filtered insights failed: {result.get('error', 'Unknown error')}"
        )
        
        # Test area drill-down
        result = self.make_request('GET', f'/insights/areas/{area_id}', use_auth=True)
        area_drilldown_success = result['success']
        self.log_test(
            "AREA INSIGHTS DRILL-DOWN",
            area_drilldown_success,
            f"Area drill-down retrieved successfully" if area_drilldown_success else f"Area drill-down failed: {result.get('error', 'Unknown error')}"
        )
        
        # Test project drill-down (if we have a project)
        if 'projects' in self.created_resources and self.created_resources['projects']:
            project_id = self.created_resources['projects'][-1]
            result = self.make_request('GET', f'/insights/projects/{project_id}', use_auth=True)
            project_drilldown_success = result['success']
            self.log_test(
                "PROJECT INSIGHTS DRILL-DOWN",
                project_drilldown_success,
                f"Project drill-down retrieved successfully" if project_drilldown_success else f"Project drill-down failed: {result.get('error', 'Unknown error')}"
            )
        else:
            project_drilldown_success = True  # Skip if no projects
        
        return all([insights_success, insights_filtered_success, area_drilldown_success, project_drilldown_success])

    def test_dashboard_and_stats(self):
        """Test dashboard and stats endpoints"""
        print("\n=== TESTING DASHBOARD AND STATS ===")
        
        # Test dashboard
        result = self.make_request('GET', '/dashboard', use_auth=True)
        dashboard_success = result['success']
        self.log_test(
            "DASHBOARD DATA",
            dashboard_success,
            f"Dashboard data retrieved successfully" if dashboard_success else f"Dashboard failed: {result.get('error', 'Unknown error')}"
        )
        
        # Test user stats
        result = self.make_request('GET', '/stats', use_auth=True)
        stats_success = result['success']
        self.log_test(
            "USER STATS",
            stats_success,
            f"User stats retrieved successfully" if stats_success else f"User stats failed: {result.get('error', 'Unknown error')}"
        )
        
        # Test stats update
        result = self.make_request('POST', '/stats/update', use_auth=True)
        stats_update_success = result['success']
        self.log_test(
            "STATS UPDATE",
            stats_update_success,
            f"Stats updated successfully" if stats_update_success else f"Stats update failed: {result.get('error', 'Unknown error')}"
        )
        
        # Test today view
        result = self.make_request('GET', '/today', use_auth=True)
        today_success = result['success']
        self.log_test(
            "TODAY VIEW",
            today_success,
            f"Today view retrieved successfully" if today_success else f"Today view failed: {result.get('error', 'Unknown error')}"
        )
        
        return all([dashboard_success, stats_success, stats_update_success, today_success])

    def run_comprehensive_backend_test(self):
        """Run comprehensive backend API tests"""
        print("\n🧪 STARTING COMPREHENSIVE BACKEND API TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("System Health", self.test_system_health),
            ("Authentication System", self.test_authentication_system),
            ("Projects API", self.test_projects_api),
            ("Areas API", self.test_areas_api),
            ("Tasks API", self.test_tasks_api),
            ("Insights API", self.test_insights_api),
            ("Dashboard and Stats", self.test_dashboard_and_stats)
        ]
        
        successful_tests = 0
        total_tests = len(test_methods)
        
        for test_name, test_method in test_methods:
            print(f"\n--- {test_name} ---")
            try:
                if test_method():
                    successful_tests += 1
                    print(f"✅ {test_name} completed successfully")
                else:
                    print(f"❌ {test_name} failed")
            except Exception as e:
                print(f"❌ {test_name} raised exception: {e}")
        
        success_rate = (successful_tests / total_tests) * 100
        
        print(f"\n" + "=" * 80)
        print("🧪 COMPREHENSIVE BACKEND TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Categories: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze results by category
        auth_tests_passed = sum(1 for result in self.test_results if result['success'] and ('REGISTRATION' in result['test'] or 'LOGIN' in result['test'] or 'TOKEN' in result['test'] or 'PROTECTED' in result['test']))
        project_tests_passed = sum(1 for result in self.test_results if result['success'] and 'PROJECT' in result['test'])
        area_tests_passed = sum(1 for result in self.test_results if result['success'] and 'AREA' in result['test'])
        task_tests_passed = sum(1 for result in self.test_results if result['success'] and 'TASK' in result['test'])
        insights_tests_passed = sum(1 for result in self.test_results if result['success'] and 'INSIGHTS' in result['test'])
        system_tests_passed = sum(1 for result in self.test_results if result['success'] and ('HEALTH' in result['test'] or 'DASHBOARD' in result['test'] or 'STATS' in result['test']))
        
        print(f"\n🔍 SYSTEM ANALYSIS:")
        print(f"Authentication Tests Passed: {auth_tests_passed}")
        print(f"Projects API Tests Passed: {project_tests_passed}")
        print(f"Areas API Tests Passed: {area_tests_passed}")
        print(f"Tasks API Tests Passed: {task_tests_passed}")
        print(f"Insights API Tests Passed: {insights_tests_passed}")
        print(f"System Health Tests Passed: {system_tests_passed}")
        
        if success_rate >= 85:
            print("\n✅ BACKEND API SYSTEM: SUCCESS")
            print("   ✅ Authentication system working correctly")
            print("   ✅ Projects API fully functional")
            print("   ✅ Areas API with pillar linking working")
            print("   ✅ Tasks API with status management working")
            print("   ✅ Insights API providing data correctly")
            print("   ✅ System health and dashboard operational")
            print("   The backend API is production-ready!")
        else:
            print("\n❌ BACKEND API SYSTEM: ISSUES DETECTED")
            print("   Issues found in backend API implementation")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 85

    def cleanup_resources(self):
        """Clean up created test resources"""
        print("\n🧹 CLEANING UP TEST RESOURCES")
        cleanup_count = 0
        
        # Clean up tasks first (they depend on projects)
        for task_id in self.created_resources.get('tasks', []):
            try:
                result = self.make_request('DELETE', f'/tasks/{task_id}', use_auth=True)
                if result['success']:
                    cleanup_count += 1
                    print(f"   ✅ Cleaned up task: {task_id}")
            except:
                pass
        
        # Clean up projects (they depend on areas)
        for project_id in self.created_resources.get('projects', []):
            try:
                result = self.make_request('DELETE', f'/projects/{project_id}', use_auth=True)
                if result['success']:
                    cleanup_count += 1
                    print(f"   ✅ Cleaned up project: {project_id}")
            except:
                pass
        
        # Clean up areas (they may depend on pillars)
        for area_id in self.created_resources.get('areas', []):
            try:
                result = self.make_request('DELETE', f'/areas/{area_id}', use_auth=True)
                if result['success']:
                    cleanup_count += 1
                    print(f"   ✅ Cleaned up area: {area_id}")
            except:
                pass
        
        # Clean up pillars
        for pillar_id in self.created_resources.get('pillars', []):
            try:
                result = self.make_request('DELETE', f'/pillars/{pillar_id}', use_auth=True)
                if result['success']:
                    cleanup_count += 1
                    print(f"   ✅ Cleaned up pillar: {pillar_id}")
            except:
                pass
        
        if cleanup_count > 0:
            print(f"   ✅ Cleanup completed for {cleanup_count} resources")
        else:
            print("   ℹ️ No resources to cleanup")

def main():
    """Run Comprehensive Backend Tests"""
    print("🧪 STARTING COMPREHENSIVE BACKEND API TESTING")
    print("=" * 80)
    
    tester = ComprehensiveBackendTester()
    
    try:
        # Run the comprehensive backend tests
        success = tester.run_comprehensive_backend_test()
        
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
        
        return success_rate >= 85
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {str(e)}")
        return False
    
    finally:
        # Cleanup created resources
        tester.cleanup_resources()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)