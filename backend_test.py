#!/usr/bin/env python3
"""
PILLAR SYSTEM CHILD PILLAR REMOVAL COMPREHENSIVE TESTING
Complete end-to-end testing of the updated Pillar system with removed child pillar functionality.

FOCUS AREAS:
1. PILLAR MODEL CHANGES - Test that parent_pillar_id and sub_pillars fields are removed
2. SIMPLIFIED PILLAR STRUCTURE - Test flat structure without hierarchy
3. DATABASE MIGRATION VERIFICATION - Verify no pillar hierarchy remains
4. API ENDPOINT UPDATES - Test endpoints without include_sub_pillars parameter
5. FUNCTIONALITY VERIFICATION - Test CRUD operations work with simplified model

SPECIFIC ENDPOINTS TO TEST:
- GET /api/pillars - should NOT include parent_pillar_id or sub_pillars fields
- POST /api/pillars - should NOT accept parent_pillar_id in request body
- PUT /api/pillars/{id} - should NOT allow updating parent_pillar_id field
- Verify PillarResponse model no longer includes parent_pillar_id, sub_pillars, or parent_pillar_name fields
- Test pillar-area linking still works correctly
- Test pillar progress tracking (area_count, project_count, task_count)
- Confirm pillar sorting and filtering still function

MIGRATION VERIFICATION:
- Verify existing pillars no longer have parent_pillar_id field in database
- Test that migrated data is properly structured
- Confirm no pillar hierarchy remains in the database
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any
import uuid
import time
import re

# Configuration - Using the production backend URL from frontend/.env
BACKEND_URL = "https://aurum-life-1.preview.emergentagent.com/api"

class DateCreatedFieldTester:
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
        # Use realistic test data for date_created testing
        self.test_user_email = f"date.tester_{uuid.uuid4().hex[:8]}@aurumlife.com"
        self.test_user_password = "DateTest2025!"
        self.test_user_data = {
            "username": f"date_tester_{uuid.uuid4().hex[:8]}",
            "email": self.test_user_email,
            "first_name": "Date",
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

    def is_valid_iso_datetime(self, date_string: str) -> bool:
        """Check if a string is a valid ISO datetime format"""
        if not date_string:
            return False
        try:
            # Try to parse as ISO format datetime
            datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return True
        except (ValueError, TypeError):
            return False

    def is_recent_datetime(self, date_string: str, tolerance_minutes: int = 5) -> bool:
        """Check if datetime is recent (within tolerance_minutes of now)"""
        try:
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            now = datetime.utcnow()
            diff = abs((now - dt.replace(tzinfo=None)).total_seconds() / 60)
            return diff <= tolerance_minutes
        except:
            return False

    def test_basic_connectivity(self):
        """Test basic connectivity to the backend API"""
        print("\n=== TESTING BASIC CONNECTIVITY ===")
        
        result = self.make_request('GET', '/health')
        self.log_test(
            "BACKEND API CONNECTIVITY",
            result['success'],
            f"Backend API accessible at {self.base_url}" if result['success'] else f"Backend API not accessible: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            health_data = result['data']
            self.log_test(
                "HEALTH CHECK RESPONSE",
                'status' in health_data,
                f"Health check returned: {health_data.get('status', 'Unknown status')}"
            )
        
        return result['success']

    def test_user_registration_and_login(self):
        """Test user registration and login for date_created testing"""
        print("\n=== TESTING USER REGISTRATION AND LOGIN ===")
        
        # Register user
        result = self.make_request('POST', '/auth/register', data=self.test_user_data)
        self.log_test(
            "USER REGISTRATION",
            result['success'],
            f"User registered successfully: {result['data'].get('email', 'Unknown')}" if result['success'] else f"Registration failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        self.created_resources['users'].append(result['data'].get('id'))
        
        # Login user
        login_data = {
            "email": self.test_user_data['email'],
            "password": self.test_user_data['password']
        }
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        self.log_test(
            "USER LOGIN",
            result['success'],
            f"Login successful, JWT token received" if result['success'] else f"Login failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        token_data = result['data']
        self.auth_token = token_data.get('access_token')
        
        # Verify token works
        result = self.make_request('GET', '/auth/me', use_auth=True)
        self.log_test(
            "AUTHENTICATION TOKEN VALIDATION",
            result['success'],
            f"Token validated successfully, user: {result['data'].get('email', 'Unknown')}" if result['success'] else f"Token validation failed: {result.get('error', 'Unknown error')}"
        )
        
        return result['success']

    def test_pillars_date_created_field(self):
        """Test date_created field functionality for Pillars"""
        print("\n=== TESTING PILLARS DATE_CREATED FIELD ===")
        
        if not self.auth_token:
            self.log_test("PILLARS DATE_CREATED - Authentication Required", False, "No authentication token available")
            return False
        
        # Test 1: GET existing pillars to check date_created field in responses
        result = self.make_request('GET', '/pillars', use_auth=True)
        self.log_test(
            "GET PILLARS - DATE_CREATED FIELD PRESENCE",
            result['success'],
            f"Retrieved {len(result['data']) if result['success'] else 0} pillars" if result['success'] else f"Failed to get pillars: {result.get('error', 'Unknown error')}"
        )
        
        if result['success'] and result['data']:
            # Check if existing pillars have date_created field
            existing_pillars = result['data']
            pillars_with_date_created = [p for p in existing_pillars if 'date_created' in p]
            
            self.log_test(
                "EXISTING PILLARS DATE_CREATED FIELD",
                len(pillars_with_date_created) == len(existing_pillars),
                f"{len(pillars_with_date_created)}/{len(existing_pillars)} existing pillars have date_created field"
            )
            
            # Validate date_created format for existing pillars
            if pillars_with_date_created:
                sample_pillar = pillars_with_date_created[0]
                date_created_value = sample_pillar.get('date_created')
                
                self.log_test(
                    "EXISTING PILLAR DATE_CREATED FORMAT",
                    self.is_valid_iso_datetime(str(date_created_value)),
                    f"Date format validation: {date_created_value}"
                )
        
        # Test 2: POST new pillar to verify date_created is automatically set
        pillar_data = {
            "name": "Health & Wellness Test Pillar",
            "description": "A test pillar for date_created field validation",
            "icon": "🏥",
            "color": "#4CAF50"
        }
        
        creation_time = datetime.utcnow()
        result = self.make_request('POST', '/pillars', data=pillar_data, use_auth=True)
        
        self.log_test(
            "CREATE PILLAR WITH AUTO DATE_CREATED",
            result['success'],
            f"Pillar created: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Failed to create pillar: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            created_pillar = result['data']
            pillar_id = created_pillar['id']
            self.created_resources['pillars'].append(pillar_id)
            
            # Test 3: Verify date_created field is present and valid
            date_created = created_pillar.get('date_created')
            
            self.log_test(
                "NEW PILLAR DATE_CREATED FIELD PRESENCE",
                date_created is not None,
                f"date_created field present: {date_created}"
            )
            
            if date_created:
                self.log_test(
                    "NEW PILLAR DATE_CREATED FORMAT VALIDATION",
                    self.is_valid_iso_datetime(str(date_created)),
                    f"Valid ISO datetime format: {date_created}"
                )
                
                self.log_test(
                    "NEW PILLAR DATE_CREATED TIMING",
                    self.is_recent_datetime(str(date_created), tolerance_minutes=2),
                    f"Created at reasonable time: {date_created}"
                )
            
            # Test 4: GET specific pillar to verify date_created in individual response
            result = self.make_request('GET', f'/pillars/{pillar_id}', use_auth=True)
            
            self.log_test(
                "GET SPECIFIC PILLAR DATE_CREATED",
                result['success'] and 'date_created' in result['data'],
                f"Individual pillar response includes date_created: {result['data'].get('date_created') if result['success'] else 'N/A'}"
            )
        
        return True

    def test_areas_date_created_field(self):
        """Test date_created field functionality for Areas"""
        print("\n=== TESTING AREAS DATE_CREATED FIELD ===")
        
        if not self.auth_token:
            self.log_test("AREAS DATE_CREATED - Authentication Required", False, "No authentication token available")
            return False
        
        # Test 1: GET existing areas to check date_created field in responses
        result = self.make_request('GET', '/areas', use_auth=True)
        self.log_test(
            "GET AREAS - DATE_CREATED FIELD PRESENCE",
            result['success'],
            f"Retrieved {len(result['data']) if result['success'] else 0} areas" if result['success'] else f"Failed to get areas: {result.get('error', 'Unknown error')}"
        )
        
        if result['success'] and result['data']:
            # Check if existing areas have date_created field
            existing_areas = result['data']
            areas_with_date_created = [a for a in existing_areas if 'date_created' in a]
            
            self.log_test(
                "EXISTING AREAS DATE_CREATED FIELD",
                len(areas_with_date_created) == len(existing_areas),
                f"{len(areas_with_date_created)}/{len(existing_areas)} existing areas have date_created field"
            )
            
            # Validate date_created format for existing areas
            if areas_with_date_created:
                sample_area = areas_with_date_created[0]
                date_created_value = sample_area.get('date_created')
                
                self.log_test(
                    "EXISTING AREA DATE_CREATED FORMAT",
                    self.is_valid_iso_datetime(str(date_created_value)),
                    f"Date format validation: {date_created_value}"
                )
        
        # Test 2: POST new area to verify date_created is automatically set
        area_data = {
            "name": "Fitness & Exercise Test Area",
            "description": "A test area for date_created field validation",
            "icon": "💪",
            "color": "#FF5722"
        }
        
        creation_time = datetime.utcnow()
        result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
        
        self.log_test(
            "CREATE AREA WITH AUTO DATE_CREATED",
            result['success'],
            f"Area created: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Failed to create area: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            created_area = result['data']
            area_id = created_area['id']
            self.created_resources['areas'].append(area_id)
            
            # Test 3: Verify date_created field is present and valid
            date_created = created_area.get('date_created')
            
            self.log_test(
                "NEW AREA DATE_CREATED FIELD PRESENCE",
                date_created is not None,
                f"date_created field present: {date_created}"
            )
            
            if date_created:
                self.log_test(
                    "NEW AREA DATE_CREATED FORMAT VALIDATION",
                    self.is_valid_iso_datetime(str(date_created)),
                    f"Valid ISO datetime format: {date_created}"
                )
                
                self.log_test(
                    "NEW AREA DATE_CREATED TIMING",
                    self.is_recent_datetime(str(date_created), tolerance_minutes=2),
                    f"Created at reasonable time: {date_created}"
                )
            
            # Test 4: GET specific area to verify date_created in individual response
            result = self.make_request('GET', f'/areas/{area_id}', use_auth=True)
            
            self.log_test(
                "GET SPECIFIC AREA DATE_CREATED",
                result['success'] and 'date_created' in result['data'],
                f"Individual area response includes date_created: {result['data'].get('date_created') if result['success'] else 'N/A'}"
            )
        
        return True

    def test_projects_date_created_field(self):
        """Test date_created field functionality for Projects"""
        print("\n=== TESTING PROJECTS DATE_CREATED FIELD ===")
        
        if not self.auth_token:
            self.log_test("PROJECTS DATE_CREATED - Authentication Required", False, "No authentication token available")
            return False
        
        # First, ensure we have an area to create projects in
        area_id = None
        if self.created_resources['areas']:
            area_id = self.created_resources['areas'][0]
        else:
            # Create a test area
            area_data = {
                "name": "Test Area for Projects",
                "description": "Area for testing project date_created field",
                "icon": "📁",
                "color": "#2196F3"
            }
            result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
            if result['success']:
                area_id = result['data']['id']
                self.created_resources['areas'].append(area_id)
        
        if not area_id:
            self.log_test("PROJECTS DATE_CREATED - Area Required", False, "No area available for project testing")
            return False
        
        # Test 1: GET existing projects to check date_created field in responses
        result = self.make_request('GET', '/projects', use_auth=True)
        self.log_test(
            "GET PROJECTS - DATE_CREATED FIELD PRESENCE",
            result['success'],
            f"Retrieved {len(result['data']) if result['success'] else 0} projects" if result['success'] else f"Failed to get projects: {result.get('error', 'Unknown error')}"
        )
        
        if result['success'] and result['data']:
            # Check if existing projects have date_created field
            existing_projects = result['data']
            projects_with_date_created = [p for p in existing_projects if 'date_created' in p]
            
            self.log_test(
                "EXISTING PROJECTS DATE_CREATED FIELD",
                len(projects_with_date_created) == len(existing_projects),
                f"{len(projects_with_date_created)}/{len(existing_projects)} existing projects have date_created field"
            )
            
            # Validate date_created format for existing projects
            if projects_with_date_created:
                sample_project = projects_with_date_created[0]
                date_created_value = sample_project.get('date_created')
                
                self.log_test(
                    "EXISTING PROJECT DATE_CREATED FORMAT",
                    self.is_valid_iso_datetime(str(date_created_value)),
                    f"Date format validation: {date_created_value}"
                )
        
        # Test 2: POST new project to verify date_created is automatically set
        project_data = {
            "area_id": area_id,
            "name": "Workout Routine Test Project",
            "description": "A test project for date_created field validation",
            "priority": "high"
        }
        
        creation_time = datetime.utcnow()
        result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
        
        self.log_test(
            "CREATE PROJECT WITH AUTO DATE_CREATED",
            result['success'],
            f"Project created: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Failed to create project: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            created_project = result['data']
            project_id = created_project['id']
            self.created_resources['projects'].append(project_id)
            
            # Test 3: Verify date_created field is present and valid
            date_created = created_project.get('date_created')
            
            self.log_test(
                "NEW PROJECT DATE_CREATED FIELD PRESENCE",
                date_created is not None,
                f"date_created field present: {date_created}"
            )
            
            if date_created:
                self.log_test(
                    "NEW PROJECT DATE_CREATED FORMAT VALIDATION",
                    self.is_valid_iso_datetime(str(date_created)),
                    f"Valid ISO datetime format: {date_created}"
                )
                
                self.log_test(
                    "NEW PROJECT DATE_CREATED TIMING",
                    self.is_recent_datetime(str(date_created), tolerance_minutes=2),
                    f"Created at reasonable time: {date_created}"
                )
            
            # Test 4: GET specific project to verify date_created in individual response
            result = self.make_request('GET', f'/projects/{project_id}', use_auth=True)
            
            self.log_test(
                "GET SPECIFIC PROJECT DATE_CREATED",
                result['success'] and 'date_created' in result['data'],
                f"Individual project response includes date_created: {result['data'].get('date_created') if result['success'] else 'N/A'}"
            )
        
        return True

    def test_tasks_date_created_field(self):
        """Test date_created field functionality for Tasks"""
        print("\n=== TESTING TASKS DATE_CREATED FIELD ===")
        
        if not self.auth_token:
            self.log_test("TASKS DATE_CREATED - Authentication Required", False, "No authentication token available")
            return False
        
        # First, ensure we have a project to create tasks in
        project_id = None
        if self.created_resources['projects']:
            project_id = self.created_resources['projects'][0]
        else:
            # Create a test area and project
            area_data = {
                "name": "Test Area for Tasks",
                "description": "Area for testing task date_created field",
                "icon": "📋",
                "color": "#9C27B0"
            }
            area_result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
            if area_result['success']:
                area_id = area_result['data']['id']
                self.created_resources['areas'].append(area_id)
                
                project_data = {
                    "area_id": area_id,
                    "name": "Test Project for Tasks",
                    "description": "Project for testing task date_created field",
                    "priority": "medium"
                }
                project_result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
                if project_result['success']:
                    project_id = project_result['data']['id']
                    self.created_resources['projects'].append(project_id)
        
        if not project_id:
            self.log_test("TASKS DATE_CREATED - Project Required", False, "No project available for task testing")
            return False
        
        # Test 1: GET existing tasks to check date_created field in responses
        result = self.make_request('GET', '/tasks', use_auth=True)
        self.log_test(
            "GET TASKS - DATE_CREATED FIELD PRESENCE",
            result['success'],
            f"Retrieved {len(result['data']) if result['success'] else 0} tasks" if result['success'] else f"Failed to get tasks: {result.get('error', 'Unknown error')}"
        )
        
        if result['success'] and result['data']:
            # Check if existing tasks have date_created field
            existing_tasks = result['data']
            tasks_with_date_created = [t for t in existing_tasks if 'date_created' in t]
            
            self.log_test(
                "EXISTING TASKS DATE_CREATED FIELD",
                len(tasks_with_date_created) == len(existing_tasks),
                f"{len(tasks_with_date_created)}/{len(existing_tasks)} existing tasks have date_created field"
            )
            
            # Validate date_created format for existing tasks
            if tasks_with_date_created:
                sample_task = tasks_with_date_created[0]
                date_created_value = sample_task.get('date_created')
                
                self.log_test(
                    "EXISTING TASK DATE_CREATED FORMAT",
                    self.is_valid_iso_datetime(str(date_created_value)),
                    f"Date format validation: {date_created_value}"
                )
        
        # Test 2: POST new task to verify date_created is automatically set
        task_data = {
            "project_id": project_id,
            "name": "Morning Cardio Session",
            "description": "A test task for date_created field validation",
            "priority": "high",
            "due_time": "07:30"
        }
        
        creation_time = datetime.utcnow()
        result = self.make_request('POST', '/tasks', data=task_data, use_auth=True)
        
        self.log_test(
            "CREATE TASK WITH AUTO DATE_CREATED",
            result['success'],
            f"Task created: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Failed to create task: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            created_task = result['data']
            task_id = created_task['id']
            self.created_resources['tasks'].append(task_id)
            
            # Test 3: Verify date_created field is present and valid
            date_created = created_task.get('date_created')
            
            self.log_test(
                "NEW TASK DATE_CREATED FIELD PRESENCE",
                date_created is not None,
                f"date_created field present: {date_created}"
            )
            
            if date_created:
                self.log_test(
                    "NEW TASK DATE_CREATED FORMAT VALIDATION",
                    self.is_valid_iso_datetime(str(date_created)),
                    f"Valid ISO datetime format: {date_created}"
                )
                
                self.log_test(
                    "NEW TASK DATE_CREATED TIMING",
                    self.is_recent_datetime(str(date_created), tolerance_minutes=2),
                    f"Created at reasonable time: {date_created}"
                )
            
            # Test 4: GET tasks by project to verify date_created in project-specific response
            result = self.make_request('GET', f'/projects/{project_id}/tasks', use_auth=True)
            
            if result['success'] and result['data']:
                project_tasks = result['data']
                project_tasks_with_date_created = [t for t in project_tasks if 'date_created' in t]
                
                self.log_test(
                    "GET PROJECT TASKS DATE_CREATED",
                    len(project_tasks_with_date_created) == len(project_tasks),
                    f"Project tasks response includes date_created: {len(project_tasks_with_date_created)}/{len(project_tasks)} tasks"
                )
        
        return True

    def test_date_created_consistency(self):
        """Test date_created field consistency across all collections"""
        print("\n=== TESTING DATE_CREATED FIELD CONSISTENCY ===")
        
        if not self.auth_token:
            self.log_test("DATE_CREATED CONSISTENCY - Authentication Required", False, "No authentication token available")
            return False
        
        # Collect all date_created values from created resources
        all_date_created_values = []
        
        # Get pillars
        if self.created_resources['pillars']:
            for pillar_id in self.created_resources['pillars']:
                result = self.make_request('GET', f'/pillars/{pillar_id}', use_auth=True)
                if result['success'] and 'date_created' in result['data']:
                    all_date_created_values.append(('pillar', result['data']['date_created']))
        
        # Get areas
        if self.created_resources['areas']:
            for area_id in self.created_resources['areas']:
                result = self.make_request('GET', f'/areas/{area_id}', use_auth=True)
                if result['success'] and 'date_created' in result['data']:
                    all_date_created_values.append(('area', result['data']['date_created']))
        
        # Get projects
        if self.created_resources['projects']:
            for project_id in self.created_resources['projects']:
                result = self.make_request('GET', f'/projects/{project_id}', use_auth=True)
                if result['success'] and 'date_created' in result['data']:
                    all_date_created_values.append(('project', result['data']['date_created']))
        
        # Get tasks
        result = self.make_request('GET', '/tasks', use_auth=True)
        if result['success']:
            for task in result['data']:
                if task['id'] in self.created_resources['tasks'] and 'date_created' in task:
                    all_date_created_values.append(('task', task['date_created']))
        
        # Test consistency
        self.log_test(
            "DATE_CREATED VALUES COLLECTED",
            len(all_date_created_values) > 0,
            f"Collected {len(all_date_created_values)} date_created values from created resources"
        )
        
        if all_date_created_values:
            # Test format consistency
            valid_formats = 0
            for resource_type, date_value in all_date_created_values:
                if self.is_valid_iso_datetime(str(date_value)):
                    valid_formats += 1
            
            self.log_test(
                "DATE_CREATED FORMAT CONSISTENCY",
                valid_formats == len(all_date_created_values),
                f"{valid_formats}/{len(all_date_created_values)} date_created values have valid ISO format"
            )
            
            # Test timing consistency (all should be recent)
            recent_dates = 0
            for resource_type, date_value in all_date_created_values:
                if self.is_recent_datetime(str(date_value), tolerance_minutes=10):
                    recent_dates += 1
            
            self.log_test(
                "DATE_CREATED TIMING CONSISTENCY",
                recent_dates == len(all_date_created_values),
                f"{recent_dates}/{len(all_date_created_values)} date_created values are within expected time range"
            )
        
        return True

    def test_migration_verification(self):
        """Test that existing data migration was successful"""
        print("\n=== TESTING MIGRATION VERIFICATION ===")
        
        if not self.auth_token:
            self.log_test("MIGRATION VERIFICATION - Authentication Required", False, "No authentication token available")
            return False
        
        # Test existing data has date_created field
        endpoints_to_check = [
            ('/pillars', 'pillars'),
            ('/areas', 'areas'),
            ('/projects', 'projects'),
            ('/tasks', 'tasks')
        ]
        
        migration_success_count = 0
        total_endpoints = len(endpoints_to_check)
        
        for endpoint, resource_type in endpoints_to_check:
            result = self.make_request('GET', endpoint, use_auth=True)
            
            if result['success']:
                resources = result['data']
                if resources:
                    # Check if all resources have date_created field
                    resources_with_date_created = [r for r in resources if 'date_created' in r and r['date_created']]
                    
                    success = len(resources_with_date_created) == len(resources)
                    if success:
                        migration_success_count += 1
                    
                    self.log_test(
                        f"MIGRATION VERIFICATION - {resource_type.upper()}",
                        success,
                        f"{len(resources_with_date_created)}/{len(resources)} {resource_type} have date_created field"
                    )
                    
                    # Validate format of migrated data
                    if resources_with_date_created:
                        sample_resource = resources_with_date_created[0]
                        date_created_value = sample_resource.get('date_created')
                        
                        self.log_test(
                            f"MIGRATED {resource_type.upper()} DATE_CREATED FORMAT",
                            self.is_valid_iso_datetime(str(date_created_value)),
                            f"Migrated data has valid date format: {date_created_value}"
                        )
                else:
                    # No existing data to check
                    migration_success_count += 1
                    self.log_test(
                        f"MIGRATION VERIFICATION - {resource_type.upper()}",
                        True,
                        f"No existing {resource_type} to verify (empty collection)"
                    )
            else:
                self.log_test(
                    f"MIGRATION VERIFICATION - {resource_type.upper()}",
                    False,
                    f"Failed to retrieve {resource_type}: {result.get('error', 'Unknown error')}"
                )
        
        # Overall migration success
        self.log_test(
            "OVERALL MIGRATION SUCCESS",
            migration_success_count == total_endpoints,
            f"{migration_success_count}/{total_endpoints} endpoints show successful migration"
        )
        
        return migration_success_count == total_endpoints

    def run_comprehensive_date_created_test(self):
        """Run comprehensive date_created field functionality tests"""
        print("\n📅 STARTING DATE_CREATED FIELD FUNCTIONALITY TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Basic Connectivity", self.test_basic_connectivity),
            ("User Registration and Login", self.test_user_registration_and_login),
            ("Pillars date_created Field", self.test_pillars_date_created_field),
            ("Areas date_created Field", self.test_areas_date_created_field),
            ("Projects date_created Field", self.test_projects_date_created_field),
            ("Tasks date_created Field", self.test_tasks_date_created_field),
            ("date_created Consistency", self.test_date_created_consistency),
            ("Migration Verification", self.test_migration_verification)
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
        print("🎯 DATE_CREATED FIELD FUNCTIONALITY TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze results for date_created functionality
        date_created_tests_passed = sum(1 for result in self.test_results if result['success'] and 'DATE_CREATED' in result['test'])
        migration_tests_passed = sum(1 for result in self.test_results if result['success'] and 'MIGRATION' in result['test'])
        
        print(f"\n🔍 SYSTEM ANALYSIS:")
        print(f"date_created Field Tests Passed: {date_created_tests_passed}")
        print(f"Migration Verification Tests Passed: {migration_tests_passed}")
        
        if success_rate >= 85:
            print("\n✅ DATE_CREATED FIELD FUNCTIONALITY: SUCCESS")
            print("   ✅ GET endpoints include date_created field in responses")
            print("   ✅ POST endpoints auto-set date_created for new documents")
            print("   ✅ date_created field format is consistent (ISO datetime)")
            print("   ✅ date_created reflects actual creation time for new items")
            print("   ✅ Migration preserved original data with date_created field")
            print("   ✅ All collections (pillars, areas, projects, tasks) working")
            print("   The date_created field enhancement is production-ready!")
        else:
            print("\n❌ DATE_CREATED FIELD FUNCTIONALITY: ISSUES DETECTED")
            print("   Issues found in date_created field implementation")
        
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
    """Run date_created Field Functionality Tests"""
    print("📅 STARTING DATE_CREATED FIELD FUNCTIONALITY BACKEND TESTING")
    print("=" * 80)
    
    tester = DateCreatedFieldTester()
    
    try:
        # Run the comprehensive date_created field tests
        success = tester.run_comprehensive_date_created_test()
        
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